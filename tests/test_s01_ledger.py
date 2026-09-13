# test_s01_ledger.py — S01 fixtures for Q29 acceptance (reproducible accounting, partial); depends on tools/ledger.py.
"""S01: J reproduces from a clean checkout, and the accounting rejects law-breaking trees (Q29)."""

import json
import shutil
import subprocess
import venv
from pathlib import Path

from tools.ledger import (
    check_commit_law,
    check_mlx_confinement,
    top_level_imports,
    check_removal_map,
    check_test_citations,
    check_tracked_artifacts,
    load_authorities,
    run,
)

REPO = Path(__file__).resolve().parent.parent


def run_source_ledger(root: Path) -> subprocess.CompletedProcess:
    """Check source law before the complete suite can produce its own Q29 report."""
    report = run(root, verify_report=False)
    return subprocess.CompletedProcess(
        args=[], returncode=int(bool(report["violations"])),
        stdout=json.dumps(report, sort_keys=True), stderr="",
    )


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
    research = root / "research"
    research.mkdir()
    (research / "RESEARCH.md").write_text("question_id: Q29\n")
    git(root, "add", "baseline.txt", "research/RESEARCH.md")
    git(root, "commit", "--quiet", "-m", "fixture baseline")
    return git(root, "rev-parse", "HEAD")


def clone_candidate(root: Path) -> None:
    """Create one clean commit from the live candidate, including its uncommitted governed files."""
    subprocess.run(["git", "clone", "--quiet", str(REPO), str(root)], check=True, capture_output=True)
    git(root, "config", "user.name", "Cassette Fixture")
    git(root, "config", "user.email", "fixture@cassette.invalid")
    git(root, "config", "commit.gpgsign", "false")
    result = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        check=True,
        capture_output=True,
    )
    candidate_paths = {Path(item.decode()) for item in result.stdout.split(b"\0") if item}
    clone_paths = {Path(item) for item in git(root, "ls-files").splitlines() if item}
    for rel in sorted(clone_paths - candidate_paths):
        target = root / rel
        if target.is_file() or target.is_symlink():
            target.unlink()
    for rel in sorted(candidate_paths):
        source = REPO / rel
        if not source.is_file():
            continue
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    git(root, "add", "--all")
    if git(root, "status", "--porcelain"):
        git(
            root,
            "commit",
            "--quiet",
            "-m",
            "Freeze the candidate accounting fixture",
            "-m",
            "Failed before: Q29 could inspect only the prior committed tree.\n"
            "Reused instead of authored: Git's clean commit and index.\n"
            "Deleted: nothing.",
        )


def test_ledger_reproducible_from_clean_checkout(tmp_path):
    """Q29 acceptance: J excludes foreign environments but includes new governed source."""
    clone = tmp_path / "clone"
    clone_candidate(clone)
    first = run_source_ledger(clone)
    second = run_source_ledger(clone)
    assert first.returncode == 0, first.stdout
    assert first.stdout == second.stdout
    report = json.loads(first.stdout)
    assert report["violations"] == []
    assert report["accounting"]["direct_dependency_manifest"], "pins must be recorded"

    for name in ("local-python", "build/runtime-3.13"):
        environment = clone / name
        venv.EnvBuilder(with_pip=False, symlinks=True).create(environment)
        foreign = environment / "lib" / "python3.13" / "site-packages" / "foreign_runtime.py"
        foreign.parent.mkdir(parents=True, exist_ok=True)
        foreign.write_text("import mlx\nimport store\n")
    isolated = run_source_ledger(clone)
    assert isolated.returncode == 0, isolated.stdout
    assert isolated.stdout == first.stdout

    (clone / "hostile_untracked.py").write_text(
        "# hostile_untracked.py — untracked hostile source; depends on sources.py.\n"
        "import mlx\n"
        "import sources\n"
    )
    (clone / "hostile_staged.py").write_text(
        "# hostile_staged.py — staged governed source; depends on (none).\nVALUE = 1\n"
    )
    hidden_research = clone / "research" / "hostile_governed.py"
    hidden_research.write_text(
        "# hostile_governed.py — tracked research source; depends on sources.py.\n"
        "import mlx\n"
        "import sources\n"
    )
    hidden_workflow = clone / ".github" / "hostile_governed.py"
    hidden_workflow.parent.mkdir(exist_ok=True)
    hidden_workflow.write_text(
        "# hostile_governed.py — tracked workflow source; depends on (none).\nimport mlx\n"
    )
    git(clone, "add", "hostile_staged.py", "research/hostile_governed.py", ".github/hostile_governed.py")
    governed = run_source_ledger(clone)
    assert governed.returncode == 1
    governed_report = json.loads(governed.stdout)
    assert set(governed_report["files_checked"]) - set(report["files_checked"]) == {
        ".github/hostile_governed.py",
        "hostile_staged.py",
        "hostile_untracked.py",
        "research/hostile_governed.py",
    }
    assert any(
        "hostile_untracked.py: mlx import outside" in item
        for item in governed_report["violations"]
    )
    assert any(
        "hostile_untracked.py: illegal import of 'sources'" in item
        for item in governed_report["violations"]
    )
    assert any(
        "research/hostile_governed.py: mlx import outside" in item
        for item in governed_report["violations"]
    )
    assert any(
        ".github/hostile_governed.py: mlx import outside" in item
        for item in governed_report["violations"]
    )


