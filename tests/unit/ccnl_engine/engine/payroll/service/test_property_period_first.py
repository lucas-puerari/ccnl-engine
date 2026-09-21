"""Hypothesis property tests for the estimate_period_effects computation path."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from hypothesis import given
from hypothesis import strategies as st

from ccnl_engine.engine.payroll.domain.scenario import PeriodPayrollInput, TaxPeriod
from ccnl_engine.engine.payroll.service.orchestrator import (
    estimate_annual,
    estimate_period_effects,
)
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _RULES,
    _build_ccnl,
    _req,
)

_LEVEL_CODES = ["2", "3", "4"]
_DATE = date(2026, 6, 1)
_TAX_PERIOD = TaxPeriod(
    start=_DATE,
    end=date(2026, 12, 31),
    eligible_work_days=(date(2026, 12, 31) - _DATE).days + 1,
)

_DEFAULT_CCNL = _build_ccnl()
_MOCK_REPO = MagicMock()
_MOCK_REPO.load_ccnl.return_value = _DEFAULT_CCNL
_MOCK_REPO.load_year_rules.return_value = _RULES
_MOCK_REPO.load_surtax_rules.return_value = None
_MOCK_REPO.load_capability_catalog.return_value = None

_EMPTY_PERIOD = PeriodPayrollInput(tax_period=_TAX_PERIOD)


class TestPeriodNonNegativity:
    """Net and gross are non-negative with any structural inputs on the period path."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=10),
    )
    def test_gross_and_net_non_negative(
        self, level_code: str, seniority_count: int
    ) -> None:
        """gross_annual and net_annual are >= 0 via estimate_period_effects."""
        calc = estimate_period_effects(
            _req(level_code=level_code, seniority_count=seniority_count),
            _EMPTY_PERIOD,
            repo=_MOCK_REPO,
        )
        assert calc.result.earnings.gross_annual >= Decimal(0)
        assert calc.result.net_annual >= Decimal(0)


class TestPeriodEffectsEquivalence:
    """Empty period input yields the same structural figures as estimate_annual."""

    @given(level_code=st.sampled_from(_LEVEL_CODES))
    def test_empty_period_gross_matches_annual(self, level_code: str) -> None:
        """estimate_period_effects with no events equals estimate_annual gross."""
        annual = estimate_annual(_req(level_code=level_code), repo=_MOCK_REPO)
        period = estimate_period_effects(
            _req(level_code=level_code),
            _EMPTY_PERIOD,
            repo=_MOCK_REPO,
        )
        assert (
            period.result.earnings.gross_annual == annual.result.earnings.gross_annual
        )

    @given(level_code=st.sampled_from(_LEVEL_CODES))
    def test_empty_period_employer_cost_matches_annual(self, level_code: str) -> None:
        """estimate_period_effects with no events equals annual employer cost."""
        annual = estimate_annual(_req(level_code=level_code), repo=_MOCK_REPO)
        period = estimate_period_effects(
            _req(level_code=level_code),
            _EMPTY_PERIOD,
            repo=_MOCK_REPO,
        )
        assert (
            period.result.employer_cost.employer_cost_annual
            == annual.result.employer_cost.employer_cost_annual
        )


class TestPeriodDeterminism:
    """estimate_period_effects is deterministic for identical inputs."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=10),
    )
    def test_period_effects_is_deterministic(
        self, level_code: str, seniority_count: int
    ) -> None:
        """Two calls with identical inputs produce identical results."""
        req = _req(level_code=level_code, seniority_count=seniority_count)
        first = estimate_period_effects(req, _EMPTY_PERIOD, repo=_MOCK_REPO)
        second = estimate_period_effects(req, _EMPTY_PERIOD, repo=_MOCK_REPO)
        assert first.result == second.result


class TestPeriodNetLeGross:
    """net_annual <= gross_annual in the period path."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=10),
    )
    def test_net_le_gross(self, level_code: str, seniority_count: int) -> None:
        """net_annual <= gross_annual via estimate_period_effects."""
        calc = estimate_period_effects(
            _req(level_code=level_code, seniority_count=seniority_count),
            _EMPTY_PERIOD,
            repo=_MOCK_REPO,
        )
        assert calc.result.net_annual <= calc.result.earnings.gross_annual
