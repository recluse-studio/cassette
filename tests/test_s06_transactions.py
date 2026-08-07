# test_s06_transactions.py — F1 process-death and APFS-remount proof for Q25/Q60/Q73; depends on errors.py, store.py.
"""S06 proves that only a fully verified generation becomes callable and every prior root survives."""

import fcntl
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

import pytest

from errors import CassetteError
from store import (
    ArtifactIdentity,
    IdentityTuple,
    TransactionContext,
    advance_generation,
    begin_generation,
    collect_garbage,
    commit_generation,
    digest_bytes,
    import_safetensors,
    load_root,
    page_locations,
    pin_generation,
    read_tensor,
    recover_generation,
    rollback_generation,
    transaction_state,
)


def _write_safetensors(path: Path, payload: bytes) -> None:
    header = {
        "__metadata__": {"fixture": "S06"},
        "weight": {"dtype": "U8", "shape": [len(payload)], "data_offsets": [0, len(payload)]},
    }
    encoded = json.dumps(header, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 8)
    path.write_bytes(len(encoded).to_bytes(8, "little") + encoded + payload)


def _identity(path: Path, label: str, parent_id: str | None = None) -> IdentityTuple:
    derived = parent_id is not None
    return IdentityTuple(
        revision_kind="tuned" if derived else "source",
        source_kind="huggingface",
        source_alias=f"fixture/{label}@main",
        canonical_locator=f"fixture/{label}",
        requested_revision="main",
        immutable_revision="git-sha1:" + ("2" if derived else "1") * 40,
        artifacts=(ArtifactIdentity(path.name, path.stat().st_size, digest_bytes(path.read_bytes())),),
        format_versions=(("safetensors", "0.6.2"),),
        tensor_index_digest=digest_bytes(f"{label}:index".encode()),
        config_digest=digest_bytes(f"{label}:config".encode()),
        architecture="S06TransactionFixture",
        operator_set=("matmul",),
        tokenizer_digest=digest_bytes(b"S06 tokenizer"),
        processor_digest=digest_bytes(b"S06 processor"),
        template_digest=digest_bytes(b"S06 template"),
        precision_scheme="u8-fixture",
        license_digest=digest_bytes(b"S06 license"),
        parent_ids=(parent_id,) if parent_id else (),
        transform_manifest_digest=digest_bytes(b"S06 tuning transform") if derived else None,
    )


def _attach(image: Path, mount: Path) -> None:
    mount.mkdir(exist_ok=True)
    subprocess.run(
        ["hdiutil", "attach", "-nobrowse", "-mountpoint", str(mount), str(image)],
        check=True,
        capture_output=True,
    )


def _detach(mount: Path) -> None:
    subprocess.run(["hdiutil", "detach", str(mount), "-quiet"], check=True, capture_output=True)


def _remount(image: Path, mount: Path) -> None:
    _detach(mount)
    _attach(image, mount)


