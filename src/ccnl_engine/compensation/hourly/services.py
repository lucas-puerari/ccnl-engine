"""Percentages a run pays on the ordinary hours worked of an hourly worker.

The base of each percentage is the base salary and the allowances it names,
as the run pays them on the hours worked
(:class:`~ccnl_engine.compensation.proration.services.HourlyBasis`).  Each
percentage is a gross earning (``hourly_percentage_earning``, policy
``it/earning/hourly_percentage``) in the INPS, IRPEF and TFR bases.  One
settled with the Cassa Edile is not paid to the worker: CCNL edilizia,
Allegato D, computes the contributions and taxes on the whole gross, then
withholds ``net_rate`` of the base as the accrual the employer remits to
the Cassa, on the account of the worker's bilateral fund contributions.
The net pay is the gross less contributions, taxes and that accrual.  The
IRPEF projection of the tax year adds the percentages of a full month to
each regular payment still to come (:func:`upcoming_percentages`).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.compensation.hourly.models import PercentageSettlement
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.decision.rules import _ccnl_rule
from ccnl_engine.extra_month.settlement.services import ExtraMonthSettlement
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.facade import (
    EmployeeWithholdingItem,
    HourlyPercentageEarning,
)
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.capability.rule.services import Rule
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.compensation.hourly.models import HourlyPercentage
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.withholding.schedule.models import WithholdingSlot

__all__ = [
    "ACCRUED",
    "PAID",
    "PercentageAmount",
    "percentage_decisions",
    "percentage_rules",
    "percentage_settlement",
    "run_percentages",
    "upcoming_percentages",
]

_ZERO = Decimal(0)
_ONE = Decimal(1)
_KIND = "hourly_percentage_earning"
_ACCRUAL_KIND = "employee_withholding_item"
#: Reason of the decision of a percentage paid to the worker.
PAID = "hourly_percentage_paid"
#: Reason of the decision of a percentage accrued with the Cassa Edile.
ACCRUED = "cassa_edile_accrued"


@dataclass(frozen=True)
class PercentageAmount:
    """One percentage of a run on the hours worked.

    Attributes:
        percentage: The clause of the CCNL.
        base: Base salary and named allowances paid on the hours.
        rate: Rate in force on the competence date.
        amount: Gross earning, ``base`` x ``rate`` to the cent.
        net_rate: Rate accrued with the Cassa Edile, ``None`` for cash.
        accrual: Amount withheld from the pay for the Cassa Edile.
    """

    percentage: HourlyPercentage
    base: Decimal
    rate: Decimal
    amount: Decimal
    net_rate: Decimal | None = None
    accrual: Decimal = _ZERO


def _base(chain: MonthlyPayChain, percentage: HourlyPercentage) -> Decimal:
    """Return the base salary and the named allowances of ``chain``.

    Returns:
        The base of ``percentage`` on the pay of ``chain``.
    """
    named = percentage.base_allowances
    return chain.base + sum((v for a, v in chain.allowances if a.code in named), _ZERO)


def run_percentages(ctx: RunContext) -> tuple[PercentageAmount, ...]:
    """Return the percentages the run pays on the hours worked.

    Returns:
        One amount per percentage of the CCNL; none unless the run pays
        the worker by the hour on stated hours.
    """
    spec = ctx.contract.ccnl.parameters.hourly_pay
    hourly = ctx.proration.hourly
    if spec is None or hourly is None or hourly.hours is None:
        return ()
    chain, day = ctx.chain, ctx.contract.tctx.competence
    amounts: list[PercentageAmount] = []
    with rule_scope(ruleset=ctx.contract.ccnl.meta.ccnl_id, feature="base_salary"):
        for percentage in spec.percentages:
            base = _base(chain, percentage)
            rate = percentage.rate.value_at(day)
            series = percentage.net_rate
            net = None if series is None else series.value_at(day)
            accrual = _ZERO if net is None else money(base * net)
            amounts.append(
                PercentageAmount(
                    percentage, base, rate, money(base * rate), net, accrual
                )
            )
    return tuple(amounts)


def _postings(
    ctx: RunContext, amount: PercentageAmount, policies: tuple[str, str]
) -> tuple[tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Return the earning of one percentage and the accrual withheld from it.

    Returns:
        The earning on ``CASH_EARNINGS``, then the Cassa Edile accrual on
        ``BILATERAL_FUND_EMPLOYEE`` when it has one.
    """
    payment = ctx.contract.tctx.payment
    clause = amount.percentage
    item_id = f"{clause.code.lower()}_{ctx.run_id}"
    items: list[PayItem] = [
        HourlyPercentageEarning(
            item_id=item_id,
            competence_period=ctx.cp,
            payment_date=payment,
            quantity=_ONE,
            amount=amount.amount,
            source=f"{clause.description}: {amount.rate} of {amount.base}",
        )
    ]
    entries = [
        _make_entry(
            item_id,
            item_id,
            _KIND,
            ctx.cp,
            payment,
            AccountKind.CASH_EARNINGS,
            amount.amount,
            policy_id=policies[0],
        )
    ]
    if amount.accrual > _ZERO:
        accrual_id = f"{clause.code.lower()}_accrual_{ctx.run_id}"
        items.append(
            EmployeeWithholdingItem(
                item_id=accrual_id,
                competence_period=ctx.cp,
                payment_date=payment,
                quantity=_ONE,
                amount=amount.accrual,
                source=f"Cassa Edile accrual: {amount.net_rate} of {amount.base}",
            )
        )
        entries.append(
            _make_entry(
                accrual_id,
                accrual_id,
                _ACCRUAL_KIND,
                ctx.cp,
                payment,
                AccountKind.BILATERAL_FUND_EMPLOYEE,
                amount.accrual,
                policy_id=policies[1],
            )
        )
    return tuple(items), tuple(entries)