def test_q78_removal_map_is_exact_and_authority_bound(tmp_path):
    """Q78 acceptance: each authored product or tool file has one real removal authority."""
    (tmp_path / "tools").mkdir()
    (tmp_path / "errors.py").write_text(
        "# errors.py — Q6 fixture authority; depends on (none).\n"
    )
    (tmp_path / "tools" / "ledger.py").write_text(
        "# ledger.py — Q29 fixture authority; depends on (none).\n"
    )
    (tmp_path / "AGENTS.md").write_text(
        "<!-- CASSETTE_REMOVAL_MAP_BEGIN -->\n"
        "```json\n"
        '{"errors.py":["Q6"],"tools/ledger.py":["Q29"]}\n'
        "```\n"
        "<!-- CASSETTE_REMOVAL_MAP_END -->\n"
    )
    files = [Path("errors.py"), Path("tools/ledger.py"), Path("tests/test_fixture.py")]
    assert check_removal_map(tmp_path, files, {"Q6", "Q29"}) == ("ran", [])

    (tmp_path / "AGENTS.md").write_text(
        "<!-- CASSETTE_REMOVAL_MAP_BEGIN -->\n"
        '{"errors.py":["Q999"],"stale.py":["Q6"]}\n'
        "<!-- CASSETTE_REMOVAL_MAP_END -->\n"
    )
    status, violations = check_removal_map(tmp_path, files, {"Q6", "Q29"})
    assert status == "ran"
    assert violations == [
        "Q78 removal map lacks authored file: tools/ledger.py",
        "Q78 removal map names no authored product or tool file: stale.py",
        "Q78 removal map entry errors.py names unknown authorities: ['Q999']",
    ]


