"""Tests for Employer.second_level_allowances — second-level bargaining.

Covers:
* guard: second_level_allowances incompatible with a RAL override
* basic amount lands in gross_monthly, gross_annual, contribution base, TFR base
* part_time_pct scaling
* months_per_year override (annualised with 1 month instead of additional_months)
* contribution_relevant=False excludes from INPS base
* tfr_relevant=False excludes from TFR base
* apprenticeship_pct_relevant=True (default) reduces amount for pct-track apprentices
* apprenticeship_pct_relevant=False keeps full part-time value for pct-track apprentices
"""

from __future__ import annotations

import pytest

from ccnl_engine.engine.contract.domain.ccnl import CCNL, SupplementaryAllowance
from ccnl_engine.engine.payroll.domain.employment import Apprentice
from ccnl_engine.engine.payroll.service.gross import _scale_second_level
from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.engine.payroll.service.rounding import money
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _RULES,
    _build_ccnl,
    _req,
)

_SL_100 = SupplementaryAllowance(
    code="ERT",
    description="Elemento territoriale",
    monthly=_D("100.00"),
)

_DEFAULT_CCNL = _build_ccnl()

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[object] = [_RULES]


@pytest.fixture(autouse=True)
def _patch_loaders(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the three loaders in orchestrator and reset mock state."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_RULES]
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl",
        lambda _: _mock_ccnl[0],
    )
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_year_rules",
        lambda *_: _mock_rules[0],
    )
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_surtax_rules",
        lambda _: None,
    )


# ---------------------------------------------------------------------------
# Guard: second_level_allowances is incompatible with RAL overrides
# ---------------------------------------------------------------------------


class TestSecondLevelGuard:
    """second_level_allowances is incompatible with RAL overrides."""

    def test_negotiated_ral_raises(self) -> None:
        """Combining second_level_allowances with RalOverride must raise."""
        with pytest.raises(ValueError, match="RAL override"):
            compute(
                _req(
                    negotiated_ral=_D("20000"),
                    second_level_allowances=(_SL_100,),
                )
            )

    def test_destination_ral_raises(self) -> None:
        """Combining second_level_allowances with DestinationRalOverride raises."""
        with pytest.raises(ValueError, match="RAL override"):
            compute(
                _req(
                    contract=Apprentice(months_elapsed=12),
                    negotiated_destination_ral=_D("20000"),
                    second_level_allowances=(_SL_100,),
                )
            )


# ---------------------------------------------------------------------------
# Basic wiring: amount appears in gross and all bases
# ---------------------------------------------------------------------------


class TestSecondLevelBasic:
    """second_level_monthly flows into gross, contribution, and TFR bases."""

    def test_second_level_monthly_on_payroll(self) -> None:
        """PayrollResult.second_level_monthly equals the scaled allowance total."""
        result = compute(_req(second_level_allowances=(_SL_100,)))
        assert result.second_level_monthly == _D("100.00")

    def test_zero_when_no_allowances(self) -> None:
        """second_level_monthly is zero when no allowances are supplied."""
        result = compute(_req())
        assert result.second_level_monthly == _D("0.00")

    def test_gross_monthly_includes_supplement(self) -> None:
        """gross_monthly = base + second_level when no other components."""
        result = compute(_req(second_level_allowances=(_SL_100,)))
        expected = money(_D("1000.00") + _D("100.00"))
        assert result.gross_monthly == expected

    def test_gross_annual_includes_supplement(self) -> None:
        """gross_annual adds second_level * additional_months."""
        result = compute(_req(second_level_allowances=(_SL_100,)))
        # base 1000 * 12 + supplement 100 * 12 = 13200
        assert result.gross_annual == _D("13200.00")

    def test_inps_base_includes_supplement(self) -> None:
        """INPS employee contribution is computed on gross including second-level."""
        base_result = compute(_req())
        sl_result = compute(_req(second_level_allowances=(_SL_100,)))
        # Supplement adds 1200/year to the INPS base; employee rate = 9.19%
        delta = sl_result.inps_employee_annual - base_result.inps_employee_annual
        assert delta == money(_D("1200.00") * _D("0.0919"))

    def test_tfr_includes_supplement(self) -> None:
        """TFR accrual base includes the second-level supplement."""
        base_result = compute(_req())
        sl_result = compute(_req(second_level_allowances=(_SL_100,)))
        delta = sl_result.tfr_annual - base_result.tfr_annual
        assert delta == money(_D("1200.00") / _D("13.5"))


