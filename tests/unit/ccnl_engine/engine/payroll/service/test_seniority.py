"""Tests for engine/compute/seniority — tiered and service-gated paths."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.contract.domain.ccnl import CCNL
from ccnl_engine.engine.payroll.service.orchestrator import compute
from tests.helpers import TEST_PROV, make_ccnl_dict
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _RULES,
    _build_ccnl,
    _req,
    _series,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_DEFAULT_CCNL = _build_ccnl()

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[object] = [_RULES]
_mock_surtax: list[SurtaxRules | None] = [None]


@pytest.fixture(autouse=True)
def _patch_loaders(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the three loaders in orchestrator and reset mock state."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_RULES]
    _mock_surtax[:] = [None]
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
        lambda _: _mock_surtax[0],
    )


# ---------------------------------------------------------------------------
# Tiered seniority (SeniorityTier / _resolve_tier_amount)
# ---------------------------------------------------------------------------


def _tiered_ccnl() -> CCNL:
    """Minimal CCNL with a 2-tier seniority ladder on level 4.

    Tier 1: 3 biennial scatti @ 10.00 EUR (months 24, 48, 72).
    Tier 2: 2 quadrennial scatti @ 15.00 EUR (months 120, 168).

    Returns:
        A validated CCNL instance with tiered seniority.
    """
    data = make_ccnl_dict(app_type="")
    data["parameters"]["seniority_increments"] = {
        "cadence_months": 24,
        "maximum_count": 5,
        "amount_by_level": {},
        "provenance": TEST_PROV,
        "tiers": [
            {
                "cadence_months": 24,
                "maximum_count": 3,
                "amount_by_level": {"4": _series("10.00")},
            },
            {
                "cadence_months": 48,
                "maximum_count": 2,
                "amount_by_level": {"4": _series("15.00")},
            },
        ],
    }
    return CCNL.model_validate(data)


class TestTieredSeniority:
    """Tests for tiered-cadence seniority resolution."""

    _TIERED_CCNL = _tiered_ccnl()

    def _compute(
        self,
        seniority_months: int | None = None,
        seniority_count: int | None = None,
        level_code: str = "4",
    ) -> PayrollResult:
        _mock_ccnl[0] = self._TIERED_CCNL
        return compute(
            _req(
                level_code=level_code,
                seniority_months=seniority_months,
                seniority_count=seniority_count,
            )
        ).result

    def test_no_seniority(self) -> None:
        """Zero service months yields zero seniority."""
        r = self._compute(seniority_months=0)
        assert r.seniority_monthly == _D(0)
        assert r.seniority_count == 0

    def test_below_first_tier_cadence(self) -> None:
        """Service months below tier-1 cadence yield no scatti."""
        r = self._compute(seniority_months=23)
        assert r.seniority_monthly == _D(0)

    def test_tier1_one_scatto(self) -> None:
        """Exactly 24 months earns the first tier-1 scatto (10.00 EUR)."""
        r = self._compute(seniority_months=24)
        assert r.seniority_monthly == _D("10.00")
        assert r.seniority_count == 1

    def test_tier1_three_scatti(self) -> None:
        """72 months (= 3x24) earns all tier-1 scatti (30.00 EUR)."""
        r = self._compute(seniority_months=72)
        assert r.seniority_monthly == _D("30.00")
        assert r.seniority_count == 3

    def test_tier2_first_scatto(self) -> None:
        """120 months (72 tier-1 + 48 tier-2) earns 1 tier-2 scatto."""
        r = self._compute(seniority_months=120)
        assert r.seniority_monthly == _D("45.00")  # 3x10 + 1x15
        assert r.seniority_count == 4

    def test_tier2_both_scatti(self) -> None:
        """168 months earns all 5 scatti (30 + 30 = 60 EUR)."""
        r = self._compute(seniority_months=168)
        assert r.seniority_monthly == _D("60.00")  # 3x10 + 2x15
        assert r.seniority_count == 5

    def test_beyond_maximum_capped(self) -> None:
        """Extra service months beyond max are ignored."""
        r = self._compute(seniority_months=9999)
        assert r.seniority_monthly == _D("60.00")
        assert r.seniority_count == 5

    def test_count_input_tier_distribution(self) -> None:
        """Explicit seniority_count distributes across tiers sequentially."""
        # count=4: tier1 fills (3) + tier2 takes 1 -> 3x10 + 1x15 = 45
        r = self._compute(seniority_count=4)
        assert r.seniority_monthly == _D("45.00")
        assert r.seniority_count == 4

    def test_level_not_in_tier_yields_zero(self) -> None:
        """A level absent from a tier's amount_by_level contributes zero."""
        # Level 2 has no entry in either tier — seniority must be zero.
        r = self._compute(seniority_months=200, level_code="2")
        assert r.seniority_monthly == _D(0)


