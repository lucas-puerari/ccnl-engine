"""Rules Diff domain models.

A :class:`RulesDiff` captures every :class:`RuleChange` observed between
two calendar dates within a single CCNL.  The object is immutable; callers
that want to annotate it with scenario-impact counts or regression status
use ``dataclasses.replace(diff, affected_scenarios=N, regression_status="passed")``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from datetime import date, datetime
    from decimal import Decimal

    from ccnl_engine.engine.provenance.domain.chain import RuleProvenance

RegressionStatus = Literal["passed", "failed", "not_run"]


@dataclass(frozen=True)
class RuleChange:
    """One changed rule between two dates within a CCNL.

    ``from_value`` is ``None`` when the rule did not exist at ``from_date``
    (newly introduced tranche).  ``to_value`` is ``None`` when the rule was
    removed at ``to_date`` (rare in practice).
    """

    path: str
    """Dot-path identifying the rule, e.g. ``"levels[C2].base_salary"``."""
    label: str
    """Human-readable description, e.g. ``"Level C2 - base salary"``."""
    unit: str
    """Measurement unit, e.g. ``"EUR/month"``, ``"hours"``, ``"%"``."""
    from_value: Decimal | None
    """Value in effect at ``from_date``, or ``None`` if not yet applicable."""
    to_value: Decimal | None
    """Value in effect at ``to_date``, or ``None`` if rule was removed."""
    effective_date: date
    """``valid_from`` of the period that became active at ``to_date``."""
    provenance: RuleProvenance | None
    """Source provenance of the new period, if available."""


@dataclass(frozen=True)
class RulesDiff:
    """Summary of all rule changes observed between two dates in a CCNL.

    ``affected_scenarios`` and ``regression_status`` default to ``0`` /
    ``"not_run"`` and are set by the caller after running
    :func:`~ccnl_engine.engine.diff.impact.count_affected_scenarios`.
    """

    ccnl_id: str
    """CCNL identifier, e.g. ``"metalmeccanico-federmeccanica"``."""
    from_date: date
    """Reference date representing the *before* state."""
    to_date: date
    """Reference date representing the *after* state."""
    changes: tuple[RuleChange, ...]
    """All detected rule changes, in tree-walk order."""
    affected_rules: int
    """Number of changed rules; always ``len(changes)``."""
    affected_scenarios: int
    """Payroll scenarios producing a different result; 0 if not computed."""
    regression_status: RegressionStatus
    """Outcome of the reference test suite; ``"not_run"`` if not computed."""
    verification_status: str
    """Inherited from ``ccnl.ruleset.verification_status``."""
    generated_at: datetime
    """Timestamp when this diff was produced."""
