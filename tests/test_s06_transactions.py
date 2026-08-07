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

import store as store_module
from errors import CassetteError
from store import (
    ArtifactIdentity,
    IdentityTuple,
    TransactionContext,
    advance_generation,
    begin_generation,
    canonical_bytes,
    collect_garbage,
    commit_generation,
    digest_bytes,
    import_safetensors,
    load_root,
    load_transaction_context,
    page_locations,
    pin_generation,
    read_tensor,
    recover_generation,
    rollback_generation,
    transaction_state,
)


pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="S06 requires arm64 macOS, APFS, hdiutil, and F_FULLFSYNC",
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


def _training_manifest(context: TransactionContext | None, candidate_root: str) -> dict:
    context = context or TransactionContext("store-generation-v1", (candidate_root,))
    return {
        "data_cursor": context.data_cursor,
        "input_digests": list(context.input_digests),
        "loss_scale": context.loss_scale,
        "operation_version": context.operation_version,
        "optimizer_step": context.optimizer_step,
        "random_seed": context.random_seed,
        "rng_state_digest": digest_bytes(context.rng_state) if context.rng_state is not None else None,
        "statistics_digest": (
            digest_bytes(context.statistics) if context.statistics is not None else None
        ),
    }


def _q73_child_id(
    cartridge: Path,
    root_digest: str,
    parent_id: str | None,
    training_manifest: dict,
) -> str:
    root = load_root(cartridge, root_digest)
    return digest_bytes(canonical_bytes({
        "parent_id": parent_id,
        "training_manifest": training_manifest,
        "ordered_page_or_delta_digests": sorted(
            location.page_digest for location in page_locations(cartridge, root_digest)
        ),
        "semantic_manifest": {
            "root_identity": root["identity"],
            "parents": root["parents"],
            "semantic_assets": root["semantic_assets"],
            "tensor_maps": root["tensor_maps"],
            "operators": root["operators"],
            "deltas": root["deltas"],
        },
    }))


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


