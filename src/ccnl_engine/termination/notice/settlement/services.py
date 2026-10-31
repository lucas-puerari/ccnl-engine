"""The separate tax of the notice indemnity of a run (art. 19 c. 2 TUIR).

The indemnity is taxed apart "per il loro ammontare complessivo, al netto
dei contributi obbligatori dovuti per legge, con l'aliquota determinata
agli effetti del comma 1": the rate of the TFR of the same termination.
The run takes it from the TFR settlement it taxes, computed or stated by
the caller; without one it withholds nothing on the indemnity and says so.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.ledger.remittance.models import SEVERANCE_WITHHOLDING
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _make_entry, _require_resolution
from ccnl_engine.termination.inputs import TerminationTFREvent

if TYPE_CHECKING:
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext

__all__ = ["RATE_UNKNOWN", "NoticeTax", "notice_tax"]

_KIND = "notice_indemnity_item"
_CAPABILITY = "termination_notice"
#: Issue of an indemnity the run cannot tax: no TFR rate in the run.
RATE_UNKNOWN = "notice_indemnity_tax_rate_unknown"
_ZERO = Decimal(0)


@dataclass(frozen=True)
class NoticeTax:
    """The separate tax of the notice indemnity of the run."""

    entries: tuple[LedgerEntry, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()


def _rate(ctx: RunContext, settled: Decimal | None) -> Decimal | None:
    if settled is not None:
        return settled
    stated = (
        e.separate_tax_rate
        for e in ctx.request.events
        if isinstance(e, TerminationTFREvent) and e.amount is not None
    )
    return next(stated, None)


def notice_tax(
    ctx: RunContext,
    items: tuple[PayItem, ...],
    apart_inps: Decimal,
    settled_rate: Decimal | None,
) -> NoticeTax:
    """Return the separate tax of the notice indemnity the run posts.

    Args:
        ctx: Context of the run.
        items: Pay items of the run's events.
        apart_inps: Employee INPS of the pay taxed apart, left out of the
            ordinary taxable.
        settled_rate: Rate the computed TFR settlement taxed with.

    Returns:
        The tax entry and its decision; an ``incomplete`` issue and
        decision when the run has no TFR rate; nothing without indemnity.
    """
    gross = sum((i.amount for i in items if i.kind == _KIND), _ZERO)
    if not gross:
        return NoticeTax()
    taxable = gross - apart_inps
    rate = _rate(ctx, settled_rate)
    inputs: dict[str, Decimal | str] = {
        "indemnity": gross,
        "employee_inps": apart_inps,
        "taxable": taxable,
    }
    if rate is None:
        issue = CalculationIssue(
            code=RATE_UNKNOWN,
            message=(
                "the notice indemnity is taxed at the rate of the TFR of the "
                "termination (art. 19 c. 2 TUIR), which the run does not "
                "settle: pass a TerminationTFREvent; no tax is withheld on it"
            ),
            status=CalculationStatus.INCOMPLETE,
            capability=_CAPABILITY,
            cause=IssueCause.CONDITION,
        )
        decision = _decision(
            ctx, CalculationStatus.INCOMPLETE, RATE_UNKNOWN, inputs, None
        )
        return NoticeTax(decisions=(decision,), issues=(issue,))
    tax = money(max(taxable, _ZERO) * rate)
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    entry = _make_entry(
        f"notice_tax_{ctx.run_id}",
        f"notice_{ctx.run_id}",
        _KIND,
        ctx.cp,
        ctx.contract.tctx.payment,
        AccountKind.SEPARATE_TAX,
        tax,
        policy_id=resolution.policy_id,
        remittance_code=SEVERANCE_WITHHOLDING,
    )
    inputs["rate"] = rate
    decision = _decision(ctx, CalculationStatus.FINAL, "taxed_at_tfr_rate", inputs, tax)
    return NoticeTax(entries=(entry,), decisions=(decision,))


def _decision(
    ctx: RunContext,
    status: CalculationStatus,
    reason: str,
    inputs: dict[str, Decimal | str],
    amount: Decimal | None,
) -> CalculationDecision:
    return CalculationDecision(
        capability=_CAPABILITY,
        status=status,
        reason_code=reason,
        rule="tax/separate:art19c2",
        rule_version=str(ctx.fiscal_year),
        inputs=inputs,
        amount=amount,
    )