# ---------------------------------------------------------------------------
# Part-time scaling
# ---------------------------------------------------------------------------


class TestSecondLevelPartTime:
    """second_level_monthly is scaled by part_time_pct."""

    def test_part_time_scales_supplement(self) -> None:
        """At 50% PT the supplement is halved."""
        result = compute(
            _req(part_time_pct=_D("0.5"), second_level_allowances=(_SL_100,))
        )
        assert result.second_level_monthly == _D("50.00")


# ---------------------------------------------------------------------------
# months_per_year override
# ---------------------------------------------------------------------------


class TestSecondLevelMonthsPerYear:
    """months_per_year limits the number of months the supplement is paid."""

    def test_months_per_year_1(self) -> None:
        """A supplement paid once a year contributes only 1 month to gross_annual."""
        once_a_year = SupplementaryAllowance(
            code="PDR",
            description="Premio di risultato",
            monthly=_D("300.00"),
            months_per_year=1,
        )
        result = compute(_req(second_level_allowances=(once_a_year,)))
        # base 12000 + prize 300 (1 month only)
        assert result.gross_annual == _D("12300.00")
        # second_level_monthly still shows the full scaled monthly amount
        assert result.second_level_monthly == _D("300.00")


# ---------------------------------------------------------------------------
# Contribution relevance flag
# ---------------------------------------------------------------------------


class TestSecondLevelContributionRelevance:
    """contribution_relevant=False excludes the supplement from the INPS base."""

    def test_not_contribution_relevant_excluded_from_inps(self) -> None:
        """INPS is unchanged when the supplement is not contribution-relevant."""
        exempt = SupplementaryAllowance(
            code="EXEM",
            description="Excluded",
            monthly=_D("100.00"),
            contribution_relevant=False,
        )
        base_result = compute(_req())
        sl_result = compute(_req(second_level_allowances=(exempt,)))
        # Supplement in gross but not in INPS base → INPS unchanged
        assert sl_result.inps_employee_annual == base_result.inps_employee_annual
        assert sl_result.gross_annual > base_result.gross_annual


# ---------------------------------------------------------------------------
# TFR relevance flag
# ---------------------------------------------------------------------------


class TestSecondLevelTfrRelevance:
    """tfr_relevant=False excludes the supplement from the TFR accrual base."""

    def test_not_tfr_relevant_excluded_from_tfr(self) -> None:
        """TFR is unchanged when the supplement is not TFR-relevant."""
        no_tfr = SupplementaryAllowance(
            code="NTFR",
            description="No TFR",
            monthly=_D("100.00"),
            tfr_relevant=False,
        )
        base_result = compute(_req())
        sl_result = compute(_req(second_level_allowances=(no_tfr,)))
        assert sl_result.tfr_annual == base_result.tfr_annual
        assert sl_result.gross_annual > base_result.gross_annual


# ---------------------------------------------------------------------------
# Apprenticeship percentage relevance
# ---------------------------------------------------------------------------


