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
CITATION_RE = re.compile(r"Q\d+|exec_[a-z0-9_]+|train_[a-z0-9_]+|source_[a-z0-9_]+|f[45]_gate|q7[89]_[a-z_]+")


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
    violations = [f"pyproject.toml: dependency '{d}' lacks an exact == pin" for d in deps if "==" not in d]
    if "==" not in python_pin:
        violations.append("pyproject.toml: requires-python lacks an exact minor pin")
    return sorted(deps), violations


def check_test_citations(root: Path, rel: Path) -> list[str]:
    violations = []
    tree = ast.parse((root / rel).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            doc = ast.get_docstring(node) or ""
            if not CITATION_RE.search(node.name) and not CITATION_RE.search(doc):
                violations.append(
                    f"{rel}::{node.name}: orphan test — cite the Qn acceptance_check or matrix row it executes"
                )
    return violations


def run(root: Path) -> dict:
    files = discover(root)
    repo_modules = PRODUCT_MODULES | {"schema", "adapters", "tools", "tests"} | {f.stem for f in files if len(f.parts) == 1}
    loc = {"product": 0, "tools": 0, "tests": 0}
    generated_loc = 0
    violations: list[str] = []

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
            violations.extend(check_test_citations(root, rel))

    pins, pin_violations = check_pins(root)
    violations.extend(pin_violations)

    return {
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
