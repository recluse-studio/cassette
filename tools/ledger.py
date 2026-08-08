# ledger.py — J accounting and structure enforcement (Q29 partial; AGENTS.md Files/Structure/Tests rules); depends on (none).
"""Recompute the machine-checkable parts of J from a clean checkout and enforce repo law.

Checks (AGENTS.md):
  1. Header law: line 1 of every authored .py file is `# <name> — <what>; depends on <files|(none)>.`
  2. Header truth (product and tools files): declared intra-repo dependencies equal actual imports.
  3. Layer law (product files): imports point downward only; L2 siblings never import each other.
  4. Runtime confinement: `mlx` imports exist only in pager.py and trainer.py.
  5. Identity authority confinement: product digest and RFC 8785 imports exist only in store.py.
  6. Test citation law: every test function cites a ledger invariant (Qn or a matrix row id).
  7. Pin law: every dependency in pyproject.toml carries an exact `==` pin.
  8. LOC accounting: logical lines per class {product, tools, tests}; generated code reported
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
import tempfile
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
IDENTITY_AUTHORITY_IMPORTS = {"blake3", "hashlib", "rfc8785"}
HEADER_RE = re.compile(r"^# (?P<name>\S+) — .+; depends on (?P<deps>.+)\.\s*$")
CITATION_RE = re.compile(r"Q\d+|[A-Za-z][A-Za-z0-9_]*_[A-Za-z0-9_]+")
# Exact pin: name, optional extras, ==version with no wildcards; a marker may follow ';'.
PIN_RE = re.compile(r"^[A-Za-z0-9_.\-]+(\[[A-Za-z0-9_,\-]+\])?==[A-Za-z0-9_.\-+!]+$")
TRACKED_ARTIFACT_RE = re.compile(r"(^|/)__pycache__(/|$)|\.py[co]$|(^|/)\.pytest_cache(/|$)")
# First commit written under AGENTS.md commit law; every later commit must answer the commit test.
COMMIT_LAW_BASELINE = "bb2fbd0546309b82fa2dbf81e8512dea0a4d3822"
COMMIT_LAW_FIELDS = (
    ("Failed before", re.compile(r"^Failed before:[ \t]+\S.*$", re.M)),
    ("Reused instead of authored", re.compile(r"^Reused instead of authored:[ \t]+\S.*$", re.M)),
    ("Deleted", re.compile(r"^Deleted:[ \t]+\S.*$", re.M)),
)
COMMIT_LAW_REPAIR_RE = re.compile(
    r"^Commit-law repair (?P<sha>[0-9a-f]{40}) "
    r"(?P<label>Failed before|Reused instead of authored|Deleted):[ \t]+(?P<value>\S.*)$"
)
ASSERTION_LIST_KEYS = {"assertions", "portability_assertions", "required_for_every_training_row"}
AUTHORITY_VALUE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\b")


def load_authorities(root: Path) -> set[str]:
    """Load only Q acceptance checks, matrix row IDs, and explicit matrix assertions."""
    authorities: set[str] = set()
    research = root / "research" / "RESEARCH.md"
    if research.exists():
        authorities |= set(re.findall(r"question_id: (Q\d+)", research.read_text(encoding="utf-8")))
    matrix = root / "research" / "ACCEPTANCE_MATRIX.yaml"
    if matrix.exists():
        text = matrix.read_text(encoding="utf-8")
        authorities |= set(re.findall(r"^\s*-?\s*id: ([A-Za-z0-9_]+)\s*$", text, re.M))
        assertion_indent = None
        for line in text.splitlines():
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if assertion_indent is not None and stripped and indent <= assertion_indent:
                assertion_indent = None
            scalar = re.match(r"assertion:\s+(.+)$", stripped)
            if scalar:
                value = AUTHORITY_VALUE_RE.match(scalar.group(1))
                if value:
                    authorities.add(value.group(1))
                continue
            key = re.match(r"([a-z_]+):\s*$", stripped)
            if key and key.group(1) in ASSERTION_LIST_KEYS:
                assertion_indent = indent
                continue
            if assertion_indent is not None and indent > assertion_indent:
                item = re.match(r"-\s+(.+)$", stripped)
                value = AUTHORITY_VALUE_RE.match(item.group(1)) if item else None
                if value:
                    authorities.add(value.group(1))
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


def top_level_imports(root: Path, rel: Path) -> set[str]:
    tree = ast.parse((root / rel).read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return found


def check_identity_authority(rel: Path, imported: set[str]) -> list[str]:
    """Q32: only store.py may import product digest or canonicalization engines."""
    forbidden = sorted(imported & IDENTITY_AUTHORITY_IMPORTS)
    if classify(rel) == "product" and rel.name != "store.py" and forbidden:
        return [f"{rel}: imports {forbidden} outside store.py (Q32 identity authority confinement)"]
    return []


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
        return "failed", ["tracked-artifact check could not run (fail-closed): not a git repository"]
    proc = _git(root, "ls-files")
    if proc is None or proc.returncode != 0:
        reason = "git unavailable or timed out" if proc is None else proc.stderr.strip() or "git ls-files failed"
        return "failed", [f"tracked-artifact check could not run (fail-closed): {reason}"]
    bad = sorted(f for f in proc.stdout.splitlines() if TRACKED_ARTIFACT_RE.search(f))
    return "ran", [f"tracked build artifact (untrack it and keep it ignored): {f}" for f in bad]


def check_commit_law(root: Path, baseline: str = COMMIT_LAW_BASELINE) -> tuple[str, list[str]]:
    """Require each governed commit's fields or one exact correction in later immutable history."""
    if not (root / ".git").exists():
        return "failed", ["commit-law check could not run (fail-closed): not a git repository"]
    proc = _git(root, "log", "--format=%H%n%B%x00", f"{baseline}..HEAD")
    if proc is None or proc.returncode != 0:
        reason = "git unavailable or timed out" if proc is None else proc.stderr.strip() or "git log failed"
        return "failed", [f"commit-law check could not run (fail-closed): {reason}"]
    commits = {}
    for block in proc.stdout.split("\x00"):
        block = block.strip()
        if not block:
            continue
        sha, _, message = block.partition("\n")
        commits[sha] = message
    violations = []
    repairs = {}
    field_patterns = dict(COMMIT_LAW_FIELDS)
    for repair_sha, message in commits.items():
        for line in message.splitlines():
            if not line.startswith("Commit-law repair"):
                continue
            match = COMMIT_LAW_REPAIR_RE.fullmatch(line)
            if match is None:
                violations.append(
                    f"commit {repair_sha[:7]} has a malformed commit-law repair"
                )
                continue
            target = match.group("sha")
            label = match.group("label")
            key = (target, label)
            if target not in commits:
                violations.append(
                    f"commit {repair_sha[:7]} commit-law repair target is not governed history: "
                    f"{target[:7]}"
                )
                continue
            ancestry = _git(root, "merge-base", "--is-ancestor", target, repair_sha)
            if ancestry is None or ancestry.returncode != 0 or target == repair_sha:
                violations.append(
                    f"commit {repair_sha[:7]} commit-law repair is not later than target "
                    f"{target[:7]}"
                )
                continue
            if field_patterns[label].search(commits[target]):
                violations.append(
                    f"commit {target[:7]} already answers {label}; repair in {repair_sha[:7]} is invalid"
                )
                continue
            if key in repairs:
                violations.append(
                    f"commit {target[:7]} has a duplicate repair for {label} in {repair_sha[:7]}"
                )
                continue
            repairs[key] = repair_sha
    for sha, message in commits.items():
        missing = [label for label, pattern in COMMIT_LAW_FIELDS if not pattern.search(message)]
        missing = [label for label in missing if (sha, label) not in repairs]
        if missing:
            violations.append(
                f"commit {sha[:7]} violates the AGENTS.md commit test — missing or empty: "
                f"{', '.join(missing)}"
            )
    return "ran", sorted(violations)


