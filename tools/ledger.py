# ledger.py — J accounting and structure enforcement (Q29 partial; AGENTS.md Files/Structure/Tests rules); depends on (none).
"""Recompute the machine-checkable parts of J from a clean checkout and enforce repo law.

Checks (AGENTS.md):
  1. Header law: line 1 of every authored .py file is `# <name> — <what>; depends on <files|(none)>.`
  2. Header truth (product and tools files): declared intra-repo dependencies equal actual imports.
  3. Layer law (product files): imports point downward only; L2 siblings never import each other.
  4. Runtime confinement: `mlx` imports exist only in pager.py and trainer.py.
  5. Test citation law: every test function cites a ledger invariant (Qn or a matrix row id).
  6. Pin law: every dependency in pyproject.toml carries an exact `==` pin.
  7. LOC accounting: logical lines per class {product, tools, tests}; generated code reported
     separately and never counted as authored.

Output is deterministic. Exit 0 when clean, 1 when any violation exists. Usage:
    python3 tools/ledger.py [repo_root]
"""

from __future__ import annotations

import ast
import io
import json
import re
import subprocess
import sys
import tokenize
from pathlib import Path

EXCLUDED_DIRS = {".git", ".github", "research", "__pycache__", ".pytest_cache", "outputs"}
GENERATED_DIRS = {"schema"}
PRODUCT_MODULES = {"errors", "store", "sources", "compiler", "pager", "trainer", "broker"}

# Structure section, AGENTS.md: allowed intra-repo import edges (downward only).
ALLOWED_EDGES = {
    "errors": set(),
    "store": {"errors", "schema"},
    "sources": {"errors", "schema", "store"},
    "compiler": {"errors", "schema", "store"},
    "pager": {"errors", "schema", "store"},
    "trainer": {"errors", "schema", "store"},
    "broker": {"errors", "schema", "store", "sources", "compiler", "pager", "trainer"},
    "adapters": {"errors", "schema", "broker"},
}
MLX_ALLOWED_FILES = {"pager.py", "trainer.py"}
HEADER_RE = re.compile(r"^# (?P<name>\S+) — .+; depends on (?P<deps>.+)\.\s*$")
CITATION_RE = re.compile(r"Q\d+|[a-z][a-z0-9_]*_[a-z0-9_]+")
# Exact pin: name, optional extras, ==version with no wildcards; a marker may follow ';'.
PIN_RE = re.compile(r"^[A-Za-z0-9_.\-]+(\[[A-Za-z0-9_,\-]+\])?==[A-Za-z0-9_.\-+!]+$")
TRACKED_ARTIFACT_RE = re.compile(r"(^|/)__pycache__(/|$)|\.py[co]$|(^|/)\.pytest_cache(/|$)")
# First commit written under AGENTS.md commit law; every later commit must answer the commit test.
COMMIT_LAW_BASELINE = "bb2fbd0546309b82fa2dbf81e8512dea0a4d3822"
COMMIT_LAW_MARKERS = ("Failed before", "Reused", "Deleted")


def load_authorities(root: Path) -> set[str]:
    """The real citation targets: question_ids from RESEARCH.md, row ids from the matrix."""
    authorities: set[str] = set()
    research = root / "research" / "RESEARCH.md"
    if research.exists():
        authorities |= set(re.findall(r"question_id: (Q\d+)", research.read_text(encoding="utf-8")))
    matrix = root / "research" / "ACCEPTANCE_MATRIX.yaml"
    if matrix.exists():
        text = matrix.read_text(encoding="utf-8")
        authorities |= set(re.findall(r"^\s*-?\s*id: ([A-Za-z0-9_]+)\s*$", text, re.M))
        # Assertion, duty, case, and operation list entries are citable authorities too
        # (AGENTS.md Tests law: "a Qn acceptance_check or a matrix row assertion").
        authorities |= set(re.findall(r"^\s+- ([a-z0-9][a-z0-9_]*_[a-z0-9_]+)\s*$", text, re.M))
    return authorities


def classify(path: Path) -> str:
    parts = path.parts
    if any(p in GENERATED_DIRS for p in parts) or "generated" in parts:
        return "generated"
    if parts[0] == "tools":
        return "tools"
    if parts[0] == "tests":
        return "tests"
    return "product"


