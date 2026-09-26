"""Tests for the split of the payroll state into tax year and obligations."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.period import PeriodState
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
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

    def test_rejects_a_credit_other_than_trattamento(self) -> None:
        """Only the trattamento integrativo recovery is modelled."""
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
        assert obligations.recovery_of(2026) == new.plan
        assert obligations.recovery_of(2024) is None
        assert obligations.carried_into(2026) == (old,)
        assert obligations.carried_into(2027) == (old, new)

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