def check_generated_integrity(root: Path) -> tuple[str, list[str]]:
    """Generated files must match both their digests and fresh generator output."""
    import hashlib

    gen_dir = root / "schema"
    if not gen_dir.exists():
        return "skipped: no generated directory", []
    files = sorted(
        p
        for p in gen_dir.rglob("*")
        if p.is_file() and p.name != "MANIFEST.json" and "__pycache__" not in p.parts
    )
    manifest_path = gen_dir / "MANIFEST.json"
    if not manifest_path.exists():
        return "failed", ["generated integrity: schema/ exists without MANIFEST.json (fail-closed)"]
    try:
        recorded = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return "failed", [f"generated integrity: MANIFEST.json unreadable (fail-closed): {exc}"]
    if not isinstance(recorded, dict) or any(
        not isinstance(name, str) or not isinstance(digest, str)
        for name, digest in getattr(recorded, "items", lambda: ())()
    ):
        return "failed", ["generated integrity: MANIFEST.json must map file names to digests"]
    violations = []
    actual_names = {p.relative_to(gen_dir).as_posix() for p in files}
    for name in sorted(actual_names - set(recorded)):
        violations.append(f"generated integrity: schema/{name} is not in MANIFEST.json")
    for name in sorted(set(recorded) - actual_names):
        violations.append(f"generated integrity: schema/{name} recorded but missing")
    for name in sorted(actual_names & set(recorded)):
        digest = hashlib.sha256((gen_dir / name).read_bytes()).hexdigest()
        if digest != recorded[name]:
            violations.append(f"generated integrity: schema/{name} hand-edited or drifted from generator")

    generator = root / "tools" / "genschema.py"
    if not generator.is_file():
        violations.append("generated integrity: schema/ exists without tools/genschema.py (fail-closed)")
        return "failed", violations
    try:
        with tempfile.TemporaryDirectory(prefix="cassette-schema-") as temp:
            expected_dir = Path(temp) / "schema"
            proc = subprocess.run(
                [sys.executable, "-B", str(generator), str(expected_dir)],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode != 0:
                reason = proc.stderr.strip() or proc.stdout.strip() or "generator failed"
                violations.append(f"generated integrity: regeneration failed (fail-closed): {reason}")
                return "failed", violations
            actual = {
                p.relative_to(gen_dir).as_posix(): p.read_bytes()
                for p in gen_dir.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts
            }
            expected = {
                p.relative_to(expected_dir).as_posix(): p.read_bytes()
                for p in expected_dir.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts
            }
            for name in sorted(set(actual) | set(expected)):
                if actual.get(name) != expected.get(name):
                    violations.append(
                        f"generated integrity: schema/{name} hand-edited or drifted from tools/genschema.py"
                    )
    except (OSError, subprocess.TimeoutExpired) as exc:
        violations.append(f"generated integrity: regeneration could not run (fail-closed): {exc}")
        return "failed", violations
    return "ran", violations


def check_test_citations(root: Path, rel: Path, authorities: set[str]) -> list[str]:
    """Require one real authority; other identifiers may accurately name fixture data."""
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
                    "resolve to no Qn acceptance_check, matrix row id, or matrix assertion"
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
    generated_status, generated_violations = check_generated_integrity(root)
    violations: list[str] = [*artifact_violations, *commit_violations, *generated_violations]

    for rel in files:
        cls = classify(rel)
        if cls == "generated":
            generated_loc += logical_loc(root, rel)
            continue
        loc[cls] += logical_loc(root, rel)

        declared, header_violation = check_header(root, rel)
        if header_violation:
            violations.append(header_violation)
        imported = top_level_imports(root, rel)
        actual = imported & repo_modules
        if cls in {"product", "tools"} and declared is not None and declared != actual:
            violations.append(
                f"{rel}: header declares deps {sorted(declared) or ['(none)']} but imports {sorted(actual) or ['(none)']}"
            )
        if cls == "product":
            owner = rel.parts[0].removesuffix(".py") if len(rel.parts) == 1 else rel.parts[0]
            allowed = ALLOWED_EDGES.get(owner, set())
            for target in sorted(actual - allowed - {owner}):
                violations.append(f"{rel}: illegal import of '{target}' (allowed: {sorted(allowed) or 'none'})")
            if "mlx" in imported and rel.name not in MLX_ALLOWED_FILES:
                violations.append(f"{rel}: mlx import outside {sorted(MLX_ALLOWED_FILES)} (Q30 confinement)")
            violations.extend(check_identity_authority(rel, imported))
        if cls == "tests":
            violations.extend(check_test_citations(root, rel, authorities))

    pins, pin_violations = check_pins(root)
    violations.extend(pin_violations)

    return {
        "checks": {
            "tracked_artifacts": artifact_status,
            "commit_law": commit_status,
            "generated_integrity": generated_status,
        },
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
