"""scripts/rename_app.py: a renamed copy of the repository still passes the structure check and
its tests, and none of the skills, glossaries or templates still name the old package."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["harness"]["app_package"]
IGNORE = shutil.ignore_patterns(".git", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", ".scratch")
PRACTICE_FILES = [".claude", "docs", ".github", "CONTEXT.md", "CLAUDE.md"]


def test_renamed_copy_passes_the_checks_and_names_the_old_package_nowhere(tmp_path: Path):
    copy = tmp_path / "repo"
    shutil.copytree(ROOT, copy, ignore=IGNORE)
    run = lambda *cmd: subprocess.run(cmd, cwd=copy, capture_output=True, text=True)  # noqa: E731

    rename = run(sys.executable, "scripts/rename_app.py", "demo")
    assert rename.returncode == 0, rename.stdout + rename.stderr
    assert (copy / "demo" / "CONTEXT.md").is_file() and not (copy / APP).exists()

    check = run(sys.executable, "scripts/check_structure.py")
    assert check.returncode == 0, check.stdout + check.stderr

    tests = run(sys.executable, "-m", "pytest", "-q", "-x", "--deselect", "tests/test_rename.py")
    assert tests.returncode == 0, tests.stdout[-3000:] + tests.stderr[-3000:]

    old_package = re.compile(rf"(^|[^A-Za-z0-9_./-]){re.escape(APP)}(/|\.|`)", re.MULTILINE)
    offenders = []
    for rel in PRACTICE_FILES + ["demo/CONTEXT.md", "demo/CLAUDE.md"]:
        paths = (copy / rel).rglob("*.md") if (copy / rel).is_dir() else [copy / rel]
        for path in paths:
            for line in path.read_text().splitlines():
                if old_package.search(line) and "harness.app" not in line:
                    offenders.append(f"{path.relative_to(copy)}: {line.strip()}")
    assert offenders == []
