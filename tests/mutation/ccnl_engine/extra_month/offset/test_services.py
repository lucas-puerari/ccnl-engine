"""Art. 143: only pre-existing remuneration months offset the fourteenth."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.extra_month.offset.services import offset_fourteenth
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.models import PayrollRun
from ccnl_engine.run.types import PeriodId


def _july(
    amount: Decimal | None,
    *,
    hired: date | None = date(2020, 1, 1),
) -> PeriodResult:
    request = PeriodCalculationRequest(
        period_id=PeriodId(year=2026, month=7),
        payment_date=date(2026, 7, 28),
        ccnl_id="studi-professionali-confprofessioni",
        level_code="4",
        employer=EmployerProfile(provincial_pay_element=False, headcount=Headcount(10)),
        run=PayrollRun.fourteenth(2026, 7),
        employment_period=None if hired is None else EmploymentPeriod(hired),
        prior_extra_month_amount=amount,
    )
    return calculate_period(
        request, repo=bundled_repository(), resolver=bundled_policies()
    )


def test_july_fourteenth_offset_and_no_prior_amount() -> None:
    """Level 4 July: 1,595.42 minus 400 = 1,195.42; zero = 1,595.42."""
    assert _july(Decimal(0)).period_gross == Decimal("1595.42")
    reduced = _july(Decimal(400))
    assert reduced.period_gross == Decimal("1195.42")
    assert not any(i.code == "prior_extra_month_unknown" for i in reduced.issues)
    assert _july(Decimal(2000)).period_gross == Decimal(0)


def test_historical_amount_unknown_blocks_only_if_clause_can_bite() -> None:
    """Missing historical fact blocks old hires, not 2025 hires: full 1,595.42."""
    old = _july(None)
    assert old.period_gross == Decimal("1595.42")
    assert any(i.fact == "prior_extra_month_amount" for i in old.issues)
    recent = _july(None, hired=date(2025, 1, 1))
    assert recent.period_gross == Decimal("1595.42")
    assert not any(i.fact == "prior_extra_month_amount" for i in recent.issues)
    assert _july(Decimal(400), hired=date(2025, 1, 1)).period_gross == Decimal(
        "1595.42"
    )


def test_termination_settles_only_the_fourteenth_difference() -> None:
    """March termination: 9/12 x 1,595.42 = 1,196.57, less 300 = 896.57."""
    request = PeriodCalculationRequest(
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 28),
        ccnl_id="studi-professionali-confprofessioni",
        level_code="4",
        employer=EmployerProfile(provincial_pay_element=False, headcount=Headcount(10)),
        run=PayrollRun.regular(2026, 3),
        employment_period=EmploymentPeriod(date(2020, 1, 1), date(2026, 3, 31)),
        prior_extra_month_amount=Decimal(400),
    )
    result = calculate_period(
        request, repo=bundled_repository(), resolver=bundled_policies()
    )
    extra = {
        item.month_number: item.amount
        for item in result.pay_items
        if item.kind == "extra_month_earning"
    }
    assert extra == {13: Decimal("398.86"), 14: Decimal("896.57")}


def test_partial_rateo_offsets_only_its_accrued_share() -> None:
    """Three twelfths of 1,595.42 = 398.86; less 3/12 of 400 = 298.86."""
    rule = (
        bundled_repository()
        .load_ccnl("studi-professionali-confprofessioni")
        .parameters.fourteenth_prior_extra_offset
    )
    chain = MonthlyPayChain(base=Decimal("398.86"), seniority=Decimal(0), allowances=())
    result = offset_fourteenth(
        chain,
        rule,
        EmploymentPeriod(date(2020, 1, 1)),
        Decimal(400),
        Decimal("0.25"),
    )
    assert result.base == Decimal("298.86")


def test_offset_can_reach_seniority_and_allowances() -> None:
    """Credit 210 against base 100 + seniority 50 + allowance 80 leaves 20."""
    contract = bundled_repository().load_ccnl("studi-professionali-confprofessioni")
    allowance = contract.level_by_code("1").fixed_allowances[0]
    chain = MonthlyPayChain(
        base=Decimal(100),
        seniority=Decimal(50),
        allowances=((allowance, Decimal(80)),),
    )
    result = offset_fourteenth(
        chain,
        contract.parameters.fourteenth_prior_extra_offset,
        EmploymentPeriod(date(2020, 1, 1)),
        Decimal(210),
        Decimal(1),
    )
    assert (result.base, result.seniority, result.allowances[0][1]) == (
        Decimal(0),
        Decimal(0),
        Decimal(20),
    )


def test_negative_historical_amount_is_rejected() -> None:
    """Negative credit is invalid rather than raising the July amount."""
    with pytest.raises(InvalidInputError):
        _july(Decimal(-1))
