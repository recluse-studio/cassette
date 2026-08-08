# test_s08_lifecycle.py — APFS removable-volume lifecycle proof for Q49; depends on errors.py, store.py.
"""S08 proves that remounts recover identity while every invalidated access dies before I/O."""

import fcntl
import json
import os
from pathlib import Path
import platform
import plistlib
import shutil
import subprocess

import pytest

from errors import CassetteError
from store import (
    ArtifactIdentity,
    CartridgeLifecycle,
    IdentityTuple,
    commit_generation,
    digest_bytes,
    import_safetensors,
    initialize_cartridge,
    page_locations,
    read_tensor,
)


pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="S08 requires arm64 macOS, APFS disk images, diskutil, and F_FULLFSYNC",
)

_CARTRIDGE_UUID = "11111111-2222-4333-8444-555555555555"
_OTHER_UUID = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"


def _create_image(base: Path, volume_name: str) -> Path:
    subprocess.run(
        [
            "hdiutil", "create", "-size", "64m", "-fs", "APFS", "-volname", volume_name,
            "-type", "SPARSE", "-quiet", str(base),
        ],
        check=True,
        capture_output=True,
    )
    return base.with_suffix(".sparseimage")


def _attach(image: Path, mount: Path, *, read_only: bool = False) -> None:
    mount.mkdir(exist_ok=True)
    command = ["hdiutil", "attach", "-nobrowse", "-mountpoint", str(mount)]
    if read_only:
        command.append("-readonly")
    subprocess.run([*command, str(image), "-quiet"], check=True, capture_output=True)


def _detach(mount: Path) -> None:
    subprocess.run(["hdiutil", "detach", str(mount), "-quiet"], check=True, capture_output=True)


def _volume_uuid(mount: Path) -> str:
    result = subprocess.run(
        ["diskutil", "info", "-plist", str(mount)], check=True, capture_output=True
    )
    value = plistlib.loads(result.stdout)["VolumeUUID"]
    assert isinstance(value, str)
    return value


def _fullsync(path: Path) -> None:
    with path.open("rb") as handle:
        os.fsync(handle.fileno())
        fcntl.fcntl(handle.fileno(), fcntl.F_FULLFSYNC)


def _write_safetensors(path: Path, payload: bytes) -> None:
    header = {
        "__metadata__": {"fixture": "S08"},
        "weight": {"dtype": "U8", "shape": [len(payload)], "data_offsets": [0, len(payload)]},
    }
    encoded = json.dumps(header, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 8)
    path.write_bytes(len(encoded).to_bytes(8, "little") + encoded + payload)


def _identity(path: Path) -> IdentityTuple:
    return IdentityTuple(
        revision_kind="source",
        source_kind="huggingface",
        source_alias="fixture/s08@main",
        canonical_locator="fixture/s08",
        requested_revision="main",
        immutable_revision="git-sha1:" + "8" * 40,
        artifacts=(ArtifactIdentity(path.name, path.stat().st_size, digest_bytes(path.read_bytes())),),
        format_versions=(("safetensors", "0.6.2"),),
        tensor_index_digest=digest_bytes(b"S08 index"),
        config_digest=digest_bytes(b"S08 config"),
        architecture="S08LifecycleFixture",
        operator_set=("matmul",),
        tokenizer_digest=digest_bytes(b"S08 tokenizer"),
        processor_digest=digest_bytes(b"S08 processor"),
        template_digest=digest_bytes(b"S08 template"),
        precision_scheme="u8-fixture",
        license_digest=digest_bytes(b"S08 license"),
        parent_ids=(),
        transform_manifest_digest=None,
    )


def _expect_stale(lifecycle: CartridgeLifecycle, access) -> None:
    with pytest.raises(CassetteError) as failure:
        lifecycle.resolve(access)
    assert failure.value.code == "CARTRIDGE_DISCONNECTED"


