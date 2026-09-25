"""Unit tests for RecoveryPlan domain type."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan

_ZERO = Decimal(0)


class TestRecoveryPlanValidation:
    """RecoveryPlan.__post_init__ rejects invalid fields."""

    def test_original_amount_zero_raises(self) -> None:
        """original_amount = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="original_amount must be > 0"):
            RecoveryPlan(
                kind="k",
                original_amount=_ZERO,
                installment_amount=Decimal("10.00"),
                installments_total=8,
                installments_posted=0,
            )

    def test_original_amount_negative_raises(self) -> None:
        """original_amount < 0 must raise ValueError."""
        with pytest.raises(ValueError, match="original_amount must be > 0"):
            RecoveryPlan(
                kind="k",
                original_amount=Decimal("-1.00"),
                installment_amount=Decimal("10.00"),
                installments_total=8,
                installments_posted=0,
            )

    def test_installment_amount_zero_raises(self) -> None:
        """installment_amount = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="installment_amount must be > 0"):
            RecoveryPlan(
                kind="k",
                original_amount=Decimal("80.00"),
                installment_amount=_ZERO,
                installments_total=8,
                installments_posted=0,
            )

    def test_installment_amount_negative_raises(self) -> None:
        """installment_amount < 0 must raise ValueError."""
        with pytest.raises(ValueError, match="installment_amount must be > 0"):
            RecoveryPlan(
                kind="k",
                original_amount=Decimal("80.00"),
                installment_amount=Decimal("-5.00"),
                installments_total=8,
                installments_posted=0,
            )

    def test_installments_total_zero_raises(self) -> None:
        """installments_total = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="installments_total must be >= 1"):
            RecoveryPlan(
                kind="k",
                original_amount=Decimal("80.00"),
                installment_amount=Decimal("10.00"),
                installments_total=0,
                installments_posted=0,
            )

    def test_installments_posted_negative_raises(self) -> None:
        """installments_posted < 0 must raise ValueError."""
        with pytest.raises(ValueError, match="installments_posted must be in"):
            RecoveryPlan(
                kind="k",
                original_amount=Decimal("80.00"),
                installment_amount=Decimal("10.00"),
                installments_total=8,
                installments_posted=-1,
            )

    def test_installments_posted_equal_total_raises(self) -> None:
        """installments_posted == installments_total must raise ValueError."""
        with pytest.raises(ValueError, match="installments_posted must be in"):
            RecoveryPlan(
                kind="k",
                original_amount=Decimal("80.00"),
                installment_amount=Decimal("10.00"),
                installments_total=8,
                installments_posted=8,
            )


class TestRecoveryPlanBehavior:
    """RecoveryPlan.next_installment and advance() correctness."""

    def _plan(self, *, posted: int = 0) -> RecoveryPlan:
        return RecoveryPlan(
            kind="trattamento_integrativo",
            original_amount=Decimal("90.00"),
            installment_amount=Decimal("11.25"),
            installments_total=8,
            installments_posted=posted,
        )

    def test_mid_period_installment_is_uniform(self) -> None:
        """Mid-plan installments equal installment_amount."""
        assert self._plan(posted=0).next_installment == Decimal("11.25")
        assert self._plan(posted=3).next_installment == Decimal("11.25")

    def test_last_installment_absorbs_residual(self) -> None:
        """Final installment absorbs any rounding residual."""
        plan = self._plan(posted=7)
        expected_residual = Decimal("90.00") - Decimal("11.25") * 7
        assert plan.next_installment == expected_residual

    def test_advance_increments_posted(self) -> None:
        """advance() returns a plan with installments_posted incremented by 1."""
        plan = self._plan(posted=0).advance()
        assert plan.installments_posted == 1

    def test_create_sets_installment_amount(self) -> None:
        """create() divides original_amount evenly and starts at posted=0."""
        plan = RecoveryPlan.create("k", Decimal("80.00"), 8)
        assert plan.installment_amount == Decimal("10.00")
        assert plan.installments_posted == 0
        assert plan.installments_total == 8
