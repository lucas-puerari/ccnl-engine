"""Every script under ``docs/examples/`` runs against the public API.

The numbered examples are the ones the guides embed: each must run and print
something. The per-contract examples in ``docs/examples/contracts/`` exist
for every bundled CCNL, exit cleanly and print the gross, the employee
contributions, the IRPEF, the net, the payability, the blocker codes and the
issue codes of the run.  The amounts are engine output, so only their shape
is checked.  A new file in either place is picked up with no test edit.
"""

from __future__ import annotations

import re
import runpy
from pathlib import Path

import pytest

from ccnl_engine.results import BlockerCode

_ROOT = Path(__file__).parents[3]
_EXAMPLES_DIR = _ROOT / "docs" / "examples"
_CCNL_DATA_DIR = _ROOT / "src" / "ccnl_engine" / "knowledge" / "ccnl" / "data"
_GUIDE_EXAMPLES = sorted(_EXAMPLES_DIR.glob("[0-9]*.py"))
_CONTRACT_EXAMPLES = sorted(
    path
    for path in (_EXAMPLES_DIR / "contracts").glob("*.py")
    if path.name != "__init__.py"
)
_AMOUNT = r"-?\d+(\.\d+)? EUR"
_CODES = r"none|[a-z0-9_]+(, [a-z0-9_]+)*"
_BLOCKERS = "none|({0})(, ({0}))*".format("|".join(code.value for code in BlockerCode))
_EXPECTED_LINES = (
    ("Gross", _AMOUNT),
    ("Contributions", _AMOUNT),
    ("IRPEF", _AMOUNT),
    ("Net", _AMOUNT),
    ("Payable", "True|False"),
    ("Blockers", _BLOCKERS),
    ("Issues", _CODES),
)


def _run(example: Path) -> None:
    """Run ``example`` as ``__main__`` and fail on a non-zero exit."""
    code = _exit_code(example)
    assert code in {0, None}, f"{example.name} exited with {code}"


def _exit_code(example: Path) -> str | int | None:
    """Run ``example`` as ``__main__``.

    Returns:
        The code of a ``SystemExit`` it raises, ``0`` when it raises none.
    """
    try:
        runpy.run_path(str(example), run_name="__main__")
    except SystemExit as exit_:
        return exit_.code
    return 0


def test_guide_examples_exist() -> None:
    """The glob below runs on the real docs tree, not an empty directory."""
    assert _GUIDE_EXAMPLES


@pytest.mark.parametrize("example", _GUIDE_EXAMPLES, ids=lambda p: p.stem)
def test_guide_example_runs_and_prints(
    example: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A guide example raises nothing and prints its result."""
    _run(example)
    assert capsys.readouterr().out.strip(), f"{example.name} printed nothing"


def test_every_bundled_ccnl_has_an_example() -> None:
    """Each CCNL of the bundle has exactly one example, and no other exists."""
    ccnls = {path.stem for path in _CCNL_DATA_DIR.glob("*.json")}

    assert ccnls
    assert {path.stem for path in _CONTRACT_EXAMPLES} == ccnls


@pytest.mark.parametrize("example", _CONTRACT_EXAMPLES, ids=lambda p: p.stem)
def test_contract_example_prints_the_run(
    example: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A per-contract example exits cleanly and prints every expected field."""
    _run(example)
    out = capsys.readouterr().out

    for label, value in _EXPECTED_LINES:
        pattern = rf"^{label}:\s+({value})$"
        assert re.search(pattern, out, re.MULTILINE), (
            f"{example.name} does not print {label!r} as {value!r}:\n{out}"
        )