def _kill_at_boundary(
    action: str,
    boundary: str,
    mount: Path,
    transaction_id: str,
    candidate_root: str = "-",
    expected_parent_root: str = "-",
    reader_root: str = "-",
    reader_bytes: bytes = b"",
    restart_bytes: bytes = b"",
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
            "_s06_boundary",
            action,
            boundary,
            str(mount / "cartridge"),
            transaction_id,
            candidate_root,
            expected_parent_root,
            restart_bytes.hex(),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    )
    try:
        observed = process.stdout.readline().strip()
        if observed != f"BOUNDARY:{boundary}":
            process.kill()
            _, process_error = process.communicate(timeout=10)
            raise AssertionError(process_error or f"expected {boundary!r}, received {observed!r}")
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
        assert parent_pin.child_id == _q73_child_id(
            cartridge, parent_root, None, _training_manifest(None, parent_root)
        )
        _remount(image, mount)
        assert recover_generation(cartridge) == parent_pin

        _kill_at_boundary(
            "begin", "before_journal", mount, "publish-child", child_root, parent_root,
            parent_root, parent_bytes,
        )
        _remount(image, mount)
        assert not (cartridge / "transactions" / "publish-child.json").exists()
        assert recover_generation(cartridge) == parent_pin
        assert begin_generation(
            cartridge, "publish-child", child_root, expected_parent_root=parent_root
        ).state == "PREPARE"

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
        journal_boundaries = (
            "journal_write",
            "journal_readback",
            "journal_fullsync",
            "journal_replace",
            "journal_directory_sync",
        )
        for index, expected_state in enumerate(transitions):
            prior = transaction_state(cartridge, "publish-child")
            _kill_at_boundary(
                "advance", "before_journal", mount, "publish-child",
                reader_root=parent_root, reader_bytes=parent_bytes,
            )
            _remount(image, mount)
            assert transaction_state(cartridge, "publish-child") == prior
            active = recover_generation(cartridge)
            publication_action = (
                prior.state == "FULLFSYNC"
                and prior.step == 5
                and prior.dependency_cursor == final_dependency_cursor
            )
            child_is_callable = prior.step >= 6 or publication_action
            assert active.root_digest == (child_root if child_is_callable else parent_root)
            assert read_tensor(cartridge, parent_pin.root_digest, "weight") == parent_bytes

            if index < len(journal_boundaries):
                boundary = journal_boundaries[index]
                _kill_at_boundary(
                    "advance", boundary, mount, "publish-child",
                    reader_root=parent_root, reader_bytes=parent_bytes,
                )
                _remount(image, mount)
                if boundary in {"journal_replace", "journal_directory_sync"}:
                    state = transaction_state(cartridge, "publish-child")
                else:
                    assert transaction_state(cartridge, "publish-child") == prior
                    state = advance_generation(cartridge, "publish-child")
            else:
                state = advance_generation(cartridge, "publish-child")
            assert f"{state.state}:{state.dependency_cursor}:{state.pointer_cursor}" == expected_state

        _remount(image, mount)
        child_pin = recover_generation(cartridge)
        assert child_pin.generation == 2 and child_pin.root_digest == child_root
        assert child_pin.child_id == _q73_child_id(
            cartridge, child_root, parent_pin.child_id, _training_manifest(None, child_root)
        )
        assert commit_generation(
            cartridge, "publish-child", child_root, expected_parent_root=parent_root
        ) == child_pin
        with pytest.raises(CassetteError) as idempotency_conflict:
            begin_generation(
                cartridge, "publish-child", parent_root, expected_parent_root=parent_root
            )
        assert idempotency_conflict.value.code == "IDEMPOTENCY_CONFLICT"
        with pytest.raises(CassetteError) as parent_conflict:
            begin_generation(
                cartridge, "publish-child", child_root, expected_parent_root=child_root
            )
        assert parent_conflict.value.code == "IDEMPOTENCY_CONFLICT"
        with pytest.raises(CassetteError) as context_conflict:
            begin_generation(
                cartridge,
                "publish-child",
                child_root,
                expected_parent_root=parent_root,
                context=TransactionContext("different-transform", (child_root,)),
            )
        assert context_conflict.value.code == "IDEMPOTENCY_CONFLICT"
        assert pin_generation(cartridge) == child_pin
        assert read_tensor(cartridge, child_pin.root_digest, "weight") == child_bytes
        assert read_tensor(cartridge, parent_pin.root_digest, "weight") == parent_bytes

        rolled_back = rollback_generation(cartridge, "rollback-child")
        assert rolled_back.generation == 3 and rolled_back.root_digest == parent_root
        assert recover_generation(cartridge) == rolled_back
        assert read_tensor(cartridge, child_pin.root_digest, "weight") == child_bytes

        orphan = cartridge / "transactions" / ".orphan.pending"
        material_orphan = cartridge / "transactions" / "material" / ".material-orphan.pending"
        material_orphan.parent.mkdir(exist_ok=True)
        orphan.write_bytes(b"unreachable")
        material_orphan.write_bytes(b"unreachable material")
        removed = collect_garbage(cartridge)
        assert {".orphan.pending", ".material-orphan.pending"} <= set(removed)
        assert not orphan.exists() and not material_orphan.exists()
        assert all((cartridge / "generations" / f"{number:020d}.json").exists()
                   for number in (1, 2, 3))
        assert read_tensor(cartridge, parent_pin.root_digest, "weight") == parent_bytes
        assert read_tensor(cartridge, child_pin.root_digest, "weight") == child_bytes

        restart_context = TransactionContext(
            "fixture-transform-v1",
            (parent_root, child_root),
            random_seed=17,
            statistics=b"S06 statistics",
            optimizer_step=23,
            rng_state=b"S06 RNG state",
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
            "statistics_digest": digest_bytes(restart_context.statistics),
            "page_results": expected_page_results,
            "optimizer_step": restart_context.optimizer_step,
            "rng_state_digest": digest_bytes(restart_context.rng_state),
            "data_cursor": restart_context.data_cursor,
            "loss_scale": restart_context.loss_scale,
        }
        assert load_transaction_context(cartridge, "corrupt-temp") == restart_context
        for field, expected in (
            ("statistics_digest", restart_context.statistics),
            ("rng_state_digest", restart_context.rng_state),
        ):
            material = cartridge / "transactions" / "material" / resume_record[field][7:]
            material.write_bytes(b"corrupt restart material")
            _fixture_fullsync(material)
            _remount(image, mount)
            with pytest.raises(CassetteError) as corrupt_material:
                advance_generation(cartridge, "corrupt-temp")
            assert corrupt_material.value.code == "SOURCE_UNAVAILABLE"
            assert recover_generation(cartridge) == rolled_back
            material.write_bytes(expected)
            _fixture_fullsync(material)
            _remount(image, mount)
            assert load_transaction_context(cartridge, "corrupt-temp") == restart_context
        recovered_context = load_transaction_context(cartridge, "corrupt-temp")
        candidate = cartridge / "transactions" / "corrupt-temp.generation-candidate"
        candidate.write_bytes(b"corrupt candidate")
        _remount(image, mount)
        resumed = commit_generation(
            cartridge,
            "corrupt-temp",
            child_root,
            expected_parent_root=parent_root,
            context=recovered_context,
        )
        assert resumed.generation == 4 and resumed.root_digest == child_root
        assert resumed.child_id == _q73_child_id(
            cartridge,
            child_root,
            rolled_back.child_id,
            _training_manifest(restart_context, child_root),
        )
        assert read_tensor(cartridge, resumed.root_digest, "weight") == child_bytes

        generation_path = cartridge / "generations" / f"{resumed.generation:020d}.json"
        generation_bytes = generation_path.read_bytes()
        generation_envelope = json.loads(generation_bytes)
        generation_envelope["record"]["child_id"] = load_root(cartridge, child_root)["identity"]
        generation_envelope["digest"] = digest_bytes(
            canonical_bytes(generation_envelope["record"])
        )
        generation_path.write_bytes(canonical_bytes(generation_envelope))
        _fixture_fullsync(generation_path)
        _remount(image, mount)
        with pytest.raises(CassetteError) as corrupt_commit:
            commit_generation(
                cartridge, "corrupt-temp", child_root, expected_parent_root=parent_root
            )
        assert corrupt_commit.value.code == "ROOT_INVALID"
        assert recover_generation(cartridge) == rolled_back
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

        for phase in ("write", "readback", "fullsync", "replace", "directory_sync"):
            transaction_id = f"material-{phase}"
            restart_bytes = f"S06 restart material at {phase}".encode()
            _kill_at_boundary(
                "begin_context",
                f"material_{phase}",
                mount,
                transaction_id,
                parent_root,
                child_root,
                parent_root,
                parent_bytes,
                restart_bytes,
            )
            _remount(image, mount)
            assert not (cartridge / "transactions" / f"{transaction_id}.json").exists()
            assert recover_generation(cartridge) == resumed
            context = TransactionContext(
                "boundary-material-v1", (parent_root,), statistics=restart_bytes
            )
            assert begin_generation(
                cartridge,
                transaction_id,
                parent_root,
                expected_parent_root=child_root,
                context=context,
            ).state == "PREPARE"
            assert load_transaction_context(cartridge, transaction_id) == context
    finally:
        subprocess.run(
            ["hdiutil", "detach", str(mount), "-quiet"], check=False, capture_output=True
        )


