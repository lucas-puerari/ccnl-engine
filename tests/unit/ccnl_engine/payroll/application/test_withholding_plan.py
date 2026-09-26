"""Unit tests for the withholding plan used by a period calculation."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.withholding._plan import (
    resolve_withholding_schedule,
    slot_share,
    upcoming_recurring_gross,
)
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest, PeriodState
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.domain.schedule import PayrollRunCount, WithholdingSchedule
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import EarningsYtd
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.service.types import MonthlyPayChain

_YEAR = 2026
_COOP_SOCIALI = "cooperative-sociali.json"
_HALF_FOURTEENTH = WithholdingSchedule.from_calendar(
    WorkCalendar.from_additional_months(_YEAR, Decimal("13.5"))
)


def _chain() -> MonthlyPayChain:
    return MonthlyPayChain(base=Decimal(1000), seniority=Decimal(0), allowances=())


class TestResolveWithholdingSchedule:
    """The period uses the requested schedule, else the CCNL standard one."""

    def test_requested_schedule_wins(self) -> None:
        """A schedule passed with the request is used unchanged."""
        ccnl = BundledKnowledgeRepository().load_ccnl(_COOP_SOCIALI)
        requested = WithholdingSchedule.from_calendar(WorkCalendar(year=_YEAR))
        resolved = resolve_withholding_schedule(
            requested, ccnl, date(_YEAR, 1, 1), _YEAR
        )
        assert resolved is requested

    def test_fractional_ccnl_default_has_one_slot_per_payslip(self) -> None:
        """Cooperative Sociali (13.5 months) defaults to 14 slots, not 13."""
        ccnl = BundledKnowledgeRepository().load_ccnl(_COOP_SOCIALI)
        resolved = resolve_withholding_schedule(None, ccnl, date(_YEAR, 1, 1), _YEAR)
        assert resolved == _HALF_FOURTEENTH
        assert resolved.run_count == PayrollRunCount(14)


class TestUpcomingRecurringGross:
    """Upcoming slots are valued at the pay their run kind carries."""

    def test_first_slot_projects_the_rest_of_the_year(self) -> None:
        """11 regular months, half a fourteenth and a full thirteenth."""
        gross = upcoming_recurring_gross(_chain(), _HALF_FOURTEENTH, 0)
        assert gross == Decimal(11 * 1000 + 500 + 1000)

    def test_last_slot_has_nothing_upcoming(self) -> None:
        """On the last slot the projection adds nothing."""
        assert upcoming_recurring_gross(_chain(), _HALF_FOURTEENTH, 13) == 0


def test_slot_share_divides_by_run_count() -> None:
    """An annual amount is split over the 14 payslips, not over 13.5."""
    assert slot_share(Decimal(1400), _HALF_FOURTEENTH) == Decimal(100)


def test_request_schedule_of_other_year_rejected() -> None:
    """A withholding schedule of another tax year is rejected."""
    with pytest.raises(ValueError, match=r"withholding_schedule\.year"):
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=1),
            payment_date=date(_YEAR, 1, 28),
            ccnl_slug=_COOP_SOCIALI,
            level_code="D2",
            withholding_schedule=WithholdingSchedule.from_calendar(
                WorkCalendar(year=_YEAR + 1)
            ),
        )


def test_standalone_december_is_not_the_last_slot_with_half_fourteenth() -> None:
    """Without a schedule, December regular still leaves the tredicesima slot.

    Thirteen slots closed out of fourteen would settle; twelve closed must
    split the balance over the December payslip and the tredicesima.
    """
    opening = PeriodState(
        ytd=TaxYearState(
            tax_year=_YEAR,
            regular_periods_closed=11,
            tax_withholding_periods_closed=12,
            earnings=EarningsYtd(taxable=Decimal("18043.97")),
        )
    )
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=12),
            payment_date=date(_YEAR, 12, 28),
            ccnl_slug=_COOP_SOCIALI,
            level_code="D2",
            opening_state=opening,
            run=PayrollRun.regular(_YEAR, 12),
        )
    )
    tax = result.tax_computation
    assert tax.withholding_due > 0
    assert tax.ordinary_tax == money(tax.withholding_due / 2)
