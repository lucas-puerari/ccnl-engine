"""Tredicesima gross is prorated by accrued months, not by payment month."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from tests.helpers import EMPLOYER_50

_CCNL = "metalmeccanico-federmeccanica.json"

_LEVEL = "C3"


class TestExtraMonthRateo:
    """Tredicesima gross is prorated by accrued months, not by payment month."""

    def _run_extra_month(
        self,
        regular_periods_closed: int,
        run: PayrollRun,
        period_month: int,
        employment_period: EmploymentPeriod | None = None,
    ) -> Decimal:
        """Run an extra-month period calculation and return period_gross.

        Returns:
            The ``period_gross`` of the extra-month run.
        """
        req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=period_month),
            payment_date=date(2026, period_month, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState(
                ytd=TaxYearState(
                    regular_periods_closed=regular_periods_closed,
                    tax_withholding_periods_closed=regular_periods_closed,
                )
            ),
            run=run,
            employment_period=employment_period,
        )
        return calculate_period(req).period_gross

    def test_december_tredicesima_is_positive(self) -> None:
        """Tredicesima paid in December produces a positive gross."""
        gross = self._run_extra_month(
            regular_periods_closed=12,
            run=PayrollRun.thirteenth(2026, 12),
            period_month=12,
        )
        assert gross > Decimal(0)

    def test_accrued_months_determine_rateo(self) -> None:
        """Six accrued months give half the gross of twelve.

        The rateo derives from the employment dates (hire 1 July: July to
        December), not from the payment month or the runs already closed:
        both runs report twelve closed periods.  Both use the same December
        salary, so the rateo is the only factor.
        """
        full_year = self._run_extra_month(
            regular_periods_closed=12,
            run=PayrollRun.thirteenth(2026, 12),
            period_month=12,
        )
        half_year = self._run_extra_month(
            regular_periods_closed=12,
            run=PayrollRun.thirteenth(2026, 12),
            period_month=12,
            employment_period=EmploymentPeriod(date(2026, 7, 1)),
        )
        assert half_year == (full_year / 2).quantize(Decimal("0.01"))

    def test_payment_month_does_not_change_accrued_gross(self) -> None:
        """A full-year employee receives the same tredicesima in June and December.

        Moving the payment date must not change the already-accrued entitlement.
        Without employment dates the worker accrues the 12 months ending in
        the payment month, so rateo=12/12=1.0 in both.
        The salary rate at the payment date may differ if there was an increase
        between June and December; the invariant is the accrual fraction, not
        the absolute amount.
        """
        jun_thirteenth = self._run_extra_month(
            regular_periods_closed=12,
            run=PayrollRun.thirteenth(2026, 6),
            period_month=6,
        )
        dec_thirteenth = self._run_extra_month(
            regular_periods_closed=12,
            run=PayrollRun.thirteenth(2026, 12),
            period_month=12,
        )
        # Both use 12/12 rateo; amounts may differ only due to salary increases.
        # Verify by checking that each equals its own month's regular gross.
        regular_june = calculate_period(
            PeriodCalculationRequest(
                employer=EMPLOYER_50,
                period_id=PeriodId(year=2026, month=6),
                payment_date=date(2026, 6, 28),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
                opening_state=PeriodState(
                    ytd=TaxYearState(
                        regular_periods_closed=5,
                        tax_withholding_periods_closed=5,
                    )
                ),
            )
        ).period_gross
        regular_dec = calculate_period(
            PeriodCalculationRequest(
                employer=EMPLOYER_50,
                period_id=PeriodId(year=2026, month=12),
                payment_date=date(2026, 12, 28),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
                opening_state=PeriodState(
                    ytd=TaxYearState(
                        regular_periods_closed=11,
                        tax_withholding_periods_closed=11,
                    )
                ),
            )
        ).period_gross
        assert jun_thirteenth == regular_june
        assert dec_thirteenth == regular_dec
