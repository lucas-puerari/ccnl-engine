"""Unit tests for close(): pure state-transition from period calculation result."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.engine.payroll.domain.ledger import AccountKind
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.close_period import close
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest, PeriodState
from ccnl_engine.payroll.domain.state import PayrollState

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_ZERO = Decimal(0)


def _req(
    month: int = 1,
    opening: PeriodState | None = None,
) -> PeriodCalculationRequest:
    """Build a minimal PeriodCalculationRequest for C3 metalmeccanico.

    Returns:
        A :class:`PeriodCalculationRequest` for ``month`` of 2026.
    """
    return PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=opening or PeriodState.zero(),
    )


class TestCloseBasic:
    """close() produces a valid PayrollState from an opening state and a result."""

    def test_returns_payroll_state(self) -> None:
        """close() returns a PayrollState instance."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        assert isinstance(close(opening, result), PayrollState)

    def test_tax_year_preserved(self) -> None:
        """tax_year is carried over from the opening state unchanged."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        assert closing.tax_year == _YEAR

    def test_periods_closed_increments(self) -> None:
        """periods_closed increases by exactly one per call."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        assert closing.periods_closed == 1

    def test_revision_id_reflects_periods_closed(self) -> None:
        """revision_id encodes tax_year and the new periods_closed count."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        assert closing.revision_id == "ytd-2026-p01"

    def test_source_period_ids_appended(self) -> None:
        """source_period_ids gains the result's period_id."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req(month=3))
        closing = close(opening, result)
        assert closing.source_period_ids == (PeriodId(year=_YEAR, month=3),)


class TestCloseContributiveAccumulation:
    """close() accumulates contributive amounts from ledger entries."""

    def test_gross_ytd_accumulates(self) -> None:
        """gross_ytd grows by the CASH_EARNINGS ledger amount each period."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        assert closing.contributive.gross_ytd == result.period_gross

    def test_inps_employee_ytd_accumulates(self) -> None:
        """inps_employee_ytd accumulates the EMPLOYEE_CONTRIBUTIONS ledger amount."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        expected = sum(
            (
                e.amount
                for e in result.ledger_entries
                if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
            ),
            _ZERO,
        )
        assert closing.contributive.inps_employee_ytd == expected

    def test_inps_employer_ytd_accumulates(self) -> None:
        """inps_employer_ytd accumulates the EMPLOYER_CONTRIBUTIONS ledger amount."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        expected = sum(
            (
                e.amount
                for e in result.ledger_entries
                if e.account == AccountKind.EMPLOYER_CONTRIBUTIONS
            ),
            _ZERO,
        )
        assert closing.contributive.inps_employer_ytd == expected

    def test_tfr_ytd_accumulates(self) -> None:
        """tfr_ytd accumulates the TFR_ACCRUAL ledger amount."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        expected = sum(
            (
                e.amount
                for e in result.ledger_entries
                if e.account == AccountKind.TFR_ACCRUAL
            ),
            _ZERO,
        )
        assert closing.contributive.tfr_ytd == expected

    def test_inail_employer_ytd_unchanged(self) -> None:
        """inail_employer_ytd carries over from opening (not in vertical slice)."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        assert closing.contributive.inail_employer_ytd == _ZERO


class TestCloseFiscalAccumulation:
    """close() accumulates fiscal amounts from ledger entries."""

    def test_irpef_withheld_ytd_accumulates(self) -> None:
        """irpef_withheld_ytd accumulates the ORDINARY_TAX ledger amount."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        expected = sum(
            (
                e.amount
                for e in result.ledger_entries
                if e.account == AccountKind.ORDINARY_TAX
            ),
            _ZERO,
        )
        assert closing.fiscal.irpef_withheld_ytd == expected

    def test_trattamento_integrativo_zero_when_no_credits(self) -> None:
        """trattamento_integrativo_ytd stays zero when no CREDITS entry exists."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        # C3 metalmeccanico earns too much for trattamento; no CREDITS entry
        has_credits = any(
            e.account == AccountKind.CREDITS for e in result.ledger_entries
        )
        closing = close(opening, result)
        if not has_credits:
            assert closing.fiscal.trattamento_integrativo_ytd == _ZERO

    def test_taxable_income_ytd_unchanged(self) -> None:
        """taxable_income_ytd carries over from opening (not in vertical slice)."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        assert closing.fiscal.taxable_income_ytd == _ZERO

    def test_irpef_withheld_grows_normatively(self) -> None:
        """irpef_withheld_ytd must not decrease across two sequential periods."""
        opening = PayrollState.zero(_YEAR)
        r1 = calculate_period(_req(month=1))
        c1 = close(opening, r1)
        r2 = calculate_period(_req(month=2, opening=r1.closing_state))
        c2 = close(c1, r2)
        assert c2.fiscal.irpef_withheld_ytd >= c1.fiscal.irpef_withheld_ytd


class TestCloseChaining:
    """close() composes correctly across multiple periods."""

    def test_two_periods_double_the_gross(self) -> None:
        """gross_ytd after two identical periods equals twice the period gross."""
        opening = PayrollState.zero(_YEAR)
        r1 = calculate_period(_req(month=1))
        c1 = close(opening, r1)
        r2 = calculate_period(_req(month=2, opening=r1.closing_state))
        c2 = close(c1, r2)
        assert c2.contributive.gross_ytd == r1.period_gross + r2.period_gross

    def test_source_period_ids_grows_per_period(self) -> None:
        """source_period_ids collects one entry per closed period."""
        opening = PayrollState.zero(_YEAR)
        r1 = calculate_period(_req(month=1))
        c1 = close(opening, r1)
        r2 = calculate_period(_req(month=2, opening=r1.closing_state))
        c2 = close(c1, r2)
        assert len(c2.source_period_ids) == 2
        assert c2.source_period_ids[0] == PeriodId(year=_YEAR, month=1)
        assert c2.source_period_ids[1] == PeriodId(year=_YEAR, month=2)

    def test_periods_closed_after_two_calls(self) -> None:
        """periods_closed equals the number of close() calls made."""
        opening = PayrollState.zero(_YEAR)
        r1 = calculate_period(_req(month=1))
        c1 = close(opening, r1)
        r2 = calculate_period(_req(month=2, opening=r1.closing_state))
        c2 = close(c1, r2)
        assert c2.periods_closed == 2

    def test_leave_state_unchanged_across_periods(self) -> None:
        """Leave state carries over from opening unchanged (not in vertical slice)."""
        opening = PayrollState.zero(_YEAR)
        result = calculate_period(_req())
        closing = close(opening, result)
        assert closing.leave == opening.leave
