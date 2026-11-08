"""Confetra maternity targets include, rather than add to, INPS pay."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.rules import MonthPay, maternity_pay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.sickness.term.rules import DailyQuota


def test_confetra_month_crosses_day_150() -> None:
    """June: 13 x (100 - 80) = 260; 17 x (50 - 80) floors at 0, not 850."""
    agreement = load_ccnl("logistica-trasporto-confetra")
    assert agreement.work_rules is not None
    assert agreement.work_rules.insured_absence is not None
    rules = agreement.work_rules.insured_absence.maternity
    assert rules is not None
    assert rules.integration_days == 150
    assert rules.next_integration_days == 30
    assert rules.next_integration_rate == Decimal("0.5")
    pay = MonthPay(
        MonthlyPayChain(Decimal(3000), Decimal(0), ()),
        DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
        0,
        Decimal(0),
    )
    args = (
        date(2026, 6, 1),
        date(2026, 6, 30),
        date(2026, 1, 15),
        pay,
        load_insured_absence_rates().maternity,
    )
    result = maternity_pay(*args, rules, Decimal(100))
    old_rules = rules.model_copy(update={"next_integration_rate": None})
    old = maternity_pay(*args, old_rules, Decimal(100))
    assert result.deduction == Decimal(3000)
    assert result.indemnity == Decimal(2400)
    assert old.integration == Decimal(260)
    assert result.integration == Decimal(260)

    # A smaller previous-month INPS base makes the second-period top-up payable.
    # 80% of 40 = 32 per day; first 13 x 68 = 884; next 17 x 18 = 306.
    old = maternity_pay(*args, old_rules, Decimal(40))
    result = maternity_pay(*args, rules, Decimal(40))
    assert result.indemnity == Decimal(960)
    assert old.integration == Decimal(884)
    assert result.integration == Decimal(1190)
    # The second period ends on leave day 180; later days have no top-up.
    later = maternity_pay(
        date(2026, 7, 20), date(2026, 7, 31), args[2], pay, args[4], rules, Decimal(40)
    )
    assert later.integration == Decimal(0)


def test_following_period_requires_complete_first_period() -> None:
    """Reject orphaned rates or durations rather than silently skipping a band."""
    agreement = load_ccnl("logistica-trasporto-confetra")
    assert agreement.work_rules is not None
    assert agreement.work_rules.insured_absence is not None
    rules = agreement.work_rules.insured_absence.maternity
    assert rules is not None
    with pytest.raises(ValidationError):
        type(rules).model_validate(rules.model_dump(exclude={"next_integration_days"}))
    with pytest.raises(ValidationError):
        type(rules).model_validate(rules.model_dump(exclude={"integration_days"}))


def test_parental_sixth_month_requires_a_following_period() -> None:
    """A parental target without a sixth-month rate must not pass validation."""
    agreement = load_ccnl("logistica-trasporto-confetra")
    assert agreement.work_rules is not None
    assert agreement.work_rules.insured_absence is not None
    rules = agreement.work_rules.insured_absence.maternity
    assert rules is not None
    data = rules.model_dump()
    data["next_integration_rate"] = None
    data["next_integration_days"] = None
    with pytest.raises(ValidationError, match="parental sixth month"):
        type(rules).model_validate(data)
