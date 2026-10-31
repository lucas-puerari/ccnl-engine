"""Monthly accrual: days served, month rule, seniority, ramp and part time."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.leave.accrual.rules import (
    AccrualFacts,
    MonthService,
    accrue_month,
    month_service,
)
from ccnl_engine.leave.balance.models import LeaveAccount
from ccnl_engine.leave.models import FerieAccrual, LeaveEntitlementTier, LeaveRules
from ccnl_engine.leave.permit.models import (
    NewHireRamp,
    PermitHours,
    PermitRules,
    RampStep,
)
from ccnl_engine.leave.types import LeaveBucket, MonthCredit

_ROL = PermitRules(
    bucket=LeaveBucket.ROL,
    annual_hours=(
        PermitHours(hours=Decimal(56)),
        PermitHours(hours=Decimal(72), headcount_above=15),
    ),
    month_credit=MonthCredit.WHOLE_MONTH,
    ramp=NewHireRamp(
        hired_after=date(2011, 3, 1),
        steps=(
            RampStep(service_months_min=0, share=Decimal(0)),
            RampStep(service_months_min=24, share=Decimal("0.5")),
        ),
    ),
)
_EX_FEST = PermitRules(
    bucket=LeaveBucket.EX_FESTIVITA, annual_hours=(PermitHours(hours=Decimal(32)),)
)
_RULES = LeaveRules(
    default_annual_days=Decimal(20),
    entitlement_tiers=(
        LeaveEntitlementTier(service_months_min=120, annual_days=Decimal(21)),
    ),
    ferie_accrual=FerieAccrual(month_credit=MonthCredit.MORE_THAN_HALF),
    permits=(_ROL, _EX_FEST),
)
_WHOLE = MonthService(served=31, days=31)


def _facts(**kwargs: object) -> AccrualFacts:
    values: dict[str, object] = {
        "year": 2026,
        "month": 1,
        "service": _WHOLE,
        "headcount": 20,
        "hired_on": date(2010, 1, 1),
        "seniority_months": 200,
        **kwargs,
    }
    return AccrualFacts(**values)  # type: ignore[arg-type]


def _credits(facts: AccrualFacts) -> dict[LeaveBucket, tuple[Decimal, bool]]:
    account = accrue_month(LeaveAccount(), _RULES, facts)
    return {b.bucket: (b.accrued_twelfths, b.exact) for b in account.balances}


def test_whole_month_accrues_every_bucket() -> None:
    """A twelfth of 21 days, 72 hours of ROL and 32 of ex festività."""
    assert _credits(_facts()) == {
        LeaveBucket.FERIE: (Decimal(21), True),
        LeaveBucket.ROL: (Decimal(72), True),
        LeaveBucket.EX_FESTIVITA: (Decimal(32), True),
    }


def test_month_fraction_follows_each_rule() -> None:
    """16 days of 31: ferie and ROL follow their rules, ex festività has none.

    Ferie (more than 15 days) accrue, ROL (whole months) does not, ex
    festività accrue nothing and turn inexact.
    """
    credited = _credits(_facts(service=MonthService(served=16, days=31)))

    assert credited == {
        LeaveBucket.FERIE: (Decimal(21), True),
        LeaveBucket.ROL: (Decimal(0), True),
        LeaveBucket.EX_FESTIVITA: (Decimal(0), False),
    }


def test_unknown_facts_turn_the_balance_inexact() -> None:
    """Unknown seniority, hire date and absences: default days, first step."""
    credited = _credits(
        _facts(
            seniority_months=None,
            hired_on=None,
            service=MonthService(served=31, days=31, known=False),
        )
    )

    assert credited == {
        LeaveBucket.FERIE: (Decimal(20), False),
        LeaveBucket.ROL: (Decimal(0), False),
        LeaveBucket.EX_FESTIVITA: (Decimal(32), False),
    }


def test_new_hire_ramp_and_part_time() -> None:
    """Hired 1 January 2024: 50% of 56 hours (10 employees) at half time."""
    credited = _credits(
        _facts(
            hired_on=date(2024, 1, 1),
            headcount=10,
            part_time_ratio=Decimal("0.5"),
        )
    )

    assert credited[LeaveBucket.ROL] == (Decimal(14), True)
    assert credited[LeaveBucket.EX_FESTIVITA] == (Decimal(16), True)


@pytest.mark.parametrize(("headcount", "hours"), [(15, Decimal(0)), (16, Decimal(72))])
def test_ramp_of_small_employers_only(headcount: int, hours: Decimal) -> None:
    """A ramp up to 15 employees: a 2026 hire of a larger employer accrues all."""
    ramp = _ROL.ramp.model_copy(update={"headcount_max": 15})  # type: ignore[union-attr]
    rules = _RULES.model_copy(
        update={"permits": (_ROL.model_copy(update={"ramp": ramp}),)}
    )
    facts = _facts(hired_on=date(2026, 1, 1), headcount=headcount)
    account = accrue_month(LeaveAccount(), rules, facts)

    rol = next(b for b in account.balances if b.bucket is LeaveBucket.ROL)
    assert (rol.accrued_twelfths, rol.exact) == (hours, True)


@pytest.mark.parametrize(
    ("hired", "months"),
    [(date(2024, 1, 31), 24), (date(2024, 3, 1), 23), (date(2024, 2, 28), 24)],
)
def test_months_since_hire_at_month_end(hired: date, months: int) -> None:
    """Whole months completed on 28 February 2026."""
    facts = _facts(hired_on=hired, month=2, service=MonthService(28, 28))

    assert facts.months_since_hire() == months


def test_months_since_hire_without_a_hire_date() -> None:
    """No hire date, no count."""
    assert _facts(hired_on=None).months_since_hire() is None


def test_month_service_within_the_employment_less_suspended_days() -> None:
    """Hired 10 March, two suspended days: 20 of 31 days served."""
    service = month_service(
        2026,
        3,
        EmploymentPeriod(date(2026, 3, 10), date(2026, 12, 31)),
        frozenset({date(2026, 3, 12), date(2026, 3, 13), date(2026, 2, 1)}),
        known=True,
    )

    assert (service.served, service.days, service.whole) == (20, 31, False)


def test_month_service_without_an_employment_counts_every_day() -> None:
    """An employment not stated serves the whole month."""
    service = month_service(2026, 2, None, frozenset(), known=False)

    assert (service.served, service.days, service.known) == (28, 28, False)


def test_ferie_without_accrual_rules_accrue_nothing() -> None:
    """A CCNL that states no ferie accrual credits only its permits."""
    rules = LeaveRules(default_annual_days=Decimal(26), permits=(_EX_FEST,))
    account = accrue_month(LeaveAccount(), rules, _facts())

    assert [b.bucket for b in account.balances] == [LeaveBucket.EX_FESTIVITA]
