# test_s01_ledger.py — S01 fixtures for Q29 acceptance (reproducible accounting, partial); depends on tools/ledger.py.
"""S01: the accounting must be reproducible from a clean checkout and must reject law-breaking trees (Q29)."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "tools" / "ledger.py"


def run_ledger(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(LEDGER), str(root)], capture_output=True, text=True
    )


def test_ledger_clean_and_deterministic_on_repo():
    """Q29 acceptance: reproduce J from a clean checkout — two runs, identical report, exit 0."""
    first = run_ledger(REPO)
    second = run_ledger(REPO)
    assert first.returncode == 0, first.stdout
    assert first.stdout == second.stdout
    report = json.loads(first.stdout)
    assert report["violations"] == []
    assert report["j_partial"]["direct_dependencies"], "pins must be recorded"


def test_ledger_rejects_header_and_pin_violations(tmp_path):
    """Q29 acceptance: the classifier is enforced — a headerless file and an unpinned dep must fail."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nrequires-python = "==3.13.*"\ndependencies = ["requests"]\n'
    )
    (tmp_path / "store.py").write_text("import os\n")
    result = run_ledger(tmp_path)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any("line 1 must be" in v for v in report["violations"])
    assert any("lacks an exact == pin" in v for v in report["violations"])
