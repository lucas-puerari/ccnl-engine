"""Rules Diff computation.

:func:`diff_ccnl` walks every date-indexed :class:`~ccnl_engine.engine.\
contract.domain.validity.TimeSeries` in a :class:`~ccnl_engine.engine.\
contract.domain.ccnl.CCNL` and reports which values changed between two
calendar dates.  The function is pure: it performs no I/O and does not
depend on the knowledge-base loader.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from ccnl_engine.engine.diff.domain.diff import RuleChange, RulesDiff

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
        LevelCategory,
        SeniorityIncrements,
        SeniorityTier,
    )
    from ccnl_engine.engine.contract.domain.validity import TimeSeries, ValidityPeriod


def diff_ccnl(ccnl: CCNL, from_date: date, to_date: date) -> RulesDiff:
    """Return every rule that changed between *from_date* and *to_date*.

    The diff is purely data-driven: it compares
    :meth:`~ccnl_engine.engine.contract.domain.validity.TimeSeries.period_at`
    for every date-indexed field in the CCNL tree.  Salary tranches,
    allowances, hourly divisor, additional months, seniority amounts, and
    employer-fund rates are all covered.

    Args:
        ccnl: A loaded CCNL object.
        from_date: Reference date representing the *before* state.
        to_date: Reference date representing the *after* state.

    Returns:
        A :class:`~ccnl_engine.engine.diff.domain.diff.RulesDiff` with
        ``affected_scenarios=0`` and ``regression_status="not_run"``.
        Use :func:`~ccnl_engine.engine.diff.impact.count_affected_scenarios`
        and ``dataclasses.replace`` to annotate those fields.

    Raises:
        ValueError: If *to_date* is not strictly after *from_date*.
    """
    if to_date <= from_date:
        msg = f"to_date ({to_date}) must be strictly after from_date ({from_date})"
        raise ValueError(msg)

    changes: list[RuleChange] = []

    # --- levels -----------------------------------------------------------
    for level in ccnl.levels:
        _check(
            changes,
            ts=level.base_salary,
            from_date=from_date,
            to_date=to_date,
            path=f"levels[{level.code}].base_salary",
            label=f"Level {level.code} - base salary",
            unit="EUR/month",
        )
        for allowance in level.fixed_allowances:
            _check(
                changes,
                ts=allowance.monthly,
                from_date=from_date,
                to_date=to_date,
                path=(
                    f"levels[{level.code}].fixed_allowances[{allowance.code}].monthly"
                ),
                label=(f"Allowance {allowance.code} - monthly (Level {level.code})"),
                unit="EUR/month",
            )

    # --- parameters -------------------------------------------------------
    params = ccnl.parameters
    _check(
        changes,
        ts=params.hourly_divisor,
        from_date=from_date,
        to_date=to_date,
        path="parameters.hourly_divisor",
        label="Parameter - hourly divisor",
        unit="hours",
    )
    _check(
        changes,
        ts=params.additional_months,
        from_date=from_date,
        to_date=to_date,
        path="parameters.additional_months",
        label="Parameter - additional months",
        unit="months",
    )

    # --- seniority increments ---------------------------------------------
    _check_seniority(changes, params.seniority_increments, from_date, to_date)

    # --- employer funds ---------------------------------------------------
    for fund in params.employer_funds:
        _check(
            changes,
            ts=fund.rate,
            from_date=from_date,
            to_date=to_date,
            path=f"parameters.employer_funds[{fund.code}].rate",
            label=f"Employer fund {fund.code} - rate",
            unit="%",
        )

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _check(
    changes: list[RuleChange],
    *,
    ts: TimeSeries,
    from_date: date,
    to_date: date,
    path: str,
    label: str,
    unit: str,
) -> None:
    """Append a RuleChange to *changes* if the TimeSeries value differs."""
    before: ValidityPeriod | None = ts.period_at(from_date)
    after: ValidityPeriod | None = ts.period_at(to_date)

    from_value: Decimal | None = before.value if before is not None else None
    to_value: Decimal | None = after.value if after is not None else None

    if from_value == to_value:
        return

    effective_date = after.valid_from if after is not None else to_date
    provenance = after.provenance if after is not None else None

    changes.append(
        RuleChange(
            path=path,
            label=label,
            unit=unit,
            from_value=from_value,
            to_value=to_value,
            effective_date=effective_date,
            provenance=provenance,
        )
    )


def _check_seniority(
    changes: list[RuleChange],
    si: SeniorityIncrements,
    from_date: date,
    to_date: date,
) -> None:
    """Walk all TimeSeries inside a SeniorityIncrements block."""
    for level_code, ts in si.amount_by_level.items():
        _check(
            changes,
            ts=ts,
            from_date=from_date,
            to_date=to_date,
            path=(f"parameters.seniority_increments.amount_by_level[{level_code}]"),
            label=f"Seniority increment - Level {level_code}",
            unit="EUR/month",
        )

    for i, tier in enumerate(si.tiers):
        _check_tier(changes, tier, i, from_date, to_date)

    for cat, by_level in si.amount_by_level_by_category.items():
        _check_seniority_category(changes, cat, by_level, from_date, to_date)

    if si.apprentice_amount is not None:
        _check(
            changes,
            ts=si.apprentice_amount,
            from_date=from_date,
            to_date=to_date,
            path="parameters.seniority_increments.apprentice_amount",
            label="Seniority increment - apprentice amount",
            unit="EUR/month",
        )


def _check_tier(
    changes: list[RuleChange],
    tier: SeniorityTier,
    index: int,
    from_date: date,
    to_date: date,
) -> None:
    for level_code, ts in tier.amount_by_level.items():
        _check(
            changes,
            ts=ts,
            from_date=from_date,
            to_date=to_date,
            path=(
                f"parameters.seniority_increments"
                f".tiers[{index}].amount_by_level[{level_code}]"
            ),
            label=(f"Seniority increment - tier {index + 1}, Level {level_code}"),
            unit="EUR/month",
        )


def _check_seniority_category(
    changes: list[RuleChange],
    category: LevelCategory,
    by_level: dict[str, TimeSeries],
    from_date: date,
    to_date: date,
) -> None:
    for level_code, ts in by_level.items():
        _check(
            changes,
            ts=ts,
            from_date=from_date,
            to_date=to_date,
            path=(
                f"parameters.seniority_increments"
                f".amount_by_level_by_category[{category}][{level_code}]"
            ),
            label=(f"Seniority increment - {category}, Level {level_code}"),
            unit="EUR/month",
        )
