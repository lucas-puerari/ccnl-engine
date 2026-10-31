"""Personal withholdings of one run: the lines, the decisions, the residual.

The run withholds them last, from the net pay its other lines leave
(:mod:`~ccnl_engine.personal_withholding.rules`):

- a salary assignment, a delegation and a maintenance order withhold their
  monthly amount on the regular payslip of the month only;
- the garnishments of a legal fraction apply to the net of every run but an
  adjustment: the extra months and the termination run are pay ("somme
  dovute ... comprese quelle dovute a causa di licenziamento", art. 545
  c. 4 c.p.c.);
- none withholds before its ``starts_on``, nor beyond what is still due.

What each run withholds is added to the amount withheld to date that the
closing state carries, across tax years.  The engine does not withhold on
the TFR: art. 545 c.p.c. extends a garnishment to the indemnities due
because of the dismissal, and art. 55 c. 2 with art. 43 c. 3 DPR 180/1950
(Normattiva page sha256
c45a1b19e7ec90407a5cd06b3e42ffab47e5f734177637b743bd21a6655af57c) retains
the indemnity paid once "fino alla concorrenza dell'intero residuo debito
per cessione", but how these combine on the TFR, a pension fund or
the Fondo Tesoreria is not modelled.  The last run of the employment
reports what each deduction leaves and the TFR it settles, and the state
carries nothing after it.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from itertools import starmap
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.facade import EmployeeWithholdingItem
from ccnl_engine.pay_item.services import _make_entry, _require_resolution
from ccnl_engine.personal_withholding.inputs import (
    FEATURE,
    INSTALLMENT_KINDS,
    PersonalWithholdingKind,
)
from ccnl_engine.personal_withholding.models import WithheldToDate
from ccnl_engine.personal_withholding.rules import DueWithholding, allocate
from ccnl_engine.run.types import RunKind
from ccnl_engine.withholding.cap.services import run_net

if TYPE_CHECKING:
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.personal_withholding.inputs import PersonalWithholding
    from ccnl_engine.personal_withholding.rules import Withheld

__all__ = [
    "SAME_KIND",
    "PersonalWithholdingPostings",
    "post_personal_withholdings",
    "same_kind_paths",
]

#: Engine limitation of two deductions sharing the measure of their kind.
SAME_KIND = "personal_withholding_same_kind"

_ZERO = Decimal(0)
_KIND = "employee_withholding_item"
_TFR_KIND = "tfr_settlement_item"


@dataclass(frozen=True)
class PersonalWithholdingPostings:
    """Personal withholdings of a run.

    Attributes:
        items: One withholding item per deduction the run withholds.
        entries: Their ``PERSONAL_WITHHOLDINGS`` entries.
        withheld: Amount withheld to date per deduction after the run;
            empty after the last run of the employment.
        decisions: One decision per deduction the run applies.
        issues: One provisional issue per deduction the last run of the
            employment leaves due.
    """

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    withheld: tuple[WithheldToDate, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()


def _base(entries: tuple[LedgerEntry, ...]) -> tuple[Decimal, Decimal]:
    """Return the net pay the limits apply to and the net TFR of the run.

    Returns:
        The net of the run without the TFR settled and its separate tax,
        and that TFR net of the tax.
    """
    tfr = tuple(e for e in entries if e.pay_item_kind == _TFR_KIND)
    tfr_net = run_net(tfr)
    return run_net(entries) - tfr_net, tfr_net


def _applies(ctx: RunContext, withholding: PersonalWithholding) -> bool:
    if withholding.starts_on > ctx.request.payment_date:
        return False
    if withholding.kind in INSTALLMENT_KINDS:
        return ctx.run_kind is RunKind.REGULAR
    return ctx.run_kind is not RunKind.ADJUSTMENT


def _active(
    ctx: RunContext, residuals: dict[str, Decimal]
) -> list[PersonalWithholding]:
    """Return the deductions the run applies, in the order of notification.

    Returns:
        Those whose ``starts_on`` has come, that the kind of the run
        withholds and that are still due.
    """
    return sorted(
        (
            w
            for w in ctx.request.personal_withholdings
            if _applies(ctx, w) and residuals[w.withholding_id]
        ),
        key=lambda w: (w.notified_on, w.withholding_id),
    )


def _residuals(ctx: RunContext) -> dict[str, Decimal]:
    carried = {
        w.withholding_id: w.withheld
        for w in ctx.opening.cash.obligations.personal_withholdings
    }
    return {
        w.withholding_id: max(_ZERO, w.total_due - carried.get(w.withholding_id, _ZERO))
        for w in ctx.request.personal_withholdings
    }


def same_kind_paths(ctx: RunContext) -> frozenset[str]:
    """Return the limitation of the run when two deductions share a measure.

    Two garnishments of the same kind, or two salary assignments, split the
    fraction of their kind in the order of notification, which no text read
    states.

    Returns:
        ``{SAME_KIND}`` when the run applies two such deductions, else empty.
    """
    kinds = [
        w.kind
        for w in _active(ctx, _residuals(ctx))
        if w.kind not in INSTALLMENT_KINDS
        or w.kind is PersonalWithholdingKind.SALARY_ASSIGNMENT
    ]
    return frozenset({SAME_KIND}) if len(set(kinds)) < len(kinds) else frozenset()


def _decision(
    ctx: RunContext,
    withholding: PersonalWithholding,
    withheld: Withheld,
    base: Decimal,
    residual: Decimal,
) -> CalculationDecision:
    installment = withholding.installment
    return CalculationDecision(
        capability=FEATURE,
        status=CalculationStatus.FINAL,
        reason_code="withheld" if withheld.amount else "nothing_withheld",
        rule=withheld.rule.rule,
        rule_version=str(ctx.request.payment_date.year),
        inputs={
            "withholding_id": withholding.withholding_id,
            "kind": withholding.kind.value,
            "notified_on": withholding.notified_on.isoformat(),
            "net_base": base,
            "legal_limit": withheld.limit,
            "installment": "none" if installment is None else installment,
            "residual_before": residual,
            "residual_after": residual - withheld.amount,
        },
        source=withheld.rule.source,
        amount=withheld.amount,
    )


def _line(
    ctx: RunContext, withholding: PersonalWithholding, amount: Decimal
) -> tuple[PayItem, LedgerEntry]:
    policy_id = _require_resolution(ctx.resolver, _KIND, ctx.policy_context).policy_id
    item_id = f"personal_withholding_{withholding.withholding_id}_{ctx.run_id}"
    payment_date = ctx.request.payment_date
    item = EmployeeWithholdingItem(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment_date,
        quantity=Decimal(1),
        amount=amount,
    )
    entry = _make_entry(
        item_id,
        item_id,
        _KIND,
        ctx.cp,
        payment_date,
        AccountKind.PERSONAL_WITHHOLDINGS,
        amount,
        policy_id=policy_id,
    )
    return item, entry


def _residual_issue(
    withholding: PersonalWithholding, residual: Decimal, tfr_net: Decimal
) -> CalculationIssue:
    return CalculationIssue(
        code="personal_withholding_residual",
        capability=FEATURE,
        message=(
            f"personal_withholdings: {residual} of the {withholding.kind.value} "
            f"{withholding.withholding_id} is still due at the end of the "
            f"employment.  The run settles {tfr_net} of TFR net of its tax, "
            "which the engine does not withhold: art. 545 c. 4 c.p.c. extends "
            "a garnishment to the indemnities due because of the dismissal, "
            "and art. 55 c. 2 and 43 c. 3 DPR 180/1950 retain them up to the "
            "whole residual of a salary assignment; tell the creditor and "
            "settle the TFR share outside the engine"
        ),
        status=CalculationStatus.PROVISIONAL,
        cause=IssueCause.RULE,
    )


def post_personal_withholdings(
    ctx: RunContext, entries: tuple[LedgerEntry, ...]
) -> PersonalWithholdingPostings:
    """Withhold the personal withholdings of the run from its net pay.

    Args:
        ctx: Context of the run.
        entries: Every other ledger entry of the run.

    Returns:
        The lines, decisions and issues of the run, and the amount withheld
        to date per deduction after it.
    """
    stated = ctx.request.personal_withholdings
    carried = {
        w.withholding_id: w.withheld
        for w in ctx.opening.cash.obligations.personal_withholdings
    }
    if not stated and not carried:
        return PersonalWithholdingPostings()
    base, tfr_net = _base(entries)
    residuals = _residuals(ctx)
    active = _active(ctx, residuals)
    dues = [
        DueWithholding(w.kind, w.installment, residuals[w.withholding_id])
        for w in active
    ]
    lines, decisions = [], []
    for withholding, withheld in zip(
        active, allocate(base, dues, ctx.request.payment_date.year), strict=True
    ):
        key = withholding.withholding_id
        decisions.append(_decision(ctx, withholding, withheld, base, residuals[key]))
        if withheld.amount:
            lines.append(_line(ctx, withholding, withheld.amount))
            residuals[key] -= withheld.amount
            carried[key] = carried.get(key, _ZERO) + withheld.amount
    final = ctx.installment_run.final
    issues = tuple(
        _residual_issue(w, residuals[w.withholding_id], tfr_net)
        for w in stated
        if final and residuals[w.withholding_id]
    )
    return PersonalWithholdingPostings(
        items=tuple(item for item, _ in lines),
        entries=tuple(entry for _, entry in lines),
        withheld=()
        if final
        else tuple(starmap(WithheldToDate, sorted(carried.items()))),
        decisions=tuple(decisions),
        issues=issues,
    )