def _kill_after_transition(
    action: str,
    mount: Path,
    transaction_id: str,
    expected_state: str,
    candidate_root: str = "-",
    expected_parent_root: str = "-",
    reader_root: str = "-",
    reader_bytes: bytes = b"",
) -> None:
    environment = os.environ.copy()
    repository = str(Path(__file__).resolve().parent.parent)
    environment["PYTHONPATH"] = repository + os.pathsep + environment.get("PYTHONPATH", "")
    reader = subprocess.Popen(
        [
            sys.executable,
            "-B",
            str(Path(__file__).resolve()),
            "_s06_reader",
            str(mount / "cartridge"),
            reader_root,
            reader_bytes.hex(),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    )
    if reader.stdout.readline().strip() != "READY":
        reader.kill()
        _, reader_error = reader.communicate(timeout=10)
        raise AssertionError(reader_error)
    process = subprocess.Popen(
        [
            sys.executable,
            "-B",
            str(Path(__file__).resolve()),
            "_s06_child",
            action,
            str(mount / "cartridge"),
            transaction_id,
            candidate_root,
            expected_parent_root,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    )
    try:
        observed = process.stdout.readline().strip()
        if observed != expected_state:
            process.kill()
            _, process_error = process.communicate(timeout=10)
            raise AssertionError(process_error)
        process.kill()
        assert process.wait(timeout=10) == -signal.SIGKILL
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        reader_output, reader_error = reader.communicate(timeout=10)
        assert reader.returncode == 0 and reader_output.strip() == "OK", reader_error


def _fixture_fullsync(path: Path) -> None:
    with path.open("rb") as handle:
        os.fsync(handle.fileno())
        fcntl.fcntl(handle.fileno(), fcntl.F_FULLFSYNC)


def test_q25_q60_q73_process_death_remount_resume_and_reader_isolation(tmp_path):
    """Q25/Q60/Q73 acceptance: kill every durable transition, remount, resume exactly, and preserve pinned and rollback roots."""

    assert platform.system() == "Darwin" and platform.machine() == "arm64"
    image_base = tmp_path / "cassette-s06"
    subprocess.run(
        [
            "hdiutil", "create", "-size", "64m", "-fs", "APFS", "-volname", "CASSETTES06",
            "-type", "SPARSE", "-quiet", str(image_base),
        ],
        check=True,
        capture_output=True,
    )
    image = image_base.with_suffix(".sparseimage")
    mount = tmp_path / "mount"
    _attach(image, mount)
    try:
        parent_bytes = b"parent-generation-bytes"
        child_bytes = b"exact-child-generation"
        parent_source = tmp_path / "parent.safetensors"
        child_source = tmp_path / "child.safetensors"
        _write_safetensors(parent_source, parent_bytes)
        _write_safetensors(child_source, child_bytes)
        cartridge = mount / "cartridge"
        parent_material = _identity(parent_source, "parent")
        parent_root = import_safetensors(
            {parent_source.name: parent_source}, cartridge, parent_material
        )
        parent_id = load_root(cartridge, parent_root)["identity"]
        child_material = _identity(child_source, "child", parent_id)
        child_root = import_safetensors({child_source.name: child_source}, cartridge, child_material)
        parent_pin = commit_generation(
            cartridge, "publish-parent", parent_root, expected_parent_root=None
        )
        assert parent_pin.generation == 1
        _remount(image, mount)
        assert recover_generation(cartridge) == parent_pin

        _kill_after_transition(
            "begin", mount, "publish-child", "PREPARE:0:0", child_root, parent_root,
            parent_root, parent_bytes,
        )
        _remount(image, mount)
        assert transaction_state(cartridge, "publish-child").state == "PREPARE"
        assert recover_generation(cartridge) == parent_pin

        segment_count = len({
            location.segment_id for location in page_locations(cartridge, child_root)
        })
        dependency_boundaries = segment_count + 2 + 3
        final_dependency_cursor = dependency_boundaries + 1
        transitions = (
            "WRITE_TEMP:0:0",
            "READBACK_HASH:0:0",
            "JOURNAL_PAGE:0:0",
            "WRITE_CANDIDATE_ROOT:0:0",
            "FULLFSYNC:0:0",
            *(f"FULLFSYNC:{cursor}:0" for cursor in range(1, final_dependency_cursor + 1)),
            f"SWAP_GENERATION_POINTER:{final_dependency_cursor}:0",
            f"FULLFSYNC:{final_dependency_cursor}:1",
            f"FULLFSYNC:{final_dependency_cursor}:2",
            f"FULLFSYNC:{final_dependency_cursor}:3",
            f"COMMITTED:{final_dependency_cursor}:3",
        )
        for expected_state in transitions:
            _kill_after_transition(
                "advance", mount, "publish-child", expected_state,
                reader_root=parent_root, reader_bytes=parent_bytes,
            )
            _remount(image, mount)
            state = transaction_state(cartridge, "publish-child")
            assert f"{state.state}:{state.dependency_cursor}:{state.pointer_cursor}" == expected_state
            active = recover_generation(cartridge)
            state_name, _, pointer_cursor = expected_state.split(":")
            child_is_callable = (
                state_name in {"SWAP_GENERATION_POINTER", "COMMITTED"}
                or int(pointer_cursor) > 0
            )
            assert active.root_digest == (child_root if child_is_callable else parent_root)
            assert read_tensor(cartridge, parent_pin.root_digest, "weight") == parent_bytes

        child_pin = recover_generation(cartridge)
        assert child_pin.generation == 2 and child_pin.root_digest == child_root
        assert commit_generation(
            cartridge, "publish-child", child_root, expected_parent_root=parent_root
        ) == child_pin
        with pytest.raises(CassetteError) as idempotency_conflict:
            begin_generation(
                cartridge, "publish-child", parent_root, expected_parent_root=parent_root
            )
        assert idempotency_conflict.value.code == "IDEMPOTENCY_CONFLICT"
        assert pin_generation(cartridge) == child_pin
        assert read_tensor(cartridge, child_pin.root_digest, "weight") == child_bytes
        assert read_tensor(cartridge, parent_pin.root_digest, "weight") == parent_bytes

        rolled_back = rollback_generation(cartridge, "rollback-child")
        assert rolled_back.generation == 3 and rolled_back.root_digest == parent_root
        assert recover_generation(cartridge) == rolled_back
        assert read_tensor(cartridge, child_pin.root_digest, "weight") == child_bytes

        orphan = cartridge / "transactions" / ".orphan.pending"
        orphan.write_bytes(b"unreachable")
        assert ".orphan.pending" in collect_garbage(cartridge)
        assert not orphan.exists()
        assert all((cartridge / "generations" / f"{number:020d}.json").exists()
                   for number in (1, 2, 3))
        assert read_tensor(cartridge, parent_pin.root_digest, "weight") == parent_bytes
        assert read_tensor(cartridge, child_pin.root_digest, "weight") == child_bytes

        restart_context = TransactionContext(
            "fixture-transform-v1",
            (parent_root, child_root),
            random_seed=17,
            statistics_digest=digest_bytes(b"S06 statistics"),
            optimizer_step=23,
            rng_state_digest=digest_bytes(b"S06 RNG state"),
            data_cursor=29,
            loss_scale="0x1.0000000000000p+0",
        )
        begin_generation(
            cartridge,
            "corrupt-temp",
            child_root,
            expected_parent_root=parent_root,
            context=restart_context,
        )
        assert advance_generation(cartridge, "corrupt-temp").state == "WRITE_TEMP"
        resume_record = json.loads(
            (cartridge / "transactions" / "corrupt-temp.json").read_bytes()
        )["record"]["resume"]
        expected_page_results = [
            {"page_digest": location.page_digest, "length": location.length}
            for location in sorted(
                page_locations(cartridge, child_root), key=lambda item: item.page_digest
            )
        ]
        assert resume_record == {
            "operation_version": restart_context.operation_version,
            "input_digests": list(restart_context.input_digests),
            "random_seed": restart_context.random_seed,
            "statistics_digest": restart_context.statistics_digest,
            "page_results": expected_page_results,
            "optimizer_step": restart_context.optimizer_step,
            "rng_state_digest": restart_context.rng_state_digest,
            "data_cursor": restart_context.data_cursor,
            "loss_scale": restart_context.loss_scale,
        }
        candidate = cartridge / "transactions" / "corrupt-temp.generation-candidate"
        candidate.write_bytes(b"corrupt candidate")
        _remount(image, mount)
        resumed = commit_generation(
            cartridge, "corrupt-temp", child_root, expected_parent_root=parent_root
        )
        assert resumed.generation == 4 and resumed.root_digest == child_root
        assert read_tensor(cartridge, resumed.root_digest, "weight") == child_bytes

        generation_path = cartridge / "generations" / f"{resumed.generation:020d}.json"
        generation_bytes = generation_path.read_bytes()
        generation_path.write_bytes(b"corrupt generation")
        _remount(image, mount)
        with pytest.raises(CassetteError) as corrupt_commit:
            commit_generation(
                cartridge, "corrupt-temp", child_root, expected_parent_root=parent_root
            )
        assert corrupt_commit.value.code == "ROOT_INVALID"
        assert recover_generation(cartridge).root_digest == parent_root
        generation_path.write_bytes(generation_bytes)
        _fixture_fullsync(generation_path)
        _remount(image, mount)
        assert recover_generation(cartridge) == resumed

        begin_generation(
            cartridge, "corrupt-journal", parent_root, expected_parent_root=child_root
        )
        journal = cartridge / "transactions" / "corrupt-journal.json"
        journal.write_bytes(b"corrupt journal")
        _remount(image, mount)
        with pytest.raises(CassetteError) as corrupt_journal:
            advance_generation(cartridge, "corrupt-journal")
        assert corrupt_journal.value.code == "SOURCE_UNAVAILABLE"
        assert recover_generation(cartridge) == resumed
        assert not (cartridge / "generations" / f"{resumed.generation + 1:020d}.json").exists()
    finally:
        subprocess.run(
            ["hdiutil", "detach", str(mount), "-quiet"], check=False, capture_output=True
        )


def _child_main() -> None:
    action, cartridge_text, transaction_id, candidate_root, expected_parent_root = sys.argv[2:]
    if action == "begin":
        state = begin_generation(
            cartridge_text,
            transaction_id,
            candidate_root,
            expected_parent_root=None if expected_parent_root == "-" else expected_parent_root,
        )
    else:
        state = advance_generation(cartridge_text, transaction_id)
    print(f"{state.state}:{state.dependency_cursor}:{state.pointer_cursor}", flush=True)
    signal.pause()


def _reader_main() -> None:
    cartridge_text, root_digest, expected_hex = sys.argv[2:]
    expected = bytes.fromhex(expected_hex)
    print("READY", flush=True)
    for _ in range(200):
        if read_tensor(cartridge_text, root_digest, "weight") != expected:
            raise AssertionError("pinned reader observed bytes outside its parent generation")
        time.sleep(0.001)
    print("OK", flush=True)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "_s06_child":
    _child_main()
elif __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "_s06_reader":
    _reader_main()
