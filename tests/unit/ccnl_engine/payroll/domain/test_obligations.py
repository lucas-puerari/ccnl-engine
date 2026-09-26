"""Tests for the split of the payroll state into tax year and obligations."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.obligations import (
    SOMMA_ESENTE_RECOVERY,
    TRATTAMENTO_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.period import PeriodState
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState


def _plan(posted: int = 0, kind: str = "trattamento_integrativo") -> RecoveryPlan:
    return RecoveryPlan(
        kind=kind,
        original_amount=Decimal(160),
        installment_amount=Decimal(20),
        installments_total=8,
        installments_posted=posted,
    )


class TestRecoveryObligation:
    """A recovery plan bound to the tax year of the credit it recovers."""

    def test_rejects_an_unmodelled_credit(self) -> None:
        """Only trattamento integrativo and somma esente recoveries exist."""
        with pytest.raises(ValueError, match=r"plan\.kind"):
            RecoveryObligation(tax_year=2026, plan=_plan(kind="bonus"))

    def test_rejects_a_tax_year_before_2020(self) -> None:
        """The origin tax year follows the same bound as the tax year state."""
        with pytest.raises(ValueError, match="tax_year must be >= 2020"):
            RecoveryObligation(tax_year=2019, plan=_plan())

    def test_advanced_posts_one_installment_and_keeps_the_origin(self) -> None:
        """Advancing moves the plan on and keeps the origin year."""
        advanced = RecoveryObligation(tax_year=2026, plan=_plan(2)).advanced()

        assert advanced == RecoveryObligation(tax_year=2026, plan=_plan(3))

    def test_advanced_after_the_last_installment_is_none(self) -> None:
        """The obligation ends with its last installment."""
        assert RecoveryObligation(tax_year=2026, plan=_plan(7)).advanced() is None


class TestEmploymentObligations:
    """Obligations carried across tax years."""

    def test_rejects_two_recoveries_of_the_same_year(self) -> None:
        """One conguaglio opens at most one recovery."""
        first = RecoveryObligation(tax_year=2026, plan=_plan())
        second = RecoveryObligation(tax_year=2026, plan=_plan(1))

        with pytest.raises(ValueError, match="same tax year"):
            EmploymentObligations(recoveries=(first, second))

    def test_queries_by_origin_year(self) -> None:
        """Recoveries are looked up by the year that opened them."""
        old = RecoveryObligation(tax_year=2025, plan=_plan(6))
        new = RecoveryObligation(tax_year=2026, plan=_plan(1))
        obligations = EmploymentObligations(recoveries=(old, new))

        assert obligations.latest_tax_year == 2026
        assert obligations.recovery_of(2026, TRATTAMENTO_RECOVERY) == new.plan
        assert obligations.recovery_of(2026, SOMMA_ESENTE_RECOVERY) is None
        assert obligations.recovery_of(2024, TRATTAMENTO_RECOVERY) is None
        assert obligations.carried_into(2026) == (old,)
        assert obligations.carried_into(2027) == (old, new)

    def test_one_recovery_per_credit_and_year(self) -> None:
        """One conguaglio can open a trattamento and a somma esente recovery."""
        tratt = RecoveryObligation(tax_year=2026, plan=_plan())
        somma = RecoveryObligation(
            tax_year=2026, plan=_plan(kind=SOMMA_ESENTE_RECOVERY)
        )
        obligations = EmploymentObligations(recoveries=(tratt, somma))

        assert obligations.recovery_of(2026, SOMMA_ESENTE_RECOVERY) == somma.plan
        assert obligations.recovery_of(2026, TRATTAMENTO_RECOVERY) == tratt.plan

    def test_empty_has_no_latest_year(self) -> None:
        """No recovery, no origin year."""
        assert EmploymentObligations().latest_tax_year is None


class TestTaxYearState:
    """Counters of the tax year and its completion."""

    def test_rejects_zero_withholding_slots(self) -> None:
        """A withholding schedule has at least one slot."""
        with pytest.raises(ValueError, match="withholding_slots"):
            TaxYearState(withholding_slots=0)

    @pytest.mark.parametrize(
        ("closed", "slots", "complete"),
        [(0, None, False), (12, 13, False), (13, 13, True)],
    )
    def test_is_complete_when_every_slot_is_closed(
        self, closed: int, slots: int | None, complete: bool
    ) -> None:
        """The year is complete once the last withholding slot is closed."""
        state = TaxYearState(
            regular_periods_closed=min(closed, 12),
            tax_withholding_periods_closed=closed,
            withholding_slots=slots,
        )

        assert state.is_complete is complete


class TestPeriodState:
    """The composite of tax year state and obligations."""

    def test_rejects_a_recovery_opened_after_its_tax_year(self) -> None:
        """A 2027 recovery cannot sit in a 2026 state."""
        obligations = EmploymentObligations(
            recoveries=(RecoveryObligation(tax_year=2027, plan=_plan()),)
        )

        with pytest.raises(ValueError, match="opened in 2027"):
            PeriodState(ytd=TaxYearState(tax_year=2026), obligations=obligations)

    def test_unbound_state_accepts_any_recovery(self) -> None:
        """Without a tax year there is nothing to compare the origin with."""
        obligations = EmploymentObligations(
            recoveries=(RecoveryObligation(tax_year=2027, plan=_plan()),)
        )

        assert PeriodState(obligations=obligations).tax_year is None


def _ids(*texts: str) -> tuple[PayrollRunId, ...]:
    return tuple(PayrollRunId.parse(t) for t in texts)


class TestClosedRunIds:
    """The runs closed in a tax year: once each, of the year, in order."""

    def _state(self, *texts: str, regular: int = 12, slots: int = 14) -> TaxYearState:
        return TaxYearState(
            tax_year=2026,
            regular_periods_closed=regular,
            tax_withholding_periods_closed=slots,
            closed_run_ids=_ids(*texts),
        )

    def test_accepts_the_runs_in_payment_order(self) -> None:
        """Regular before the extra month of the same month."""
        state = self._state("2026-06-regular", "2026-06-fourteenth", "2026-07-regular")

        assert [str(r) for r in state.closed_run_ids] == [
            "2026-06-regular",
            "2026-06-fourteenth",
            "2026-07-regular",
        ]

    def test_rejects_a_duplicate(self) -> None:
        """A run closes once."""
        with pytest.raises(ValueError, match="already processed"):
            self._state("2026-01-regular", "2026-01-regular")

    def test_rejects_a_run_out_of_order(self) -> None:
        """The extra month of June cannot close after July."""
        with pytest.raises(ValueError, match="out of order"):
            self._state("2026-07-regular", "2026-06-fourteenth")

    def test_rejects_a_run_of_a_later_year(self) -> None:
        """A 2027 run cannot belong to tax year 2026."""
        with pytest.raises(ValueError, match="after the tax year 2026"):
            self._state("2027-01-regular")

    def test_adjustment_and_late_runs_are_not_ordered(self) -> None:
        """A correction of March and a late December 2025 run after May."""
        state = self._state(
            "2026-05-regular", "2026-03-adjustment", "2025-12-regular", regular=2
        )

        assert len(state.closed_run_ids) == 3

    def test_rejects_ids_without_a_tax_year(self) -> None:
        """Closed runs belong to a tax year."""
        with pytest.raises(ValueError, match="requires a tax_year"):
            TaxYearState(
                regular_periods_closed=1,
                tax_withholding_periods_closed=1,
                closed_run_ids=_ids("2026-01-regular"),
            )

    @pytest.mark.parametrize(
        ("regular", "slots", "match"),
        [(0, 2, "regular runs"), (1, 1, "slot-consuming runs")],
    )
    def test_rejects_more_runs_than_the_counters(
        self, regular: int, slots: int, match: str
    ) -> None:
        """The ids never outnumber the runs the counters closed."""
        with pytest.raises(ValueError, match=match):
            self._state(
                "2026-01-regular", "2026-06-fourteenth", regular=regular, slots=slots
            )

    def test_check_next_run(self) -> None:
        """The same rules apply to the next run before it is computed."""
        state = self._state("2026-03-regular", regular=1, slots=1)

        state.check_next_run(PayrollRunId.parse("2026-04-regular"))
        with pytest.raises(ValueError, match="out of order"):
            state.check_next_run(PayrollRunId.parse("2026-02-regular"))

    def test_unbound_state_only_rejects_duplicates(self) -> None:
        """Without a tax year a first run of any year can close."""
        TaxYearState().check_next_run(PayrollRunId.parse("2030-01-regular"))
