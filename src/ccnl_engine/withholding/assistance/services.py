"""The payslip settlement of the 730-4 statements of the worker.

A regular run settles what the statements schedule for its month
(:func:`~ccnl_engine.withholding.assistance.rules.schedule`) and what an
earlier month could not withhold:

- a refund is paid whole and compensated by the employer (CREDITS, codes
  1631, 3796, 3797).  The engine sees one worker, not the withholdings of
  every employee the employer may compensate with (DM 164/1999 art. 19 c.
  2): it pays the refund on the first pay;
- a debt is withheld from the pay left after every other line (ORDINARY_TAX
  or SURTAX, codes 4731, 4730, 3803, 3846, 3845, with the installment
  interest 1630, 3790, 3795).  What the pay cannot cover is withheld on
  the next pay of the year with the interest of 0.4% a month (art. 19 c. 1;
  730/2026 instructions p. 173); what December still leaves is
  communicated to the worker (c. 5).

None of it is withholding on the pay of the run: it settles the tax return,
so it stays out of the IRPEF and surtax withheld of the year.
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
from ccnl_engine.pay_item.facade import EmployeeWithholdingItem, TaxRefundItem
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _make_entry, _require_resolution
from ccnl_engine.run.models import RunKind
from ccnl_engine.withholding.assistance.inputs import Form730Installment, Form730Kind
from ccnl_engine.withholding.assistance.rules import schedule

if TYPE_CHECKING:
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext

__all__ = ["CAPABILITY", "Form730Postings", "settle_form730"]

#: Capability of the settlement of the tax return.
CAPABILITY = "fiscal_adjustment"
#: Interest on a debt the pay could not cover, per month (art. 19 c. 1).
INCAPIENZA_RATE = Decimal("0.004")
_ZERO = Decimal(0)
_DECEMBER = 12
_WITHHOLDING = "employee_withholding_item"
_REFUND = "tax_refund_item"
_SURTAX = frozenset({
    Form730Kind.REGIONAL_SURTAX,
    Form730Kind.MUNICIPAL_SURTAX,
    Form730Kind.MUNICIPAL_SURTAX_ADVANCE,
})
#: Code of the principal, of the interest and of the refund of each line.
_CODES: dict[Form730Kind, tuple[str, str, str]] = {
    Form730Kind.IRPEF_BALANCE: ("4731", "1630", "1631"),
    Form730Kind.IRPEF_FIRST_ADVANCE: ("4730", "1630", "1631"),
    Form730Kind.IRPEF_SECOND_ADVANCE: ("4730", "1630", "1631"),
    Form730Kind.REGIONAL_SURTAX: ("3803", "3790", "3796"),
    Form730Kind.MUNICIPAL_SURTAX: ("3846", "3795", "3797"),
    Form730Kind.MUNICIPAL_SURTAX_ADVANCE: ("3845", "3795", "3797"),
}


@dataclass(frozen=True)
class Form730Postings:
    """What the run settles of the 730-4 statements.

    Attributes:
        items: The withholding and refund items.
        entries: Their ledger entries.
        carried: Installments a later pay of the year settles.
        decisions: The settlement decision, when the run settled any.
        issues: The debt December could not withhold.
    """

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    carried: tuple[Form730Installment, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()


def _due(ctx: RunContext) -> tuple[list[Form730Installment], list[Form730Installment]]:
    """Return the installments the run settles and those of later months.

    Returns:
        Those due by the run's month, and the carried ones of later months.
    """
    month = (ctx.request.period_id.year, ctx.request.period_id.month)
    carried = ctx.opening.cash.obligations.form730
    later = [i for i in carried if (i.year, i.month) > month]
    due = [i for i in carried if (i.year, i.month) <= month]
    for statement in ctx.request.tax_returns:
        due.extend(i for i in schedule(statement) if (i.year, i.month) == month)
    return due, later


def _line(
    ctx: RunContext,
    kind: Form730Kind,
    role: str,
    amount: Decimal,
    *,
    refund: bool = False,
) -> tuple[PayItem, LedgerEntry]:
    principal, interest, refunded = _CODES[kind]
    code = refunded if refund else interest if role == "interest" else principal
    item_id = f"form730_{kind.value}_{role}_{ctx.run_id}"
    payment = ctx.request.payment_date
    item_type = TaxRefundItem if refund else EmployeeWithholdingItem
    kind_name = _REFUND if refund else _WITHHOLDING
    policy = _require_resolution(ctx.resolver, kind_name, ctx.policy_context).policy_id
    if refund:
        account = AccountKind.CREDITS
    else:
        account = AccountKind.SURTAX if kind in _SURTAX else AccountKind.ORDINARY_TAX
    item = item_type(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=Decimal(1),
        amount=amount,
    )
    entry = _make_entry(
        item_id,
        item_id,
        kind_name,
        ctx.cp,
        payment,
        account,
        amount,
        policy_id=policy,
        remittance_code=code,
    )
    return item, entry


def settle_form730(ctx: RunContext, net: Decimal) -> Form730Postings:
    """Settle the 730-4 statements on a regular run with ``net`` pay left.

    Returns:
        The refunds and debts the run settles, what it carries to a later
        pay of the year, its decision and, in December, the issue of the
        debt left to the worker.
    """
    carried_in = ctx.opening.cash.obligations.form730
    if ctx.run_kind is not RunKind.REGULAR:
        return Form730Postings(carried=carried_in)
    due, later = _due(ctx)
    if not due:
        return Form730Postings(carried=tuple(later))
    lines: list[tuple[PayItem, LedgerEntry]] = []
    refunded = _ZERO
    for i in (i for i in due if i.amount < _ZERO):
        refunded += -i.amount
        lines.append(_line(ctx, i.kind, "refund", -i.amount, refund=True))
    available = net + refunded
    withheld = _ZERO
    left: list[Form730Installment] = []
    for i in (i for i in due if i.amount >= _ZERO):
        interest = min(i.interest, available)
        principal = min(i.amount, available - interest)
        available -= interest + principal
        withheld += interest + principal
        for role, amount in (("interest", interest), ("principal", principal)):
            if amount > _ZERO:
                lines.append(_line(ctx, i.kind, role, amount))
        residual = i.amount + i.interest - interest - principal
        if residual > _ZERO:
            left.append(_carry(i, residual))
    return _postings(ctx, lines, later, left, withheld, refunded)


def _carry(i: Form730Installment, residual: Decimal) -> Form730Installment:
    """Return the residual of ``i`` on the next pay, with its interest.

    Returns:
        The installment of the next month, or of the same month in December
        (which no later pay of the year settles).
    """
    month = min(i.month + 1, _DECEMBER)
    return Form730Installment(
        i.kind, i.year, month, residual, money(residual * INCAPIENZA_RATE)
    )


def _postings(
    ctx: RunContext,
    lines: list[tuple[PayItem, LedgerEntry]],
    later: list[Form730Installment],
    left: list[Form730Installment],
    withheld: Decimal,
    refunded: Decimal,
) -> Form730Postings:
    december = ctx.request.period_id.month == _DECEMBER
    unpaid = sum((i.amount for i in left), _ZERO) if december else _ZERO
    status = CalculationStatus.PROVISIONAL if unpaid else CalculationStatus.FINAL
    decision = CalculationDecision(
        capability=CAPABILITY,
        status=status,
        reason_code="form730_settled",
        rule="dm-164-1999-art19",
        rule_version=str(ctx.request.period_id.year),
        inputs={
            "withheld": str(withheld),
            "refunded": str(refunded),
            "carried": str(sum((i.amount for i in left), _ZERO)),
        },
        amount=withheld - refunded,
    )
    issues = (
        ()
        if not unpaid
        else (
            CalculationIssue(
                code="form730_debt_unrecovered",
                capability=CAPABILITY,
                message=(
                    f"730: {unpaid} the pay of the year could not withhold is "
                    "communicated to the worker, who pays it (DM 164/1999 "
                    "art. 19 c. 5)"
                ),
                status=CalculationStatus.PROVISIONAL,
                cause=IssueCause.CONDITION,
            ),
        )
    )
    return Form730Postings(
        items=tuple(i for i, _ in lines),
        entries=tuple(e for _, e in lines),
        carried=(*later, *([] if december else left)),
        decisions=(decision,),
        issues=issues,
    )