def test_q49_disconnect_remount_identity_readonly_and_replacement(tmp_path):
    """Q49 acceptance: every removable-volume event invalidates access, then exact remount verification alone restores eligible operations."""

    source_image = _create_image(tmp_path / "cassette-s08-source", "CASSETTES08SOURCE")
    replacement_image = _create_image(
        tmp_path / "cassette-s08-replacement", "CASSETTES08REPLACEMENT"
    )
    mount_a = tmp_path / "mount-a"
    mount_b = tmp_path / "mount-b"
    replacement_mount = tmp_path / "mount-replacement"
    mounted = set()

    def attach(image: Path, mount: Path, *, read_only: bool = False) -> None:
        _attach(image, mount, read_only=read_only)
        mounted.add(mount)

    def detach(mount: Path) -> None:
        _detach(mount)
        mounted.discard(mount)

    try:
        attach(source_image, mount_a)
        source = tmp_path / "source.safetensors"
        expected = b"S08 removable cartridge bytes"
        _write_safetensors(source, expected)
        cartridge = mount_a / "cartridge"
        root = import_safetensors({source.name: source}, cartridge, _identity(source))
        pin = commit_generation(cartridge, "s08-initial-generation", root, expected_parent_root=None)
        assert initialize_cartridge(cartridge, _CARTRIDGE_UUID) == _CARTRIDGE_UUID
        source_filesystem = _volume_uuid(mount_a)

        lifecycle = CartridgeLifecycle(_CARTRIDGE_UUID)
        mounted_identity = lifecycle.mount(cartridge, source_filesystem)
        assert lifecycle.state == "MOUNTED_VERIFIED"
        assert mounted_identity.cartridge_uuid == _CARTRIDGE_UUID
        assert mounted_identity.filesystem_uuid == source_filesystem.lower()
        assert (mounted_identity.root_generation, mounted_identity.root_digest) == (
            pin.generation, root,
        )
        access = lifecycle.begin("initial-read", write=False)
        assert read_tensor(lifecycle.resolve(access), root, "weight") == expected
        assert lifecycle.finish(access) == mounted_identity

        lifecycle.unmount()
        _expect_stale(lifecycle, access)
        detach(mount_a)
        attach(source_image, mount_b)
        cartridge = mount_b / "cartridge"
        assert lifecycle.mount(cartridge, _volume_uuid(mount_b)) == mounted_identity

        for event in ("port_migration", "bus_reset"):
            access = lifecycle.begin(f"before-{event}", write=False)
            lifecycle.event(event)
            assert lifecycle.state == "REVALIDATING"
            _expect_stale(lifecycle, access)
            detach(mount_b)
            attach(source_image, mount_a)
            cartridge = mount_a / "cartridge"
            assert lifecycle.mount(cartridge, _volume_uuid(mount_a)).root_digest == root
            detach(mount_a)
            attach(source_image, mount_b)
            cartridge = mount_b / "cartridge"
            lifecycle.event("port_migration")
            assert lifecycle.mount(cartridge, _volume_uuid(mount_b)).root_digest == root

        access = lifecycle.begin("before-sleep", write=False)
        lifecycle.event("sleep")
        assert lifecycle.state == "SLEEPING"
        _expect_stale(lifecycle, access)
        detach(mount_b)
        attach(source_image, mount_a)
        lifecycle.event("wake")
        assert lifecycle.state == "REVALIDATING"
        cartridge = mount_a / "cartridge"
        lifecycle.mount(cartridge, _volume_uuid(mount_a))

        access = lifecycle.begin("before-disconnect", write=True)
        lifecycle.event("disconnect")
        assert lifecycle.state == "DISCONNECTED"
        _expect_stale(lifecycle, access)
        detach(mount_a)
        attach(source_image, mount_b)
        cartridge = mount_b / "cartridge"
        lifecycle.mount(cartridge, _volume_uuid(mount_b))

        root_path = cartridge / "roots" / root.removeprefix("blake3:")
        root_bytes = root_path.read_bytes()
        lifecycle.unmount()
        root_path.write_bytes(b"corrupt root")
        _fullsync(root_path)
        with pytest.raises(CassetteError) as corrupt_root:
            lifecycle.mount(cartridge, _volume_uuid(mount_b))
        assert corrupt_root.value.code == "ROOT_INVALID"
        assert lifecycle.state == "FAILED"
        root_path.write_bytes(root_bytes)
        _fullsync(root_path)
        assert lifecycle.mount(cartridge, _volume_uuid(mount_b)).root_digest == root

        lifecycle.unmount()
        location = page_locations(cartridge, root)[0]
        segment_path = cartridge / "segments" / location.segment_id.removeprefix("blake3:")
        segment_bytes = segment_path.read_bytes()
        segment_path.write_bytes(bytes([segment_bytes[0] ^ 1]) + segment_bytes[1:])
        _fullsync(segment_path)
        with pytest.raises(CassetteError) as corrupt_page:
            lifecycle.mount(cartridge, _volume_uuid(mount_b))
        assert corrupt_page.value.code == "PAGE_CORRUPT"
        assert lifecycle.state == "FAILED"
        segment_path.write_bytes(segment_bytes)
        _fullsync(segment_path)
        assert lifecycle.mount(cartridge, _volume_uuid(mount_b)).root_digest == root

        lifecycle.unmount()
        marker = cartridge / "cartridge.json"
        marker_bytes = marker.read_bytes()
        marker.write_bytes(b'{"cartridge_uuid":"' + _OTHER_UUID.encode() + b'"}')
        _fullsync(marker)
        with pytest.raises(CassetteError) as wrong_logical:
            lifecycle.mount(cartridge, _volume_uuid(mount_b))
        assert wrong_logical.value.code == "CARTRIDGE_IDENTITY_MISMATCH"
        assert lifecycle.state == "FAILED"
        marker.write_bytes(marker_bytes)
        _fullsync(marker)
        lifecycle.mount(cartridge, _volume_uuid(mount_b))

        attach(replacement_image, replacement_mount)
        replacement_cartridge = replacement_mount / "cartridge"
        shutil.copytree(cartridge, replacement_cartridge)
        replacement_filesystem = _volume_uuid(replacement_mount)
        assert replacement_filesystem.lower() != source_filesystem.lower()
        detach(replacement_mount)
        lifecycle.unmount()
        detach(mount_b)

        attach(replacement_image, replacement_mount)
        with pytest.raises(CassetteError) as wrong_physical:
            lifecycle.mount(replacement_cartridge, replacement_filesystem)
        assert wrong_physical.value.code == "CARTRIDGE_IDENTITY_MISMATCH"
        assert lifecycle.state == "FAILED"
        replacement_identity = lifecycle.mount(
            replacement_cartridge, replacement_filesystem, replacement=True
        )
        assert replacement_identity.cartridge_uuid == _CARTRIDGE_UUID
        assert replacement_identity.filesystem_uuid == replacement_filesystem.lower()
        assert replacement_identity.root_digest == root

        lifecycle.unmount()
        detach(replacement_mount)
        attach(replacement_image, replacement_mount, read_only=True)
        replacement_cartridge = replacement_mount / "cartridge"
        lifecycle.mount(replacement_cartridge, _volume_uuid(replacement_mount))
        assert lifecycle.state == "READ_ONLY"
        sentinel = replacement_cartridge / "forbidden-write"
        with pytest.raises(CassetteError) as read_only:
            lifecycle.begin("forbidden-write", write=True)
        assert read_only.value.code == "CARTRIDGE_READ_ONLY"
        assert not sentinel.exists()
        access = lifecycle.begin("readonly-read", write=False)
        assert read_tensor(lifecycle.resolve(access), root, "weight") == expected
        lifecycle.finish(access)
        assert lifecycle.state == "READ_ONLY"
        lifecycle.unmount()

        allowed = {
            "UNMOUNTED": {"MOUNTED_UNVERIFIED"},
            "MOUNTED_UNVERIFIED": {"MOUNTED_VERIFIED", "READ_ONLY", "DISCONNECTED", "FAILED"},
            "MOUNTED_VERIFIED": {"ACTIVE", "UNMOUNTED", "DISCONNECTED", "SLEEPING", "REVALIDATING", "FAILED"},
            "ACTIVE": {"QUIESCING", "DISCONNECTED", "SLEEPING", "REVALIDATING", "FAILED"},
            "QUIESCING": {"MOUNTED_VERIFIED", "READ_ONLY", "DISCONNECTED", "SLEEPING", "REVALIDATING", "FAILED"},
            "DISCONNECTED": {"REVALIDATING"},
            "SLEEPING": {"REVALIDATING"},
            "REVALIDATING": {"MOUNTED_VERIFIED", "READ_ONLY", "DISCONNECTED", "SLEEPING", "FAILED"},
            "READ_ONLY": {"UNMOUNTED", "DISCONNECTED", "SLEEPING", "REVALIDATING", "FAILED"},
            "FAILED": {"UNMOUNTED", "DISCONNECTED", "REVALIDATING"},
        }
        assert all(after in allowed[before] for before, after in lifecycle.transitions)
        assert set(sum(([before, after] for before, after in lifecycle.transitions), [])) == set(allowed)
    finally:
        for mount in tuple(mounted):
            subprocess.run(
                ["hdiutil", "detach", str(mount), "-quiet"], check=False, capture_output=True
            )
