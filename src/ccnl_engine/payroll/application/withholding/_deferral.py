"""Year-end IRPEF shortfall deferred to the next year on written request.

The conguaglio of tax year N withholds what the pay covers
(:mod:`~ccnl_engine.payroll.application.withholding._cap`).  When the
worker asked in writing to defer the rest (art. 23 c. 3 DPR 600/1973, see
:mod:`~ccnl_engine.payroll.domain.shortfall_deferral`), the IRPEF left
becomes a :class:`~ccnl_engine.payroll.domain.shortfall_deferral\
.DeferredShortfall` instead of the provisional issue, and the payslips of
N+1 from March withhold it with its interest.  Only the IRPEF is deferred:
the norm defers the "imposte dovute in sede di conguaglio", and the surtax
and the credit recoveries carried for lack of pay keep the issue.

The principal and the interest are posted to ``ORDINARY_TAX`` coded 1066,
"Ritenute [...] operate dopo il relativo conguaglio di fine anno" (ris. AdE
6/E of 28 January 2021, which institutes it for the withholding of art. 23
c. 3 second sentence), with N as the reference year.  The interest takes
the code of the IRPEF it refers to, as the norm remits it "con le modalità
previste per le somme cui si riferisce".  Neither enters the IRPEF withheld
of N+1.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.withholding._cap import unrecovered_issue
from ccnl_engine.payroll.application.withholding._deferral_lines import (
    CAPABILITY,
    deferral_decision,
    deferred_lines,
    unrecovered_deferral,
    withheld_decision,
)
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.domain.shortfall_deferral import (
    DEFERRAL_MONTHLY_RATE,
    FIRST_DEFERRAL_MONTH,
    DeferredShortfall,
)
from ccnl_engine.shared.domain.errors import OutOfScopeError

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.withholding._cap import CappedWithholding
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.payroll.domain.shortfall_deferral import DeferredInstallment

__all__ = ["CAPABILITY", "DeferredPostings", "defer_shortfall", "post_deferred"]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class DeferredPostings:
    """Deferred IRPEF of earlier years a run withholds.

    Attributes:
        items: Withholding items of the principal and of the interest.
        entries: Their ``ORDINARY_TAX`` entries, coded 1066.
        remaining: Deferred shortfalls after the run: those still running,
            then the one the run opened.
        decisions: One decision per deferral withheld, opened, not
            possible or left unrecovered.
        issues: A provisional issue per deferral left unrecovered.
    """

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    remaining: tuple[DeferredShortfall, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()


def _reject_refund_while_deferred(ctx: RunContext, capped: CappedWithholding) -> None:
    """Reject a refund of IRPEF of a tax year whose conguaglio deferred some.

    A later run of the year (an adjustment, a termination) that settles the
    balance again counts the deferred IRPEF as withheld.  A refund would
    give back tax the worker has not paid yet; lowering the deferral
    instead is not modelled.

    Raises:
        OutOfScopeError: When the run refunds IRPEF and a deferral of its
            tax year is open.
    """
    deferred = ctx.opening.obligations.deferred_of(ctx.fiscal_year)
    if deferred is None or capped.amounts.period_irpef >= _ZERO:
        return
    msg = (
        f"the run refunds {-capped.amounts.period_irpef} IRPEF while "
        f"{deferred.irpef} IRPEF of the conguaglio {deferred.tax_year} is "
        "deferred on written request: lowering the deferral is not modelled"
    )
    raise OutOfScopeError(
        msg,
        reason="shortfall_deferral_refund",
        feature=CAPABILITY,
        remediation="lower the deferred IRPEF by the refund and settle it manually",
    )


def defer_shortfall(
    ctx: RunContext, capped: CappedWithholding
) -> tuple[CappedWithholding, DeferredShortfall | None]:
    """Defer the IRPEF shortfall of the conguaglio on the written request.

    Returns:
        ``capped`` unchanged without a request, off the conguaglio or with
        no IRPEF left.  On the last run of the employment no payslip
        follows: a ``deferral_not_possible`` decision is added and the
        issue kept.  Otherwise the shortfall without its IRPEF, the issue
        only for what is left, a ``shortfall_deferred`` decision, and the
        deferred shortfall.  A request signed outside the tax year and the
        following January and February is rejected by
        :meth:`~ccnl_engine.payroll.domain.shortfall_deferral\
.ShortfallDeferralRequest.check_for`.
    """
    _reject_refund_while_deferred(ctx, capped)
    request = ctx.request.prior_year.shortfall_deferral
    shortfall = capped.shortfall
    if request is None or not ctx.conguaglio or shortfall.irpef == _ZERO:
        return capped, None
    year = ctx.fiscal_year
    request.check_for(year)
    inputs: dict[str, Decimal | str] = {
        "signed_on": request.signed_on.isoformat(),
        "irpef_shortfall": shortfall.irpef,
    }
    if ctx.installment_run.final:
        decision = deferral_decision(ctx, "deferral_not_possible", _ZERO, inputs)
        return replace(capped, decisions=(*capped.decisions, decision)), None
    period = ctx.request.period_id
    deferred = DeferredShortfall(
        tax_year=year,
        signed_on=request.signed_on,
        deferred_from=date(period.year, period.month, 1),
        irpef=shortfall.irpef,
    )
    left = replace(shortfall, irpef=_ZERO)
    inputs["first_month"] = f"{year + 1}-{FIRST_DEFERRAL_MONTH:02d}"
    inputs["monthly_rate"] = DEFERRAL_MONTHLY_RATE
    decision = deferral_decision(ctx, "shortfall_deferred", shortfall.irpef, inputs)
    return (
        replace(
            capped,
            shortfall=left,
            decisions=(*capped.decisions, decision),
            issues=(unrecovered_issue(left),) if left.total else (),
        ),
        deferred,
    )


def post_deferred(
    ctx: RunContext, available: Decimal, opened: DeferredShortfall | None = None
) -> DeferredPostings:
    """Withhold the IRPEF deferred by earlier conguagli from the pay left.

    A run of the year after the conguaglio, from March and other than an
    adjustment, withholds the largest principal whose interest fits in
    ``available``.  What the conguaglio of that year or the last run of the
    employment leaves is dropped with a provisional issue.

    Args:
        ctx: Context of the run.
        available: Net pay of the run after every other line.
        opened: Deferred shortfall the conguaglio of this run opened.

    Returns:
        The postings, and the deferred shortfalls still running followed
        by ``opened``.
    """
    postings = DeferredPostings()
    for deferred in ctx.opening.obligations.deferred_shortfall:
        one = _post_one(ctx, deferred, available)
        available -= sum((e.amount for e in one.entries), _ZERO)
        postings = _join(postings, one)
    if opened is None:
        return postings
    return _join(postings, DeferredPostings(remaining=(opened,)))


def _join(first: DeferredPostings, second: DeferredPostings) -> DeferredPostings:
    return DeferredPostings(
        first.items + second.items,
        first.entries + second.entries,
        first.remaining + second.remaining,
        first.decisions + second.decisions,
        first.issues + second.issues,
    )


def _post_one(
    ctx: RunContext, deferred: DeferredShortfall, available: Decimal
) -> DeferredPostings:
    """Return what the run withholds of ``deferred`` and what is left of it.

    Returns:
        Nothing withheld before the year after the conguaglio, the deferral
        kept unless the run is the last of the employment.  In that year,
        from March and on a run other than an adjustment, the installment
        ``available`` covers; what is left is kept, or dropped with an
        issue on the conguaglio, the last run of the employment or another
        year.
    """
    year, month = ctx.fiscal_year, ctx.request.period_id.month
    if year < deferred.withheld_in and not ctx.installment_run.final:
        return DeferredPostings(remaining=(deferred,))
    posted: DeferredInstallment | None = None
    after: DeferredShortfall | None = deferred
    if deferred.due_in(year, month) and ctx.run_kind is not RunKind.ADJUSTMENT:
        posted, after = deferred.post(available, year, month)
    withheld = DeferredPostings()
    if posted is not None:
        items, entries = deferred_lines(ctx, deferred, posted)
        withheld = DeferredPostings(
            tuple(items),
            tuple(entries),
            decisions=(withheld_decision(ctx, deferred, posted),),
        )
    if after is None:
        return withheld
    if ctx.conguaglio or year != after.withheld_in:
        decision, issue = unrecovered_deferral(ctx, after)
        return _join(withheld, DeferredPostings(decisions=(decision,), issues=(issue,)))
    return _join(withheld, DeferredPostings(remaining=(after,)))
