"""ccnl_engine.engine.diff — Rules Diff computation and formatting.

Compares a :class:`~ccnl_engine.engine.contract.domain.ccnl.CCNL` at two
calendar dates and reports every rule that changed.
"""

from ccnl_engine.engine.diff.compute import diff_ccnl
from ccnl_engine.engine.diff.domain.diff import RuleChange, RulesDiff
from ccnl_engine.engine.diff.format import format_diff
from ccnl_engine.engine.diff.impact import count_affected_scenarios

__all__ = [
    "RuleChange",
    "RulesDiff",
    "count_affected_scenarios",
    "diff_ccnl",
    "format_diff",
]
