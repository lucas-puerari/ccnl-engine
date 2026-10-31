"""Leave rules: tiers by seniority and date, month credit, permits and ramps.

CCNL Funzioni Centrali 2022-2024 art. 21 cc. 2, 4-5: 28 days, 26 for the
first three years of a first public employment; the CCNL 2025-2027 art. 21,
in force from 1 January 2027, gives 28 days to every worker.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.leave.models import FerieAccrual, LeaveEntitlementTier, LeaveRules
from ccnl_engine.leave.permit.models import (
    NewHireRamp,
    PermitHours,
    PermitRules,
    RampStep,
)
from ccnl_engine.leave.types import LeaveBucket, MonthCredit

_RULES = LeaveRules(
    default_annual_days=Decimal(28),
    entitlement_tiers=(
        LeaveEntitlementTier(
            service_months_min=0, annual_days=Decimal(26), valid_until=date(2027, 1, 1)
        ),
        LeaveEntitlementTier(service_months_min=36, annual_days=Decimal(28)),
    ),
)


@pytest.mark.parametrize(
    ("months", "day", "days"),
    [
        (12, date(2026, 6, 1), 26),
        (12, date(2027, 1, 1), 28),
        (40, date(2026, 6, 1), 28),
        (None, date(2026, 6, 1), 28),
    ],
)
def test_tier_in_force_on_the_day(months: int | None, day: date, days: int) -> None:
    """The 26 days end on 1 January 2027; seniority unknown takes the default."""
    assert _RULES.annual_days(months, day) == Decimal(days)


def test_tier_from_a_date() -> None:
    """A tier that starts later is not in force before."""
    tier = LeaveEntitlementTier(annual_days=Decimal(30), valid_from=date(2027, 1, 1))

    assert not tier.in_force(date(2026, 12, 31))
    assert tier.in_force(date(2027, 1, 1))


def _permit(**kwargs: object) -> PermitRules:
    values: dict[str, object] = {
        "bucket": LeaveBucket.ROL,
        "annual_hours": (PermitHours(hours=Decimal(56)),),
        **kwargs,
    }
    return PermitRules.model_validate(values)


@pytest.mark.parametrize(
    ("credit", "served", "expected"),
    [
        (MonthCredit.WHOLE_MONTH, 30, True),
        (MonthCredit.WHOLE_MONTH, 29, False),
        (MonthCredit.MORE_THAN_HALF, 16, True),
        (MonthCredit.MORE_THAN_HALF, 15, False),
    ],
)
def test_month_credit(credit: MonthCredit, served: int, expected: bool) -> None:
    """A whole month, or more than fifteen days of a 30-day month."""
    assert credit.credits(served, 30) is expected


def test_permit_hours_by_employer_size() -> None:
    """Commercio Art. 158: 56 hours up to 15 employees, 72 above."""
    permit = _permit(
        annual_hours=(
            PermitHours(hours=Decimal(56)),
            PermitHours(hours=Decimal(72), headcount_above=15),
        )
    )

    assert permit.hours_for(15) == Decimal(56)
    assert permit.hours_for(16) == Decimal(72)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"bucket": LeaveBucket.FERIE},
        {"bucket": LeaveBucket.EX_FESTIVITA, "includes_ex_festivita": True},
        {"annual_hours": (PermitHours(hours=Decimal(1), headcount_above=15),)},
        {
            "annual_hours": (
                PermitHours(hours=Decimal(1)),
                PermitHours(hours=Decimal(2)),
            )
        },
    ],
)
def test_invalid_permit_is_rejected(kwargs: dict[str, object]) -> None:
    """Ferie, a pooled ex festività, no default size or two default sizes."""
    with pytest.raises(ValidationError):
        _permit(**kwargs)


def test_ramp_share_by_hire_date_and_months() -> None:
    """Commercio Art. 158: 0% before two years for the hires after 1 March 2011."""
    ramp = NewHireRamp(
        hired_after=date(2011, 3, 1),
        steps=(
            RampStep(service_months_min=0, share=Decimal(0)),
            RampStep(service_months_min=24, share=Decimal("0.5")),
        ),
    )

    assert ramp.share(date(2011, 3, 1), 0) == 1
    assert ramp.share(date(2026, 1, 1), 23) == 0
    assert ramp.share(date(2026, 1, 1), 24) == Decimal("0.5")


def test_ramp_gates_by_hire_window_and_employer_size() -> None:
    """Hires after ``hired_until`` and employers above the size accrue in full."""
    ramp = NewHireRamp(
        hired_after=date(2024, 2, 16),
        hired_until=date(2027, 2, 15),
        headcount_max=40,
        steps=(RampStep(service_months_min=0, share=Decimal(0)),),
    )

    assert ramp.share(date(2027, 2, 15), 0) == 0
    assert ramp.share(date(2027, 2, 16), 0) == 1
    assert (ramp.covers(40), ramp.covers(41)) == (True, False)


def test_ramp_must_start_at_zero_months() -> None:
    """A ramp whose first step is not at hire is rejected."""
    with pytest.raises(ValidationError, match="start at 0 months"):
        NewHireRamp(
            hired_after=date(2011, 3, 1),
            steps=(RampStep(service_months_min=12, share=Decimal(1)),),
        )


def test_rules_reject_a_pool_beside_its_ex_festivita() -> None:
    """A rol pool that includes the ex festività leaves no separate bucket."""
    with pytest.raises(ValidationError, match="distinct buckets"):
        LeaveRules(
            default_annual_days=Decimal(26),
            permits=(
                _permit(includes_ex_festivita=True),
                _permit(bucket=LeaveBucket.EX_FESTIVITA),
            ),
        )


def test_buckets_and_seniority_dependence() -> None:
    """The accrued buckets, and the days that change with the seniority."""
    rules = LeaveRules(
        default_annual_days=Decimal(20),
        entitlement_tiers=(
            LeaveEntitlementTier(service_months_min=120, annual_days=Decimal(21)),
        ),
        ferie_accrual=FerieAccrual(),
        permits=(_permit(),),
    )

    assert rules.buckets == {LeaveBucket.FERIE, LeaveBucket.ROL}
    assert rules.days_depend_on_seniority(date(2026, 1, 1))
    assert not _RULES.buckets
    assert not LeaveRules(default_annual_days=Decimal(26)).days_depend_on_seniority(
        date(2026, 1, 1)
    )


def test_bucket_units() -> None:
    """Ferie are counted in days, the permits in hours."""
    assert [b.unit for b in LeaveBucket] == ["days", "hours", "hours"]
