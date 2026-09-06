"""Smoke-test every script in docs/examples/.

Each script is executed via runpy.run_path(). If any example raises an
exception, the test fails — ensuring that API changes that break examples
are caught in CI rather than silently producing stale documentation.

A new .py file in docs/examples/ is automatically picked up; no test edit
is needed.
"""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest

_EXAMPLES_DIR = Path(__file__).parent.parent.parent / "docs" / "examples"
_EXAMPLE_FILES = sorted(_EXAMPLES_DIR.glob("*.py"))


@pytest.mark.parametrize("example_file", _EXAMPLE_FILES, ids=lambda p: p.stem)
def test_example_runs(example_file: Path) -> None:
    """Execute the example script and assert it raises no exception."""
    runpy.run_path(str(example_file))
