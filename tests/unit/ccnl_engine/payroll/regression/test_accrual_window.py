"""Regression tests verifying extra-month rateo is based on accrued months.

These tests were initially marked xfail while the rateo was derived from the
payment calendar month.  The rateo now counts the qualifying months of the
12-month window ending in the payment month, from the employment dates.

Normative basis:
  INPS circ. 154/2014: tredicesima matura nell'anno solare in costanza di rapporto.
  CCNL lavoro domestico art. 38: rateo pari ai mesi di servizio nella finestra.
"""

from __future__ import annotations

from datetime import date

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import EmploymentPeriod
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest, PeriodState
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState

_CCNL_METALMECCANICO = "metalmeccanico-federmeccanica.json"
_LEVEL_C3 = "C3"
_CCNL_COMMERCIO = "commercio-confcommercio.json"
_LEVEL_4 = "4"
_YEAR = 2026


def _extra_month_req(
    ccnl: str,
    level: str,
    payment_month: int,
    run: PayrollRun,
    regular_periods_closed: int = 12,
    employment_period: EmploymentPeriod | None = None,
) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=_YEAR, month=payment_month),
        payment_date=date(_YEAR, payment_month, 28),
        ccnl_slug=ccnl,
        level_code=level,
        opening_state=PeriodState(
            ytd=TaxYearState(
                regular_periods_closed=regular_periods_closed,
                tax_withholding_periods_closed=regular_periods_closed,
            )
        ),
        run=run,
        employment_period=employment_period,
    )


def test_full_year_tredicesima_same_gross_june_vs_december() -> None:
    """Full-year tredicesima must have the same rateo in June and December.

    C3 metalmeccanico has a salary increase effective 2026-06-01, so June and
    December use the same table value.  With 12/12 rateo, both must produce the
    same gross.
    """
    gross_june = calculate_period(
        _extra_month_req(
            _CCNL_METALMECCANICO,
            _LEVEL_C3,
            payment_month=6,
            run=PayrollRun.thirteenth(_YEAR, 6),
        )
    ).period_gross
    gross_december = calculate_period(
        _extra_month_req(
            _CCNL_METALMECCANICO,
            _LEVEL_C3,
            payment_month=12,
            run=PayrollRun.thirteenth(_YEAR, 12),
        )
    ).period_gross
    assert gross_june == gross_december


def test_full_year_tredicesima_equals_monthly_gross() -> None:
    """Full-year tredicesima (12/12) must equal one regular monthly gross.

    With all 12 months accrued, the rateo is 1.0 and the tredicesima must
    equal the base salary for that payment month.
    """
    thirteenth_gross = calculate_period(
        _extra_month_req(
            _CCNL_METALMECCANICO,
            _LEVEL_C3,
            payment_month=6,
            run=PayrollRun.thirteenth(_YEAR, 6),
        )
    ).period_gross

    regular_gross = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=6),
            payment_date=date(_YEAR, 6, 28),
            ccnl_slug=_CCNL_METALMECCANICO,
            level_code=_LEVEL_C3,
            opening_state=PeriodState(
                ytd=TaxYearState(
                    regular_periods_closed=5,
                    tax_withholding_periods_closed=5,
                )
            ),
        )
    ).period_gross

    assert thirteenth_gross == regular_gross


def test_six_month_employee_same_rateo_june_vs_december() -> None:
    """A six-month employee must receive 6/12 regardless of payment month.

    Employed 1 January to 30 June 2026: the June window (July 2025 to June
    2026) and the December window (January to December 2026) each hold six
    employed months, so the rateo is 6/12 in both.
    """
    six_months = EmploymentPeriod(date(_YEAR, 1, 1), date(_YEAR, 6, 30))
    gross_june = calculate_period(
        _extra_month_req(
            _CCNL_METALMECCANICO,
            _LEVEL_C3,
            payment_month=6,
            run=PayrollRun.thirteenth(_YEAR, 6),
            regular_periods_closed=6,
            employment_period=six_months,
        )
    ).period_gross
    gross_december = calculate_period(
        _extra_month_req(
            _CCNL_METALMECCANICO,
            _LEVEL_C3,
            payment_month=12,
            run=PayrollRun.thirteenth(_YEAR, 12),
            regular_periods_closed=6,
            employment_period=six_months,
        )
    ).period_gross
    assert gross_june == gross_december


def test_commercio_level4_quattordicesima_full_year_at_june_rate() -> None:
    """Full-year Commercio L4 quattordicesima in June must equal the June regular gross.

    With 12 months accrued, rateo=12/12=1.0 and the June payment must equal
    the June monthly gross (not 891.88, which was the 6/12 buggy value).
    """
    quattordicesima_june = calculate_period(
        _extra_month_req(
            _CCNL_COMMERCIO,
            _LEVEL_4,
            payment_month=6,
            run=PayrollRun.fourteenth(_YEAR, 6),
        )
    ).period_gross

    regular_june = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=6),
            payment_date=date(_YEAR, 6, 28),
            ccnl_slug=_CCNL_COMMERCIO,
            level_code=_LEVEL_4,
            opening_state=PeriodState(
                ytd=TaxYearState(
                    regular_periods_closed=5,
                    tax_withholding_periods_closed=5,
                )
            ),
        )
    ).period_gross

    assert quattordicesima_june == regular_june
