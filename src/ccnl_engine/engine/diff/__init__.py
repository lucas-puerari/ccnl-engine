"""ccnl_engine.engine.diff — Rules Diff computation and formatting.

Compares a :class:`~ccnl_engine.engine.contract.domain.ccnl.CCNL` at two
calendar dates and reports every rule that changed.
"""

from __future__ import annotations

from ccnl_engine.engine.diff.service.compute import RuleChange, RulesDiff, diff_ccnl
from ccnl_engine.engine.diff.service.format import format_diff

__all__ = [
    "RuleChange",
    "RulesDiff",
    "diff_ccnl",
    "format_diff",
]
