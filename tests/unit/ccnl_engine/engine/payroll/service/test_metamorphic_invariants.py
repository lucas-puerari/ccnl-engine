"""Metamorphic invariants and reconciliation tests for the payroll engine.

These tests verify relational properties that must hold across different
scenarios: the output changes in the expected direction when inputs change,
and accounting identities hold across all valid inputs.

Properties covered:
  - Higher RAL does not reduce gross pay.
  - 50% part-time scales gross exactly by 0.5.
  - Employee contributions never exceed the contribution base.
  - Net = gross - employee contributions - taxes + credits.
  - Employer cost = gross + employer contributions + funds + TFR.
  - Splitting a sick episode in two preserves the total deduction.
  - Monthly gross_monthly * additional_months == gross_annual within rounding.
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ccnl_engine.engine.contract.domain.absence import AbsenceRules, DailyDivisorMethod
from ccnl_engine.engine.payroll.domain.employment import FixedTerm, Permanent
from ccnl_engine.engine.payroll.domain.supplements import AbsenceDays
from ccnl_engine.engine.payroll.service.absence import compute_absence_deduction
from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.engine.payroll.service.rounding import money
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _RULES,
    _build_ccnl,
    _req,
)

_ZERO = Decimal(0)
_LEVEL_CODES = ["2", "3", "4"]
_SENIORITY_MAX = 10

_DEFAULT_CCNL = _build_ccnl()

_MOCK_REPO = MagicMock()
_MOCK_REPO.load_ccnl.return_value = _DEFAULT_CCNL
_MOCK_REPO.load_year_rules.return_value = _RULES
_MOCK_REPO.load_surtax_rules.return_value = None


def _compute(scenario: object) -> object:
    """Run compute() with test CCNL and rules mocked in.

    Returns:
        Calculation result with all gross, net and cost figures.
    """
    with patch(
        "ccnl_engine.engine.payroll.service.pipeline._default_repo",
        new=_MOCK_REPO,
    ):
        return compute(scenario)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Metamorphic: higher RAL does not reduce gross
# ---------------------------------------------------------------------------


class TestRalMonotonicity:
    """A higher negotiated RAL yields equal or greater gross_annual."""

    @given(
        base_ral=st.integers(min_value=10000, max_value=50000),
        delta=st.integers(min_value=100, max_value=10000),
    )
    def test_higher_ral_does_not_reduce_gross(self, base_ral: int, delta: int) -> None:
        """gross_annual with RAL+delta >= gross_annual with RAL."""
        low = _compute(_req(level_code="4", negotiated_ral=Decimal(base_ral)))
        high = _compute(_req(level_code="4", negotiated_ral=Decimal(base_ral + delta)))
        assert (
            high.result.earnings.gross_annual >= low.result.earnings.gross_annual  # type: ignore[attr-defined]
        )


# ---------------------------------------------------------------------------
# Metamorphic: part-time 50% halves gross exactly
# ---------------------------------------------------------------------------


class TestPartTimeExactScaling:
    """50% part-time worker has gross_annual = full-time * 0.5."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_50pct_part_time_halves_gross(
        self, level_code: str, seniority_count: int
    ) -> None:
        """gross_annual at 50% = money(full_gross * 0.5)."""
        full = _compute(
            _req(level_code=level_code, seniority_count=seniority_count)
        ).result  # type: ignore[attr-defined]
        half = _compute(
            _req(
                level_code=level_code,
                seniority_count=seniority_count,
                part_time_ratio=Decimal("0.5"),
            )
        ).result  # type: ignore[attr-defined]
        assert half.earnings.gross_annual == money(
            full.earnings.gross_annual * Decimal("0.5")
        )

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_50pct_part_time_halves_gross_monthly(
        self, level_code: str, seniority_count: int
    ) -> None:
        """gross_monthly at 50% = money(full_gross_monthly * 0.5)."""
        full = _compute(
            _req(level_code=level_code, seniority_count=seniority_count)
        ).result  # type: ignore[attr-defined]
        half = _compute(
            _req(
                level_code=level_code,
                seniority_count=seniority_count,
                part_time_ratio=Decimal("0.5"),
            )
        ).result  # type: ignore[attr-defined]
        assert half.earnings.gross_monthly == money(
            full.earnings.gross_monthly * Decimal("0.5")
        )


# ---------------------------------------------------------------------------
# Invariant: contributions do not exceed the applicable gross base
# ---------------------------------------------------------------------------


class TestContributionsDoNotExceedBase:
    """Employee INPS contributions are always <= gross_annual."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_inps_employee_does_not_exceed_gross(
        self, level_code: str, seniority_count: int
    ) -> None:
        """Employee INPS <= gross_annual for all valid scenarios."""
        result = _compute(
            _req(level_code=level_code, seniority_count=seniority_count)
        ).result  # type: ignore[attr-defined]
        assert result.contributions.inps_employee_annual <= result.earnings.gross_annual

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_inps_employer_does_not_exceed_gross(
        self, level_code: str, seniority_count: int
    ) -> None:
        """Employer INPS <= 2 * gross_annual (no contribution exceeds twice gross)."""
        result = _compute(
            _req(level_code=level_code, seniority_count=seniority_count)
        ).result  # type: ignore[attr-defined]
        assert result.contributions.inps_employer_annual <= (
            Decimal(2) * result.earnings.gross_annual
        )


# ---------------------------------------------------------------------------
# Accounting identity: net = earnings - contributions - taxes + credits
# ---------------------------------------------------------------------------


class TestNetAccountingIdentity:
    """net_annual satisfies the statutory accounting identity."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_net_accounting_identity(
        self, level_code: str, seniority_count: int
    ) -> None:
        """Net = gross - inps_emp - irpef_net - addizionali + TI + somma_esente."""
        result = _compute(
            _req(level_code=level_code, seniority_count=seniority_count)
        ).result  # type: ignore[attr-defined]
        e = result.earnings
        c = result.contributions
        t = result.taxes
        expected_net = money(
            e.gross_annual
            - c.inps_employee_annual
            - c.bilateral_employee_annual
            - t.irpef_net
            - t.addizionale_regionale_annual
            - t.addizionale_comunale_annual
            + t.trattamento_integrativo
            + t.somma_esente
        )
        assert result.net_annual == expected_net


