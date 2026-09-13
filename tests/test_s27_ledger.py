# test_s27_ledger.py — S27 complete J and isolated Q78 removal-proof fixtures; depends on tools/ledger.py.
"""S27 proves the final accounting and refuses maps whose named owners are removable."""

from pathlib import Path

import pytest

from tools.ledger import (
    J_LABELS,
    _j_values,
    build_accounting,
    check_removal_map,
    discover,
    load_authorities,
    load_removal_map,
    removal_experiment,
    removal_proof_node,
    run,
)

REPO = Path(__file__).resolve().parent.parent


def test_q29_complete_j_classifies_every_surface_and_exposes_all_nine_coordinates(tmp_path):
    """Q29 acceptance: the clean classifier reproduces every J coordinate and catches added surface."""
    report = run(REPO, verify_report=False)
    assert report["violations"] == []
    accounting = report["accounting"]
    assert J_LABELS == [
        "failed_acceptance_rows",
        "new_numerical_kernels",
        "authored_executable_LOC",
        "independent_processes",
        "language_runtimes",
        "direct_dependencies",
        "model_specific_branches",
        "duplicate_authorities",
        "shipped_binary_bytes",
    ]
    assert _j_values(accounting, 0) == [
        0,
        0,
        accounting["authored_executable_loc"]["total"],
        1,
        1,
        9,
        0,
        0,
        sum((REPO / row["path"]).stat().st_size for row in accounting["shipped_binary_files"]),
    ]
    assert set(accounting["source_files"]) == {"generated", "product", "tests", "tools"}
    assert set(accounting["source_files"]["product"]) == {
        "adapters/__init__.py", "broker.py", "cli.py", "compiler.py", "errors.py", "pager.py",
        "sources.py", "store.py", "trainer.py",
    }

    (tmp_path / "pyproject.toml").write_text('[project]\nrequires-python = "==3.13.*"\n')
    (tmp_path / "hostile.py").write_text(
        "# hostile.py — injected Q29 surface; depends on (none).\n"
        "import hashlib\nimport subprocess\n"
        "def choose(model_family):\n"
        "    if model_family == 'Kimi-K3':\n"
        "        return 1\n"
    )
    (tmp_path / "authored.metal").write_text("kernel void authored() {}\n")
    (tmp_path / "payload.bin").write_bytes(b"\x00binary")
    injected = build_accounting(
        tmp_path,
        [Path("hostile.py")],
        {"product": 1, "tools": 0, "tests": 0},
        0,
        [],
    )
    assert injected["new_numerical_kernel_sites"] == ["authored.metal"]
    assert injected["process_spawn_sites"] == ["hostile.py:import:subprocess"]
    assert injected["model_specific_branch_table"] == ["hostile.py:5"]
    assert injected["duplicate_authority_sites"] == ["hostile.py:identity:hashlib"]
    assert injected["shipped_binary_files"] == [{"bytes": 7, "path": "payload.bin"}]


def test_q78_completed_map_resolves_each_owner_to_one_direct_cited_proof():
    """Q78 acceptance: every completed-tree owner has one declared authority and direct proof node."""
    files = discover(REPO)
    authorities = load_authorities(REPO)
    assert check_removal_map(REPO, files, authorities) == ("ran", [])
    removal_map, errors = load_removal_map(REPO)
    assert errors == [] and removal_map is not None
    assert len(removal_map) == 14
    for target, rows in removal_map.items():
        assert len(rows) == 1
        node = removal_proof_node(REPO, target, rows[0])
        assert node is not None
        assert node.startswith("tests/test_") and "::test_" in node


def test_q78_isolated_deletion_rejects_a_nonconsequential_map_entry(tmp_path):
    """Q78 acceptance: a mapped file whose direct cited proof survives deletion is rejected."""
    tests = tmp_path / "tests"
    tests.mkdir()
    target = tmp_path / "unused.py"
    target.write_text("# unused.py — optional Q29 owner; depends on (none).\nVALUE = 1\n")
    (tests / "test_optional.py").write_text(
        "# test_optional.py — Q29 optional-owner fixture; depends on unused.py.\n"
        "import unused\n\n"
        "def test_q29_optional_owner():\n"
        "    \"\"\"Q29 acceptance: this assertion deliberately survives an inert imported owner.\"\"\"\n"
        "    assert True\n"
    )
    with pytest.raises(ValueError, match="nonconsequential map entry survived executable bypass"):
        removal_experiment(tmp_path, "unused.py", "Q29")
    assert target.read_text() == "# unused.py — optional Q29 owner; depends on (none).\nVALUE = 1\n"
