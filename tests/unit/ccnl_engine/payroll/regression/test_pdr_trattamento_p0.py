"""Regression tests for the two P0 normative bugs fixed in this PR.

T01 — PdR 6,000 EUR with annual cap 5,000 EUR:
    The 1,000 EUR excess must return to the ordinary IRPEF base.
    Source: L. 199/2025 art. 1 co. 9.

T03 — Second PdR bonus with partially consumed plafond:
    Only the remaining headroom is eligible; the excess is ordinary.
    Source: L. 199/2025 art. 1 co. 9 — cumulative 5,000 EUR cap.

T04 — Trattamento integrativo: no over-recovery across a full year.
    Once the recognized credit has been fully recovered,
    credit_recovered_ytd must never exceed credit_recognized_ytd.
    Source: D.L. 3/2020 art. 1 co. 3.

T-I16 — TrattamentoAccount invariant: recovered > recognized raises ValueError
    at construction, preventing the invalid state from being representable.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.credit_accounts import TrattamentoAccount
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.events import BonusEvent
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult

_CCNL_METAL = "metalmeccanico-federmeccanica.json"
_LEVEL_C3 = "C3"
_CCNL_PORTIERI = "portieri-fabbricati-confedilizia.json"
_LEVEL_B5 = "B5"
_YEAR = 2026
_ZERO = Decimal(0)

_PRIOR_INCOME = Decimal("25000.00")


def _req_metal(
    month: int,
    opening: PeriodState | None = None,
    events: tuple[object, ...] = (),
    income: Decimal | None = _PRIOR_INCOME,
) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        prior_year=PriorYearTaxFacts(employment_income=income),
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL_METAL,
        level_code=_LEVEL_C3,
        opening_state=opening or PeriodState.zero(),
        events=events,  # type: ignore[arg-type]
    )


def _req_portieri(
    month: int,
    opening: PeriodState | None = None,
    events: tuple[object, ...] = (),
    income: Decimal | None = _PRIOR_INCOME,
) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        prior_year=PriorYearTaxFacts(employment_income=income),
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL_PORTIERI,
        level_code=_LEVEL_B5,
        opening_state=opening or PeriodState.zero(),
        events=events,  # type: ignore[arg-type]
    )


def _sum_account(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum((e.amount for e in result.ledger_entries if e.account == account), _ZERO)


class TestT01PdRExcessReturnsToIrpef:
    """T01: PdR 6,000 EUR with 5,000 EUR annual cap."""

    def test_substitute_tax_capped_at_5000(self) -> None:
        """SUBSTITUTE_TAX must be 50.00 (5,000 EUR * 1%), not 60.00."""
        bonus = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("6000.00"),
            kind="productivity_bonus",
        )
        result = calculate_period(_req_metal(1, events=(bonus,)))
        sub_tax = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
        assert sub_tax == Decimal("50.00"), (
            f"Expected SUBSTITUTE_TAX=50.00 (5,000 * 1%); got {sub_tax}. "
            "The 1,000 EUR excess must not be taxed at the substitute rate."
        )

    def test_pdr_ytd_capped_at_5000(self) -> None:
        """pdr_ytd must record 5,000 EUR eligible, not 6,000 EUR gross."""
        bonus = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("6000.00"),
            kind="productivity_bonus",
        )
        result = calculate_period(_req_metal(1, events=(bonus,)))
        assert result.closing_state.ytd.fringe.pdr == Decimal("5000.00"), (
            f"pdr_ytd must be 5,000 (cap); got {result.closing_state.ytd.fringe.pdr}."
        )

    def test_excess_increases_ordinary_irpef_base(self) -> None:
        """Ordinary IRPEF must be higher for a 6,000 EUR PdR than for 5,000 EUR."""
        bonus_5k = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("5000.00"),
            kind="productivity_bonus",
        )
        bonus_6k = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("6000.00"),
            kind="productivity_bonus",
        )
        result_5k = calculate_period(_req_metal(1, events=(bonus_5k,)))
        result_6k = calculate_period(_req_metal(1, events=(bonus_6k,)))
        irpef_5k = _sum_account(result_5k, AccountKind.ORDINARY_TAX)
        irpef_6k = _sum_account(result_6k, AccountKind.ORDINARY_TAX)
        assert irpef_6k > irpef_5k, (
            f"A 6,000 EUR PdR must produce higher IRPEF than 5,000 EUR "
            f"because the 1,000 EUR excess returns to the ordinary base. "
            f"Got irpef_5k={irpef_5k}, irpef_6k={irpef_6k}."
        )

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants including I16 must pass."""
        bonus = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("6000.00"),
            kind="productivity_bonus",
        )
        opening = PeriodState.zero()
        result = calculate_period(_req_metal(1, opening=opening, events=(bonus,)))
        rec = reconcile(result, opening)
        assert rec.ok, f"Reconcile violated: {rec.violations}"


