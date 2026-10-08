"""The INPS base of other employments a request states in its opening state."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.current_year import (
    CurrentYearTaxFacts,
    IncomeEstimateQuality,
)
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState

_IMPORTED = PeriodState(
    accrual=EmploymentAccrualState(
        inps_bases=(InpsBaseYtd(2026, Decimal(9000), Decimal(4000)),)
    )
)


def _facts(tax_year: int, inps_base: str) -> CurrentYearTaxFacts:
    return CurrentYearTaxFacts(
        tax_year=tax_year,
        other_employment_income=Decimal(5000),
        other_employment_inps_base=Decimal(inps_base),
        other_income=Decimal(0),
        main_dwelling_income=Decimal(0),
        exempt_regime_income=Decimal(0),
        estimated_on=date(tax_year, 3, 1),
        quality=IncomeEstimateQuality.CERTIFIED,
    )


def _request(
    current_year: CurrentYearTaxFacts | None, payment_date: date = date(2026, 6, 27)
) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        period_id=PeriodId(year=2026, month=6),
        payment_date=payment_date,
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employer=EmployerProfile(headcount=Headcount(50)),
        opening_state=_IMPORTED,
        current_year=current_year,
    )


def test_the_declaration_of_the_competence_year_replaces_the_carried_base() -> None:
    """The latest declaration of the year wins; this employment's base stays."""
    request = _request(_facts(2026, "6500.00"))

    assert request.opening_state.accrual.inps_base(2026) == InpsBaseYtd(
        2026, Decimal(9000), Decimal("6500.00")
    )


def test_a_declaration_of_another_year_leaves_the_state() -> None:
    """Facts of 2027 do not state the base of the 2026 competence year."""
    request = _request(_facts(2027, "6500.00"), payment_date=date(2027, 1, 12))

    assert request.opening_state is _IMPORTED


def test_no_declaration_leaves_the_state() -> None:
    """Without current-year facts the base carried in the state counts."""
    assert _request(None).opening_state is _IMPORTED
