"""Rules Diff domain types and computation.

:func:`diff_ccnl` walks every date-indexed
:class:`~ccnl_engine.contract.domain.validity.TimeSeries` in a
:class:`~ccnl_engine.contract.domain.identity.CCNL` (see
:mod:`~ccnl_engine.diff.service.rule_walk`) and reports which values
changed between two calendar dates.  The function is pure: it performs no
I/O and does not depend on the knowledge-base loader.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Literal

from ccnl_engine.diff.service.rule_walk import dated_rules
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import datetime as _datetime
    from decimal import Decimal

    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.contract.domain.validity import ValidityPeriod
    from ccnl_engine.diff.service.rule_walk import DatedRule
    from ccnl_engine.provenance.domain.chain import RuleProvenance

RegressionStatus = Literal["passed", "failed", "not_run"]


@dataclass(frozen=True)
class RuleChange:
    """One changed rule between two dates within a CCNL."""

    path: str
    label: str
    unit: str
    from_value: Decimal | None
    to_value: Decimal | None
    effective_date: date
    provenance: RuleProvenance | None


@dataclass(frozen=True)
class RulesDiff:
    """Summary of all rule changes observed between two dates in a CCNL."""

    ccnl_id: str
    from_date: date
    to_date: date
    changes: tuple[RuleChange, ...]
    affected_rules: int
    affected_scenarios: int
    regression_status: RegressionStatus
    verification_status: str
    generated_at: _datetime


def diff_ccnl(ccnl: CCNL, from_date: date, to_date: date) -> RulesDiff:
    """Return every rule that changed between *from_date* and *to_date*.

    The diff is purely data-driven: it compares
    :meth:`~ccnl_engine.contract.domain.validity.TimeSeries.period_at`
    for every date-indexed field in the CCNL tree.  Salary tranches,
    allowances, hourly divisor, additional months, seniority amounts, and
    employer-fund rates are all covered.

    Args:
        ccnl: A loaded CCNL object.
        from_date: Reference date representing the *before* state.
        to_date: Reference date representing the *after* state.

    Returns:
        A :class:`~ccnl_engine.diff.service.compute.RulesDiff` with
        ``affected_scenarios=0`` and ``regression_status="not_run"``.
        Use :func:`~ccnl_engine.diff.impact.count_affected_scenarios`
        and ``dataclasses.replace`` to annotate those fields.

    Raises:
        InvalidInputError: If *to_date* is not strictly after *from_date*.
    """
    if to_date <= from_date:
        msg = f"to_date ({to_date}) must be strictly after from_date ({from_date})"
        raise InvalidInputError(
            msg,
            remediation=(
                "Swap the arguments or use a to_date that is later than from_date."
            ),
        )

    changes = [
        change
        for rule in dated_rules(ccnl)
        if (change := _change(rule, from_date, to_date)) is not None
    ]
    ccnl_id = ccnl.meta.ccnl_id
    verification_status = (
        ccnl.ruleset.verification_status if ccnl.ruleset is not None else "unverified"
    )
    return RulesDiff(
        ccnl_id=ccnl_id,
        from_date=from_date,
        to_date=to_date,
        changes=tuple(changes),
        affected_rules=len(changes),
        affected_scenarios=0,
        regression_status="not_run",
        verification_status=verification_status,
        generated_at=datetime.now(tz=UTC),
    )


def _change(rule: DatedRule, from_date: date, to_date: date) -> RuleChange | None:
    """Return the change of *rule* between the two dates.

    Returns:
        The change, or ``None`` when the value is the same on both dates.
    """
    before: ValidityPeriod | None = rule.series.period_at(from_date)
    after: ValidityPeriod | None = rule.series.period_at(to_date)

    from_value: Decimal | None = before.value if before is not None else None
    to_value: Decimal | None = after.value if after is not None else None

    if from_value == to_value:
        return None

    effective_date = after.valid_from if after is not None else to_date
    provenance = after.provenance if after is not None else None

    return RuleChange(
        path=rule.path,
        label=rule.label,
        unit=rule.unit,
        from_value=from_value,
        to_value=to_value,
        effective_date=effective_date,
        provenance=provenance,
    )
