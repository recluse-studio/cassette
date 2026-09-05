# ledger.py — complete J accounting and isolated component-removal proof (Q29/Q78); depends on (none).
"""Recompute J from a clean checkout and enforce repository law.

Checks (AGENTS.md):
  1. Header law: line 1 of every authored .py file is `# <name> — <what>; depends on <files|(none)>.`
  2. Header truth (product and tools files): declared intra-repo dependencies equal actual imports.
  3. Layer law (product files): imports point downward only; L2 siblings never import each other.
  4. Runtime confinement: `mlx` imports exist only in pager.py and trainer.py.
  5. Identity authority confinement: product digest and RFC 8785 imports exist only in store.py.
  6. Test citation law: every test function cites a ledger invariant (Qn or a matrix row id).
  7. Pin law: every dependency in pyproject.toml carries an exact `==` pin.
  8. Governed-source accounting: Git-owned and intentionally untracked source is measured; foreign
     interpreter environments, dependency trees, and ignored caches are not repository code.
  9. Removal-map law: every authored product or tool file names one declared acceptance authority;
     isolated deletion must fail a direct, cited proof while its unchanged control passes.
 10. LOC accounting: logical lines per class {product, tools, tests}; generated code reported
     separately and never counted as authored.
 11. Complete J: source classification, process/runtime/dependency manifests, kernel and model-
     branch audits, duplicate-authority audit, and shipped binary closure are deterministic.

Output is deterministic. Exit 0 when clean, 1 when any violation exists. Usage:
    python3 tools/ledger.py [repo_root]
    python3 tools/ledger.py --prove-j [repo_root] [report_path]
"""

from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import tokenize
from pathlib import Path

UNTRACKED_CACHE_DIRS = {".git", "__pycache__", ".pytest_cache"}
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
# The aggregate S00-S19 audit established the citation baseline at this immutable commit.
COMMIT_AUTHORITY_BASELINE = "246d52cbc0367074fd42e65055420a826c0113ff"
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
REMOVAL_MAP_BEGIN = "<!-- CASSETTE_REMOVAL_MAP_BEGIN -->"
REMOVAL_MAP_END = "<!-- CASSETTE_REMOVAL_MAP_END -->"
J_REPORT = Path("tools/generated/s27_j_report.json")
NATIVE_KERNEL_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".m", ".mm", ".metal", ".rs", ".swift"}
PROCESS_MODULES = {"multiprocessing", "subprocess"}
PROCESS_CALLS = {"fork", "forkpty", "posix_spawn", "posix_spawnp", "system"}
MODEL_BRANCH_NAMES = {"model_family", "model_name", "model_type"}
MODEL_NAME_RE = re.compile(
    r"(?<![a-z0-9])(kimi|qwen|llama|mistral|mixtral|gemma|deepseek)(?![a-z0-9])", re.I
)


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
    """Return Git-owned and intentionally introduced Python source, not foreign environments."""

    def git_paths(*args: str) -> list[Path] | None:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", *args],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None
        return [Path(item) for item in result.stdout.split("\0") if item]

    def eligible(rel: Path) -> bool:
        return rel.suffix == ".py" and (root / rel).is_file()

    def foreign_environment(rel: Path) -> bool:
        return any(
            (root / parent / "pyvenv.cfg").is_file()
            for parent in (rel.parent, *rel.parent.parents)
        )

    tracked = git_paths("--cached")
    untracked = git_paths("--others", "--exclude-standard")
    if tracked is None or untracked is None:
        return [
            path.relative_to(root)
            for path in sorted(root.rglob("*.py"))
            if not any(part in UNTRACKED_CACHE_DIRS for part in path.relative_to(root).parts)
            and not foreign_environment(path.relative_to(root))
        ]

    owned = {rel for rel in tracked if eligible(rel)}
    for rel in untracked:
        if not eligible(rel) or any(part in UNTRACKED_CACHE_DIRS for part in rel.parts):
            continue
        if foreign_environment(rel):
            continue
        owned.add(rel)
    return sorted(owned)