class TestSecondLevelApprenticeshipPct:
    """apprenticeship_pct_relevant controls whether apprenticeship_pct applies."""

    _APPRENTICE = Apprentice(months_elapsed=12)

    def test_pct_relevant_true_applies_apprenticeship_factor(self) -> None:
        """By default the apprenticeship percentage (80%) also scales the supplement."""
        result = compute(
            _req(contract=self._APPRENTICE, second_level_allowances=(_SL_100,))
        )
        # 100 * 1 (PT) * 0.80 (apprenticeship_pct) = 80
        assert result.second_level_monthly == _D("80.00")

    def test_pct_relevant_false_skips_apprenticeship_factor(self) -> None:
        """When apprenticeship_pct_relevant=False only part_time_pct applies."""
        full_value = SupplementaryAllowance(
            code="EDR",
            description="EDR not reduced by apprenticeship %",
            monthly=_D("100.00"),
            apprenticeship_pct_relevant=False,
        )
        result = compute(
            _req(contract=self._APPRENTICE, second_level_allowances=(full_value,))
        )
        # 100 * 1 (PT) — apprenticeship_pct NOT applied
        assert result.second_level_monthly == _D("100.00")


# ---------------------------------------------------------------------------
# Rounding policy
# ---------------------------------------------------------------------------


class TestSecondLevelRoundingPolicy:
    """Single-round after all scaling factors.

    Rounding occurs once after all factors are combined: money(x * pt * app).
    Double-rounding — money(money(x * pt) * app) — diverges at half-cent values.

    The ``0.05 * 0.5 * 0.5`` synthetic probe from the review:
        double-rounding: money(money(0.05 * 0.5) * 0.5)
            = money(money(0.03) * 0.5) = money(0.015) = 0.02
        single-rounding: money(0.05 * 0.5 * 0.5) = money(0.0125) = 0.01

    Tests call ``_scale_second_level`` directly to avoid full payroll plumbing.
    """

    def test_single_round_half_cent_part_time_only(self) -> None:
        """Half-cent value 0.05 at PT=50%: money(0.025) rounds to 0.03."""
        sl = SupplementaryAllowance(
            code="HALF", description="Half-cent probe", monthly=_D("0.05")
        )
        pairs, total = _scale_second_level([sl], _D("0.5"), None)
        # 0.05 * 0.5 = 0.025 → HALF_UP → 0.03
        assert pairs[0][0] == _D("0.03")
        assert total == _D("0.03")

    def test_single_round_half_cent_both_factors(self) -> None:
        """0.05 * 0.5 * 0.5 = 0.0125 → rounds to 0.01 (single-round).

        Double-rounding: money(money(0.025) * 0.5)
        = money(0.03 * 0.5) = money(0.015) = 0.02.
        """
        sl = SupplementaryAllowance(
            code="HALF", description="Half-cent probe", monthly=_D("0.05")
        )
        pairs, total = _scale_second_level([sl], _D("0.5"), _D("0.5"))
        assert pairs[0][0] == _D("0.01")
        assert total == _D("0.01")

    def test_pct_irrelevant_item_not_double_rounded(self) -> None:
        """apprenticeship_pct_relevant=False skips app factor; PT rounds once."""
        sl = SupplementaryAllowance(
            code="EDR",
            description="Not app-scaled",
            monthly=_D("0.05"),
            apprenticeship_pct_relevant=False,
        )
        pairs, total = _scale_second_level([sl], _D("0.5"), _D("0.5"))
        # app factor skipped; 0.05 * 0.5 = 0.025 → 0.03
        assert pairs[0][0] == _D("0.03")
        assert total == _D("0.03")

    def test_multiple_allowances_each_rounded_once(self) -> None:
        """Each allowance is rounded once after all factors; total is also rounded."""
        a1 = SupplementaryAllowance(code="A1", description="A1", monthly=_D("0.05"))
        a2 = SupplementaryAllowance(code="A2", description="A2", monthly=_D("0.05"))
        pairs, total = _scale_second_level([a1, a2], _D("0.5"), _D("0.5"))
        assert pairs[0][0] == _D("0.01")
        assert pairs[1][0] == _D("0.01")
        assert total == _D("0.02")
