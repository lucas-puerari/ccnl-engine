"""Unit tests for calculate_competence_year() and WorkCalendar."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.application.calculate_competence_year import (
    calculate_competence_year,
)
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.year import _sequence as sequence_module
from ccnl_engine.payroll.domain.assurance import BlockerCode
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.calendar_override import (
    CalendarOverride,
    CalendarOverrideReason,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.employment import Permanent
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.events import AbsenceEvent
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.shared.domain.errors import InvalidInputError
from tests.fixtures.current_year import employment_only
from tests.fixtures.opening_state import fresh_tax_year
from tests.fixtures.residence import resident
from tests.helpers import year_plan

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026


class TestYearResult:
    """CompetenceYearResult stores period results and aggregated totals."""

    def test_frozen(self) -> None:
        """CompetenceYearResult is immutable."""
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        with pytest.raises(AttributeError):
            result.year = 2025  # type: ignore[misc]

    def test_year_stored(self) -> None:
        """Year matches the requested year."""
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        assert result.year == _YEAR

    def test_calendar_year_mismatch_raises(self) -> None:
        """An override for another year raises InvalidInputError."""
        override = CalendarOverride(
            calendar=WorkCalendar.from_additional_months(2025, 13),
            reason=CalendarOverrideReason.PAYMENT_MONTH,
            note="wrong year",
        )
        with pytest.raises(InvalidInputError, match="year 2025"):
            calculate_competence_year(
                year_plan(_YEAR, _CCNL, _LEVEL, calendar_override=override)
            )


class TestCalculateYear:
    """calculate_competence_year() chains calculate_period across every run."""

    def test_produces_13_period_results(self) -> None:
        """Metalmeccanico grants a tredicesima: 12 regular runs plus one."""
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        assert len(result.period_results) == 13

    def test_annual_gross_equals_sum_of_periods(self) -> None:
        """annual_gross is the exact sum of all period_gross values."""
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        expected = sum((r.period_gross for r in result.period_results), Decimal(0))
        assert result.annual_gross == expected

    def test_annual_net_equals_sum_of_periods(self) -> None:
        """annual_net is the exact sum of all period_net values."""
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        expected = sum((r.period_net for r in result.period_results), Decimal(0))
        assert result.annual_net == expected

    def test_annual_employer_cost_equals_sum_of_periods(self) -> None:
        """annual_employer_cost is the exact sum of all period_employer_cost values."""
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        expected = sum(
            (r.period_employer_cost for r in result.period_results), Decimal(0)
        )
        assert result.annual_employer_cost == expected

    def test_state_threaded_across_periods(self) -> None:
        """Closing state of period N is the opening state of period N+1."""
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        for i in range(1, 12):
            prev = result.period_results[i - 1]
            curr = result.period_results[i]
            assert curr.closing_state.accrual.regular_months(_YEAR) == (
                prev.closing_state.accrual.regular_months(_YEAR) + 1
            )

    def test_regular_months_reach_12(self) -> None:
        """After the year twelve regular months are closed, extra runs aside."""
        closing = calculate_competence_year(
            year_plan(_YEAR, _CCNL, _LEVEL)
        ).closing_state
        assert closing.accrual.regular_months(_YEAR) == 12

    def test_period_ids_are_in_order(self) -> None:
        """Regular period results are ordered January to December."""
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        regular = [
            r
            for r in result.period_results
            if r.run is not None and r.run.run_kind == "regular"
        ]
        for i, pr in enumerate(regular, start=1):
            assert pr.period_id.month == i
            assert pr.period_id.year == _YEAR

    def test_explicit_contract_type(self) -> None:
        """An explicitly supplied contract_type is used instead of the default."""
        result = calculate_competence_year(
            year_plan(_YEAR, _CCNL, _LEVEL, contract_type=Permanent())
        )
        assert len(result.period_results) == 13

    def test_month_keyed_events_injected(self) -> None:
        """Events keyed by month are applied to the correct period."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 3, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        result = calculate_competence_year(
            year_plan(_YEAR, _CCNL, _LEVEL, events={3: (absence,)})
        )
        # March net must be lower than January net (absence in EMPLOYEE_DEDUCTIONS)
        jan_net = result.period_results[0].period_net
        mar_net = result.period_results[2].period_net
        assert mar_net < jan_net

    def test_all_period_gross_values_positive(self) -> None:
        """With no events every period_gross value is positive."""
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        for r in result.period_results:
            assert r.period_gross > Decimal(0)

    def test_gross_ytd_accumulates_correctly(self) -> None:
        """gross_ytd in the last closing state equals annual_gross."""
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        dec_state = result.period_results[-1].closing_state
        assert dec_state.cash.earnings.gross == result.annual_gross

    def test_calendar_none_auto_derives_from_ccnl(self) -> None:
        """Without an override the CCNL additional_months sets the calendar.

        metalmeccanico-federmeccanica has additional_months=13: one
        tredicesima paid in December.
        """
        result = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        assert result.calendar == WorkCalendar.from_additional_months(_YEAR, 13)
        assert result.calendar_override is None


