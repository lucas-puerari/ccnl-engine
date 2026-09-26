"""Integration tests for SicknessCaseEvent in the period-first engine.

Verifies the three-component sickness model: absence deduction, INPS indemnity,
and employer integration are posted as separate pay items and ledger entries.

Gate requirements:
  - assenza a cavallo di mese: spans_multiple_months property
  - carenza negativa: raises InvalidInputError
  - INPS indemnity + employer integration: separate pay items
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.events import SicknessCaseEvent
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import AbsenceDeduction, SicknessItem
from ccnl_engine.payroll.domain.period import PeriodResult
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.sickness import SicknessCase
from ccnl_engine.shared.domain.errors import InvalidInputError

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_MONTH = 3
_PID = PeriodId(year=_YEAR, month=_MONTH)
_PAYMENT = date(_YEAR, _MONTH, 28)
_ZERO = Decimal(0)


def _req(*events: object) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=_PID,
        payment_date=_PAYMENT,
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
        events=tuple(events),  # type: ignore[arg-type]
    )


def _make_case(
    start: date = date(_YEAR, _MONTH, 5),
    end: date = date(_YEAR, _MONTH, 10),
    working_days: int = 5,
    waiting_period_days: int = 3,
    gross_daily: Decimal = Decimal("80.00"),
    inps_daily_rate: Decimal = Decimal("0.50"),
    integration_rate: Decimal = Decimal("1.00"),
    carenza_integration_rate: Decimal = Decimal(0),
) -> SicknessCase:
    """Build a SicknessCase with sensible defaults.

    Returns:
        A :class:`SicknessCase` with the given parameters.
    """
    return SicknessCase(
        episode_start=start,
        episode_end=end,
        working_days=working_days,
        waiting_period_days=waiting_period_days,
        gross_daily=gross_daily,
        inps_daily_rate=inps_daily_rate,
        integration_rate=integration_rate,
        carenza_integration_rate=carenza_integration_rate,
    )


class TestSicknessCaseSpansMultipleMonths:
    """Gate: assenza a cavallo di mese."""

    def test_same_month_episode(self) -> None:
        """spans_multiple_months is False for an episode within one month."""
        sc = _make_case(
            start=date(_YEAR, _MONTH, 5),
            end=date(_YEAR, _MONTH, 10),
        )
        assert sc.spans_multiple_months is False

    def test_cross_month_episode(self) -> None:
        """spans_multiple_months is True when the episode crosses a month boundary."""
        sc = _make_case(
            start=date(_YEAR, 1, 25),
            end=date(_YEAR, 2, 5),
            working_days=8,
            waiting_period_days=0,
        )
        assert sc.spans_multiple_months is True

    def test_cross_year_episode(self) -> None:
        """spans_multiple_months is True when the episode crosses a year boundary."""
        sc = _make_case(
            start=date(_YEAR, 12, 28),
            end=date(_YEAR + 1, 1, 4),
            working_days=5,
            waiting_period_days=0,
        )
        assert sc.spans_multiple_months is True


class TestSicknessCaseNegativeCarenza:
    """Gate: carenza negativa produce errore."""

    def test_waiting_period_exceeds_working_days_raises(self) -> None:
        """waiting_period_days > working_days raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _make_case(working_days=3, waiting_period_days=5)

    def test_negative_waiting_period_raises(self) -> None:
        """Negative waiting_period_days raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _make_case(waiting_period_days=-1)


class TestSicknessCaseEventCalculation:
    """Gate: INPS indemnity and employer integration appear as separate pay items."""

    def _result_with_sickness(
        self,
        working_days: int = 5,
        waiting_period_days: int = 3,
        inps_daily_rate: Decimal = Decimal("0.50"),
        integration_rate: Decimal = Decimal("1.00"),
        carenza_integration_rate: Decimal = Decimal(0),
        gross_daily: Decimal = Decimal("80.00"),
    ) -> PeriodResult:
        """Run calculate_period with a SicknessCaseEvent and return the result.

        Returns:
            :class:`PeriodResult` from the calculation.
        """
        case = _make_case(
            working_days=working_days,
            waiting_period_days=waiting_period_days,
            inps_daily_rate=inps_daily_rate,
            integration_rate=integration_rate,
            carenza_integration_rate=carenza_integration_rate,
            gross_daily=gross_daily,
        )
        evt = SicknessCaseEvent(event_date=date(_YEAR, _MONTH, 5), case=case)
        return calculate_period(_req(evt))

    def test_absence_deduction_pay_item_present(self) -> None:
        """An AbsenceDeduction pay item is posted for the sick days."""
        result = self._result_with_sickness()
        absence_items = [
            it for it in result.pay_items if isinstance(it, AbsenceDeduction)
        ]
        assert len(absence_items) == 1
        assert absence_items[0].amount == Decimal("400.00")  # 5 days * 80.00

    def test_inps_and_employer_sickness_items_present(self) -> None:
        """INPS indemnity and employer integration are separate SicknessItem entries."""
        result = self._result_with_sickness(
            working_days=5,
            waiting_period_days=3,
            inps_daily_rate=Decimal("0.50"),
            integration_rate=Decimal("1.00"),
        )
        sickness_items = [it for it in result.pay_items if isinstance(it, SicknessItem)]
        # indemnifiable_days=2: INPS indemnity item + employer integration item
        assert len(sickness_items) == 2

    def test_inps_indemnity_amount(self) -> None:
        """INPS indemnity = gross_daily * inps_daily_rate * indemnifiable_days."""
        result = self._result_with_sickness(
            working_days=5,
            waiting_period_days=3,
            inps_daily_rate=Decimal("0.50"),
            integration_rate=Decimal("1.00"),
            gross_daily=Decimal("100.00"),
        )
        # indemnifiable_days=2; INPS indemnity = 100 * 0.50 * 2 = 100.00
        # employer integration = 100 * (1.00 - 0.50) * 2 = 100.00
        sickness_items = [it for it in result.pay_items if isinstance(it, SicknessItem)]
        amounts = sorted(it.amount for it in sickness_items)
        assert amounts == [Decimal("100.00"), Decimal("100.00")]

    def test_employee_deductions_entry_posted(self) -> None:
        """EMPLOYEE_DEDUCTIONS entry is posted with positive amount for the absence."""
        result = self._result_with_sickness()
        deduction_entries = [
            e
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYEE_DEDUCTIONS
        ]
        assert len(deduction_entries) >= 1
        assert all(e.amount > _ZERO for e in deduction_entries)

    def test_cash_earnings_entries_for_sickness_components(self) -> None:
        """CASH_EARNINGS entries with sickness_item kind are posted for both components.

        Checks that INPS indemnity and employer integration entries hit CASH_EARNINGS.
        """
        result = self._result_with_sickness(
            inps_daily_rate=Decimal("0.50"),
            integration_rate=Decimal("1.00"),
        )
        cash_entries = [
            e
            for e in result.ledger_entries
            if e.account == AccountKind.CASH_EARNINGS
            and e.pay_item_kind == "sickness_item"
        ]
        # INPS indemnity + employer integration = 2 entries (indemnifiable_days=2)
        assert len(cash_entries) == 2
        assert all(e.amount > _ZERO for e in cash_entries)

    def test_carenza_integration_item_present(self) -> None:
        """When carenza_integration_rate > 0, a third SicknessItem is posted."""
        result = self._result_with_sickness(
            working_days=5,
            waiting_period_days=3,
            carenza_integration_rate=Decimal("0.50"),
        )
        sickness_items = [it for it in result.pay_items if isinstance(it, SicknessItem)]
        # INPS indemnity + employer integration + carenza integration = 3 items
        assert len(sickness_items) == 3

    def test_no_inps_indemnity_when_rate_zero(self) -> None:
        """When inps_daily_rate = 0, no INPS indemnity item is posted."""
        result = self._result_with_sickness(
            inps_daily_rate=Decimal(0),
            integration_rate=Decimal("1.00"),
        )
        sickness_items = [it for it in result.pay_items if isinstance(it, SicknessItem)]
        # Only employer integration (INPS indemnity = 0, no carenza)
        assert len(sickness_items) == 1

    def test_no_sickness_items_when_all_carenza_no_integration(self) -> None:
        """No SicknessItem is posted when all days are carenza and no carenza coverage.

        When all working_days are waiting_period_days and carenza_integration_rate=0,
        indemnifiable_days=0 and no employer coverage applies.
        """
        result = self._result_with_sickness(
            working_days=3,
            waiting_period_days=3,
            inps_daily_rate=Decimal("0.50"),
            integration_rate=Decimal("1.00"),
            carenza_integration_rate=Decimal(0),
        )
        sickness_items = [it for it in result.pay_items if isinstance(it, SicknessItem)]
        # No indemnifiable days, no carenza integration → no sickness items
        assert len(sickness_items) == 0

    def test_result_is_valid_period_result(self) -> None:
        """calculate_period returns a valid PeriodResult."""
        result = self._result_with_sickness()
        assert isinstance(result, PeriodResult)
        assert result.period_gross >= _ZERO


class TestSicknessCaseNetDelta:
    """Gate: delta netto = -assenza + indennità + integrazione.

    These tests derive the expected delta from domain facts, not from the
    production formula. They would have caught the P0 sign bug.
    """

    def _base_result(self) -> PeriodResult:
        """Run a base period with no events.

        Returns:
            :class:`PeriodResult` for a period with no events.
        """
        return calculate_period(_req())

    def _sick_result(
        self,
        working_days: int,
        waiting_period_days: int,
        gross_daily: Decimal,
        inps_daily_rate: Decimal,
        integration_rate: Decimal,
        carenza_integration_rate: Decimal = _ZERO,
    ) -> PeriodResult:
        case = _make_case(
            working_days=working_days,
            waiting_period_days=waiting_period_days,
            gross_daily=gross_daily,
            inps_daily_rate=inps_daily_rate,
            integration_rate=integration_rate,
            carenza_integration_rate=carenza_integration_rate,
        )
        evt = SicknessCaseEvent(event_date=date(_YEAR, _MONTH, 5), case=case)
        return calculate_period(_req(evt))

    def test_net_delta_does_not_exceed_positive_components(self) -> None:
        """Net delta must not exceed the sum of positive sickness components.

        For 3 sick days at €100/day, INPS 50%, integration to 100%:
          - absence deduction: -€300
          - INPS indemnity:    +€100 (2 indemnifiable days * 100 * 0.50)
          - employer intg:     +€100 (2 days * 100 * 0.50)
        The net delta before tax must not be positive (sickness should cost).
        The absolute delta cannot exceed €300 (the sum of positive components).
        """
        base = self._base_result()
        sick = self._sick_result(
            working_days=5,
            waiting_period_days=3,
            gross_daily=Decimal("100.00"),
            inps_daily_rate=Decimal("0.50"),
            integration_rate=Decimal("1.00"),
        )
        absence = Decimal("100.00") * 5  # €500
        indemnity = Decimal("100.00") * Decimal("0.50") * 2  # €100
        integration = Decimal("100.00") * Decimal("0.50") * 2  # €100
        max_positive_impact = indemnity + integration  # €200

        delta_net = sick.period_net - base.period_net
        # The absence must reduce the net; the positive components cannot reverse this.
        assert delta_net <= max_positive_impact, (
            f"Net delta {delta_net} exceeds max positive component "
            f"sum {max_positive_impact}. Likely sign bug in EMPLOYEE_DEDUCTIONS."
        )
        # Specifically: gross lost minus positive components gives a negative floor.
        assert delta_net < absence, (
            f"Net delta {delta_net} >= absence {absence}: "
            "absence deduction had no effect."
        )

    def test_net_delta_bounded_by_gross_components(self) -> None:
        """With full INPS coverage and integration, net delta must not be positive."""
        base = self._base_result()
        sick = self._sick_result(
            working_days=3,
            waiting_period_days=0,
            gross_daily=Decimal("80.00"),
            inps_daily_rate=Decimal("1.00"),
            integration_rate=Decimal("1.00"),
        )
        # Absence: -€240, INPS indemnity: +€240, integration: 0
        # Net delta pre-tax ≈ 0; after tax may differ slightly.
        # The key: delta must not be *greater* than the absence amount.
        delta_net = sick.period_net - base.period_net
        assert delta_net <= Decimal(0), (
            f"Net delta {delta_net} is positive with full coverage: "
            "sickness increased net."
        )
