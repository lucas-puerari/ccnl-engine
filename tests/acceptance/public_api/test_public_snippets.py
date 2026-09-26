"""Smoke tests: every public code example in docs/examples/ must run without error."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_EXAMPLES_DIR = Path(__file__).parents[3] / "docs" / "examples"
_EXAMPLE_FILES = sorted(_EXAMPLES_DIR.glob("[0-9]*.py"))


@pytest.mark.parametrize("example_path", _EXAMPLE_FILES, ids=lambda p: p.stem)
def test_example_runs_without_error(
    example_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Import and execute a docs example; fail if it raises."""
    module_name = f"_docs_example_{example_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, example_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    out = capsys.readouterr().out
    assert out.strip(), f"{example_path.name} produced no output"