def load_removal_map(root: Path) -> tuple[dict[str, list[str]] | None, list[str]]:
    """Read the single AGENTS-owned Q78 map without accepting a parallel authority."""
    path = root / "AGENTS.md"
    if not path.is_file():
        return None, ["Q78 removal map is unavailable: AGENTS.md is missing"]
    source = path.read_text(encoding="utf-8")
    if source.count(REMOVAL_MAP_BEGIN) != 1 or source.count(REMOVAL_MAP_END) != 1:
        return None, ["Q78 removal map requires exactly one bounded AGENTS.md authority block"]
    body = source.split(REMOVAL_MAP_BEGIN, 1)[1].split(REMOVAL_MAP_END, 1)[0].strip()
    if body.startswith("```json") and body.endswith("```"):
        body = body[len("```json"):-len("```")].strip()
    try:
        removal_map = json.loads(body)
    except json.JSONDecodeError as error:
        return None, [f"Q78 removal map is not canonical JSON: {error}"]
    if not isinstance(removal_map, dict):
        return None, ["Q78 removal map must be one object keyed by repository path"]
    return removal_map, []


def check_removal_map(
    root: Path, files: list[Path], authorities: set[str]
) -> tuple[str, list[str]]:
    """Require one declared, real authority for every authored product and tool file."""
    removal_map, violations = load_removal_map(root)
    if removal_map is None:
        return "failed", violations
    required = {
        rel.as_posix()
        for rel in files
        if classify(rel) in {"product", "tools"}
    }
    violations.extend(
        f"Q78 removal map lacks authored file: {name}"
        for name in sorted(required - set(removal_map))
    )
    violations.extend(
        f"Q78 removal map names no authored product or tool file: {name}"
        for name in sorted(set(removal_map) - required)
    )
    for name in sorted(set(removal_map) & required):
        rows = removal_map[name]
        if (
            not isinstance(rows, list)
            or len(rows) != 1
            or any(not isinstance(row, str) or not row for row in rows)
        ):
            violations.append(f"Q78 removal map entry {name} requires exactly one nonempty authority ID")
            continue
        unknown = sorted(set(rows) - authorities)
        if unknown:
            violations.append(f"Q78 removal map entry {name} names unknown authorities: {unknown}")
            continue
        header = (root / name).read_text(encoding="utf-8").splitlines()[0]
        undeclared = sorted(set(rows) - set(re.findall(r"Q\d+", header)))
        if undeclared:
            violations.append(
                f"Q78 removal map entry {name} names authorities absent from its file header: {undeclared}"
            )
    return "ran", violations


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