def percentage_settlement(ctx: RunContext) -> ExtraMonthSettlement:
    """Return the percentages of the run with the bases they enter.

    Returns:
        The earnings and accruals with their ledger entries, the earnings
        added to the bases their policy names; nothing without any.
    """
    amounts = tuple(a for a in run_percentages(ctx) if a.amount > _ZERO)
    if not amounts:
        return ExtraMonthSettlement()
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    withheld = _require_resolution(ctx.resolver, _ACCRUAL_KIND, ctx.policy_context)
    policies = (resolution.policy_id, withheld.policy_id)
    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    for amount in amounts:
        posted = _postings(ctx, amount, policies)
        items, entries = items + posted[0], entries + posted[1]
    treatment = _treatment_from_resolution(resolution)
    total = sum((a.amount for a in amounts), _ZERO)
    return ExtraMonthSettlement(
        items=items,
        entries=entries,
        inps_base=total if treatment.inps else _ZERO,
        tfr_base=total if treatment.tfr else _ZERO,
        irpef_base=total if treatment.irpef else _ZERO,
    )


def percentage_decisions(ctx: RunContext) -> tuple[CalculationDecision, ...]:
    """Return one ``base_salary`` decision per percentage of the run.

    Returns:
        A decision with reason ``hourly_percentage_paid`` or
        ``cassa_edile_accrued``, its base, rate and accrual; none unless
        the run pays the worker by the hour on stated hours.
    """
    ccnl = ctx.contract.ccnl
    rule, version = _ccnl_rule(ccnl, ctx.contract.tctx.competence.year)
    decisions: list[CalculationDecision] = []
    for amount in run_percentages(ctx):
        clause = amount.percentage
        accrued = clause.settlement is PercentageSettlement.CASSA_EDILE
        inputs: dict[str, Decimal | str] = {
            "settlement": clause.settlement.value,
            "base": amount.base,
            "rate": amount.rate,
            "base_allowances": ",".join(clause.base_allowances) or "none",
        }
        if amount.net_rate is not None:
            inputs |= {"net_rate": amount.net_rate, "accrual": amount.accrual}
        decisions.append(
            CalculationDecision(
                capability="base_salary",
                status=CalculationStatus.FINAL,
                reason_code=ACCRUED if accrued else PAID,
                rule=f"{rule}:hourly_pay.percentages[{clause.code}]",
                rule_version=version,
                inputs=inputs,
                source=clause.provenance.location,
                amount=amount.amount,
            )
        )
    return tuple(decisions)


def percentage_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the clauses of the percentages the run pays.

    Returns:
        Each clause with its provenance; empty when the run pays none.
    """
    rule = _ccnl_rule(ctx.contract.ccnl, ctx.contract.tctx.competence.year)[0]
    return tuple(
        (
            f"{rule}:hourly_pay.percentages[{a.percentage.code}]",
            a.percentage.provenance,
        )
        for a in run_percentages(ctx)
    )


def upcoming_percentages(
    ccnl: CCNL,
    chain: MonthlyPayChain,
    day: date,
    upcoming: tuple[WithholdingSlot, ...],
) -> Decimal:
    """Return the percentages the regular payments still to come will pay.

    The IRPEF projection values each upcoming slot with the monthly pay
    chain; a worker paid by the hour also earns the percentages on it, as
    on a full month of hours.

    Returns:
        The percentages of ``chain`` times the upcoming regular slots; zero
        for a CCNL that pays no percentage.
    """
    spec = ccnl.parameters.hourly_pay
    percentages = () if spec is None else spec.percentages
    with rule_scope(ruleset=ccnl.meta.ccnl_id, feature="base_salary"):
        monthly = sum(
            (money(_base(chain, p) * p.rate.value_at(day)) for p in percentages),
            _ZERO,
        )
    regular = sum(1 for slot in upcoming if slot.run.run_kind == RunKind.REGULAR)
    return monthly * regular