class TestT03SecondPdRPartialPlafond:
    """T03: second PdR with partially consumed plafond."""

    def test_first_pdr_fully_eligible(self) -> None:
        """First 3,000 EUR PdR is fully eligible: sub_tax = 30.00."""
        bonus = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("3000.00"),
            kind="productivity_bonus",
        )
        result = calculate_period(_req_metal(1, events=(bonus,)))
        sub_tax = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
        assert sub_tax == Decimal("30.00")
        assert result.closing_state.ytd.fringe.pdr == Decimal("3000.00")

    def test_second_pdr_only_headroom_eligible(self) -> None:
        """Second 3,000 EUR PdR: only 2,000 EUR headroom left, sub_tax = 20.00."""
        bonus1 = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("3000.00"),
            kind="productivity_bonus",
        )
        r1 = calculate_period(_req_metal(1, events=(bonus1,)))

        bonus2 = BonusEvent(
            event_date=date(_YEAR, 2, 15),
            amount=Decimal("3000.00"),
            kind="productivity_bonus",
        )
        r2 = calculate_period(_req_metal(2, opening=r1.closing_state, events=(bonus2,)))
        sub_tax = _sum_account(r2, AccountKind.SUBSTITUTE_TAX)
        assert sub_tax == Decimal("20.00"), (
            f"Expected 20.00 (2,000 EUR * 1%); got {sub_tax}. "
            "Only 2,000 EUR headroom remains after first period."
        )
        assert r2.closing_state.ytd.fringe.pdr == Decimal("5000.00")

    def test_second_pdr_excess_in_ordinary_base(self) -> None:
        """The 1,000 EUR excess in period 2 must raise ordinary IRPEF vs zero-bonus."""
        bonus1 = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("3000.00"),
            kind="productivity_bonus",
        )
        r1 = calculate_period(_req_metal(1, events=(bonus1,)))

        bonus2 = BonusEvent(
            event_date=date(_YEAR, 2, 15),
            amount=Decimal("3000.00"),
            kind="productivity_bonus",
        )
        r2_with_bonus = calculate_period(
            _req_metal(2, opening=r1.closing_state, events=(bonus2,))
        )
        r2_no_bonus = calculate_period(_req_metal(2, opening=r1.closing_state))
        irpef_bonus = _sum_account(r2_with_bonus, AccountKind.ORDINARY_TAX)
        irpef_plain = _sum_account(r2_no_bonus, AccountKind.ORDINARY_TAX)
        assert irpef_bonus > irpef_plain, (
            "The 1,000 EUR excess PdR must raise ordinary IRPEF in period 2."
        )


class TestT04TrattamentoNoOverRecovery:
    """T04: trattamento integrativo — recovered never exceeds recognized."""

    def test_no_over_recovery_across_12_months(self) -> None:
        """After Jan credit + Feb large bonus, recovery never exceeds recognized.

        Source: D.L. 3/2020 art. 1 co. 3 — the claw-back cannot exceed
        the credit originally granted.
        """
        opening = PeriodState.zero()
        for month in range(1, 13):
            events: tuple[object, ...] = ()
            if month == 2:
                events = (
                    BonusEvent(
                        event_date=date(_YEAR, 2, 15),
                        amount=Decimal("25000.00"),
                        kind="bonus",
                    ),
                )
            req = _req_portieri(month, opening=opening, events=events)
            result = calculate_period(req)
            cs = result.closing_state
            assert cs.ytd.trattamento.recovered <= cs.ytd.trattamento.recognized, (
                f"Month {month}: recovered {cs.ytd.trattamento.recovered} > "
                f"recognized {cs.ytd.trattamento.recognized}"
            )
            rec = reconcile(result, opening)
            assert rec.ok, f"Month {month} reconcile failed: {rec.violations}"
            opening = result.closing_state

    def test_january_credit_recognized(self) -> None:
        """Portieri B5 January must recognize trattamento integrativo = 92.31."""
        result = calculate_period(_req_portieri(1))
        tratt = result.tax_computation.trattamento_integrativo
        assert tratt == Decimal("92.31"), (
            f"Expected 92.31 trattamento integrativo in January for B5; got {tratt}."
        )


class TestI16ReconciliationInvariant:
    """TrattamentoAccount.recovered must never exceed recognized."""

    def test_over_recovery_raises_at_construction(self) -> None:
        """TrattamentoAccount raises when recovered > recognized."""
        with pytest.raises(ValueError, match="recovered"):
            TrattamentoAccount(
                recognized=Decimal("50.00"),
                recovered=Decimal("100.00"),
            )

    def test_equal_recovered_and_recognized_accepted(self) -> None:
        """TrattamentoAccount accepts recovered == recognized (full recovery)."""
        acc = TrattamentoAccount(
            recognized=Decimal("92.31"),
            recovered=Decimal("92.31"),
        )
        assert acc.recovered == acc.recognized

    def test_zero_recovered_accepted(self) -> None:
        """TrattamentoAccount accepts recovered == 0 (no recovery yet)."""
        acc = TrattamentoAccount(
            recognized=Decimal("92.31"),
            recovered=Decimal("0.00"),
        )
        assert acc.recovered == Decimal("0.00")


class TestPdREligibilityFailClosed:
    """Fail-closed: unknown prior income must not grant the PdR substitute rate."""

    def test_unknown_prior_income_no_substitute_tax(self) -> None:
        """A productivity_bonus with unknown prior income yields SUBSTITUTE_TAX=0.

        Fail-closed: when the worker's prior-year reddito is unknown the engine
        must apply ordinary IRPEF rather than the 1% substitute rate.
        """
        bonus = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("1000.00"),
            kind="productivity_bonus",
        )
        result = calculate_period(_req_metal(1, events=(bonus,), income=None))
        sub_tax = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
        assert sub_tax == _ZERO, (
            f"productivity_bonus with unknown prior-year income must not receive "
            f"the substitute rate; got SUBSTITUTE_TAX={sub_tax}."
        )