# ---------------------------------------------------------------------------
# Excluded categories
# ---------------------------------------------------------------------------


class TestExcludedCategories:
    """excluded_categories guard zeroes seniority for matching categories."""

    def test_excluded_category_zeroes_seniority(self) -> None:
        """Workers with category in excluded_categories accrue no scatti."""
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.2.category": "operaio",
            "parameters.seniority_increments.excluded_categories": ["operaio"],
        })
        r = compute(_req(seniority_months=120))
        assert r.seniority_count == 0
        assert r.seniority_monthly == _D("0.00")


# ---------------------------------------------------------------------------
# Service-gated allowances (Allowance.service_months_threshold)
# ---------------------------------------------------------------------------


def _service_gated_ccnl() -> CCNL:
    """Minimal CCNL with two service-gated annual allowances on level 4.

    Allowance A: threshold=60 months, 50 EUR/year (months_per_year=1).
    Allowance B: threshold=120 months, 150 EUR/year (months_per_year=1).

    Returns:
        A validated CCNL instance with service-gated allowances.
    """
    data = make_ccnl_dict(app_type="")
    data["parameters"]["seniority_increments"] = {
        "cadence_months": 24,
        "maximum_count": 0,
        "amount_by_level": {},
        "provenance": TEST_PROV,
    }
    data["levels"][2]["fixed_allowances"] = [
        {
            "code": "PREMIO_5YR",
            "description": "Premio 5 anni",
            "monthly": _series("50.00"),
            "months_per_year": 1,
            "service_months_threshold": 60,
            "provenance": TEST_PROV,
        },
        {
            "code": "PREMIO_10YR",
            "description": "Premio 10 anni",
            "monthly": _series("150.00"),
            "months_per_year": 1,
            "service_months_threshold": 120,
            "provenance": TEST_PROV,
        },
    ]
    return CCNL.model_validate(data)


class TestServiceGatedAllowances:
    """Tests for Allowance.service_months_threshold gating."""

    _GATED_CCNL = _service_gated_ccnl()

    def _compute(
        self,
        seniority_months: int | None = None,
        seniority_count: int | None = None,
    ) -> PayrollResult:
        _mock_ccnl[0] = self._GATED_CCNL
        return compute(
            _req(
                seniority_months=seniority_months,
                seniority_count=seniority_count,
            )
        ).result

    def test_below_threshold_no_allowance(self) -> None:
        """Below the 5yr threshold no allowance is included."""
        r = self._compute(seniority_months=59)
        assert r.allowances_monthly == _D(0)

    def test_at_first_threshold(self) -> None:
        """At 60 months the 5yr premio (50 EUR) is active."""
        r = self._compute(seniority_months=60)
        assert r.allowances_monthly == _D("50.00")

    def test_at_second_threshold(self) -> None:
        """At 120 months both premi are active (50 + 150 = 200 monthly)."""
        r = self._compute(seniority_months=120)
        assert r.allowances_monthly == _D("200.00")

    def test_no_seniority_months_excludes_gated(self) -> None:
        """With only seniority_count, gated allowances are excluded."""
        r = self._compute(seniority_count=0)
        assert r.allowances_monthly == _D(0)

    def test_annual_gross_uses_months_per_year(self) -> None:
        """Annual gross reflects months_per_year=1 (not x14 additional months)."""
        r_with = self._compute(seniority_months=60)
        r_without = self._compute(seniority_months=59)
        # Annual difference must be 50x1, not 50x14
        diff = r_with.gross_annual - r_without.gross_annual
        assert diff == _D("50.00")
