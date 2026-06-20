from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, Callable, TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from ailint.parser import Section


class CLIResult(NamedTuple):
    stdout: str
    stderr: str
    returncode: int


@pytest.fixture
def fixtures_dir() -> Path:
    """Returns the Path to tests/fixtures."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def parse_fixture(fixtures_dir: Path) -> Callable[[str], list[Section]]:
    """Fixture that returns a function to read and parse a fixture file."""
    from ailint.parser import parse

    def _parse_fixture(name: str) -> list[Section]:
        fixture_file = fixtures_dir / name
        content = fixture_file.read_text(encoding="utf-8")
        return parse(content)

    return _parse_fixture


@pytest.fixture
def run_cli() -> Callable[[list[str]], CLIResult]:
    """Fixture that returns a function to run python -m ailint.cli via subprocess."""
    def _run_cli(args: list[str]) -> CLIResult:
        src_path = str(Path(__file__).parent.parent / "src")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join([src_path, env.get("PYTHONPATH", "")])

        result = subprocess.run(
            [sys.executable, "-m", "ailint.cli"] + list(args),
            capture_output=True,
            text=True,
            env=env,
        )
        return CLIResult(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
        )

    return _run_cli
