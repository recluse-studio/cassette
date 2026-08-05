# test_s01_ledger.py — S01 fixtures for Q29 acceptance (reproducible accounting, partial); depends on tools/ledger.py.
"""S01: J reproduces from a clean checkout, and the accounting rejects law-breaking trees (Q29)."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "tools" / "ledger.py"


def run_ledger(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(LEDGER), str(root)], capture_output=True, text=True)


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


def test_ledger_rejects_header_pin_citation_and_failed_check_violations(tmp_path):
    """Q29 acceptance: enforcement — headerless file, marker-masked and wildcard pins, unresolvable
    citations, and unrunnable checks (fail-closed) all fail; assertion citations resolve."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nrequires-python = "==3.13.*"\n'
        'dependencies = ["requests>=2,==2.*", "foo==2.*"]\n'
    )
    (tmp_path / "store.py").write_text("import os\n")
    (tmp_path / ".git").write_text("")  # git present but broken: checks must fail closed, not pass
    (tmp_path / "research").mkdir()
    (tmp_path / "research" / "RESEARCH.md").write_text("question_id: Q1\n")
    (tmp_path / "research" / "ACCEPTANCE_MATRIX.yaml").write_text(
        "training_assertions:\n  required_for_every_training_row:\n    - q23_placement\n"
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text(
        '# test_x.py — fixture; depends on (none).\n'
        'def test_something():\n    """Cites Q999 only."""\n'
        'def test_placement():\n    """Exercises q23_placement."""\n'
    )
    result = run_ledger(tmp_path)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any("line 1 must be" in v for v in report["violations"])
    assert any("'requests>=2,==2.*' is not an exact" in v for v in report["violations"])
    assert any("'foo==2.*' is not an exact" in v for v in report["violations"])
    assert any("test_something" in v and "resolve to no" in v for v in report["violations"])
    assert not any("test_placement" in v for v in report["violations"])
    assert any("could not run (fail-closed)" in v for v in report["violations"])
