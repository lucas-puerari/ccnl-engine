"""Extra-month ratei in the year: run rateo, settlement at termination, absences."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import (
    YearResult,
    calculate_year,
)
from ccnl_engine.payroll.application.year._extra_month_accrual import (
    non_accruing_days,
    termination_settlements,
)
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.events import AbsenceEvent, OvertimeEvent
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
from ccnl_engine.payroll.service.irpef_deductions import work_income_deduction
from ccnl_engine.payroll.service.tax_computation import compute_tax
from tests.helpers import make_year_rules, year_input

_COMMERCIO = "commercio-confcommercio.json"
_METALMECCANICO = "metalmeccanico-federmeccanica.json"
_YEAR = 2026


def _commercio_year(employment: EmploymentPeriod) -> YearResult:
    return calculate_year(
        year_input(_YEAR, _COMMERCIO, "4", employment_period=employment)
    )


def _extra_items(result: YearResult) -> dict[str, Decimal]:
    return {
        item.item_id: item.amount
        for r in result.period_results
        for item in r.pay_items
        if item.kind == "extra_month_earning"
    }


class TestTerminationSettlement:
    """Ratei of extra months not yet paid are liquidated on the last run."""

    def test_both_extra_months_settle_on_the_termination_run(self) -> None:
        """July to September: 3/12 of each, 445.95 on a 1,783.75 monthly pay."""
        result = _commercio_year(
            EmploymentPeriod(date(_YEAR, 7, 1), date(_YEAR, 9, 30))
        )
        september = result.period_results[-1]
        assert _extra_items(result) == {
            "extra_month_thirteenth_2026-09-regular": Decimal("445.95"),
            "extra_month_fourteenth_2026-09-regular": Decimal("445.95"),
        }
        policies = {
            e.policy_decision_id
            for e in september.ledger_entries
            if e.pay_item_kind == "extra_month_earning"
        }
        assert policies == {"it/earning/extra_month"}
        assert september.period_gross == Decimal("2675.65")
        assert september.closing_state.ytd.earnings.inps_base == Decimal("6243.15")

    def test_extra_run_in_the_termination_month_is_not_settled_again(self) -> None:
        """Ended 10 June: the June quattordicesima run pays; May closes 13th.

        June has 10 employed days, so it does not qualify: the
        quattordicesima accrues July 2025 to May 2026 (11/12) and the
        tredicesima January to May (5/12), both on the June runs.
        """
        employment = EmploymentPeriod(date(2020, 1, 1), date(_YEAR, 6, 10))
        result = _commercio_year(employment)
        kinds = [r.run.run_kind for r in result.period_results if r.run]
        assert kinds[-2:] == [RunKind.REGULAR, RunKind.FOURTEENTH]
        assert list(_extra_items(result)) == ["extra_month_thirteenth_2026-06-regular"]

    def test_short_employment_below_the_threshold_settles_nothing(self) -> None:
        """Employed 20 to 30 September: 11 days, no qualifying month."""
        result = _commercio_year(
            EmploymentPeriod(date(_YEAR, 9, 20), date(_YEAR, 9, 30))
        )
        assert _extra_items(result) == {}
        assert result.annual_gross == Decimal("1783.75")

    def test_thirteen_month_contract_settles_only_the_tredicesima(self) -> None:
        """Metalmeccanico ended 31 May: the May run pays 5/12 of the 13th."""
        result = calculate_year(
            year_input(
                _YEAR,
                _METALMECCANICO,
                "C3",
                employment_period=EmploymentPeriod(
                    date(2020, 1, 1), date(_YEAR, 5, 31)
                ),
            )
        )
        assert list(_extra_items(result)) == ["extra_month_thirteenth_2026-05-regular"]

    def test_employment_ending_in_a_later_year_settles_nothing(self) -> None:
        """An end in 2027 is not a termination of the 2026 payroll."""
        calendar = WorkCalendar.from_additional_months(_YEAR, 14)
        employment = EmploymentPeriod(date(2020, 1, 1), date(2027, 3, 31))
        assert termination_settlements(calendar, employment, frozenset()) == {}
        assert termination_settlements(calendar, None, frozenset()) == {}


class TestSuspendingAbsences:
    """Only absences flagged as suspending accrual reduce the ratei."""

    def test_aspettativa_removes_a_month_from_the_tredicesima(self) -> None:
        """Twenty days of aspettativa in April leave ten: April drops out."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 4, 1),
            hours=Decimal(120),
            hourly_rate=Decimal(10),
            end_date=date(_YEAR, 4, 20),
            suspends_accrual=True,
        )
        full = calculate_year(year_input(_YEAR, _METALMECCANICO, "C3"))
        reduced = calculate_year(
            year_input(_YEAR, _METALMECCANICO, "C3", events={4: (absence,)})
        )
        assert reduced.period_results[-1].period_gross < (
            full.period_results[-1].period_gross
        )

    def test_only_flagged_absence_days_are_collected(self) -> None:
        """Flagged absences count whatever run they belong to; others do not."""
        flagged = AbsenceEvent(
            event_date=date(_YEAR, 4, 1),
            hours=Decimal(8),
            hourly_rate=Decimal(10),
            suspends_accrual=True,
        )
        unflagged = AbsenceEvent(
            event_date=date(_YEAR, 5, 1), hours=Decimal(8), hourly_rate=Decimal(10)
        )
        overtime = OvertimeEvent(
            event_date=date(_YEAR, 5, 2), hours=Decimal(1), hourly_rate=Decimal(10)
        )
        days = non_accruing_days((unflagged, overtime, flagged))
        assert days == frozenset({date(_YEAR, 4, 1)})


