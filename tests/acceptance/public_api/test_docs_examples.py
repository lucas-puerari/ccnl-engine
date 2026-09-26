"""Every script under ``docs/examples/`` runs against the public API.

The numbered examples are the ones the guides embed: each must run and print
something. The per-contract examples in ``docs/examples/contracts/`` must run
without error. A new file in either place is picked up with no test edit.
"""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest

_EXAMPLES_DIR = Path(__file__).parents[3] / "docs" / "examples"
_GUIDE_EXAMPLES = sorted(_EXAMPLES_DIR.glob("[0-9]*.py"))
_CONTRACT_EXAMPLES = sorted(
    path
    for path in (_EXAMPLES_DIR / "contracts").glob("*.py")
    if path.name != "__init__.py"
)


def test_guide_examples_exist() -> None:
    """The glob below runs on the real docs tree, not an empty directory."""
    assert _GUIDE_EXAMPLES


@pytest.mark.parametrize("example", _GUIDE_EXAMPLES, ids=lambda p: p.stem)
def test_guide_example_runs_and_prints(
    example: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A guide example raises nothing and prints its result."""
    runpy.run_path(str(example), run_name="__main__")
    assert capsys.readouterr().out.strip(), f"{example.name} printed nothing"


@pytest.mark.parametrize("example", _CONTRACT_EXAMPLES, ids=lambda p: p.stem)
def test_contract_example_runs(example: Path) -> None:
    """A per-contract example raises nothing."""
    runpy.run_path(str(example), run_name="__main__")
