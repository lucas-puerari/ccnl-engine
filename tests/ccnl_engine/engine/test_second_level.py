"""Tests for Scenario.second_level_allowances — second-level bargaining.

Covers:
* guard: negotiated_ral / negotiated_destination_ral mutually exclusive
* basic amount lands in gross_monthly, gross_annual, contribution base, TFR base
* part_time_pct scaling
* months_per_year override (annualised with 1 month instead of additional_months)
* contribution_relevant=False excludes from INPS base
* tfr_relevant=False excludes from TFR base
* apprenticeship_pct_relevant=True (default) reduces amount for pct-track apprentices
* apprenticeship_pct_relevant=False keeps full part-time value for pct-track apprentices
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.compute import Scenario, compute
from ccnl_engine.engine.rounding import money
from ccnl_engine.models.ccnl import CCNL, SupplementaryAllowance
from ccnl_engine.models.employment import Apprentice, Permanent
from tests.conftest import make_ccnl_dict, make_year_rules

_D = Decimal
_DATE = date(2026, 6, 1)
_RULES = make_year_rules()
_CCNL = CCNL.model_validate(make_ccnl_dict())

_SL_100 = SupplementaryAllowance(
    code="ERT",
    description="Elemento territoriale",
    monthly=_D("100.00"),
)


def _sl_scenario(
    employment: object = None,
    **kwargs: object,
) -> Scenario:
    return Scenario(
        level_code="4",
        as_of=_DATE,
        employment=employment if employment is not None else Permanent(),  # type: ignore[arg-type]
        num_employees=50,
        **kwargs,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# Guard: mutually exclusive with negotiated_ral / negotiated_destination_ral
# ---------------------------------------------------------------------------


class TestSecondLevelGuard:
    """second_level_allowances is incompatible with negotiated RAL overrides."""

    def test_negotiated_ral_raises(self) -> None:
        """Combining second_level_allowances with negotiated_ral must raise."""
        with pytest.raises(ValueError, match="negotiated_ral"):
            _sl_scenario(
                second_level_allowances=(_SL_100,),
                negotiated_ral=_D("20000"),
            )

    def test_negotiated_destination_ral_raises(self) -> None:
        """Combining second_level_allowances with negotiated_destination_ral raises."""
        with pytest.raises(ValueError, match="negotiated_ral"):
            _sl_scenario(
                Apprentice(months_elapsed=12),
                second_level_allowances=(_SL_100,),
                negotiated_destination_ral=_D("20000"),
            )


# ---------------------------------------------------------------------------
# Basic wiring: amount appears in gross and all bases
# ---------------------------------------------------------------------------


class TestSecondLevelBasic:
    """second_level_monthly flows into gross, contribution, and TFR bases."""

    def test_second_level_monthly_on_payslip(self) -> None:
        """Payslip.second_level_monthly equals the scaled allowance total."""
        result = compute(
            _CCNL, _RULES, _sl_scenario(second_level_allowances=(_SL_100,))
        )
        assert result.second_level_monthly == _D("100.00")

    def test_zero_when_no_allowances(self) -> None:
        """second_level_monthly is zero when no allowances are supplied."""
        result = compute(_CCNL, _RULES, _sl_scenario())
        assert result.second_level_monthly == _D("0.00")

    def test_gross_monthly_includes_supplement(self) -> None:
        """gross_monthly = base + second_level when no other components."""
        result = compute(
            _CCNL, _RULES, _sl_scenario(second_level_allowances=(_SL_100,))
        )
        expected = money(_D("1000.00") + _D("100.00"))
        assert result.gross_monthly == expected

    def test_gross_annual_includes_supplement(self) -> None:
        """gross_annual adds second_level * additional_months."""
        result = compute(
            _CCNL, _RULES, _sl_scenario(second_level_allowances=(_SL_100,))
        )
        # base 1000 * 12 + supplement 100 * 12 = 13200
        assert result.gross_annual == _D("13200.00")

    def test_inps_base_includes_supplement(self) -> None:
        """INPS employee contribution is computed on gross including second-level."""
        base_result = compute(_CCNL, _RULES, _sl_scenario())
        sl_result = compute(
            _CCNL, _RULES, _sl_scenario(second_level_allowances=(_SL_100,))
        )
        # Supplement adds 1200/year to the INPS base; employee rate = 9.19%
        delta = sl_result.inps_employee_annual - base_result.inps_employee_annual
        assert delta == money(_D("1200.00") * _D("0.0919"))

    def test_tfr_includes_supplement(self) -> None:
        """TFR accrual base includes the second-level supplement."""
        base_result = compute(_CCNL, _RULES, _sl_scenario())
        sl_result = compute(
            _CCNL, _RULES, _sl_scenario(second_level_allowances=(_SL_100,))
        )
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
            _CCNL,
            _RULES,
            _sl_scenario(
                second_level_allowances=(_SL_100,),
                part_time_pct=_D("0.5"),
            ),
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
        result = compute(
            _CCNL, _RULES, _sl_scenario(second_level_allowances=(once_a_year,))
        )
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
        base_result = compute(_CCNL, _RULES, _sl_scenario())
        sl_result = compute(
            _CCNL, _RULES, _sl_scenario(second_level_allowances=(exempt,))
        )
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
        base_result = compute(_CCNL, _RULES, _sl_scenario())
        sl_result = compute(
            _CCNL, _RULES, _sl_scenario(second_level_allowances=(no_tfr,))
        )
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
            _CCNL,
            _RULES,
            _sl_scenario(self._APPRENTICE, second_level_allowances=(_SL_100,)),
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
            _CCNL,
            _RULES,
            _sl_scenario(self._APPRENTICE, second_level_allowances=(full_value,)),
        )
        # 100 * 1 (PT) — apprenticeship_pct NOT applied
        assert result.second_level_monthly == _D("100.00")
