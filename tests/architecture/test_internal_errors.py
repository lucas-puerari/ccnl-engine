"""Internal errors stay inside the engine.

:class:`~ccnl_engine.contract.identity.rules_validity.SeriesGapError` is the
internal signal of a rule series without a value on a date.  It is a
``ValueError`` on purpose: only the modules below catch it, and
:func:`~ccnl_engine.contract.identity.rules_validity.rule_scope` translates it into
the public :class:`~ccnl_engine.MissingRuleError`.  A new module that
handles it must be added here, so that every place it can escape from is
reviewed; a module that stops using it must be removed.
"""

from __future__ import annotations

import ast
import importlib.resources
from pathlib import Path

import ccnl_engine
from ccnl_engine.contract.identity.rules_validity import SeriesGapError
from ccnl_engine.errors import CcnlEngineError
from tests.architecture._imports import read_package

_SRC = Path(str(importlib.resources.files("ccnl_engine"))).parent

#: Modules that define, raise or catch ``SeriesGapError``.
SERIES_GAP_MODULES: frozenset[str] = frozenset({
    "ccnl_engine.contract.identity.rules_validity",
    "ccnl_engine.contract.identity.validators",
    "ccnl_engine.payroll.service.chain",
})


def _modules_naming(name: str) -> set[str]:
    return {
        module.name
        for module in read_package(_SRC).values()
        if any(
            isinstance(node, ast.Name | ast.alias)
            and name in {getattr(node, "id", None), getattr(node, "name", None)}
            for node in ast.walk(module.tree)
        )
        or any(
            isinstance(node, ast.ClassDef) and node.name == name
            for node in ast.walk(module.tree)
        )
    }


def test_series_gap_error_is_handled_only_where_it_is_translated() -> None:
    """The allowlist is exact: no new handler, no stale entry."""
    assert _modules_naming(SeriesGapError.__name__) == SERIES_GAP_MODULES


def test_series_gap_error_is_not_public() -> None:
    """It is neither exported nor an engine error a caller could catch."""
    assert SeriesGapError.__name__ not in ccnl_engine.__all__
    assert not issubclass(SeriesGapError, CcnlEngineError)
