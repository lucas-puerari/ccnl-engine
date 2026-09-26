"""Regression evidence: counterexamples from §2.2 of REVIEW.md.

Each test asserts the CORRECT behaviour and is marked xfail(strict=True)
because the bug is present on main.  When a later PR fixes the underlying
issue the xfail turns into an XPASS, causing CI to fail and prompting the
developer to remove the marker.

Counterexamples (REVIEW §2.2):
  CE-3  excess YTD withheld produces a refund of 0.00 instead of a credit
  CE-4  two fringe events below the per-event threshold yield taxable = 0.00
        instead of taxable = 400.00 (cumulative threshold not applied)
  CE-5  WelfareEvent increases cash earnings and gross (non-cash benefit
        should not appear as monetary pay)
  CE-6  an event amount with sub-cent precision produces reconcile ok=False
        (fixed in PR-05: period_net derived from ledger)

Note: CE-1 and CE-2 tested the old PayrollEngine API delegating to the
annual-first path. PR-02 wired PayrollEngine.calculate_period() to the
period-first core, eliminating that path. Those counterexamples no longer
apply and the tests have been removed.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.events import (
    BonusEvent,
    FringeEvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.ytd_accounts import TaxYtd

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026

_ZERO = Decimal(0)


def _req(
    month: int = 1,
    opening: PeriodState | None = None,
    events: tuple[object, ...] = (),
) -> PeriodCalculationRequest:
    if opening is None:
        opening = PeriodState.zero()
    return PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=opening,
        events=events,  # type: ignore[arg-type]
    )


def _sum_account(result: PeriodCalculationResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        _ZERO,
    )


# ---------------------------------------------------------------------------
# CE-3: pregresso superiore al debito → rimborso 0.00
# ---------------------------------------------------------------------------


def test_ce3_excess_ytd_produces_refund() -> None:
    """CE-3: when YTD already withheld exceeds annual liability a refund must appear.

    A December calculation with irpef_withheld_ytd=5000 and annual IRPEF
    liability well below 5000 must post a TaxRefundItem in CREDITS rather than
    a negative ORDINARY_TAX entry (refunds now use the explicit TaxRefundItem
    representation instead of a signed withholding entry).
    """
    high_ytd = PeriodState(
        regular_periods_closed=11,
        tax_withholding_periods_closed=12,
        tax=TaxYtd(irpef=Decimal("5000.00")),
    )
    result = calculate_period(_req(month=12, opening=high_ytd))

    # Refund appears as a positive CREDITS entry (tax_refund_item), not as
    # negative ORDINARY_TAX.
    refund = sum(
        e.amount
        for e in result.ledger_entries
        if e.account == AccountKind.CREDITS and e.pay_item_kind == "tax_refund_item"
    )
    assert refund > _ZERO, (
        f"No TaxRefundItem in CREDITS when 5000 YTD withheld exceeds liability; "
        f"ORDINARY_TAX = {_sum_account(result, AccountKind.ORDINARY_TAX)}"
    )


# ---------------------------------------------------------------------------
# CE-4: due fringe da 200 con soglia 258,23 — imponibile 0.00 invece di 400.00
# ---------------------------------------------------------------------------


def test_ce4_cumulative_fringe_threshold() -> None:
    """CE-4: two fringe events whose cumulative sum exceeds the threshold are taxable.

    Two FringeEvent(600) in the same period: cumulative = 1200, which exceeds
    the 2026 standard threshold (1000 EUR under L. 207/2024). Both amounts must
    become taxable, increasing ORDINARY_TAX relative to a no-fringe baseline.
    """
    event_date = date(_YEAR, 1, 15)
    fringe_a = FringeEvent(event_date=event_date, amount=Decimal("600.00"))
    fringe_b = FringeEvent(event_date=event_date, amount=Decimal("600.00"))
    result_with_fringe = calculate_period(_req(events=(fringe_a, fringe_b)))
    result_without = calculate_period(_req())

    tax_with = _sum_account(result_with_fringe, AccountKind.ORDINARY_TAX)
    tax_without = _sum_account(result_without, AccountKind.ORDINARY_TAX)

    assert tax_with > tax_without, (
        f"ORDINARY_TAX with cumulative fringe ({tax_with}) must exceed "
        f"base case ({tax_without}): two fringe events at 600 (total 1200) "
        "exceed the 2026 threshold (1000) and must be fully taxable."
    )


# ---------------------------------------------------------------------------
# CE-5: welfare da 100 → cash earnings e lordo aumentano di 100
# ---------------------------------------------------------------------------


def test_ce5_welfare_does_not_increase_cash_earnings() -> None:
    """CE-5: a WelfareEvent must not increase period_gross or CASH_EARNINGS.

    After the fix calculate_period with WelfareEvent(100) must produce the
    same period_gross and CASH_EARNINGS as a calculation with no events.
    Currently welfare increases both by 100.
    """
    welfare = WelfareEvent(event_date=date(_YEAR, 1, 15), amount=Decimal("100.00"))
    result_with = calculate_period(_req(events=(welfare,)))
    result_without = calculate_period(_req())

    assert result_with.period_gross == result_without.period_gross, (
        f"period_gross with welfare ({result_with.period_gross}) must equal "
        f"period_gross without ({result_without.period_gross})"
    )

    cash_with = _sum_account(result_with, AccountKind.CASH_EARNINGS)
    cash_without = _sum_account(result_without, AccountKind.CASH_EARNINGS)
    assert cash_with == cash_without, (
        f"CASH_EARNINGS with welfare ({cash_with}) must equal "
        f"CASH_EARNINGS without ({cash_without})"
    )


# ---------------------------------------------------------------------------
# CE-6: riconciliazione con frazioni di centesimo → ok=False
# ---------------------------------------------------------------------------


def test_ce6_sub_cent_event_amount_reconciles() -> None:
    """CE-6: event amounts with sub-cent precision reconcile cleanly.

    period_net is derived from the same ledger entries, so sub-cent amounts
    on both sides of the I9 identity cancel out and reconcile passes.
    """
    welfare_subcent = WelfareEvent(
        event_date=date(_YEAR, 1, 15), amount=Decimal("100.001")
    )
    result = calculate_period(_req(events=(welfare_subcent,)))
    opening = PeriodState.zero()

    r = reconcile(result, opening)
    assert r.ok, f"reconcile must pass even with sub-cent event amount: {r.violations}"


# ---------------------------------------------------------------------------
# Gate PR-14: credito riconosciuto e recuperato aggiorna i progressivi YTD
# ---------------------------------------------------------------------------

_CCNL_TRATT = "portieri-fabbricati-confedilizia.json"
_LEVEL_TRATT = "B5"  # 1,264.51 EUR/month (terziario sector, trattamento integrativo)


def _req_tratt(
    month: int,
    opening: PeriodState | None = None,
    events: tuple[object, ...] = (),
) -> PeriodCalculationRequest:
    if opening is None:
        opening = PeriodState.zero()
    return PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL_TRATT,
        level_code=_LEVEL_TRATT,
        opening_state=opening,
        events=events,  # type: ignore[arg-type]
    )


def test_credit_recognized_in_january_recovered_in_february() -> None:
    """Gate: credit_recognized_ytd and credit_recovered_ytd both advance correctly.

    Period 1 (January): B5 portieri salary (~15k EUR annual, terziario sector)
    → trattamento integrativo given → credit_recognized_ytd > 0.
    Period 2 (February): same salary + 25,000 EUR bonus → annual projection
    far above 28k EUR → annual trattamento = 0 → period_tratt < 0 (recovery)
    → credit_recovered_ytd > 0, credit_recognized_ytd unchanged.
    """
    # Period 1: January — B5 portieri baseline, no events
    result1 = calculate_period(_req_tratt(month=1))
    state1 = result1.closing_state
    assert state1.trattamento.recognized > _ZERO, (
        "Trattamento integrativo must be recognized in January for B5 portieri "
        "income level (~15k EUR annual, terziario sector)"
    )
    assert state1.trattamento.recovered == _ZERO

    # Period 2: February — large bonus pushes projected annual income above 28k EUR
    bonus = BonusEvent(event_date=date(_YEAR, 2, 15), amount=Decimal("25000.00"))
    result2 = calculate_period(_req_tratt(month=2, opening=state1, events=(bonus,)))
    state2 = result2.closing_state

    assert state2.trattamento.recognized == state1.trattamento.recognized, (
        "credit_recognized_ytd must not grow when period_tratt <= 0"
    )
    assert state2.trattamento.recovered > _ZERO, (
        "Trattamento integrativo must be partially recovered in February "
        "when a 25,000 EUR bonus projects annual income far above 28k EUR"
    )
