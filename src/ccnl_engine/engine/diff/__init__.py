"""ccnl_engine.engine.diff — Rules Diff computation and formatting.

Compares a :class:`~ccnl_engine.engine.contract.domain.ccnl.CCNL` at two
calendar dates and reports every rule that changed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.diff.service.compute import RuleChange, RulesDiff, diff_ccnl
from ccnl_engine.engine.diff.service.format import format_diff

if TYPE_CHECKING:
    from ccnl_engine.engine.diff.service.impact import ImpactResult

__all__ = [
    "ImpactResult",
    "RuleChange",
    "RulesDiff",
    "count_affected_scenarios",  # noqa: F822
    "diff_ccnl",
    "format_diff",
]


def __getattr__(name: str) -> object:
    if name in {"ImpactResult", "count_affected_scenarios"}:
        from ccnl_engine.engine.diff.service import impact as _impact  # noqa: PLC0415

        return getattr(_impact, name)
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
