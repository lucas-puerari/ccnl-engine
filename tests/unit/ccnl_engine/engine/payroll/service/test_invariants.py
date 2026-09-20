"""Hypothesis property tests for economic invariants in the payroll engine."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from hypothesis import assume, given
from hypothesis import strategies as st

from ccnl_engine.engine.payroll.domain.employment import Apprentice
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual as compute
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _RULES,
    _build_ccnl,
    _req,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.calculation import Calculation

_DEFAULT_CCNL = _build_ccnl()
_LEVEL_CODES = ["2", "3", "4"]
_SENIORITY_MAX = 10

_MOCK_REPO = MagicMock()
_MOCK_REPO.load_ccnl.return_value = _DEFAULT_CCNL
_MOCK_REPO.load_year_rules.return_value = _RULES
_MOCK_REPO.load_surtax_rules.return_value = None


def _compute(scenario: object) -> Calculation:
    """Run compute() with the test CCNL and rules mocked in.

    Returns:
        Calculation result with all gross, net, and cost figures.
    """
    with patch(
        "ccnl_engine.engine.payroll.service.pipeline._default_repo",
        new=_MOCK_REPO,
    ):
        return compute(scenario)  # type: ignore[arg-type]


class TestNonNegativity:
    """gross_annual and net_annual are never negative."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_gross_and_net_are_non_negative(
        self, level_code: str, seniority_count: int
    ) -> None:
        """Gross and net annual figures are always non-negative."""
        scenario = _req(level_code=level_code, seniority_count=seniority_count)
        result = _compute(scenario).result
        assert result.earnings.gross_annual >= Decimal(0)
        assert result.net_annual >= Decimal(0)


class TestDecimalQuantization:
    """All monetary outputs are quantized to two decimal places."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_monetary_outputs_have_two_decimal_places(
        self, level_code: str, seniority_count: int
    ) -> None:
        """gross_annual and net_annual have at most two decimal places."""
        scenario = _req(level_code=level_code, seniority_count=seniority_count)
        result = _compute(scenario).result
        assert result.earnings.gross_annual == (
            result.earnings.gross_annual.quantize(Decimal("0.01"))
        )
        assert result.net_annual == result.net_annual.quantize(Decimal("0.01"))
        assert result.earnings.gross_monthly == (
            result.earnings.gross_monthly.quantize(Decimal("0.01"))
        )


class TestNetLeGross:
    """Net annual pay never exceeds gross annual pay."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_net_le_gross(self, level_code: str, seniority_count: int) -> None:
        """net_annual <= gross_annual: taxes and contributions are non-negative."""
        scenario = _req(level_code=level_code, seniority_count=seniority_count)
        result = _compute(scenario).result
        assert result.net_annual <= result.earnings.gross_annual


class TestSeniorityMonotonicity:
    """Gross pay is non-decreasing as seniority increases (level 4 only)."""

    @given(
        low=st.integers(min_value=0, max_value=_SENIORITY_MAX),
        high=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_gross_non_decreasing_in_seniority(self, low: int, high: int) -> None:
        """More seniority steps yield equal or greater gross annual pay on level 4."""
        assume(low < high)
        low_result = _compute(_req(level_code="4", seniority_count=low)).result
        high_result = _compute(_req(level_code="4", seniority_count=high)).result
        assert high_result.earnings.gross_annual >= low_result.earnings.gross_annual


class TestLevelMonotonicity:
    """Higher-order levels yield equal or greater gross pay than lower ones."""

    def test_level4_gross_ge_level3(self) -> None:
        """Level 4 gross >= level 3 gross at zero seniority."""
        r4 = _compute(_req(level_code="4", seniority_count=0)).result
        r3 = _compute(_req(level_code="3", seniority_count=0)).result
        assert r4.earnings.gross_annual >= r3.earnings.gross_annual

    def test_level3_gross_ge_level2(self) -> None:
        """Level 3 gross >= level 2 gross at zero seniority."""
        r3 = _compute(_req(level_code="3", seniority_count=0)).result
        r2 = _compute(_req(level_code="2", seniority_count=0)).result
        assert r3.earnings.gross_annual >= r2.earnings.gross_annual


class TestDeterminism:
    """Same inputs always produce the same outputs."""

    @given(
        level_code=st.sampled_from(_LEVEL_CODES),
        seniority_count=st.integers(min_value=0, max_value=_SENIORITY_MAX),
    )
    def test_compute_is_deterministic(
        self, level_code: str, seniority_count: int
    ) -> None:
        """Two calls with the same scenario return equal gross and net figures."""
        scenario = _req(level_code=level_code, seniority_count=seniority_count)
        r1 = _compute(scenario).result
        r2 = _compute(scenario).result
        assert r1.earnings.gross_annual == r2.earnings.gross_annual
        assert r1.net_annual == r2.net_annual


class TestPartTimeScaling:
    """Part-time gross is no greater than full-time gross."""

    @given(numerator=st.integers(min_value=1, max_value=99))
    def test_part_time_gross_le_full_time(self, numerator: int) -> None:
        """Part-time ratio < 1 yields gross_annual <= full-time gross_annual."""
        ratio = Decimal(numerator) / Decimal(100)
        full = _compute(_req(level_code="4", seniority_count=0)).result
        part = _compute(
            _req(level_code="4", seniority_count=0, part_time_ratio=ratio)
        ).result
        assert part.earnings.gross_annual <= full.earnings.gross_annual


class TestApprenticePayLeDestination:
    """Apprentice gross is no greater than the destination level permanent gross."""

    def test_apprentice_gross_le_destination(self) -> None:
        """Apprentice at 80% of level 4 has gross_annual <= permanent level 4 gross."""
        app_scenario = _req(
            level_code="4", seniority_count=0, contract=Apprentice(months_elapsed=0)
        )
        app_result = _compute(app_scenario).result
        perm_result = _compute(_req(level_code="4", seniority_count=0)).result
        assert app_result.earnings.gross_annual <= perm_result.earnings.gross_annual