def discover(root: Path) -> list[Path]:
    files = []
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        files.append(rel)
    return files


def logical_loc(root: Path, rel: Path) -> int:
    """Logical lines of code: NEWLINE-terminated statements minus docstring statements."""
    source = (root / rel).read_text(encoding="utf-8")
    try:
        newlines = sum(
            1
            for tok in tokenize.generate_tokens(io.StringIO(source).readline)
            if tok.type == tokenize.NEWLINE
        )
    except tokenize.TokenError:
        return sum(1 for line in source.splitlines() if line.strip() and not line.lstrip().startswith("#"))
    docstrings = 0
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                body = node.body
                if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                    docstrings += 1
    except SyntaxError:
        pass
    return max(newlines - docstrings, 0)


def intra_repo_imports(root: Path, rel: Path, repo_modules: set[str]) -> set[str]:
    tree = ast.parse((root / rel).read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in repo_modules:
                    found.add(top)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            if top in repo_modules:
                found.add(top)
    return found


def imports_mlx(root: Path, rel: Path) -> bool:
    tree = ast.parse((root / rel).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(a.name.split(".")[0] == "mlx" for a in node.names):
            return True
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "mlx":
            return True
    return False


def check_header(root: Path, rel: Path) -> tuple[set[str] | None, str | None]:
    """Return (declared_deps, violation). Declared deps are module stems; None deps on failure."""
    first = (root / rel).read_text(encoding="utf-8").splitlines()
    if not first:
        return None, f"{rel}: empty file has no header"
    m = HEADER_RE.match(first[0])
    if not m:
        return None, f"{rel}: line 1 must be '# <name> — <what>; depends on <files|(none)>.'"
    if m.group("name") != rel.name:
        return None, f"{rel}: header names '{m.group('name')}', file is '{rel.name}'"
    deps_text = m.group("deps").strip()
    if deps_text == "(none)":
        return set(), None
    declared = {Path(d.strip()).stem for d in deps_text.split(",") if d.strip()}
    return declared, None


def check_pins(root: Path) -> tuple[list[str], list[str]]:
    """Return (pinned_dependency_strings, violations) from pyproject.toml."""
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    try:
        import tomllib  # Python 3.11+

        data = tomllib.loads(text)
        deps = list(data.get("project", {}).get("dependencies", []))
        for group in data.get("dependency-groups", {}).values():
            deps.extend(d for d in group if isinstance(d, str))
        python_pin = data.get("project", {}).get("requires-python", "")
    except ModuleNotFoundError:  # sandbox interpreters below 3.11
        dep_blocks = re.findall(r"dependencies\s*=\s*\[(.*?)\]", text, re.S)
        groups = re.search(r"\[dependency-groups\](.*)", text, re.S)
        if groups:
            dep_blocks.extend(re.findall(r"=\s*\[(.*?)\]", groups.group(1), re.S))
        deps = []
        for block in dep_blocks:
            deps.extend(re.findall(r'"([^"]+)"', block))
        python_pin = next(iter(re.findall(r'requires-python\s*=\s*"([^"]+)"', text)), "")
    violations = [
        f"pyproject.toml: dependency '{d}' is not an exact name==version pin"
        for d in deps
        if not PIN_RE.match(d.split(";")[0].strip())
    ]
    if not re.match(r"^==\d+\.\d+(\.\*|\.\d+)?$", python_pin.strip()):
        violations.append("pyproject.toml: requires-python lacks an exact minor pin")
    return sorted(deps), violations


def _git(root: Path, *args: str) -> subprocess.CompletedProcess | None:
    """Run git; None means git itself was unavailable or timed out (callers fail closed)."""
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def check_tracked_artifacts(root: Path) -> tuple[str, list[str]]:
    """Build artifacts must never be tracked. A check that cannot run is a violation, not a pass."""
    if not (root / ".git").exists():
        return "skipped: not a git repository", []
    proc = _git(root, "ls-files")
    if proc is None or proc.returncode != 0:
        reason = "git unavailable or timed out" if proc is None else proc.stderr.strip() or "git ls-files failed"
        return "failed", [f"tracked-artifact check could not run (fail-closed): {reason}"]
    bad = sorted(f for f in proc.stdout.splitlines() if TRACKED_ARTIFACT_RE.search(f))
    return "ran", [f"tracked build artifact (untrack it and keep it ignored): {f}" for f in bad]


def check_commit_law(root: Path) -> tuple[str, list[str]]:
    """Every commit after the baseline answers the AGENTS.md commit test; unverifiable is a violation."""
    if not (root / ".git").exists():
        return "skipped: not a git repository", []
    proc = _git(root, "log", "--format=%H%n%B%x00", f"{COMMIT_LAW_BASELINE}..HEAD")
    if proc is None or proc.returncode != 0:
        reason = "git unavailable or timed out" if proc is None else proc.stderr.strip() or "git log failed"
        return "failed", [f"commit-law check could not run (fail-closed): {reason}"]
    violations = []
    for block in proc.stdout.split("\x00"):
        block = block.strip()
        if not block:
            continue
        sha, _, message = block.partition("\n")
        missing = [m for m in COMMIT_LAW_MARKERS if m not in message]
        if missing:
            violations.append(
                f"commit {sha[:7]} violates the AGENTS.md commit test — missing: {', '.join(missing)}"
            )
    return "ran", sorted(violations)


def check_test_citations(root: Path, rel: Path, authorities: set[str]) -> list[str]:
    """A citation must resolve to a real authority (Q29/Tests law); Q999 is not a citation."""
    violations = []
    tree = ast.parse((root / rel).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            doc = ast.get_docstring(node) or ""
            cited = set(CITATION_RE.findall(node.name)) | set(CITATION_RE.findall(doc))
            if not authorities:
                if not cited:
                    violations.append(f"{rel}::{node.name}: orphan test — no invariant cited")
                continue
            if not (cited & authorities):
                violations.append(
                    f"{rel}::{node.name}: orphan test — citations {sorted(cited) or ['(none)']} "
                    "resolve to no Qn acceptance_check or matrix row id"
                )
    return violations


def run(root: Path) -> dict:
    files = discover(root)
    authorities = load_authorities(root)
    repo_modules = PRODUCT_MODULES | {"schema", "adapters", "tools", "tests"} | {f.stem for f in files if len(f.parts) == 1}
    loc = {"product": 0, "tools": 0, "tests": 0}
    generated_loc = 0
    artifact_status, artifact_violations = check_tracked_artifacts(root)
    commit_status, commit_violations = check_commit_law(root)
    violations: list[str] = [*artifact_violations, *commit_violations]

    for rel in files:
        cls = classify(rel)
        if cls == "generated":
            generated_loc += logical_loc(root, rel)
            continue
        loc[cls] += logical_loc(root, rel)

        declared, header_violation = check_header(root, rel)
        if header_violation:
            violations.append(header_violation)
        actual = intra_repo_imports(root, rel, repo_modules)
        if cls in {"product", "tools"} and declared is not None and declared != actual:
            violations.append(
                f"{rel}: header declares deps {sorted(declared) or ['(none)']} but imports {sorted(actual) or ['(none)']}"
            )
        if cls == "product":
            owner = rel.parts[0].removesuffix(".py") if len(rel.parts) == 1 else rel.parts[0]
            allowed = ALLOWED_EDGES.get(owner, set())
            for target in sorted(actual - allowed - {owner}):
                violations.append(f"{rel}: illegal import of '{target}' (allowed: {sorted(allowed) or 'none'})")
            if imports_mlx(root, rel) and rel.name not in MLX_ALLOWED_FILES:
                violations.append(f"{rel}: mlx import outside {sorted(MLX_ALLOWED_FILES)} (Q30 confinement)")
        if cls == "tests":
            violations.extend(check_test_citations(root, rel, authorities))

    pins, pin_violations = check_pins(root)
    violations.extend(pin_violations)

    return {
        "checks": {"tracked_artifacts": artifact_status, "commit_law": commit_status},
        "j_partial": {
            "authored_executable_loc": loc,
            "generated_loc_reported_separately": generated_loc,
            "direct_dependencies": pins,
            "language_runtimes": ["python"],
            "independent_processes_declared": 1,
        },
        "files_checked": [str(f) for f in files],
        "violations": sorted(violations),
    }


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    report = run(root.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