def test_ledger_rejects_header_pin_and_failed_check_violations(tmp_path):
    """Q29 acceptance: header, pin, artifact, and commit checks each fail closed."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nrequires-python = "==3.13.*"\n'
        'dependencies = ["requests>=2,==2.*", "foo==2.*"]\n'
        '[build-system]\nrequires = ["build>=1", "setuptools==84.*"]\n'
    )
    (tmp_path / "store.py").write_text("import os\n")
    (tmp_path / ".git").write_text("")  # git present but broken: checks must fail closed, not pass
    result = run_source_ledger(tmp_path)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any("line 1 must be" in v for v in report["violations"])
    assert any("'requests>=2,==2.*' is not an exact" in v for v in report["violations"])
    assert any("'foo==2.*' is not an exact" in v for v in report["violations"])
    assert any("'build>=1' is not an exact" in v for v in report["violations"])
    assert any("'setuptools==84.*' is not an exact" in v for v in report["violations"])
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
        "Failed before: Q29 had no candidate record.\n"
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
        "Failed before: Q29 published fixture omitted all three required fields.\n"
        "Reused instead of authored: the immutable target commit and Git history.\n"
        "Deleted: nothing.\n\n"
        f"Commit-law repair {broken_sha} Failed before: Q29 had no candidate record.\n"
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
        "Failed before: Q29 invalid correction cases lacked executable proof.\n"
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


def test_q30_computed_runtime_acquisition_stays_with_exact_owner_paths(tmp_path):
    """Q30 acceptance: ledger rejects computed runtime acquisition outside pager/trainer."""
    forbidden = (
        "__import__('mlx.core')",
        "__import__('m' + 'lx.core')",
        "name = 'mlx.core'\n__import__(name)",
        "import importlib\nimportlib.import_module('mlx.core')",
        "import importlib as loader\nloader.import_module('m' + 'lx.core')",
        "from importlib import import_module as load\nload('mlx.core')",
        "load = __import__\nload('mlx.core')",
        "from builtins import __import__ as load\nload('mlx.core')",
        "getattr(__import__('importlib'), 'import_module')('mlx.core')",
        "getattr(__import__('importlib'), 'import_module')(name='mlx.core')",
        "import importlib\nvars(importlib)['import_module']('mlx.core')",
        "import importlib as library\nload = getattr(library, 'import_' + 'module')\nload('mlx.core')",
        "import importlib as library\nnamespace = library.__dict__\nnamespace['import_module']('mlx.core')",
        "import builtins as library\ngetattr(library, '__import__')('mlx.core')",
        "__import__('builtins').__dict__['__import__']('mlx.core')",
        "from importlib import __dict__ as namespace\nnamespace['import_module']('mlx.core')",
        "from importlib import *\nimport_module('mlx.core')",
        "import importlib.util as utility\ngetattr(utility, 'find_spec')('mlx.core')",
        "__builtins__['__import__']('mlx.core')",
        "getattr(__builtins__, '__import__')('mlx.core')",
        "__builtins__.get('__import__')('mlx.core')",
        "__import__('core', globals={'__package__': 'mlx'}, level=1)",
        "__import__('core', {'__package__': 'mlx'}, None, [], 1)",
        "__import__('core', **{'globals': {'__package__': 'mlx'}, 'level': 1})",
    )
    for rel in (Path("compiler.py"), Path("tools/pager.py")):
        (tmp_path / rel).parent.mkdir(exist_ok=True)
        for source in forbidden:
            (tmp_path / rel).write_text(source + "\n")
            violations = check_mlx_confinement(tmp_path, rel, top_level_imports(tmp_path, rel))
            assert violations, (rel, source)
            assert all("Q30 confinement" in item for item in violations)
    for rel in (Path("pager.py"), Path("trainer.py")):
        for source in forbidden:
            (tmp_path / rel).write_text(source + "\n")
            assert check_mlx_confinement(tmp_path, rel, top_level_imports(tmp_path, rel)) == []
    rel = Path("compiler.py")
    for source in (
        "import math", "__import__('math')",
        "import importlib as loader\nloader.import_module('json')",
        "import importlib as loader\nloader.import_module(name='json')",
        "from importlib import import_module as load\nload('json')",
        "import builtins as loader\nloader.__import__('math')",
    ):
        (tmp_path / rel).write_text(source + "\n")
        assert check_mlx_confinement(tmp_path, rel, top_level_imports(tmp_path, rel)) == []

    clone = tmp_path / "candidate"
    clone_candidate(clone)
    assert run(clone, verify_report=False)["violations"] == []
    for rel in (Path("compiler.py"), Path("tools/pager.py")):
        target = clone / rel
        original = target.read_bytes() if target.exists() else None
        target.write_text(f"# {rel.name} — Q30 computed-import fixture; depends on (none).\n" + forbidden[8] + "\n")
        try:
            violations = run(clone, verify_report=False)["violations"]
            assert any(str(rel) in item and "Q30 confinement" in item for item in violations), violations
        finally:
            if original is None:
                target.unlink()
            else:
                target.write_bytes(original)
