"""Tests for the obligations that survive the change of tax year."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.obligations import (
    SOMMA_ESENTE_RECOVERY,
    TRATTAMENTO_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.recovery_plan import InstallmentRun, RecoveryPlan


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
        with pytest.raises(InvalidInputError, match=r"plan\.kind"):
            RecoveryObligation(tax_year=2026, plan=_plan(kind="bonus"))

    def test_rejects_a_tax_year_before_2020(self) -> None:
        """The origin tax year follows the same bound as the tax year state."""
        with pytest.raises(InvalidInputError, match="tax_year must be an int >= 2020"):
            RecoveryObligation(tax_year=2019, plan=_plan())

    def test_post_moves_one_installment_and_keeps_the_origin(self) -> None:
        """An ordinary run posts 20 of 160 and keeps the origin year."""
        posted, after = RecoveryObligation(tax_year=2026, plan=_plan(2)).post(
            InstallmentRun()
        )

        assert posted.amount == Decimal(20)
        assert posted.reason == "installment_posted"
        assert after == RecoveryObligation(tax_year=2026, plan=_plan(3))

    def test_post_after_the_last_installment_is_none(self) -> None:
        """The obligation ends with its last installment."""
        posted, after = RecoveryObligation(tax_year=2026, plan=_plan(7)).post(
            InstallmentRun()
        )

        assert posted.reason == "last_installment_posted"
        assert after is None

    def test_final_run_settles_the_residual(self) -> None:
        """Two of eight posted: the final run recovers 160 - 2 x 20 = 120."""
        posted, after = RecoveryObligation(tax_year=2026, plan=_plan(2)).post(
            InstallmentRun(final=True, adjustment=True)
        )

        assert posted.amount == Decimal(120)
        assert posted.reason == "settled_at_termination"
        assert after is None

    def test_adjustment_run_posts_one_installment(self) -> None:
        """An adjustment run posts the next installment with its own reason."""
        posted, after = RecoveryObligation(tax_year=2026, plan=_plan(7)).post(
            InstallmentRun(adjustment=True)
        )

        assert posted.amount == Decimal(20)
        assert posted.reason == "installment_posted_adjustment_run"
        assert after is None


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