class TestStandaloneExtraRun:
    """A period request without an accrual counts it from the employment."""

    @staticmethod
    def _gross(
        ccnl: str, level: str, run: PayrollRun, employment: EmploymentPeriod | None
    ) -> Decimal:
        calendar = WorkCalendar.from_additional_months(_YEAR, 14)
        request = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=run.month),
            payment_date=date(_YEAR, run.month, 28),
            ccnl_slug=ccnl,
            level_code=level,
            run=run,
            employment_period=employment,
            withholding_schedule=WithholdingSchedule.from_calendar(calendar),
        )
        return calculate_period(request).period_gross

    def test_half_quattordicesima_takes_the_ccnl_fraction(self) -> None:
        """Cooperative Sociali grants 13.5 months: the 14th is half a month."""
        run = PayrollRun.fourteenth(_YEAR, 6)
        full = self._gross(
            "cooperative-sociali.json", "D2", PayrollRun.regular(_YEAR, 6), None
        )
        half = self._gross("cooperative-sociali.json", "D2", run, None)
        assert half == pytest.approx(full / 2, abs=Decimal("0.02"))

    def test_extra_month_absent_from_the_ccnl_counts_as_full(self) -> None:
        """A 13-month CCNL has no quattordicesima fraction: a full month."""
        run = PayrollRun.fourteenth(_YEAR, 6)
        hired = EmploymentPeriod(date(_YEAR, 1, 1))
        six = self._gross(_METALMECCANICO, "C3", run, hired)
        twelve = self._gross(_METALMECCANICO, "C3", run, None)
        assert six == pytest.approx(twelve / 2, abs=Decimal("0.02"))


def test_employment_days_reach_the_work_deduction() -> None:
    """Employed 1 July to 30 September: 92 days reach the art. 13 deduction."""
    result = _commercio_year(EmploymentPeriod(date(_YEAR, 7, 1), date(_YEAR, 9, 30)))
    last = result.period_results[-1]
    components = {c.name: c.amount for c in last.tax_computation.components}
    taxable = last.closing_state.ytd.earnings.taxable
    assert components["work_deduction"] == work_income_deduction(taxable, 92)
    assert components["work_deduction"] < work_income_deduction(taxable)


def test_employment_days_are_capped_at_365() -> None:
    """A leap year fully employed has 366 days; the deduction uses 365."""
    rules = make_year_rules()
    schedule = WithholdingSchedule.from_calendar(WorkCalendar(year=_YEAR))
    capped = compute_tax(
        Decimal(20_000), rules, withholding_schedule=schedule, eligible_work_days=366
    ).computation
    full = compute_tax(
        Decimal(20_000), rules, withholding_schedule=schedule
    ).computation
    assert capped == full
