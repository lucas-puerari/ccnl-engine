"""Credits, withholding cap and base posting of one run."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import (
    _make_entry,
    _require_resolution,
)
from ccnl_engine.payroll.application.post_ledger import (
    _build_pay_items,
    _project_ledger,
)
from ccnl_engine.payroll.application.withholding._cap import cap_withholding
from ccnl_engine.payroll.application.withholding._carried_recovery import (
    CarriedRecoveries,
    post_carried_recoveries,
)
from ccnl_engine.payroll.application.withholding._somma_esente import (
    SommaEsenteOutcome,
    SommaEsentePosting,
    resolve_somma_esente,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import TaxCreditItem
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.withholding._cap import CappedWithholding
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


def _no_credits(ctx: RunContext) -> RunCredits:
    """Return the credits of an employer that is not a withholding agent.

    Such an employer never recognizes a credit or withholds a tax, so an
    opening state carrying a recovery, a withholding shortfall or tax
    withheld cannot come from its payslips.

    Returns:
        No somma esente and no carried recovery.

    Raises:
        InvalidInputError: When the opening state carries a recovery, a
            withholding shortfall or IRPEF or surtax withheld.
    """
    opening = ctx.opening
    ytd = opening.ytd
    if (
        opening.obligations.recoveries
        or ytd.shortfall.total
        or ytd.tax.irpef
        or ytd.tax.surtax
    ):
        msg = (
            "the employer is not a withholding agent (art. 23 c. 1 D.P.R. "
            "600/1973): the opening state cannot carry credit recoveries, a "
            "withholding shortfall or tax withheld"
        )
        raise InvalidInputError(msg, feature="withholding_agent")
    return RunCredits(SommaEsenteOutcome(), CarriedRecoveries())


def run_credits(ctx: RunContext, tax_computation: TaxComputation) -> RunCredits:
    """Settle the somma esente and post the recoveries carried into the year.

    Returns:
        The somma esente outcome and the carried recoveries of the run;
        none for an employer that is not a withholding agent.
    """
    if not ctx.withholding_agent:
        return _no_credits(ctx)
    request, contract = ctx.request, ctx.contract
    run = ctx.installment_run
    somma = resolve_somma_esente(
        tax_computation,
        contract.year_rules,
        ctx.opening,
        ctx.withholding_schedule,
        ctx.fiscal_year,
        SommaEsentePosting(
            ctx.resolver,
            ctx.policy_context,
            ctx.cp,
            request.payment_date,
            ctx.run_id,
            run,
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
        run,
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


def _recovery_adjustment(
    ctx: RunContext, amount: Decimal
) -> tuple[tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Return the ``credit_recovery_shortfall`` line of ``amount``.

    A positive ``amount`` is a recovery of the run the pay does not cover:
    it is given back on ``CREDIT_RECOVERY_SHORTFALL``.  A negative one is a
    recovery carried in and withheld now, posted to ``CREDIT_RECOVERIES``.
    Neither is coded: the shortfall is not tracked by recovered credit.

    Returns:
        Empty tuples for a zero amount; otherwise one signed tax credit
        item and its non-negative entry.
    """
    if amount == Decimal(0):
        return (), ()
    item_id = f"credit_recovery_shortfall_{ctx.run_id}"
    payment_date = ctx.request.payment_date
    policy_id = _require_resolution(
        ctx.resolver, "tax_credit_item", ctx.policy_context
    ).policy_id
    item = TaxCreditItem(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment_date,
        quantity=Decimal(1),
        amount=amount,
    )
    entry = _make_entry(
        item_id,
        item_id,
        "tax_credit_item",
        ctx.cp,
        payment_date,
        (
            AccountKind.CREDIT_RECOVERY_SHORTFALL
            if amount > 0
            else AccountKind.CREDIT_RECOVERIES
        ),
        abs(amount),
        policy_id=policy_id,
    )
    return (item,), (entry,)


def post_run(
    ctx: RunContext,
    amounts: _PeriodAmounts,
    other_entries: tuple[LedgerEntry, ...],
) -> RunPostings:
    """Cap the withholding to the pay left and post the base lines of the run.

    The base ledger is projected once, and again when the cap lowered the
    IRPEF or surtax of the run.  A credit recovery the pay cannot cover is
    given back by one ``credit_recovery_shortfall`` line.

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
        last_slot=ctx.installment_run.final
        or (
            ctx.run_kind.consumes_withholding_slot
            and ctx.withholding_schedule.remaining(slots_closed) == 1
        ),
        rules=ctx.contract.year_rules,
    )
    if capped.amounts is not amounts:
        amounts = capped.amounts
        ledger_entries = _base_ledger(ctx, amounts)
    pay_items = _build_pay_items(
        amounts, ctx.chain, request.period_id, request.payment_date, run_tag=ctx.run_id
    )
    items, entries = _recovery_adjustment(ctx, capped.recovery_adjustment)
    return RunPostings(
        amounts,
        pay_items + items,
        ledger_entries + other_entries + entries,
        capped,
    )
