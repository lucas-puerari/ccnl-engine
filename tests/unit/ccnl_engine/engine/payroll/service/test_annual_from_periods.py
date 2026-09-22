"""Unit tests for AnnualPayrollSummary and summarize_payroll_year."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.payroll_state import PayrollState
from ccnl_engine.engine.payroll.domain.period_payroll import (
    AnnualPayrollSummary,
    PayrollYearResult,
    PeriodPayrollResult,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    PeriodPayrollInput,
)
from ccnl_engine.engine.payroll.service.orchestrator import (
    compute_payroll_year,
    summarize_payroll_year,
)

_ZERO = Decimal(0)
_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_AS_OF = date(2026, 1, 1)
_YEAR = 2026
_DEFAULT_PERIODS = tuple(PeriodPayrollInput() for _ in range(12))


def _structural() -> AnnualEstimateInput:
    """Return a minimal structural scenario.

    Returns:
        A minimal :class:`AnnualEstimateInput` with required fields only.
    """
    return AnnualEstimateInput(
        employee=Employee(level_code=_LEVEL),
        employment=Employment(
            ccnl=_CCNL,
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=_AS_OF,
        ),
    )


def _year_result() -> PayrollYearResult:
    """Compute and return a full-year result for tests.

    Returns:
        A :class:`PayrollYearResult` for a standard 2026 year.
    """
    from ccnl_engine.engine.payroll.domain.period_payroll import (  # noqa: PLC0415
        PayrollYearRequest,
    )

    req = PayrollYearRequest(
        structural=_structural(),
        year=_YEAR,
        month_periods=_DEFAULT_PERIODS,
        opening_state=PayrollState.zero(),
    )
    return compute_payroll_year(req)


class TestSummarizePayrollYearReturnType:
    """summarize_payroll_year returns a correctly typed AnnualPayrollSummary."""

    def test_returns_annual_payroll_summary(self) -> None:
        """Return type is AnnualPayrollSummary."""
        result = summarize_payroll_year(_year_result())
        assert isinstance(result, AnnualPayrollSummary)

    def test_summary_is_frozen(self) -> None:
        """AnnualPayrollSummary is immutable."""
        summary = summarize_payroll_year(_year_result())
        with pytest.raises(Exception, match="total_gross"):
            summary.total_gross = Decimal(0)  # type: ignore[misc]

    def test_closing_state_is_payroll_state(self) -> None:
        """closing_state is a PayrollState instance."""
        summary = summarize_payroll_year(_year_result())
        assert isinstance(summary.closing_state, PayrollState)


class TestSummarizePayrollYearAggregation:
    """Monetary totals are correct sums of period figures."""

    def test_total_gross_equals_sum_of_periods(self) -> None:
        """total_gross equals sum of period_gross across all twelve periods."""
        year = _year_result()
        summary = summarize_payroll_year(year)
        expected = sum((p.period_gross for p in year.periods), _ZERO)
        assert summary.total_gross == expected

    def test_total_net_equals_sum_of_periods(self) -> None:
        """total_net equals sum of period_net across all twelve periods."""
        year = _year_result()
        summary = summarize_payroll_year(year)
        expected = sum((p.period_net for p in year.periods), _ZERO)
        assert summary.total_net == expected

    def test_total_employer_cost_equals_sum_of_periods(self) -> None:
        """total_employer_cost equals sum of period_employer_cost."""
        year = _year_result()
        summary = summarize_payroll_year(year)
        expected = sum((p.period_employer_cost for p in year.periods), _ZERO)
        assert summary.total_employer_cost == expected

    def test_total_gross_is_positive(self) -> None:
        """total_gross is strictly greater than zero."""
        summary = summarize_payroll_year(_year_result())
        assert summary.total_gross > _ZERO

    def test_total_net_is_positive(self) -> None:
        """total_net is strictly greater than zero."""
        summary = summarize_payroll_year(_year_result())
        assert summary.total_net > _ZERO

    def test_total_employer_cost_is_positive(self) -> None:
        """total_employer_cost is strictly greater than zero."""
        summary = summarize_payroll_year(_year_result())
        assert summary.total_employer_cost > _ZERO

    def test_employer_cost_exceeds_gross(self) -> None:
        """Total employer cost exceeds total gross (includes INPS employer)."""
        summary = summarize_payroll_year(_year_result())
        assert summary.total_employer_cost > summary.total_gross


class TestSummarizePayrollYearClosingState:
    """closing_state mirrors PayrollYearResult.closing_state."""

    def test_closing_state_matches_year_result(self) -> None:
        """closing_state is the same object as year_result.closing_state."""
        year = _year_result()
        summary = summarize_payroll_year(year)
        assert summary.closing_state is year.closing_state

    def test_gross_ytd_matches_total_gross(self) -> None:
        """closing_state.gross_annual_ytd equals total_gross."""
        year = _year_result()
        summary = summarize_payroll_year(year)
        assert summary.closing_state.gross_annual_ytd == summary.total_gross


class TestSummarizePayrollYearLedger:
    """ledger_entries aggregates entries from all periods in order."""

    def test_ledger_entries_is_tuple(self) -> None:
        """ledger_entries is a tuple."""
        summary = summarize_payroll_year(_year_result())
        assert isinstance(summary.ledger_entries, tuple)

    def test_ledger_entry_count_is_sum_of_period_counts(self) -> None:
        """Total ledger entry count equals sum of per-period entry counts."""
        year = _year_result()
        summary = summarize_payroll_year(year)
        expected_count = sum(len(p.ledger_entries) for p in year.periods)
        assert len(summary.ledger_entries) == expected_count

    def test_ledger_entries_non_empty(self) -> None:
        """ledger_entries is not empty for a standard year."""
        summary = summarize_payroll_year(_year_result())
        assert len(summary.ledger_entries) > 0

    def test_ledger_entries_order_preserved(self) -> None:
        """Entries from January appear before entries from December."""
        year = _year_result()
        summary = summarize_payroll_year(year)
        jan_count = len(year.periods[0].ledger_entries)
        if jan_count > 0 and len(year.periods[11].ledger_entries) > 0:
            first_entry = summary.ledger_entries[0]
            assert first_entry == year.periods[0].ledger_entries[0]


class TestSummarizePayrollYearPublicApi:
    """AnnualPayrollSummary and PayrollEngine.summarize are in the public API."""

    def test_payroll_engine_in_dunder_all(self) -> None:
        """PayrollEngine is listed in ccnl_engine.__all__."""
        import ccnl_engine  # noqa: PLC0415

        assert "PayrollEngine" in ccnl_engine.__all__

    def test_annual_summary_importable_from_ccnl_engine(self) -> None:
        """AnnualPayrollSummary can be imported from ccnl_engine."""
        import ccnl_engine  # noqa: PLC0415

        assert ccnl_engine.AnnualPayrollSummary is AnnualPayrollSummary

    def test_annual_summary_in_dunder_all(self) -> None:
        """AnnualPayrollSummary is listed in ccnl_engine.__all__."""
        import ccnl_engine  # noqa: PLC0415

        assert "AnnualPayrollSummary" in ccnl_engine.__all__


class TestSummarizePayrollYearZeroState:
    """Behaviour when all period monetary values are zero (degenerate case)."""

    def test_zero_periods_give_zero_totals(self) -> None:
        """A PayrollYearResult with zero period values sums to zero."""
        zero_state = PayrollState.zero()
        zero_period = PeriodPayrollResult(
            opening_state=zero_state,
            closing_state=zero_state,
            period_gross=_ZERO,
            period_net=_ZERO,
            period_employer_cost=_ZERO,
            ledger_entries=(),
        )
        year = PayrollYearResult(
            periods=tuple(zero_period for _ in range(12)),
            closing_state=zero_state,
        )
        summary = summarize_payroll_year(year)
        assert summary.total_gross == _ZERO
        assert summary.total_net == _ZERO
        assert summary.total_employer_cost == _ZERO
        assert summary.ledger_entries == ()
