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

Note: CE-1 and CE-2 tested the old PayrollEngine API delegating to the
annual-first path. PR-02 wired PayrollEngine.calculate_period() to the
period-first core, eliminating that path. Those counterexamples no longer
apply and the tests have been removed.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.ledger import AccountKind
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.events import (
    FringeEvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026

_FRINGE_THRESHOLD = Decimal("258.23")
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


@pytest.mark.xfail(
    strict=True,
    reason=(
        "CE-3 P0.2: calculate_period clamps withholding to zero via max(0, ...) "
        "at calculate_period.py:250.  When irpef_withheld_ytd (5000) exceeds the "
        "estimated annual liability the worker is owed a refund; instead the "
        "engine silently returns 0 and does not produce a TaxRefundItem."
    ),
)
def test_ce3_excess_ytd_produces_refund() -> None:
    """CE-3: when YTD already withheld exceeds annual liability a refund must appear.

    After the fix a December calculation with irpef_withheld_ytd=5000 and an
    annual IRPEF liability well below 5000 must post a negative ORDINARY_TAX
    entry (i.e. the engine owes the worker a conguaglio credit) or produce an
    explicit TaxRefundItem.
    Currently calculate_period.py:250 applies ``max(0, ...)`` which clamps the
    credit to zero and posts ORDINARY_TAX = 0 — the refund disappears silently.
    """
    high_ytd = PeriodState(
        months_closed=11,
        irpef_withheld_ytd=Decimal("5000.00"),
    )
    result = calculate_period(_req(month=12, opening=high_ytd))

    # The ORDINARY_TAX ledger amount must be negative (a credit) when YTD
    # withheld exceeds the remaining annual liability.
    tax = _sum_account(result, AccountKind.ORDINARY_TAX)
    assert tax < _ZERO, (
        f"ORDINARY_TAX with 5000 YTD already withheld is {tax} (should be negative "
        "to represent the refund owed); max(0,...) suppresses the credit."
    )


# ---------------------------------------------------------------------------
# CE-4: due fringe da 200 con soglia 258,23 — imponibile 0.00 invece di 400.00
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "CE-4 P0.7: _fringe_bases() compares each FringeEvent independently "
        "against the exempt threshold (calculate_period.py:320-329).  Two events "
        "of 200 are individually below 258.23 and both return (0, 0).  The "
        "cumulative total (400) exceeds the annual threshold so the full 400 "
        "must become taxable, but the engine reports an IRPEF fringe base of 0."
    ),
)
def test_ce4_cumulative_fringe_threshold() -> None:
    """CE-4: two fringe events whose sum exceeds the threshold must be fully taxable.

    After the fix two FringeEvent(200) with exempt_threshold=258.23 in the
    same period must add 400.00 to the IRPEF base (both amounts become
    taxable once the cumulative total exceeds the threshold).
    Currently the engine evaluates the threshold per-event and returns 0.
    """
    event_date = date(_YEAR, 1, 15)
    fringe_a = FringeEvent(
        event_date=event_date,
        amount=Decimal("200.00"),
        exempt_threshold=_FRINGE_THRESHOLD,
    )
    fringe_b = FringeEvent(
        event_date=event_date,
        amount=Decimal("200.00"),
        exempt_threshold=_FRINGE_THRESHOLD,
    )
    result_with_fringe = calculate_period(_req(events=(fringe_a, fringe_b)))
    result_without = calculate_period(_req())

    # The two fringes must increase the IRPEF-liable base by their combined 400.
    # We observe this as an increase in ORDINARY_TAX relative to the base case.
    tax_with = _sum_account(result_with_fringe, AccountKind.ORDINARY_TAX)
    tax_without = _sum_account(result_without, AccountKind.ORDINARY_TAX)

    assert tax_with > tax_without, (
        f"ORDINARY_TAX with cumulative fringe ({tax_with}) must exceed "
        f"base case ({tax_without}): two fringe events at 200 with threshold "
        f"258.23 must be fully taxable (400 total)."
    )


# ---------------------------------------------------------------------------
# CE-5: welfare da 100 → cash earnings e lordo aumentano di 100
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "CE-5 P0.7: WelfareEvent increments total_gross and posts to "
        "CASH_EARNINGS (calculate_period.py:546-557).  Welfare benefits are "
        "non-cash/exempt; they must not appear as monetary earnings in the "
        "period_gross or in CASH_EARNINGS."
    ),
)
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


@pytest.mark.xfail(
    strict=True,
    reason=(
        "CE-6 P0.8: event amounts are not normalised through money() before "
        "being posted to the ledger.  A sub-cent event amount (e.g. 100.001) "
        "propagates into the ledger entries, making the I9 derived net a "
        "3-decimal-place value that does not match the money()-rounded "
        "period_net stored in the result."
    ),
)
def test_ce6_sub_cent_event_amount_reconciles() -> None:
    """CE-6: event amounts with sub-cent precision must reconcile cleanly.

    After the fix calculate_period must either normalise all event amounts
    through money() before posting them, or reject sub-cent inputs with a
    validation error.  Currently a WelfareEvent(100.001) results in a
    CASH_EARNINGS ledger entry of 100.001, which causes the I9 net identity
    to fail (derived = 3-decimal-place value, period_net = rounded value).
    """
    welfare_subcent = WelfareEvent(
        event_date=date(_YEAR, 1, 15), amount=Decimal("100.001")
    )
    result = calculate_period(_req(events=(welfare_subcent,)))
    opening = PeriodState.zero()

    r = reconcile(result, opening)
    assert r.ok, f"reconcile must pass even with sub-cent event amount: {r.violations}"
