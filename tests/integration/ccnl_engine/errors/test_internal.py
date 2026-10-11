"""Internal errors stay inside the engine.

:class:`~ccnl_engine.agreement.validity.rules.SeriesGapError` is the
internal signal of a rule series without a value on a date.  It is a
``ValueError`` on purpose: only the modules below catch it, and
:func:`~ccnl_engine.agreement.validity.rules.rule_scope` translates it into
the public :class:`~ccnl_engine.MissingRuleError`.  A new module that
handles it must be added here, so that every place it can escape from is
reviewed; a module that stops using it must be removed.
"""

from __future__ import annotations

import ast
import importlib.resources
from pathlib import Path

import ccnl_engine
from ccnl_engine.agreement.validity.rules import SeriesGapError
from ccnl_engine.errors import CcnlEngineError

_PACKAGE = Path(str(importlib.resources.files("ccnl_engine")))

#: Modules that define, raise or catch ``SeriesGapError``.
SERIES_GAP_MODULES: frozenset[str] = frozenset({
    "ccnl_engine.agreement.validity.rules",
    "ccnl_engine.agreement.validators",
    "ccnl_engine.compensation.element.rules",
})


def _parsed_modules() -> dict[str, ast.Module]:
    """Parse every module of the package, keyed by dotted name.

    Returns:
        The syntax tree of each module; a package by its own name.
    """
    modules: dict[str, ast.Module] = {}
    for path in sorted(_PACKAGE.rglob("*.py")):
        parts = path.relative_to(_PACKAGE.parent).with_suffix("").parts
        name = ".".join(parts[:-1] if parts[-1] == "__init__" else parts)
        modules[name] = ast.parse(path.read_text(encoding="utf-8"))
    return modules


def _modules_naming(name: str) -> set[str]:
    return {
        module
        for module, tree in _parsed_modules().items()
        if any(
            isinstance(node, ast.Name | ast.alias)
            and name in {getattr(node, "id", None), getattr(node, "name", None)}
            for node in ast.walk(tree)
        )
        or any(
            isinstance(node, ast.ClassDef) and node.name == name
            for node in ast.walk(tree)
        )
    }


def test_series_gap_error_is_handled_only_where_it_is_translated() -> None:
    """The allowlist is exact: no new handler, no stale entry."""
    assert _modules_naming(SeriesGapError.__name__) == SERIES_GAP_MODULES


def test_series_gap_error_is_not_public() -> None:
    """It is neither exported nor an engine error a caller could catch."""
    assert SeriesGapError.__name__ not in ccnl_engine.__all__
    assert not issubclass(SeriesGapError, CcnlEngineError)