# ---------------------------------------------------------------------------
# Accounting identity: employer cost = gross + employer contributions + TFR
# ---------------------------------------------------------------------------


class TestEmployerCostIdentity:
    """employer_cost_annual satisfies the accounting identity."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_employer_cost_accounting_identity(
        self, level_code: str, seniority_count: int
    ) -> None:
        """Employer cost = gross + inps_employer + employer_funds + tfr + bilateral."""
        result = _compute(
            _req(level_code=level_code, seniority_count=seniority_count)
        ).result  # type: ignore[attr-defined]
        e = result.earnings
        c = result.contributions
        expected_cost = money(
            e.gross_annual
            + c.inps_employer_annual
            + c.employer_funds_annual
            + c.tfr_annual
            + c.bilateral_employer_annual
        )
        assert result.employer_cost.employer_cost_annual == expected_cost


# ---------------------------------------------------------------------------
# Reconciliation: gross_annual matches money(gross_monthly * additional_months)
# ---------------------------------------------------------------------------


class TestGrossReconciliation:
    """gross_annual and gross_monthly reconcile within the rounding policy."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_gross_annual_equals_monthly_times_12(
        self, level_code: str, seniority_count: int
    ) -> None:
        """gross_annual == money(gross_monthly * 12) for 12-month test CCNL."""
        result = _compute(
            _req(level_code=level_code, seniority_count=seniority_count)
        ).result  # type: ignore[attr-defined]
        assert result.earnings.gross_annual == money(
            result.earnings.gross_monthly * Decimal(12)
        )

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_net_monthly_equals_net_annual_divided_by_12(
        self, level_code: str, seniority_count: int
    ) -> None:
        """net_monthly == money(net_annual / 12) for 12-month test CCNL."""
        result = _compute(
            _req(level_code=level_code, seniority_count=seniority_count)
        ).result  # type: ignore[attr-defined]
        assert result.net_monthly == money(result.net_annual / Decimal(12))


# ---------------------------------------------------------------------------
# Sick episode splitting: splitting N unpaid days into two half-periods
# preserves the total absence deduction (additive property).
# ---------------------------------------------------------------------------

_GROSS_MONTHLY = Decimal("1000.00")
_HOURLY_RATE = Decimal("5.95")  # 1000 / 168
_ABSENCE_RULES_BY_26 = AbsenceRules(daily_divisor_method=DailyDivisorMethod.BY_26)


class TestSickEpisodeSplitting:
    """Splitting N unpaid absence days into two N/2 periods preserves the total."""

    @pytest.mark.parametrize("total_days", [2, 6, 10])
    def test_split_absence_episode_preserves_total(self, total_days: int) -> None:
        """Two half-episodes sum to the same absence deduction as one whole."""
        half = Decimal(total_days) / Decimal(2)

        def _deduct(days: Decimal) -> Decimal:
            return compute_absence_deduction(
                absence_input=AbsenceDays(unpaid_days=days),
                absence_rules=_ABSENCE_RULES_BY_26,
                gross_monthly=_GROSS_MONTHLY,
                hourly_rate=_HOURLY_RATE,
            )

        deduction_whole = _deduct(Decimal(total_days))
        deduction_half_a = _deduct(half)
        deduction_half_b = _deduct(half)
        assert deduction_half_a + deduction_half_b == deduction_whole

    def test_zero_absence_days_yields_zero_deduction(self) -> None:
        """Zero unpaid days: deduction=0."""
        result = compute_absence_deduction(
            absence_input=AbsenceDays(unpaid_days=_ZERO),
            absence_rules=_ABSENCE_RULES_BY_26,
            gross_monthly=_GROSS_MONTHLY,
            hourly_rate=_HOURLY_RATE,
        )
        assert result == _ZERO


# ---------------------------------------------------------------------------
# Metamorphic: fixed-term employer cost > permanent employer cost
# ---------------------------------------------------------------------------


class TestFixedTermCostHigherThanPermanent:
    """Fixed-term employer cost > permanent (NASpI addizionale surcharge)."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_fixed_term_employer_cost_exceeds_permanent(
        self, level_code: str, seniority_count: int
    ) -> None:
        """Fixed-term employer_cost_annual > permanent employer_cost_annual."""
        perm = _compute(
            _req(
                level_code=level_code,
                seniority_count=seniority_count,
                contract=Permanent(),
            )
        ).result  # type: ignore[attr-defined]
        ft = _compute(
            _req(
                level_code=level_code,
                seniority_count=seniority_count,
                contract=FixedTerm(),
            )
        ).result  # type: ignore[attr-defined]
        assert (
            ft.employer_cost.employer_cost_annual
            > perm.employer_cost.employer_cost_annual
        )
