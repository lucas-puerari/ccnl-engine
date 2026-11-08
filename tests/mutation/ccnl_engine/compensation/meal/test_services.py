"""Daily contractual meal benefits on caller-verified eligible days."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WorkerCategory
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.period.results import PeriodResult
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


def _run(
    *,
    year: int,
    month: int,
    days: int | None,
    headcount: int = 11,
    level: str = "4",
    ccnl_id: str = "ced-assoced",
    run: PayrollRun | None = None,
) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=run or PayrollRun.regular(year=year, month=month),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level,
                category=(
                    WorkerCategory.QUADRO
                    if level in {"Q", "QDIR"}
                    else WorkerCategory.IMPIEGATO
                ),
                seniority=new_hire(year),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(year, month, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(headcount)),
            facts=PeriodFacts(
                meal_benefit_days=days, regione="IT-25", comune_belfiore="A005"
            ),
        )
    )


def test_daily_meal_benefit_2026() -> None:
    """October 2026: 20 eligible days * EUR 8 = EUR 160, versus EUR 0 undeclared."""
    before = _run(year=2026, month=10, days=None)
    after = _run(year=2026, month=10, days=20)
    welfare = [item for item in after.pay_items if item.kind == "welfare_item"]
    assert sum((item.amount for item in welfare), Decimal(0)) == Decimal("160.00")
    assert not [item for item in before.pay_items if item.kind == "welfare_item"]
    assert after.period_gross == before.period_gross


@pytest.mark.parametrize(("level", "fixed"), [("Q", "258.00"), ("QDIR", "296.00")])
def test_existing_fixed_allowance_and_daily_benefit(level: str, fixed: str) -> None:
    """October 2026: Q/QDIR fixed EUR 258/296 plus 10 days * EUR 8 = EUR 80."""
    result = _run(year=2026, month=10, days=10, level=level)
    assert sum(
        (i.amount for i in result.pay_items if "INDENNITA_FUNZIONE" in i.item_id),
        Decimal(0),
    ) == Decimal(fixed)
    assert sum(
        (i.amount for i in result.pay_items if i.kind == "welfare_item"),
        Decimal(0),
    ) == Decimal("80.00")


def test_daily_rate_change_is_dated() -> None:
    """The 2022 daily EUR 6 becomes EUR 8 on 1 September 2025."""
    ccnl = BundledKnowledgeRepository().load_ccnl("ced-assoced")
    rates = ccnl.parameters.meal_benefit_daily
    assert rates is not None
    assert rates.value_at(date(2025, 8, 31)) == Decimal("6.00")
    assert rates.value_at(date(2025, 9, 1)) == Decimal("8.00")


def test_meal_benefit_does_not_guess_eligible_days() -> None:
    """An unverified month and a declared zero-day month both pay EUR 0."""
    for days in (None, 0):
        result = _run(year=2026, month=1, days=days)
        assert not [i for i in result.pay_items if i.kind == "welfare_item"]


def test_days_must_fit_competence_month() -> None:
    """February 2026 cannot include 30 eligible EUR 8 voucher days."""
    with pytest.raises(InvalidInputError, match="meal_benefit_days"):
        _run(year=2026, month=2, days=30)


def test_extra_month_has_no_eligible_voucher_days() -> None:
    """An extra-month run cannot claim EUR 8 * 1 = EUR 8 of vouchers."""
    with pytest.raises(InvalidInputError, match="regular or termination"):
        _run(
            year=2026,
            month=12,
            days=1,
            run=PayrollRun.thirteenth(year=2026, payment_month=12),
        )


def test_no_contract_rate_does_not_guess_a_voucher_value() -> None:
    """A contract without a daily rate cannot guess EUR 8 for one day."""
    with pytest.raises(InvalidInputError, match="no contractual daily"):
        _run(year=2026, month=1, days=1, ccnl_id="commercio-confcommercio")


def test_headcount_is_a_strict_threshold() -> None:
    """Ten employees cannot qualify for EUR 8 * 1 = EUR 8 of meal benefits."""
    with pytest.raises(InvalidInputError, match="more than 10"):
        _run(year=2026, month=10, days=1, headcount=10)


@pytest.mark.parametrize("days", [-1, 32, True, 2.5])
def test_invalid_eligible_days_are_rejected(days: object) -> None:
    """Only integral eligible counts from 0 through 31 can generate benefits."""
    with pytest.raises(InvalidInputError):
        PeriodFacts(meal_benefit_days=days)  # type: ignore[arg-type]