class TestEmploymentPeriodRuns:
    """The employment period selects the runs of the year."""

    def test_mid_month_hire_starts_in_the_hire_month(self) -> None:
        """Hired 15 March, open-ended: March to December plus the tredicesima."""
        result = calculate_competence_year(
            year_plan(
                _YEAR,
                _CCNL,
                _LEVEL,
                employment_period=EmploymentPeriod(date(_YEAR, 3, 15)),
            )
        )
        runs = [
            (r.period_id.month, r.run.run_kind) for r in result.period_results if r.run
        ]
        assert runs == [(m, RunKind.REGULAR) for m in range(3, 13)] + [
            (12, RunKind.THIRTEENTH)
        ]

    def test_partial_month_is_prorated_and_whole_months_are_not(self) -> None:
        """Hired 15 March: March pays 14/26 of 2,158.26, April the month.

        By hand: 1 March 2026 is a Sunday; 16-21, 23-28, 30 and 31 March
        are the 14 Mondays to Saturdays employed (15 March is a Sunday), so
        March pays 2,158.26 x 14 / 26 = 1,162.14.
        """
        result = calculate_competence_year(
            year_plan(
                _YEAR,
                _CCNL,
                _LEVEL,
                facts=resident(),
                employment_period=EmploymentPeriod(date(_YEAR, 3, 15)),
                current_year=employment_only(_YEAR),
            )
        )
        march, april = result.period_results[0], result.period_results[1]
        assert march.period_gross == Decimal("1162.14")
        assert april.period_gross == Decimal("2158.26")
        assert [i.code for i in march.issues] == []
        assert march.assurance.calculation is CalculationStatus.FINAL

    def test_year_assurance_combines_the_runs(self) -> None:
        """A CCNL without a partial-month rule blocks March and the year once.

        The vetro CCNL records no daily divisor: the hire month is not paid
        as a full month, its blocker reaches the year exactly once.
        """
        result = calculate_competence_year(
            year_plan(
                _YEAR,
                "vetro-meccanizzato-assovetro.json",
                "C",
                employment_period=EmploymentPeriod(date(_YEAR, 3, 15)),
            )
        )
        march = result.period_results[0]
        partial = (BlockerCode.CALCULATION_ISSUE, None, "partial_month_rule_missing")
        keys = [(b.code, b.feature, b.detail) for b in result.blockers]

        assert march.period_gross == Decimal("0.00")
        assert partial in {(b.code, b.feature, b.detail) for b in march.blockers}
        assert keys.count(partial) == 1
        assert len(keys) == len(set(keys))
        assert not result.is_payable
        assert result.rulesets == march.rulesets

    def test_termination_in_may_has_no_december_tredicesima(self) -> None:
        """Ended 31 May: five regular runs, no extra-month run.

        The income of five months is within the 20,000 EUR limit of the
        somma esente, whose reddito complessivo (L. 207/2024 art. 1 c. 4)
        includes the income beyond this employment the plan does not state:
        the result is incomplete for that alone.
        """
        result = calculate_competence_year(
            year_plan(
                _YEAR,
                _CCNL,
                _LEVEL,
                facts=resident(),
                employment_period=EmploymentPeriod(
                    date(2020, 1, 1), date(_YEAR, 5, 31)
                ),
                opening_state=fresh_tax_year(_YEAR),
            )
        )
        assert [r.run.run_kind for r in result.period_results if r.run] == [
            RunKind.REGULAR
        ] * 5
        assert result.assurance.calculation is CalculationStatus.INCOMPLETE
        assert {i.code for r in result.period_results for i in r.issues} == {
            "somma_esente_income_unknown"
        }

    def test_employment_outside_the_year_is_rejected(self) -> None:
        """An employment ended in 2025 has nothing to compute in 2026."""
        with pytest.raises(InvalidInputError, match="no day in 2026"):
            calculate_competence_year(
                year_plan(
                    _YEAR,
                    _CCNL,
                    _LEVEL,
                    employment_period=EmploymentPeriod(
                        date(2025, 1, 1), date(2025, 12, 31)
                    ),
                )
            )

    def test_requests_carry_selected_slots_and_clipped_window(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Slots match the selected runs; the windows start at hire.

        Hired 10 March: March has 22 employed days, so it qualifies.  The
        quattordicesima accrues March to June (4/12), the tredicesima March
        to December (10/12).
        """
        requests: list[PeriodCalculationRequest] = []

        def _spy(req: PeriodCalculationRequest, **kwargs: object) -> PeriodResult:
            requests.append(req)
            return calculate_period(req, **kwargs)  # type: ignore[arg-type]

        monkeypatch.setattr(sequence_module, "calculate_period", _spy)
        calculate_competence_year(
            year_plan(
                _YEAR,
                "commercio-confcommercio.json",
                "4",
                employment_period=EmploymentPeriod(date(_YEAR, 3, 10)),
            )
        )
        schedule = requests[0].withholding_schedule
        assert schedule is not None
        assert tuple(s.run for s in schedule.slots) == tuple(
            r.run for r in requests if r.run is not None
        )
        accruals = {
            r.run.run_kind: r.extra_month_accrual
            for r in requests
            if r.run is not None and r.extra_month_accrual is not None
        }
        fourteenth = accruals[RunKind.FOURTEENTH]
        thirteenth = accruals[RunKind.THIRTEENTH]
        assert fourteenth.window.start == date(_YEAR, 3, 10)
        assert fourteenth.window.nominal_start == date(_YEAR - 1, 7, 1)
        assert fourteenth.months == 4
        assert thirteenth.window.start == date(_YEAR, 3, 10)
        assert thirteenth.months == 10
        assert requests[0].extra_month_accrual is None
        assert all(not r.extra_month_settlements for r in requests)


class TestCalendarOverride:
    """An override replaces the standard calendar only when it is valid."""

    def test_payment_month_override_keeps_the_annual_gross(self) -> None:
        """Commercio quattordicesima paid in July: same gross, later run."""
        commercio = "commercio-confcommercio.json"
        override = CalendarOverride(
            calendar=WorkCalendar.from_additional_months(
                _YEAR, 14, fourteenth_payment_month=7
            ),
            reason=CalendarOverrideReason.PAYMENT_MONTH,
            note="quattordicesima paid with the July salary",
        )
        standard = calculate_competence_year(year_plan(_YEAR, commercio, "4"))
        moved = calculate_competence_year(
            year_plan(_YEAR, commercio, "4", calendar_override=override)
        )
        run_ids = [r.run.run_id for r in moved.period_results if r.run is not None]
        assert run_ids[7] == f"{_YEAR}-07-fourteenth"
        assert moved.annual_gross == standard.annual_gross
        assert moved.calendar is override.calendar
        assert moved.calendar_override is override

    def test_withholding_schedule_follows_the_override(self) -> None:
        """Every run carries a slot of the same schedule built from the override."""
        override = CalendarOverride(
            calendar=WorkCalendar.from_additional_months(_YEAR, 14),
            reason=CalendarOverrideReason.MORE_FAVOURABLE_TREATMENT,
            note="company agreement grants a quattordicesima",
        )
        result = calculate_competence_year(
            year_plan(_YEAR, _CCNL, _LEVEL, calendar_override=override)
        )
        assert len(result.period_results) == 14
        last = result.period_results[-1].closing_state
        assert last.cash.withholding_payments_closed == 14

    def test_override_that_drops_the_ccnl_extra_month_is_rejected(self) -> None:
        """No reason lets an override remove the tredicesima the CCNL grants."""
        override = CalendarOverride(
            calendar=WorkCalendar(year=_YEAR),
            reason=CalendarOverrideReason.PAYMENT_MONTH,
            note="no tredicesima",
        )
        with pytest.raises(InvalidInputError, match="thirteenth"):
            calculate_competence_year(
                year_plan(_YEAR, _CCNL, _LEVEL, calendar_override=override)
            )
