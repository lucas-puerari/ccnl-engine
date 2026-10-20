"""The import and size gates of the architecture check."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from scripts.architecture.check import (
    BASELINE,
    CONTRACT,
    MAX_LINES,
    SOURCE,
    check_imports,
    check_sizes,
    load_baseline,
    main,
    read_contract,
    update_baseline,
)

if TYPE_CHECKING:
    from pathlib import Path

_CONTRACT = """# Architecture contract

## Dependency tiers

| Tier | Concepts |
|---|---|
| orchestration | `api`, `period` |
| computation | `sickness` |
| norms | `run` |

| Importer | Imported | Reason |
|---|---|---|
{exceptions}

## Next section

| orchestration | `sickness` |
"""

_UPWARD = "sickness/rules.py: imports period/services.py of tier orchestration"


def _contract(*exceptions: str) -> str:
    return _CONTRACT.format(exceptions="\n".join(exceptions))


def _tree(root: Path, files: dict[str, str]) -> Path:
    """Write a package holding ``files`` beside an empty package root.

    Returns:
        The package directory.
    """
    source = root / "src" / "ccnl_engine"
    for relative, text in {"__init__.py": "import ccnl_engine.api\n", **files}.items():
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return source


def test_the_contract_page_gives_every_concept_a_tier() -> None:
    """The tier table covers every root of the package and lists the exceptions."""
    contract = read_contract(CONTRACT.read_text(encoding="utf-8"))
    roots = {path.stem for path in SOURCE.iterdir() if path.suffix in {"", ".py"}}
    roots -= {"__init__", "__pycache__"}
    assert roots <= set(contract.tiers)
    assert (
        "seniority/services.py",
        "capability/rule/services.py",
    ) in contract.exceptions


def test_the_real_tree_passes() -> None:
    """The package keeps the tiers and the size baseline."""
    assert main([]) == 0


def test_an_upward_import_fails(tmp_path: Path) -> None:
    """A computation module importing orchestration fails; the reverse passes."""
    source = _tree(
        tmp_path,
        {
            "sickness/rules.py": "from ccnl_engine.period.services import x\n",
            "period/services.py": "from ccnl_engine.sickness.rules import y\n",
        },
    )
    errors = check_imports(source, _contract())
    assert len(errors) == 1
    assert errors[0].startswith(_UPWARD)


@pytest.mark.parametrize(
    "text",
    [
        (
            "from typing import TYPE_CHECKING\n"
            "if TYPE_CHECKING:\n    from ccnl_engine.period.services import x\n"
        ),
        (
            "import typing\n"
            "if typing.TYPE_CHECKING:\n    import ccnl_engine.period.services\n"
        ),
        "from ccnl_engine.run.models import x\nimport os\n",
        "from . import models\n",
    ],
)
def test_a_type_checking_or_lower_import_passes(tmp_path: Path, text: str) -> None:
    """Typing-only imports, lower tiers, the standard library and siblings pass."""
    source = _tree(tmp_path, {"sickness/rules.py": text})
    assert check_imports(source, _contract()) == []


@pytest.mark.parametrize(
    "text",
    [
        "def f():\n    from ccnl_engine.period.services import x\n",
        (
            "from typing import TYPE_CHECKING\n"
            "if TYPE_CHECKING:\n    pass\n"
            "else:\n    from ccnl_engine.period.services import x\n"
        ),
        "from ..period.services import x\n",
    ],
)
def test_a_runtime_upward_import_fails_wherever_it_sits(
    tmp_path: Path, text: str
) -> None:
    """A lazy, else-branch or relative upward import still runs, so it fails."""
    source = _tree(tmp_path, {"sickness/rules.py": text})
    errors = check_imports(source, _contract())
    assert [error[: len(_UPWARD)] for error in errors] == [_UPWARD]


def test_a_listed_upward_import_passes_and_fails_once_gone(tmp_path: Path) -> None:
    """A listed pair passes while imported and fails once stale."""
    row = "| `sickness/rules.py` | `period/services.py` | The reason |"
    source = _tree(
        tmp_path, {"sickness/rules.py": "import ccnl_engine.period.services\n"}
    )
    assert check_imports(source, _contract(row)) == []
    (source / "sickness" / "rules.py").write_text("", encoding="utf-8")
    assert check_imports(source, _contract(row)) == [
        (
            "sickness/rules.py: the contract lists an upward import of "
            "period/services.py that no longer exists"
        )
    ]


@pytest.mark.parametrize(
    ("files", "error"),
    [
        ({"ledger/models.py": ""}, "ledger/models.py: concept ledger has no tier"),
        (
            {"sickness/rules.py": "from ccnl_engine import api\n"},
            "sickness/rules.py: imports the package root ccnl_engine",
        ),
        (
            {"sickness/rules.py": "import ccnl_engine.ledger.models\n"},
            "sickness/rules.py: imports ledger, a concept with no tier",
        ),
    ],
)
def test_a_concept_without_a_tier_or_the_package_root_fails(
    tmp_path: Path, files: dict[str, str], error: str
) -> None:
    """Unknown concepts and imports of the package root fail closed."""
    source = _tree(tmp_path, files)
    assert check_imports(source, _contract()) == [error]


@pytest.mark.parametrize(
    "text", ["# no section\n", "## Dependency tiers\n\nNo table.\n"]
)
def test_a_contract_without_a_tier_table_is_rejected(text: str) -> None:
    """A contract page without the tier table cannot be read."""
    with pytest.raises(ValueError, match="architecture contract"):
        read_contract(text)


def _lines(count: int) -> str:
    return "x = 1\n" * count


def test_a_new_oversize_module_fails(tmp_path: Path) -> None:
    """A module over the limit that the baseline does not list fails."""
    source = _tree(tmp_path, {"run/models.py": _lines(MAX_LINES + 1)})
    assert check_sizes(source, {}) == [
        (
            f"src/ccnl_engine/run/models.py: {MAX_LINES + 1} lines, "
            f"over the limit of {MAX_LINES}"
        )
    ]


def test_a_listed_module_may_shrink_but_not_grow(tmp_path: Path) -> None:
    """A listed module passes below its baseline and fails above it."""
    module = "src/ccnl_engine/run/models.py"
    source = _tree(tmp_path, {"run/models.py": _lines(MAX_LINES + 5)})
    assert check_sizes(source, {module: MAX_LINES + 9}) == []
    assert check_sizes(source, {module: MAX_LINES + 4}) == [
        f"{module}: {MAX_LINES + 5} lines, grew from {MAX_LINES + 4}"
    ]


def test_a_listed_module_that_fits_fails_until_removed(tmp_path: Path) -> None:
    """A listed module back within the limit must leave the baseline."""
    module = "src/ccnl_engine/run/models.py"
    source = _tree(tmp_path, {"run/models.py": _lines(MAX_LINES)})
    assert check_sizes(source, {module: MAX_LINES + 1}) == [
        f"{module}: listed in the baseline but gone or within {MAX_LINES} lines"
    ]


def test_update_baseline_records_a_shrink_and_refuses_growth(tmp_path: Path) -> None:
    """The update refuses growth and records a module that now fits."""
    module = "src/ccnl_engine/run/models.py"
    source = _tree(tmp_path, {"run/models.py": _lines(MAX_LINES + 2)})
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({module: MAX_LINES + 1}), encoding="utf-8")
    assert len(update_baseline(source, baseline)) == 1
    assert load_baseline(baseline) == {module: MAX_LINES + 1}
    (source / "run" / "models.py").write_text(_lines(MAX_LINES), encoding="utf-8")
    assert update_baseline(source, baseline) == []
    assert load_baseline(baseline) == {}


def test_the_baseline_lists_only_modules_over_the_limit() -> None:
    """Every baseline entry is over the limit."""
    assert all(lines > MAX_LINES for lines in load_baseline(BASELINE).values())


def test_main_reports_the_errors_of_the_update(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A refused update prints why and exits with 1."""
    source = _tree(tmp_path, {"run/models.py": _lines(MAX_LINES + 1)})
    baseline = tmp_path / "baseline.json"
    baseline.write_text("{}", encoding="utf-8")
    monkeypatch.setattr("scripts.architecture.check.SOURCE", source)
    monkeypatch.setattr("scripts.architecture.check.BASELINE", baseline)
    assert main(["--update-baseline"]) == 1
    assert "over the limit" in capsys.readouterr().out