def _pause_at_boundary(boundary: str) -> None:
    print(f"BOUNDARY:{boundary}", flush=True)
    signal.pause()


def _install_boundary(
    boundary: str, cartridge: Path, transaction_id: str, restart_bytes: bytes
) -> None:
    journal = cartridge / "transactions" / f"{transaction_id}.json"
    if boundary.startswith("material_"):
        target = cartridge / "transactions" / "material" / digest_bytes(restart_bytes)[7:]
        phase = f"journal_{boundary.removeprefix('material_')}"
    else:
        target = journal
        phase = boundary
    pending = target.with_name(f".{target.name}.pending")
    if phase == "before_journal":
        def stop_before_journal(_cartridge, _record):
            _pause_at_boundary(boundary)

        store_module._write_transaction = stop_before_journal
    elif phase == "journal_write":
        original = Path.write_bytes

        def stop_after_write(path, payload):
            result = original(path, payload)
            if path == pending:
                _pause_at_boundary(boundary)
            return result

        Path.write_bytes = stop_after_write
    elif phase == "journal_readback":
        original = Path.read_bytes

        def stop_after_readback(path):
            payload = original(path)
            if path == pending:
                _pause_at_boundary(boundary)
            return payload

        Path.read_bytes = stop_after_readback
    elif phase == "journal_fullsync":
        original = store_module._fullsync_file

        def stop_after_fullsync(path, object_id):
            original(path, object_id)
            if path == pending:
                _pause_at_boundary(boundary)

        store_module._fullsync_file = stop_after_fullsync
    elif phase == "journal_replace":
        original = store_module.os.replace

        def stop_after_replace(source, destination):
            original(source, destination)
            if Path(destination) == target:
                _pause_at_boundary(boundary)

        store_module.os.replace = stop_after_replace
    elif phase == "journal_directory_sync":
        original_replace = store_module.os.replace
        original_sync = store_module._sync_directory
        replaced = False

        def observe_replace(source, destination):
            nonlocal replaced
            original_replace(source, destination)
            replaced = Path(destination) == target

        def stop_after_directory_sync(path, object_id):
            original_sync(path, object_id)
            if replaced and path == target.parent:
                _pause_at_boundary(boundary)

        store_module.os.replace = observe_replace
        store_module._sync_directory = stop_after_directory_sync
    else:
        raise AssertionError(f"unknown S06 boundary {boundary!r}")


def _boundary_main() -> None:
    (
        action,
        boundary,
        cartridge_text,
        transaction_id,
        candidate_root,
        expected_parent_root,
        restart_hex,
    ) = sys.argv[2:]
    restart_bytes = bytes.fromhex(restart_hex)
    _install_boundary(boundary, Path(cartridge_text), transaction_id, restart_bytes)
    if action in {"begin", "begin_context"}:
        begin_generation(
            cartridge_text,
            transaction_id,
            candidate_root,
            expected_parent_root=None if expected_parent_root == "-" else expected_parent_root,
            context=(
                TransactionContext(
                    "boundary-material-v1", (candidate_root,), statistics=restart_bytes
                )
                if action == "begin_context" else None
            ),
        )
    else:
        advance_generation(cartridge_text, transaction_id)
    raise AssertionError(f"S06 boundary {boundary!r} was not reached")


def _reader_main() -> None:
    cartridge_text, root_digest, expected_hex = sys.argv[2:]
    expected = bytes.fromhex(expected_hex)
    print("READY", flush=True)
    for _ in range(200):
        if read_tensor(cartridge_text, root_digest, "weight") != expected:
            raise AssertionError("pinned reader observed bytes outside its parent generation")
        time.sleep(0.001)
    print("OK", flush=True)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "_s06_boundary":
    _boundary_main()
elif __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "_s06_reader":
    _reader_main()
