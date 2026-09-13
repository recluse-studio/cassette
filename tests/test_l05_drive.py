# test_l05_drive.py — L05 mounted-APFS drive selection and store-root proof for Q44/Q49/Q53; depends on errors.py, store.py.
"""Exercise the store-owned L05 drive path on a disposable macOS APFS image."""

import plistlib
from pathlib import Path
import platform
import shutil
import stat
import subprocess

import pytest

from errors import CassetteError
from store import (
    CapacityCoordinator,
    compare_inventory,
    create_selected_root,
    digest_bytes,
    inventory_step,
    list_external_apfs_volumes,
    revalidate_external_apfs_volume,
    select_external_apfs_volume,
    verify_campaign_artifact,
    write_campaign_artifact,
)


pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="L05 drive discovery requires macOS APFS and its native volume interfaces",
)


def _attached_apfs_image(tmp_path: Path) -> tuple[Path, Path]:
    image = tmp_path / "cassette-l05.sparseimage"
    subprocess.run(
        [
            "/usr/bin/hdiutil", "create", "-size", "64m", "-fs", "APFS",
            "-volname", "CassetteL05", "-type", "SPARSE", "-quiet", str(image),
        ],
        check=True,
        capture_output=True,
    )
    attached = subprocess.run(
        ["/usr/bin/hdiutil", "attach", "-nobrowse", "-plist", str(image)],
        check=True,
        capture_output=True,
    )
    records = plistlib.loads(attached.stdout)["system-entities"]
    mount = next(Path(record["mount-point"]) for record in records if "mount-point" in record)
    return image, mount


def test_q41_q44_q49_q53_l05_discovers_nested_root_and_revalidates_apfs_volume(tmp_path):
    """Q41/Q44/Q49/Q53: an APFS image proves exact nested-root containment, denial, creation, and disconnection refusal."""

    image, mount = _attached_apfs_image(tmp_path)
    attached = True
    original_mode = stat.S_IMODE(mount.stat().st_mode)
    try:
        volume = next(item for item in list_external_apfs_volumes() if item.mount_path == str(mount))
        assert volume.filesystem == "apfs"
        assert volume.volume_uuid
        assert volume.available_bytes > 0

        selected = select_external_apfs_volume(volume.volume_uuid)
        assert selected.volume == volume
        assert selected.writer.executable
        assert selected.writer.pid > 0

        parent = mount / "drewwiberg-lacie"
        parent.mkdir()
        parent.chmod(0o755)
        preserved = parent / "preserved.txt"
        preserved.write_bytes(b"keep")
        (mount / "linked-parent").symlink_to(parent, target_is_directory=True)
        mount.chmod(0o555)
        try:
            assert stat.S_IMODE(mount.stat().st_mode) == 0o555
            assert parent.stat().st_mode & stat.S_IWUSR
            with pytest.raises(CassetteError) as denied:
                create_selected_root(selected, "Denied", operation_id="l05-apfs-image-denied")
            assert denied.value.code == "CAPABILITY_MISMATCH"
            assert "PermissionError errno 13" in denied.value.detail

            before = inventory_step(mount, excluded=("drewwiberg-lacie/Cassette",))
            assert before["status"] == "PASS"
            assert before["inventory"] == {
                "drewwiberg-lacie": {"type": "directory", "logical_bytes": len(b"keep")},
                "linked-parent": {"type": "link", "logical_bytes": 0},
            }
            cartridge, cartridge_uuid = create_selected_root(
                selected,
                "drewwiberg-lacie/Cassette",
                operation_id="l05-apfs-image",
                cartridge_uuid="eff24757-de64-4a3c-8355-cde95ad6014d",
            )
            assert cartridge == parent / "Cassette"
            assert cartridge_uuid == "eff24757-de64-4a3c-8355-cde95ad6014d"
            assert (cartridge / "cartridge.json").is_file()
            assert preserved.read_bytes() == b"keep"
            after = inventory_step(mount, excluded=("drewwiberg-lacie/Cassette",))
            compare_inventory(before["inventory"], after["inventory"])

            probe_payload = bytes(4096)
            probe_digest = digest_bytes(probe_payload)
            with pytest.raises(CassetteError) as absent:
                verify_campaign_artifact(
                    cartridge, "l05-probe", "durability.bin", probe_digest, len(probe_payload)
                )
            assert absent.value.code == "ROOT_INVALID"
            probe = write_campaign_artifact(
                CapacityCoordinator(cartridge), "l05-probe", "durability.bin", probe_payload
            )
            assert verify_campaign_artifact(
                cartridge, "l05-probe", "durability.bin", probe_digest, len(probe_payload)
            ) == {
                "attempt": "l05-probe",
                "name": "durability.bin",
                "digest": probe_digest,
                "bytes": len(probe_payload),
            }
            hard_link = probe.with_name("durability-link.bin")
            hard_link.hardlink_to(probe)
            with pytest.raises(CassetteError) as multiply_linked:
                verify_campaign_artifact(
                    cartridge, "l05-probe", "durability.bin", probe_digest, len(probe_payload)
                )
            assert multiply_linked.value.code == "ROOT_INVALID"
            hard_link.unlink()
            linked_attempt = probe.parent.parent / "linked-probe"
            linked_attempt.symlink_to(probe.parent, target_is_directory=True)
            with pytest.raises(CassetteError) as linked:
                verify_campaign_artifact(
                    cartridge, "linked-probe", "durability.bin", probe_digest, len(probe_payload)
                )
            assert linked.value.code == "ROOT_INVALID"
            linked_attempt.unlink()
            probe.write_bytes(b"x" * len(probe_payload))
            with pytest.raises(CassetteError) as corrupt:
                verify_campaign_artifact(
                    cartridge, "l05-probe", "durability.bin", probe_digest, len(probe_payload)
                )
            assert corrupt.value.code == "ROOT_INVALID"
            probe.unlink()

            for destination, code in (
                ("../outside", "INVALID_REQUEST"),
                ("linked-parent/Cassette", "CONTAINMENT_REJECTED"),
            ):
                with pytest.raises(CassetteError) as rejected:
                    create_selected_root(selected, destination, operation_id="l05-contained")
                assert rejected.value.code == code
        finally:
            mount.chmod(original_mode)
        assert revalidate_external_apfs_volume(selected).volume.volume_uuid == volume.volume_uuid

        subprocess.run(
            ["/usr/bin/hdiutil", "detach", str(mount), "-quiet"],
            check=True,
            capture_output=True,
        )
        attached = False
        with pytest.raises(CassetteError) as disconnected:
            revalidate_external_apfs_volume(selected)
        assert disconnected.value.code == "CARTRIDGE_DISCONNECTED"
    finally:
        if attached:
            subprocess.run(
                ["/usr/bin/hdiutil", "detach", str(mount), "-quiet"],
                check=True,
                capture_output=True,
            )
        if image.is_dir():
            shutil.rmtree(image)
        else:
            image.unlink(missing_ok=True)