def check_mlx_confinement(root: Path, rel: Path, imported: set[str]) -> list[str]:
    """Reject direct imports and indirect MLX runtime access outside its two owners."""

    if rel.as_posix() in MLX_ALLOWED_FILES:
        return []
    if "mlx" in imported:
        return [f"{rel}: mlx import outside {sorted(MLX_ALLOWED_FILES)} (Q30 confinement)"]
    tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=str(rel))
    loaders = {"__import__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in {"importlib", "builtins"}:
            loaders.update(
                alias.asname or alias.name for alias in node.names
                if alias.name in {"import_module", "__import__"}
            )
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Name) and node.id in loaders
            or isinstance(node, ast.Attribute) and node.attr in {"import_module", "__import__"}
        ):
            continue
        call = parents.get(node)
        # Only an immediate literal import proves that acquisition excludes MLX.
        if isinstance(call, ast.Call) and call.func is node:
            argument = call.args[0] if call.args else next(
                (item.value for item in call.keywords if item.arg == "name"), None
            )
            if (
                isinstance(argument, ast.Constant) and isinstance(argument.value, str)
                and argument.value and not argument.value.startswith(".")
                and argument.value.split(".")[0] != "mlx"
            ):
                continue
        return [f"{rel}: unresolved or MLX dynamic import outside {sorted(MLX_ALLOWED_FILES)} (Q30 confinement)"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and (
            node.attr == "_mlx_runtime"
            or isinstance(node.value, ast.Name) and node.value.id == "mx"
        ):
            return [
                f"{rel}: MLX runtime reference outside {sorted(MLX_ALLOWED_FILES)} "
                "(Q30 confinement)"
            ]
        if isinstance(node, ast.Name) and node.id == "_mlx_runtime":
            return [
                f"{rel}: MLX runtime reference outside {sorted(MLX_ALLOWED_FILES)} "
                "(Q30 confinement)"
            ]
    return []


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


def check_commit_law(
    root: Path,
    baseline: str = COMMIT_LAW_BASELINE,
    authority_baseline: str | None = None,
) -> tuple[str, list[str]]:
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
            repairs[key] = (repair_sha, match.group("value"))
    for sha, message in commits.items():
        missing = [label for label, pattern in COMMIT_LAW_FIELDS if not pattern.search(message)]
        missing = [label for label in missing if (sha, label) not in repairs]
        if missing:
            violations.append(
                f"commit {sha[:7]} violates the AGENTS.md commit test — missing or empty: "
                f"{', '.join(missing)}"
            )
    citation_baseline = (
        COMMIT_AUTHORITY_BASELINE if baseline == COMMIT_LAW_BASELINE else baseline
    ) if authority_baseline is None else authority_baseline
    cited = _git(root, "rev-list", f"{citation_baseline}..HEAD")
    if cited is None or cited.returncode != 0:
        reason = "git unavailable or timed out" if cited is None else cited.stderr.strip() or "git rev-list failed"
        violations.append(f"commit authority-citation check could not run (fail-closed): {reason}")
    else:
        authorities = load_authorities(root)
        for sha in cited.stdout.splitlines():
            message = commits.get(sha, "")
            match = re.search(r"^Failed before:[ \t]+(.+)$", message, re.M)
            repair = repairs.get((sha, "Failed before"))
            value = match.group(1) if match is not None else repair[1] if repair else None
            values = set(CITATION_RE.findall(value)) if value is not None else set()
            if value is not None and not values & authorities:
                violations.append(
                    f"commit {sha[:7]} Failed before cites no research question, matrix row, "
                    "or matrix assertion"
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


def _module_name(path: str) -> str:
    rel = Path(path)
    parts = rel.with_suffix("").parts
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def _imports(tree: ast.AST) -> set[str]:
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def removal_proof_node(root: Path, target: str, authority: str) -> str | None:
    """Find the first test that cites the mapped authority and directly imports its owner."""
    module = _module_name(target)
    candidates = []
    for path in sorted((root / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if not any(name == module or name.startswith(f"{module}.") for name in _imports(tree)):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.name.startswith("test"):
                continue
            cited = set(CITATION_RE.findall(node.name)) | set(CITATION_RE.findall(ast.get_docstring(node) or ""))
            if authority in cited:
                candidates.append(f"{path.relative_to(root).as_posix()}::{node.name}")
    return min(candidates) if candidates else None


def _pytest(root: Path, node: str | None = None) -> subprocess.CompletedProcess:
    command = [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    if node:
        command.append(node)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    return subprocess.run(
        command, cwd=root, capture_output=True, text=True, timeout=3600, env=environment
    )


def _bypass_source(source: bytes, marker: str) -> bytes:
    """Preserve import shape while making every executable function expose removal on use."""
    tree = ast.parse(source.decode())

    class Bypass(ast.NodeTransformer):
        def _replace(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
            node.body = [ast.Raise(ast.Call(ast.Name("RuntimeError", ast.Load()), [ast.Constant(marker)], []))]
            return node

        visit_FunctionDef = _replace
        visit_AsyncFunctionDef = _replace

    return (ast.unparse(ast.fix_missing_locations(Bypass().visit(tree))) + "\n").encode()


def removal_experiment(root: Path, target: str, authority: str) -> dict:
    """Require one cited proof to fail under physical deletion and executable bypass."""
    node = removal_proof_node(root, target, authority)
    if node is None:
        raise ValueError(f"Q78 {target} -> {authority} has no direct cited proof")
    control = _pytest(root, node)
    if control.returncode:
        raise ValueError(f"Q78 control failed for {target} -> {authority}: {control.stdout}{control.stderr}")
    path = root / target
    original, mode = path.read_bytes(), path.stat().st_mode
    path.unlink()
    try:
        removed = _pytest(root, node)
    finally:
        path.write_bytes(original)
        path.chmod(mode)
    if removed.returncode == 0:
        raise ValueError(f"Q78 nonconsequential map entry survived deletion: {target} -> {authority}")
    witness = _module_name(target).split(".")[-1].lower()
    if witness not in f"{removed.stdout}\n{removed.stderr}".lower():
        raise ValueError(f"Q78 deletion of {target} failed outside its component boundary")
    if path.read_bytes() != original:
        raise ValueError(f"Q78 experiment did not restore {target} byte-exactly")
    marker = f"Q78_BYPASS_{_module_name(target).replace('.', '_')}"
    path.write_bytes(_bypass_source(original, marker))
    try:
        bypassed = _pytest(root, node)
    finally:
        path.write_bytes(original)
        path.chmod(mode)
    if bypassed.returncode == 0:
        raise ValueError(f"Q78 nonconsequential map entry survived executable bypass: {target} -> {authority}")
    if marker not in f"{bypassed.stdout}\n{bypassed.stderr}":
        raise ValueError(f"Q78 bypass of {target} failed outside its executable boundary")
    return {
        "authority": authority,
        "bypass_exit_code": bypassed.returncode,
        "control_exit_code": control.returncode,
        "proof_node": node,
        "removed_exit_code": removed.returncode,
        "target": target,
    }


def _owned_files(root: Path) -> list[Path]:
    def foreign_environment(rel: Path) -> bool:
        return any(
            (root / parent / "pyvenv.cfg").is_file()
            for parent in (rel.parent, *rel.parent.parents)
        )

    proc = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if proc is None or proc.returncode:
        return sorted(
            path.relative_to(root) for path in root.rglob("*")
            if path.is_file() and not foreign_environment(path.relative_to(root))
        )
    return sorted(
        Path(name) for name in proc.stdout.split("\0")
        if name and (root / name).is_file() and not foreign_environment(Path(name))
    )


def _call_name(node: ast.Call) -> str:
    parts, value = [], node.func
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def build_accounting(root: Path, files: list[Path], loc: dict, generated_loc: int, pins: list[str]) -> dict:
    """Build Q29's classifier, manifests, branch table, authority table, and binary closure."""
    source_files = {kind: [] for kind in ("product", "tools", "tests", "generated")}
    kernel_sites, process_sites, model_sites, authority_sites = [], [], [], []
    for rel in files:
        source_files[classify(rel)].append(rel.as_posix())
        if classify(rel) != "product":
            continue
        tree = ast.parse((root / rel).read_text(encoding="utf-8"))
        imports = _imports(tree)
        process_sites.extend(f"{rel}:import:{name}" for name in sorted(imports & PROCESS_MODULES))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call = _call_name(node)
                if call in {f"os.{name}" for name in PROCESS_CALLS}:
                    process_sites.append(f"{rel}:{node.lineno}:{call}")
                if call.endswith(("metal_kernel", "custom_kernel")):
                    kernel_sites.append(f"{rel}:{node.lineno}:{call}")
            if isinstance(node, (ast.If, ast.IfExp)):
                names = {item.id for item in ast.walk(node.test) if isinstance(item, ast.Name)}
                strings = [item.value for item in ast.walk(node.test) if isinstance(item, ast.Constant) and isinstance(item.value, str)]
                if names & MODEL_BRANCH_NAMES or any(MODEL_NAME_RE.search(value) for value in strings):
                    model_sites.append(f"{rel}:{node.lineno}")
        if rel.name != "store.py":
            authority_sites.extend(
                f"{rel}:identity:{name}" for name in sorted(imports & IDENTITY_AUTHORITY_IMPORTS)
            )
        if rel.name != "errors.py" and any(
            isinstance(node, (ast.Assign, ast.AnnAssign))
            and any(isinstance(name, ast.Name) and name.id == "CODES" for name in ast.walk(node))
            for node in tree.body
        ):
            authority_sites.append(f"{rel}:error-vocabulary")
    owned = _owned_files(root)
    kernel_sites.extend(rel.as_posix() for rel in owned if rel.suffix.lower() in NATIVE_KERNEL_SUFFIXES)
    binaries = []
    for rel in owned:
        payload = (root / rel).read_bytes()
        try:
            payload.decode("utf-8")
        except UnicodeDecodeError:
            binaries.append({"bytes": len(payload), "path": rel.as_posix()})
        else:
            if b"\0" in payload:
                binaries.append({"bytes": len(payload), "path": rel.as_posix()})
    python_pin = re.search(r'requires-python\s*=\s*"([^"]+)"', (root / "pyproject.toml").read_text(encoding="utf-8"))
    return {
        "authored_executable_loc": {
            "product": loc["product"], "tools": loc["tools"], "total": loc["product"] + loc["tools"]
        },
        "direct_dependency_manifest": pins,
        "duplicate_authority_sites": sorted(set(authority_sites)),
        "generated_loc_reported_separately": generated_loc,
        "language_runtime_manifest": [{"name": "python", "pin": python_pin.group(1) if python_pin else ""}],
        "model_specific_branch_table": sorted(set(model_sites)),
        "new_numerical_kernel_sites": sorted(set(kernel_sites)),
        "process_manifest": [{"mechanism": "one asyncio process", "runtime": "python"}],
        "process_spawn_sites": sorted(set(process_sites)),
        "shipped_binary_files": binaries,
        "source_files": source_files,
        "test_loc_reported_separately": loc["tests"],
    }


J_LABELS = [
    "failed_acceptance_rows", "new_numerical_kernels", "authored_executable_LOC",
    "independent_processes", "language_runtimes", "direct_dependencies",
    "model_specific_branches", "duplicate_authorities", "shipped_binary_bytes",
]


def _j_values(accounting: dict, failed_rows: int) -> list[int]:
    return [
        failed_rows,
        len(accounting["new_numerical_kernel_sites"]),
        accounting["authored_executable_loc"]["total"],
        len(accounting["process_manifest"]) + len(accounting["process_spawn_sites"]),
        len(accounting["language_runtime_manifest"]),
        len(accounting["direct_dependency_manifest"]),
        len(accounting["model_specific_branch_table"]),
        len(accounting["duplicate_authority_sites"]),
        sum(item["bytes"] for item in accounting["shipped_binary_files"]),
    ]


def _evidence_digest(root: Path) -> str:
    fixed = {"AGENTS.md", "MATHS.md", "ORIGINAL_REMIT.md", "PHILOSOPHY.md", "pyproject.toml", "uv.lock"}
    paths = [
        rel for rel in _owned_files(root)
        if rel != J_REPORT and (
            rel.as_posix() in fixed or rel.suffix == ".py"
            or rel.parts[0] in {"research", "schema", "tests"}
            or rel.parts[:2] == ("tools", "generated")
        )
    ]
    digest = hashlib.sha256()
    for rel in paths:
        payload = (root / rel).read_bytes()
        digest.update(rel.as_posix().encode() + b"\0" + str(len(payload)).encode() + b"\0" + payload)
    return f"sha256:{digest.hexdigest()}"


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode() + b"\n"


def prove_complete_j(root: Path) -> dict:
    """Execute Q29/Q78 from one clean checkout and return its deterministic report."""
    status = _git(root, "status", "--porcelain", "--untracked-files=all")
    if status is None or status.returncode or status.stdout:
        raise ValueError("Q29 complete J proof requires one clean Git checkout")
    baseline = run(root, verify_report=False)
    if baseline["violations"]:
        raise ValueError(f"Q29 baseline ledger failed: {baseline['violations']}")
    suite = _pytest(root)
    print(suite.stdout, file=sys.stderr, end="")
    if suite.returncode:
        raise ValueError(f"Q29 full suite failed: {suite.stdout}{suite.stderr}")
    summary = re.search(r"(?P<passed>\d+) passed(?:, (?P<skipped>\d+) skipped)?", suite.stdout)
    if summary is None:
        raise ValueError("Q29 full suite emitted no exact pytest pass count")
    removal_map, errors = load_removal_map(root)
    if removal_map is None or errors:
        raise ValueError(f"Q78 removal map failed: {errors}")
    removals = []
    for target, rows in sorted(removal_map.items()):
        if not isinstance(rows, list) or len(rows) != 1:
            raise ValueError(f"Q78 {target} must name exactly one removal authority")
        removals.append(removal_experiment(root, target, rows[0]))
    final_status = _git(root, "status", "--porcelain", "--untracked-files=all")
    if final_status is None or final_status.returncode or final_status.stdout:
        raise ValueError("Q78 removal campaign did not restore the clean checkout")
    accounting = baseline["accounting"]
    return {
        "accounting": accounting,
        "evidence_digest": _evidence_digest(root),
        "j": {"labels": J_LABELS, "values": _j_values(accounting, 0)},
        "removal_proofs": removals,
        "schema_version": 1,
        "suite": {
            "command": f"{Path(sys.executable).name} -B -m pytest -q -p no:cacheprovider",
            "failed_acceptance_rows": [],
            "passed": int(summary.group("passed")),
            "skipped": int(summary.group("skipped") or 0),
        },
    }


def check_j_report(root: Path, accounting: dict) -> tuple[str, list[str], dict | None]:
    """Bind the committed S27 report to the exact executable and acceptance-evidence tree."""
    implementation_path = root / "IMPLEMENTATION.md"
    implementation = implementation_path.read_text(encoding="utf-8") if implementation_path.is_file() else ""
    block = implementation.split("  - id: S27", 1)[1].split("  - id: S28", 1)[0] if "  - id: S27" in implementation else ""
    required = bool(re.search(r"^\s*status:\s*DONE\b", block, re.M))
    path = root / J_REPORT
    if not path.is_file():
        return ("failed", [f"Q29 complete J report is missing: {J_REPORT}"], None) if required else ("pending: S27", [], None)
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return "failed", [f"Q29 complete J report is unreadable: {error}"], None
    violations = []
    if path.read_bytes() != _canonical_json(report):
        violations.append("Q29 complete J report is not canonical JSON")
    if set(report) != {"accounting", "evidence_digest", "j", "removal_proofs", "schema_version", "suite"}:
        violations.append("Q29 complete J report has an inexact top-level field set")
        return "ran", violations, report
    if report["schema_version"] != 1:
        violations.append("Q29 complete J report has an unsupported schema version")
    if report["accounting"] != accounting:
        violations.append("Q29 complete J report accounting is stale")
    if report["evidence_digest"] != _evidence_digest(root):
        violations.append("Q29 complete J report evidence digest is stale")
    if report["j"] != {"labels": J_LABELS, "values": _j_values(accounting, 0)}:
        violations.append("Q29 complete J tuple disagrees with the current accounting")
    suite = report["suite"]
    if not isinstance(suite, dict) or suite.get("failed_acceptance_rows") != [] or not isinstance(suite.get("passed"), int) or suite.get("passed", 0) < 1:
        violations.append("Q29 complete J report lacks one passing zero-failure full-suite result")
    removal_map, map_errors = load_removal_map(root)
    violations.extend(map_errors)
    expected = {}
    if removal_map is not None:
        for target, rows in removal_map.items():
            if isinstance(rows, list) and len(rows) == 1:
                expected[target] = (rows[0], removal_proof_node(root, target, rows[0]))
    proofs = report["removal_proofs"]
    if not isinstance(proofs, list) or {item.get("target") for item in proofs if isinstance(item, dict)} != set(expected):
        violations.append("Q78 complete removal proof set disagrees with the current map")
    else:
        for item in proofs:
            target = item["target"]
            authority, node = expected[target]
            if set(item) != {"authority", "bypass_exit_code", "control_exit_code", "proof_node", "removed_exit_code", "target"}:
                violations.append(f"Q78 removal proof for {target} has an inexact field set")
            elif item["authority"] != authority or item["proof_node"] != node:
                violations.append(f"Q78 removal proof for {target} is stale or misbound")
            elif (
                item["control_exit_code"] != 0
                or not isinstance(item["removed_exit_code"], int)
                or item["removed_exit_code"] == 0
                or not isinstance(item["bypass_exit_code"], int)
                or item["bypass_exit_code"] == 0
            ):
                violations.append(f"Q78 removal proof for {target} is nonconsequential")
    return "ran", violations, report


def run(root: Path, *, verify_report: bool = True) -> dict:
    files = discover(root)
    authorities = load_authorities(root)
    repo_modules = PRODUCT_MODULES | {"schema", "adapters", "tools", "tests"} | {f.stem for f in files if len(f.parts) == 1}
    loc = {"product": 0, "tools": 0, "tests": 0}
    generated_loc = 0
    artifact_status, artifact_violations = check_tracked_artifacts(root)
    commit_status, commit_violations = check_commit_law(root)
    generated_status, generated_violations = check_generated_integrity(root)
    removal_status, removal_violations = check_removal_map(root, files, authorities)
    violations: list[str] = [
        *artifact_violations,
        *commit_violations,
        *generated_violations,
        *removal_violations,
    ]

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
            violations.extend(check_mlx_confinement(root, rel, imported))
            violations.extend(check_identity_authority(rel, imported))
        if cls == "tests":
            violations.extend(check_test_citations(root, rel, authorities))

    pins, pin_violations = check_pins(root)
    violations.extend(pin_violations)
    accounting = build_accounting(root, files, loc, generated_loc, pins)
    for key, label in (
        ("new_numerical_kernel_sites", "Q30 undeclared authored numerical kernel"),
        ("process_spawn_sites", "Q29 independent process outside the one-process contract"),
        ("model_specific_branch_table", "Q29 model-specific branch is not data"),
        ("duplicate_authority_sites", "Q32 duplicate authority"),
    ):
        violations.extend(f"{label}: {site}" for site in accounting[key])
    report_status, report_violations, report = (
        check_j_report(root, accounting) if verify_report else ("not requested", [], None)
    )
    violations.extend(report_violations)

    return {
        "checks": {
            "tracked_artifacts": artifact_status,
            "commit_law": commit_status,
            "generated_integrity": generated_status,
            "removal_map": removal_status,
            "complete_j_report": report_status,
        },
        "accounting": accounting,
        "j": report["j"] if report is not None and not report_violations else None,
        "files_checked": [str(f) for f in files],
        "violations": sorted(violations),
    }


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--prove-j":
        root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
        output = Path(sys.argv[3]) if len(sys.argv) > 3 else root / J_REPORT
        try:
            payload = _canonical_json(prove_complete_j(root.resolve()))
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(payload)
            sys.stdout.buffer.write(payload)
            return 0
        except (OSError, subprocess.TimeoutExpired, ValueError) as error:
            print(str(error), file=sys.stderr)
            return 1
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    report = run(root.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
