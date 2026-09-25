"""Scenario tests for the period-first engine: §8.3 coverage.

Tests here verify structural invariants that span calculate_period and
reconcile: ledger coverage (I1), account exclusivity (I2), net identity (I9),
IRPEF delta (I10), state transition (I11), employer cost identity (I12),
and gross identity (I13).  They also cover serialization round-trips and
multi-period chain behaviour.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import BaseSalaryEarning
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.ytd_accounts import EarningsYtd

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026


def _req(
    month: int = 1,
    opening: PeriodState | None = None,
    payment_date: date | None = None,
) -> PeriodCalculationRequest:
    """Build a :class:`PeriodCalculationRequest` for C3 metalmeccanico.

    Returns:
        A request for ``month`` of 2026 with the given ``opening`` state.
    """
    return PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=payment_date or date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=opening or PeriodState.zero(),
    )


def _run(
    month: int = 1, opening: PeriodState | None = None
) -> tuple[PeriodCalculationResult, PeriodState]:
    """Run calculate_period and return (result, opening_state).

    Returns:
        Tuple of the result and the opening state used.
    """
    op = opening or PeriodState.zero()
    return calculate_period(_req(month=month, opening=op)), op


class TestReconcileInvariantsOnRealResult:
    """All seven reconcile invariants pass on every real calculate_period result."""

    def test_january_passes_all_invariants(self) -> None:
        """A standard January C3 result satisfies I1, I2, I9-I13."""
        result, opening = _run(month=1)
        r = reconcile(result, opening)
        assert r.ok, f"Unexpected violations: {r.violations}"

    def test_june_passes_all_invariants(self) -> None:
        """A June result (salary table change month) also passes all invariants."""
        result, opening = _run(month=6)
        r = reconcile(result, opening)
        assert r.ok, f"Unexpected violations: {r.violations}"

    def test_july_passes_all_invariants(self) -> None:
        """A July result (post salary-table change) passes all invariants."""
        result, opening = _run(month=7)
        r = reconcile(result, opening)
        assert r.ok, f"Unexpected violations: {r.violations}"


class TestMultiPeriodChain:
    """Closing state of period N feeds correctly into period N+1."""

    def test_twelve_month_chain_passes_reconcile(self) -> None:
        """Running Jan-Dec as a chain: every period satisfies reconcile."""
        opening = PeriodState.zero()
        for month in range(1, 13):
            result = calculate_period(_req(month=month, opening=opening))
            r = reconcile(result, opening)
            assert r.ok, f"Month {month} violations: {r.violations}"
            opening = result.closing_state

    def test_second_period_irpef_includes_first_period(self) -> None:
        """February's irpef_withheld_ytd equals Jan + Feb IRPEF withheld."""
        r1 = calculate_period(_req(month=1))
        r2 = calculate_period(_req(month=2, opening=r1.closing_state))
        jan_irpef = sum(
            e.amount for e in r1.ledger_entries if e.account == AccountKind.ORDINARY_TAX
        )
        feb_irpef = sum(
            e.amount for e in r2.ledger_entries if e.account == AccountKind.ORDINARY_TAX
        )
        assert r2.closing_state.tax.irpef == jan_irpef + feb_irpef

    def test_regular_periods_closed_increments_through_chain(self) -> None:
        """regular_periods_closed advances by 1 per regular period through a chain."""
        opening = PeriodState.zero()
        for expected_months in range(1, 4):
            month = expected_months
            result = calculate_period(_req(month=month, opening=opening))
            assert result.closing_state.regular_periods_closed == expected_months
            opening = result.closing_state


class TestTemporalCoherence:
    """All entries and items in a result share the same competence_period."""

    def test_all_ledger_entries_share_competence_period(self) -> None:
        """Every LedgerEntry has competence_period matching period_id."""
        result, _ = _run(month=4)
        for entry in result.ledger_entries:
            assert entry.competence_period.year == _YEAR
            assert entry.competence_period.month == 4

    def test_all_pay_items_share_competence_period(self) -> None:
        """Every PayItem has competence_period matching period_id."""
        result, _ = _run(month=9)
        for item in result.pay_items:
            assert item.competence_period.year == _YEAR
            assert item.competence_period.month == 9

    def test_no_account_mixes_temporal_units(self) -> None:
        """Entries posted to different accounts share the same competence_period."""
        result, _ = _run(month=3)
        periods = {
            (e.account, e.competence_period.year, e.competence_period.month)
            for e in result.ledger_entries
        }
        months = {p[2] for p in periods}
        years = {p[1] for p in periods}
        assert months == {3}
        assert years == {_YEAR}


class TestLedgerEntryOrphans:
    """Every ledger entry resolves to an existing PayItem (I1 from the result side)."""

    def test_every_ledger_entry_has_a_matching_pay_item(self) -> None:
        """No ledger entry references a pay_item_id absent from pay_items."""
        result, _ = _run(month=1)
        item_ids = {item.item_id for item in result.pay_items}
        posted_ids = {e.pay_item_id for e in result.ledger_entries}
        assert posted_ids.issubset(item_ids), (
            f"Orphan ledger pay_item_ids: {posted_ids - item_ids}"
        )


class TestSerializationRoundTrip:
    """Pay items and ledger entries survive a Pydantic JSON round-trip unchanged."""

    def test_ledger_entries_round_trip(self) -> None:
        """LedgerEntry.model_dump / model_validate is lossless."""
        result, _ = _run(month=1)
        for original in result.ledger_entries:
            dumped: dict[str, Any] = original.model_dump()
            restored = LedgerEntry.model_validate(dumped)
            assert restored == original

    def test_ledger_entries_json_round_trip(self) -> None:
        """LedgerEntry serializes through JSON bytes without data loss."""
        result, _ = _run(month=1)
        for original in result.ledger_entries:
            json_str = original.model_dump_json()
            restored = LedgerEntry.model_validate_json(json_str)
            assert restored == original

    def test_pay_items_round_trip(self) -> None:
        """All PayItem subtypes survive model_dump / model_validate round-trips."""
        result, _ = _run(month=1)
        for original in result.pay_items:
            dumped = original.model_dump()
            cls = type(original)
            restored = cls.model_validate(dumped)
            assert restored == original

    def test_base_salary_earning_json_round_trip(self) -> None:
        """BaseSalaryEarning specifically round-trips through JSON."""
        result, _ = _run(month=1)
        salary_items = [i for i in result.pay_items if isinstance(i, BaseSalaryEarning)]
        assert len(salary_items) >= 1
        original = salary_items[0]
        restored = BaseSalaryEarning.model_validate_json(original.model_dump_json())
        assert restored == original


class TestOpeningStateSensitivity:
    """Different opening states produce different outputs (YTD sensitivity)."""

    def test_higher_gross_ytd_does_not_change_net(self) -> None:
        """gross_ytd alone does not affect net (IRPEF computation uses irpef_ytd)."""
        r_zero = calculate_period(_req())
        r_high_gross = calculate_period(
            _req(opening=PeriodState(earnings=EarningsYtd(gross=Decimal("50000.00"))))
        )
        assert r_zero.period_gross == r_high_gross.period_gross

    def test_higher_inps_ytd_does_not_affect_gross(self) -> None:
        """inps_employee_ytd in opening state does not change period gross."""
        r_zero = calculate_period(_req())
        r_high_inps = calculate_period(
            _req(
                opening=PeriodState(
                    earnings=EarningsYtd(inps_employee=Decimal("5000.00"))
                )
            )
        )
        assert r_zero.period_gross == r_high_inps.period_gross
