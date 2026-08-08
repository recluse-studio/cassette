# test_s01_ledger.py — S01 fixtures for Q29 acceptance (reproducible accounting, partial); depends on tools/ledger.py.
"""S01: J reproduces from a clean checkout, and the accounting rejects law-breaking trees (Q29)."""

import json
import subprocess
import sys
from pathlib import Path

from tools.ledger import (
    check_commit_law,
    check_test_citations,
    check_tracked_artifacts,
    load_authorities,
)

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "tools" / "ledger.py"


def run_ledger(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(LEDGER), str(root)], capture_output=True, text=True)


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def init_git(root: Path) -> str:
    git(root, "init", "--quiet")
    git(root, "config", "user.name", "Cassette Fixture")
    git(root, "config", "user.email", "fixture@cassette.invalid")
    git(root, "config", "commit.gpgsign", "false")
    (root / "baseline.txt").write_text("baseline\n")
    git(root, "add", "baseline.txt")
    git(root, "commit", "--quiet", "-m", "fixture baseline")
    return git(root, "rev-parse", "HEAD")


def test_ledger_reproducible_from_clean_checkout(tmp_path):
    """Q29 acceptance: reproduce J from a clean checkout — clone HEAD, run twice, identical clean report."""
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "--quiet", str(REPO), str(clone)], check=True, capture_output=True)
    first = run_ledger(clone)
    second = run_ledger(clone)
    assert first.returncode == 0, first.stdout
    assert first.stdout == second.stdout
    report = json.loads(first.stdout)
    assert report["violations"] == []
    assert report["j_partial"]["direct_dependencies"], "pins must be recorded"


