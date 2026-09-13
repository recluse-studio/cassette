# test_l05_package.py — Q31 supported launch from an installed local wheel; depends on pyproject.toml.
"""Prove the declared console entry uses the installed package closure, never this checkout."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import site
import subprocess
import sys
import tempfile
import zipfile


REPO = Path(__file__).resolve().parents[1]
UV = "/opt/homebrew/bin/uv"
RUNTIME_MODULES = ("broker", "cli", "compiler", "errors", "pager", "sources", "store", "trainer")


def _run(*command: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(command, cwd=cwd, env=environment, text=True, capture_output=True, check=True)


def _governed_source(destination: Path) -> None:
    """Copy all Git-governed files while excluding repository metadata and ignored dependency caches."""
    listing = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
        check=True,
    ).stdout.split(b"\0")
    for encoded in listing:
        if not encoded:
            continue
        relative = Path(encoded.decode())
        source = REPO / relative
        if source.is_file():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def test_q31_supported_launch_uses_only_the_installed_local_wheel():
    """Q31: the supported `cassette` launch loads runtime code and generated schemas from its installed wheel."""
    with tempfile.TemporaryDirectory(prefix="cassette-package-") as temporary:
        workspace = Path(temporary)
        source = workspace / "source"
        _governed_source(source)
        wheel_dir = workspace / "wheel"
        _run(UV, "build", "--offline", "--wheel", "--out-dir", str(wheel_dir), cwd=source)
        wheel = next(wheel_dir.glob("cassette-*.whl"))
        with zipfile.ZipFile(wheel) as archive:
            names = set(archive.namelist())
        assert {f"{module}.py" for module in RUNTIME_MODULES} <= names
        schema_files = {f"schema/{path.relative_to(source / 'schema').as_posix()}" for path in (source / "schema").rglob("*.json")}
        assert {"adapters/__init__.py", "schema/tables.py", "schema/validator.py"} | schema_files <= names
        assert not any(name.startswith(("tests/", "tools/", "research/", "pure_math_", ".agents/")) for name in names)

        environment = workspace / "environment"
        _run(UV, "venv", "--offline", "--python", sys.executable, str(environment), cwd=workspace)
        python = environment / "bin" / "python"
        dependency_site = Path(site.getsitepackages()[0]).resolve()
        scratch_site = next((environment / "lib").glob("python*/site-packages"))
        (scratch_site / "cassette-pinned-dependencies.pth").write_text(str(dependency_site) + "\n", encoding="utf-8")
        _run(UV, "pip", "install", "--offline", "--no-deps", "--python", str(python), str(wheel), cwd=workspace)
        launch = _run(str(environment / "bin" / "cassette"), "--help", cwd=workspace)
        assert "usage: cassette" in launch.stdout

        probe = """
import json
from pathlib import Path
import sys
import adapters, broker, cli, compiler, errors, pager, schema.validator, sources, store, trainer
modules = (adapters, broker, cli, compiler, errors, pager, schema.validator, sources, store, trainer)
paths = [str(Path(module.__file__).resolve()) for module in modules]
assert all(path.startswith(str(Path(sys.prefix).resolve())) for path in paths), paths
assert (Path(schema.validator.__file__).parent / "source_catalogue.json").is_file()
print(json.dumps(paths))
"""
        loaded = _run(str(python), "-c", probe, cwd=workspace)
        assert str(source) not in loaded.stdout
