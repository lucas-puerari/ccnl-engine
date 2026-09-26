"""Hypothesis property tests for the period-first compute path.

These tests verify structural properties of the period-first engine
(calculate_period) that must hold for any structurally valid input.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from hypothesis import given, settings
from hypothesis import strategies as st

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import TaxYtd

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL_CODES = ["C1", "C3", "D1"]
_YEAR = 2026

_MONTHS = st.integers(min_value=1, max_value=12)
_LEVELS = st.sampled_from(_LEVEL_CODES)


def _req(
    level_code: str,
    month: int = 1,
    irpef_ytd: Decimal = Decimal(0),
) -> PeriodCalculationRequest:
    """Build a :class:`PeriodCalculationRequest` for ``level_code``.

    Returns:
        A request for ``month`` of 2026 with the given YTD state.
    """
    return PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=level_code,
        opening_state=PeriodState(ytd=TaxYearState(tax=TaxYtd(irpef=irpef_ytd))),
    )


class TestPeriodNonNegativity:
    """Gross and net are non-negative for any valid level and month."""

    @given(level_code=_LEVELS, month=_MONTHS)
    @settings(max_examples=36)
    def test_gross_non_negative(self, level_code: str, month: int) -> None:
        """period_gross is >= 0 for every level and month combination."""
        result = calculate_period(_req(level_code=level_code, month=month))
        assert result.period_gross >= Decimal(0)

    @given(level_code=_LEVELS, month=_MONTHS)
    @settings(max_examples=36)
    def test_net_non_negative(self, level_code: str, month: int) -> None:
        """period_net is >= 0 for every level and month combination."""
        result = calculate_period(_req(level_code=level_code, month=month))
        assert result.period_net >= Decimal(0)


class TestPeriodDeterminism:
    """calculate_period is deterministic for identical inputs."""

    @given(level_code=_LEVELS, month=_MONTHS)
    @settings(max_examples=36)
    def test_period_is_deterministic(self, level_code: str, month: int) -> None:
        """Two calls with identical inputs produce identical results."""
        req = _req(level_code=level_code, month=month)
        first = calculate_period(req)
        second = calculate_period(req)
        assert first.period_gross == second.period_gross
        assert first.period_net == second.period_net
        assert first.closing_state == second.closing_state


class TestNetLeGross:
    """period_net <= period_gross for any valid level and month."""

    @given(level_code=_LEVELS, month=_MONTHS)
    @settings(max_examples=36)
    def test_net_le_gross(self, level_code: str, month: int) -> None:
        """Net pay is always <= gross pay (deductions and taxes reduce take-home)."""
        result = calculate_period(_req(level_code=level_code, month=month))
        assert result.period_net <= result.period_gross