def test_ledger_rejects_header_pin_and_failed_check_violations(tmp_path):
    """Q29 acceptance: header, pin, artifact, and commit checks each fail closed."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nrequires-python = "==3.13.*"\n'
        'dependencies = ["requests>=2,==2.*", "foo==2.*"]\n'
    )
    (tmp_path / "store.py").write_text("import os\n")
    (tmp_path / ".git").write_text("")  # git present but broken: checks must fail closed, not pass
    result = run_ledger(tmp_path)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any("line 1 must be" in v for v in report["violations"])
    assert any("'requests>=2,==2.*' is not an exact" in v for v in report["violations"])
    assert any("'foo==2.*' is not an exact" in v for v in report["violations"])
    assert any("tracked-artifact check could not run (fail-closed)" in v for v in report["violations"])
    assert any("commit-law check could not run (fail-closed)" in v for v in report["violations"])

    not_repo = tmp_path / "not-repo"
    not_repo.mkdir()
    assert check_tracked_artifacts(not_repo) == (
        "failed",
        ["tracked-artifact check could not run (fail-closed): not a git repository"],
    )
    assert check_commit_law(not_repo) == (
        "failed",
        ["commit-law check could not run (fail-closed): not a git repository"],
    )


def test_authorities_are_rows_and_assertions_not_neighboring_lists(tmp_path):
    """Q29 acceptance: citations resolve only to Q checks, matrix rows, and assertion fields."""
    research = tmp_path / "research"
    research.mkdir()
    (research / "RESEARCH.md").write_text("question_id: Q1\n")
    (research / "ACCEPTANCE_MATRIX.yaml").write_text(
        "fixture_gate_rows:\n"
        "  - id: f4_gate\n"
        "source_rows:\n"
        "  - id: source_fixture\n"
        "    cases:\n"
        "      - ordinary_warm\n"
        "    assertions:\n"
        "      - exact_assertion\n"
        "    gates:\n"
        "      - q68_usability_floors\n"
        "    duties:\n"
        "      - native_routing_correctness\n"
        "    required_traces:\n"
        "      - discovery_and_negotiation\n"
        "    portability_assertions:\n"
        "      - portable_assertion (Q11, Q59)\n"
        "training_rows:\n"
        "  - id: training_fixture\n"
        "    operations:\n"
        "      - adapter_sft_131072_tokens\n"
        "    assertion: singular_assertion\n"
        "training_assertions:\n"
        "  required_for_every_training_row:\n"
        "    - required_assertion\n"
        "failure_rows:\n"
        "  injections:\n"
        "    - cartridge_disconnect\n"
        "minimum_code_rows:\n"
        "  - id: minimum_code_fixture\n"
        "    assertions:\n"
        "      - clean_build_reproduces_metric_J\n"
    )
    authorities = load_authorities(tmp_path)
    assert authorities == {
        "Q1",
        "f4_gate",
        "source_fixture",
        "training_fixture",
        "minimum_code_fixture",
        "exact_assertion",
        "portable_assertion",
        "singular_assertion",
        "required_assertion",
        "clean_build_reproduces_metric_J",
    }
    tests = tmp_path / "tests"
    tests.mkdir()
    citation_fixture = tests / "test_citations.py"
    citation_fixture.write_text(
        'def test_question():\n    """Q1"""\n    pass\n'
        'def test_gate_row():\n    """f4_gate"""\n    pass\n'
        'def test_row():\n    """source_fixture"""\n    pass\n'
        'def test_assertion():\n    """clean_build_reproduces_metric_J"""\n    pass\n'
        'def test_fixture_context():\n    """Q1 uses cartridge_disconnect."""\n    pass\n'
        'def test_case():\n    """ordinary_warm"""\n    pass\n'
        'def test_operation():\n    """adapter_sft_131072_tokens"""\n    pass\n'
        'def test_injection():\n    """cartridge_disconnect"""\n    pass\n'
        'def test_nested_gate():\n    """q68_usability_floors"""\n    pass\n'
        'def test_duty():\n    """native_routing_correctness"""\n    pass\n'
        'def test_trace():\n    """discovery_and_negotiation"""\n    pass\n'
    )
    violations = check_test_citations(tmp_path, citation_fixture.relative_to(tmp_path), authorities)
    assert len(violations) == 6
    assert any("test_case" in violation and "ordinary_warm" in violation for violation in violations)
    assert any(
        "test_operation" in violation and "adapter_sft_131072_tokens" in violation
        for violation in violations
    )
    assert any(
        "test_injection" in violation and "cartridge_disconnect" in violation
        for violation in violations
    )
    assert any(
        "test_nested_gate" in violation and "q68_usability_floors" in violation
        for violation in violations
    )
    assert any(
        "test_duty" in violation and "native_routing_correctness" in violation
        for violation in violations
    )
    assert any(
        "test_trace" in violation and "discovery_and_negotiation" in violation
        for violation in violations
    )


def test_tracked_artifact_check_detects_real_git_index_entry(tmp_path):
    """Q29 acceptance: a tracked build artifact fails in a functioning Git repository."""
    init_git(tmp_path)
    artifact = tmp_path / "__pycache__" / "owned.pyc"
    artifact.parent.mkdir()
    artifact.write_bytes(b"fixture")
    git(tmp_path, "add", "--force", "__pycache__/owned.pyc")
    status, violations = check_tracked_artifacts(tmp_path)
    assert status == "ran"
    assert violations == [
        "tracked build artifact (untrack it and keep it ignored): __pycache__/owned.pyc"
    ]


def test_commit_law_requires_anchored_nonempty_fields(tmp_path):
    """Q29 acceptance: commit-law fields and later repairs are exact, anchored, and fail-closed."""
    baseline = init_git(tmp_path)
    (tmp_path / "candidate.txt").write_text("candidate\n")
    git(tmp_path, "add", "candidate.txt")
    git(
        tmp_path,
        "commit",
        "--quiet",
        "-m",
        "This mentions Failed before, Reused instead of authored, and Deleted without fields.",
    )
    status, violations = check_commit_law(tmp_path, baseline)
    assert status == "ran"
    assert len(violations) == 1
    assert "missing or empty: Failed before, Reused instead of authored, Deleted" in violations[0]

    git(
        tmp_path,
        "commit",
        "--amend",
        "--quiet",
        "-m",
        "Compliant fixture",
        "-m",
        "Failed before: no candidate record existed.\n"
        "Reused instead of authored: Git's existing commit object.\n"
        "Deleted: nothing.",
    )
    status, violations = check_commit_law(tmp_path, baseline)
    assert status == "ran"
    assert violations == []

    repair_repo = tmp_path / "append-only-repair"
    repair_repo.mkdir()
    repair_baseline = init_git(repair_repo)
    (repair_repo / "broken.txt").write_text("published without fields\n")
    git(repair_repo, "add", "broken.txt")
    git(repair_repo, "commit", "--quiet", "-m", "Published fixture without fields")
    broken_sha = git(repair_repo, "rev-parse", "HEAD")
    (repair_repo / "repair.txt").write_text("append-only correction\n")
    git(repair_repo, "add", "repair.txt")
    git(
        repair_repo,
        "commit",
        "--quiet",
        "-m",
        "Record published-message correction",
        "-m",
        "Failed before: the published fixture omitted all three required fields.\n"
        "Reused instead of authored: the immutable target commit and Git history.\n"
        "Deleted: nothing.\n\n"
        f"Commit-law repair {broken_sha} Failed before: no candidate record existed.\n"
        f"Commit-law repair {broken_sha} Reused instead of authored: Git's commit object.\n"
        f"Commit-law repair {broken_sha} Deleted: nothing.",
    )
    repair_sha = git(repair_repo, "rev-parse", "HEAD")
    status, violations = check_commit_law(repair_repo, repair_baseline)
    assert status == "ran"
    assert violations == []

    git(
        repair_repo,
        "commit",
        "--allow-empty",
        "--quiet",
        "-m",
        "Reject invalid correction records",
        "-m",
        "Failed before: invalid correction cases lacked executable proof.\n"
        "Reused instead of authored: the existing fixture repository.\n"
        "Deleted: nothing.\n\n"
        f"Commit-law repair {broken_sha} Deleted: duplicate correction.\n"
        f"Commit-law repair {repair_sha} Deleted: field already answered.\n"
        "Commit-law repair 0000000000000000000000000000000000000000 Deleted: unknown target.\n"
        "Commit-law repair short Deleted: malformed target.",
    )
    status, violations = check_commit_law(repair_repo, repair_baseline)
    assert status == "ran"
    assert any("duplicate repair" in violation for violation in violations)
    assert any("already answers Deleted" in violation for violation in violations)
    assert any("target is not governed history" in violation for violation in violations)
    assert any("malformed commit-law repair" in violation for violation in violations)
