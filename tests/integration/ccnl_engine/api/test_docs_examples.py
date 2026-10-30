"""Every script under ``docs/examples/``, the README and docstring examples run.

The theme examples (``docs/examples/<theme>/example.py``) are the ones the
guides embed: each must run and print something. The per-contract examples in
``docs/examples/agreement/<slug>/example.py`` exist
for every bundled CCNL, exit cleanly and print the gross, the employee
contributions, the IRPEF, the net, the payability, the blocker codes and the
issue codes of the run.  The amounts are engine output, so only their shape
is checked.  A new file in either place is picked up with no test edit.
"""

from __future__ import annotations

import ast
import re
import runpy
import textwrap
from pathlib import Path

import pytest

from ccnl_engine.results import BlockerCode

_ROOT = Path(__file__).parents[4]
_EXAMPLES_DIR = _ROOT / "docs" / "examples"
_README = _ROOT / "README.md"
_SOURCE_DIR = _ROOT / "src" / "ccnl_engine"
#: A literal block a docstring opens with ``Example::`` or ``Usage::``.
_DOCSTRING_BLOCK = re.compile(
    r"^[ \t]*(?:Example|Usage)::\n\n((?:[ \t]+.*\n|\n)+)", re.MULTILINE
)
_CCNL_DATA_DIR = _ROOT / "src" / "ccnl_engine" / "knowledge" / "agreement"
_GUIDE_EXAMPLES = sorted(_EXAMPLES_DIR.glob("*/example.py"))
_CONTRACT_EXAMPLES = sorted((_EXAMPLES_DIR / "agreement").glob("*/example.py"))
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
    assert code in {0, None}, f"{example.parent.name} exited with {code}"


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


@pytest.mark.parametrize("example", _GUIDE_EXAMPLES, ids=lambda p: p.parent.name)
def test_guide_example_runs_and_prints(
    example: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A guide example raises nothing and prints its result."""
    _run(example)
    assert capsys.readouterr().out.strip(), f"{example.parent.name} printed nothing"


def test_every_bundled_ccnl_has_an_example() -> None:
    """Each CCNL of the bundle has exactly one example, and no other exists."""
    ccnls = {path.stem for path in _CCNL_DATA_DIR.glob("*.json")}

    assert ccnls
    assert {path.parent.name for path in _CONTRACT_EXAMPLES} == ccnls


def test_every_contract_example_prints_the_run(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each per-contract example exits cleanly and prints every expected field."""
    missing: dict[str, list[str]] = {}
    for example in _CONTRACT_EXAMPLES:
        _run(example)
        out = capsys.readouterr().out
        absent = [
            label
            for label, value in _EXPECTED_LINES
            if not re.search(rf"^{label}:\s+({value})$", out, re.MULTILINE)
        ]
        if absent:
            missing[example.parent.name] = absent
    assert missing == {}


def test_readme_example_runs(capsys: pytest.CaptureFixture[str]) -> None:
    """The README has one Python example, and it runs and prints."""
    blocks = re.findall(r"```python\n(.*?)```", _README.read_text("utf-8"), re.DOTALL)

    assert len(blocks) == 1
    exec(compile(blocks[0], str(_README), "exec"), {"__name__": "__main__"})
    assert capsys.readouterr().out.strip()


def _docstring_examples() -> list[tuple[str, str]]:
    """Return every ``Example::`` or ``Usage::`` block of the package.

    Returns:
        ``(location, code)`` pairs, the code dedented.
    """
    examples: list[tuple[str, str]] = []
    for path in sorted(_SOURCE_DIR.rglob("*.py")):
        tree = ast.parse(path.read_text("utf-8"))
        nodes = [tree, *ast.walk(tree)]
        for node in nodes:
            if not isinstance(
                node,
                ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
            ):
                continue
            doc = ast.get_docstring(node, clean=False)
            for block in _DOCSTRING_BLOCK.findall(f"{doc}\n" if doc else ""):
                name = getattr(node, "name", "module")
                location = f"{path.relative_to(_SOURCE_DIR)}:{name}"
                examples.append((location, textwrap.dedent(block)))
    return list(dict.fromkeys(examples))


_DOCSTRING_EXAMPLES = _docstring_examples()


def test_docstring_examples_exist() -> None:
    """The scan finds the examples of the facade and of the package."""
    assert {location for location, _ in _DOCSTRING_EXAMPLES} >= {
        "__init__.py:module",
        "api.py:PayrollEngine",
    }


@pytest.mark.parametrize(
    ("location", "code"), _DOCSTRING_EXAMPLES, ids=[e[0] for e in _DOCSTRING_EXAMPLES]
)
def test_docstring_example_runs(location: str, code: str) -> None:
    """A docstring example runs as written: it is the first code users copy."""
    exec(compile(code, location, "exec"), {"__name__": "__main__"})
