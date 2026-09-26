"""Credits, withholding cap and base posting of one run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.post_ledger import (
    _build_pay_items,
    _project_ledger,
)
from ccnl_engine.payroll.application.withholding._cap import cap_withholding
from ccnl_engine.payroll.application.withholding._carried_recovery import (
    post_carried_recoveries,
)
from ccnl_engine.payroll.application.withholding._somma_esente import (
    SommaEsentePosting,
    resolve_somma_esente,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.withholding._cap import CappedWithholding
    from ccnl_engine.payroll.application.withholding._carried_recovery import (
        CarriedRecoveries,
    )
    from ccnl_engine.payroll.application.withholding._somma_esente import (
        SommaEsenteOutcome,
    )
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.payroll.domain.tax import TaxComputation


@dataclass(frozen=True)
class RunCredits:
    """Somma esente and recoveries carried from an earlier tax year."""

    somma: SommaEsenteOutcome
    carried: CarriedRecoveries


@dataclass(frozen=True)
class RunPostings:
    """Base pay items and ledger of the run after the withholding cap.

    ``amounts`` are the amounts after the cap; ``entries`` hold every ledger
    entry of the run, the base ones first.
    """

    amounts: _PeriodAmounts
    pay_items: tuple[PayItem, ...]
    entries: tuple[LedgerEntry, ...]
    capped: CappedWithholding


def run_credits(ctx: RunContext, tax_computation: TaxComputation) -> RunCredits:
    """Settle the somma esente and post the recoveries carried into the year.

    Returns:
        The somma esente outcome and the carried recoveries of the run.
    """
    request, contract = ctx.request, ctx.contract
    somma = resolve_somma_esente(
        tax_computation,
        contract.year_rules,
        ctx.opening,
        ctx.withholding_schedule,
        ctx.fiscal_year,
        SommaEsentePosting(
            ctx.resolver, ctx.policy_context, ctx.cp, request.payment_date, ctx.run_id
        ),
    )
    carried = post_carried_recoveries(
        ctx.opening.obligations,
        ctx.fiscal_year,
        ctx.resolver,
        ctx.policy_context,
        ctx.cp,
        request.payment_date,
        ctx.run_id,
    )
    return RunCredits(somma, carried)


def _base_ledger(ctx: RunContext, amounts: _PeriodAmounts) -> tuple[LedgerEntry, ...]:
    request = ctx.request
    return _project_ledger(
        amounts,
        ctx.chain,
        request.period_id,
        request.payment_date,
        ctx.resolver,
        ctx.policy_context,
        run_tag=ctx.run_id,
    )


def post_run(
    ctx: RunContext,
    amounts: _PeriodAmounts,
    other_entries: tuple[LedgerEntry, ...],
) -> RunPostings:
    """Cap the withholding to the pay left and post the base lines of the run.

    The base ledger is projected once, and again when the cap lowered the
    IRPEF or surtax of the run.

    Returns:
        The capped amounts, the base pay items and every ledger entry.
    """
    request, opening = ctx.request, ctx.opening
    ledger_entries = _base_ledger(ctx, amounts)
    slots_closed = opening.ytd.tax_withholding_periods_closed
    capped = cap_withholding(
        amounts,
        ledger_entries + other_entries,
        opening.ytd.shortfall,
        last_slot=ctx.run_kind.consumes_withholding_slot
        and ctx.withholding_schedule.remaining(slots_closed) == 1,
        rules=ctx.contract.year_rules,
    )
    if capped.amounts is not amounts:
        amounts = capped.amounts
        ledger_entries = _base_ledger(ctx, amounts)
    pay_items = _build_pay_items(
        amounts, ctx.chain, request.period_id, request.payment_date, run_tag=ctx.run_id
    )
    return RunPostings(amounts, pay_items, ledger_entries + other_entries, capped)
