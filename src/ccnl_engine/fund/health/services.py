"""The contractual funds of a run: the shares, or the element instead.

For every fund of the CCNL that covers the worker
(:class:`~ccnl_engine.fund.health.models.ContractualFund`): a fund the CCNL
owes with no alternative is paid; for a fund with an elemento distinto, or
one way of a group, the employer states whether it pays it
(``EmployerProfile.contractual_funds``).  A fund paid posts the employer
share as a cost, with the INPS solidarity contribution on it, and withholds
the worker share, out of the IRPEF base when the fund is a health fund; a
fund not paid owes the worker its elemento distinto, an earning in the INPS
and IRPEF bases (and the TFR base when the CCNL says so).  The shares are
per capita: a fixed share is due in full whatever the part time, a share in
percent follows the minimo of the run.  The element is pay: it follows the
minimo of the run (part time, partial month, extra-month ratei) unless the
CCNL owes it in full.  Left unstated, the choices are a missing fact: the
owed funds are posted, the others are not, and the run is not payable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.employment.inputs import Permanent
from ccnl_engine.extra_month.settlement.services import ExtraMonthSettlement
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.models import (
    EmployeeWithholdingItem,
    EmployerContributionItem,
    FixedAllowanceEarning,
    WelfareItem,
)
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _make_entry
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from ccnl_engine.agreement.validity.rules import TimeSeries
    from ccnl_engine.fund.health.models import ContractualFund, FundAmount
    from ccnl_engine.period.context.services import RunContext

__all__ = ["CAPABILITY", "FACT", "FundOutcome", "contractual_funds"]

#: Capability the funds are decided and reported under.
CAPABILITY = "contractual_funds"
#: Public fact the employer states the funds it pays with.
FACT = "contractual_funds"
_ZERO = Decimal(0)
_MONTHS = Decimal(12)
_ONE = Decimal(1)
_EXTRA_KINDS = frozenset({RunKind.THIRTEENTH, RunKind.FOURTEENTH})


@dataclass(frozen=True)
class FundOutcome:
    """What the contractual funds add to a run.

    Attributes:
        settlement: Items, ledger entries and bases of the run.
        decisions: One decision per fund that covers the worker.
        issues: The missing fact, when the funds are not stated.
    """

    settlement: ExtraMonthSettlement = field(default_factory=ExtraMonthSettlement)
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()


def contractual_funds(ctx: RunContext) -> FundOutcome:
    """Return the shares or the elements of the funds of the run.

    Returns:
        The outcome; empty when no fund of the CCNL covers the worker on
        this run.
    """
    covered = tuple(
        f for f in ctx.contract.ccnl.parameters.health_funds if _covers(ctx, f)
    )
    if not covered:
        return FundOutcome()
    stated = ctx.request.employer.contractual_funds
    funds = _one_per_group(covered, stated)
    chosen = tuple(f for f in funds if _a_choice(f))
    if stated is None and chosen:
        owed = tuple(f for f in funds if not _a_choice(f))
        outcome = _post(ctx, owed, frozenset(f.code for f in owed))
        return FundOutcome(
            settlement=outcome.settlement,
            decisions=outcome.decisions
            + tuple(_decision(ctx, f, "required_fact_missing", None) for f in chosen),
            issues=(_unknown_issue(chosen),),
        )
    paid = frozenset(stated or ()) | frozenset(
        f.code for f in funds if not _a_choice(f)
    )
    return _post(ctx, funds, paid)


def _a_choice(fund: ContractualFund) -> bool:
    """Whether the employer chooses between ``fund`` and something else.

    A fund with an elemento distinto, or one way of a group, is a choice
    the employer states; a fund the CCNL owes with no alternative is paid
    whatever the employer states.

    Returns:
        True when the fund needs ``EmployerProfile.contractual_funds``.
    """
    return fund.alternative is not None or fund.group is not None


def _post(
    ctx: RunContext, funds: tuple[ContractualFund, ...], paid: frozenset[str]
) -> FundOutcome:
    """Post the shares of the funds paid and the elements of the others.

    Returns:
        The settlement and one decision per fund.
    """
    parts = [_paid(ctx, f) if f.code in paid else _element(ctx, f) for f in funds]
    return FundOutcome(
        settlement=ExtraMonthSettlement(
            items=tuple(i for p in parts for i in p.items),
            entries=tuple(e for p in parts for e in p.entries),
            inps_base=sum((p.inps_base for p in parts), _ZERO),
            tfr_base=sum((p.tfr_base for p in parts), _ZERO),
            irpef_base=sum((p.irpef_base for p in parts), _ZERO),
        ),
        decisions=tuple(
            _decision(
                ctx,
                f,
                "fund_paid" if f.code in paid else "alternative_element_paid",
                p,
            )
            for f, p in zip(funds, parts, strict=True)
        ),
    )


def _one_per_group(
    funds: tuple[ContractualFund, ...], stated: frozenset[str] | None
) -> tuple[ContractualFund, ...]:
    """Keep one way of each group of alternative funds.

    Returns:
        The ungrouped funds and, of each group, the funds the employer
        names, or its first fund when it names none (or states nothing).
    """
    named = stated or frozenset()
    kept: list[ContractualFund] = []
    for fund in funds:
        if fund.group is None:
            kept.append(fund)
            continue
        members = [f for f in funds if f.group == fund.group]
        chosen = [f for f in members if f.code in named] or members[:1]
        if fund in chosen:
            kept.append(fund)
    return tuple(kept)


def _covers(ctx: RunContext, fund: ContractualFund) -> bool:
    """Whether ``fund`` covers the worker on this run.

    Returns:
        True when the category, the level and the contract type are covered
        and the fund or its element is due on the kind of run.
    """
    if fund.categories is not None and ctx.worker_category not in fund.categories:
        return False
    if fund.levels is not None and ctx.contract.level.code not in fund.levels:
        return False
    if fund.permanent_only and not isinstance(ctx.request.contract_type, Permanent):
        return False
    extra = ctx.run_kind in _EXTRA_KINDS
    if fund.charged_in_month is not None:
        return not extra and _charged_now(ctx, fund.charged_in_month)
    return not extra or fund.extra_months or fund.alternative_extra_months


def _charged_now(ctx: RunContext, month: TimeSeries) -> bool:
    """Whether the run falls in the month a yearly amount is charged.

    Returns:
        True when the competence month is the month of its year; false
        before the first year the series names.
    """
    day = ctx.contract.tctx.competence
    period = month.period_at(day)
    return period is not None and period.value == day.month


def _monthly(
    ctx: RunContext,
    fund: ContractualFund,
    amount: FundAmount | None,
    *,
    scaled: bool = False,
    whole_year: bool = False,
) -> Decimal:
    """Return ``amount`` on the minimo of the run.

    Returns:
        The fixed amount, scaled like the minimo when ``scaled``, plus the
        rate of the minimo and of the allowances the fund names in
        ``rate_allowances``, as the run pays them, to the cent; zero for no
        amount.
    """
    if amount is None:
        return _ZERO
    day = ctx.contract.tctx.competence
    paid = ctx.chain.base
    rate_base = paid + sum(
        (v for a, v in ctx.chain.allowances if a.code in fund.rate_allowances),
        _ZERO,
    )
    full = ctx.contract.level.base_salary.value_at(day)
    fixed = _ZERO if amount.monthly is None else amount.monthly.value_at(day)
    if amount.annual is not None:
        fixed += amount.annual.value_at(day) / (_ONE if whole_year else _MONTHS)
    rate = _ZERO if amount.rate is None else amount.rate.value_at(day)
    if scaled:
        fixed = fixed * paid / full
    return money(fixed + rate * rate_base)


def _extra(ctx: RunContext) -> bool:
    return ctx.run_kind in _EXTRA_KINDS


def _paid(ctx: RunContext, fund: ContractualFund) -> ExtraMonthSettlement:
    if _extra(ctx) and not fund.extra_months:
        return ExtraMonthSettlement()
    whole = fund.charged_in_month is not None
    employer = _monthly(ctx, fund, _employer_share(ctx, fund), whole_year=whole)
    employee = _monthly(ctx, fund, fund.employee, whole_year=whole)
    solidarity = money(employer * fund.solidarity_rate)
    if fund.welfare:
        return _welfare(ctx, fund, employer)
    cp, payment = ctx.cp, ctx.contract.tctx.payment
    base = f"{fund.code}_{ctx.run_id}"
    items: list[EmployerContributionItem | EmployeeWithholdingItem] = []
    entries = []
    for suffix, amount, account, item_type, kind in (
        (
            "er",
            employer,
            AccountKind.BILATERAL_FUND_EMPLOYER,
            EmployerContributionItem,
            "employer_contribution_item",
        ),
        (
            "solidarity",
            solidarity,
            AccountKind.EMPLOYER_CONTRIBUTIONS,
            EmployerContributionItem,
            "employer_contribution_item",
        ),
        (
            "emp",
            employee,
            AccountKind.BILATERAL_FUND_EMPLOYEE,
            EmployeeWithholdingItem,
            "employee_withholding_item",
        ),
    ):
        if not amount:
            continue
        item_id = f"{base}_{suffix}"
        items.append(
            item_type(
                item_id=item_id,
                competence_period=cp,
                payment_date=payment,
                quantity=Decimal(1),
                amount=amount,
                source=fund.description,
            )
        )
        entries.append(
            _make_entry(item_id, item_id, kind, cp, payment, account, amount)
        )
    return ExtraMonthSettlement(
        items=tuple(items),
        entries=tuple(entries),
        irpef_base=-employee if fund.employee_deductible else _ZERO,
    )


def _employer_share(ctx: RunContext, fund: ContractualFund) -> FundAmount:
    """Return the employer share of the worker: reduced for short part time.

    Returns:
        ``fund.reduced_employer`` when the worker works at most
        ``fund.reduced_up_to_weekly_hours`` a week, ``fund.employer``
        otherwise.
    """
    limit, reduced = fund.reduced_up_to_weekly_hours, fund.reduced_employer
    hours = ctx.request.weekly_hours
    if limit is None or reduced is None or hours is None:
        return fund.employer
    return reduced if Decimal(hours.value) <= limit else fund.employer


def _welfare(
    ctx: RunContext, fund: ContractualFund, amount: Decimal
) -> ExtraMonthSettlement:
    """Post a welfare benefit the employer makes available to the worker.

    Returns:
        A welfare item and its non-cash benefit entry, an employer cost
        outside the pay and its bases.
    """
    item_id = f"{fund.code}_{ctx.run_id}_welfare"
    cp, payment = ctx.cp, ctx.contract.tctx.payment
    item = WelfareItem(
        item_id=item_id,
        competence_period=cp,
        payment_date=payment,
        quantity=Decimal(1),
        amount=amount,
        source=fund.description,
    )
    entry = _make_entry(
        item_id,
        item_id,
        "welfare_item",
        cp,
        payment,
        AccountKind.NON_CASH_BENEFITS,
        amount,
    )
    return ExtraMonthSettlement(items=(item,), entries=(entry,))


def _element(ctx: RunContext, fund: ContractualFund) -> ExtraMonthSettlement:
    if fund.alternative is None or (_extra(ctx) and not fund.alternative_extra_months):
        return ExtraMonthSettlement()
    amount = _monthly(ctx, fund, fund.alternative, scaled=fund.alternative_scaled)
    item_id = f"{fund.code}_element_{ctx.run_id}"
    cp, payment = ctx.cp, ctx.contract.tctx.payment
    item = FixedAllowanceEarning(
        item_id=item_id,
        competence_period=cp,
        payment_date=payment,
        quantity=Decimal(1),
        amount=amount,
        source=f"elemento distinto in place of {fund.description}",
        allowance_code=f"{fund.code}_element",
    )
    entry = _make_entry(
        item_id,
        item_id,
        "fixed_allowance_earning",
        cp,
        payment,
        AccountKind.CASH_EARNINGS,
        amount,
    )
    return ExtraMonthSettlement(
        items=(item,),
        entries=(entry,),
        inps_base=amount,
        tfr_base=amount if fund.alternative_tfr else _ZERO,
        irpef_base=amount,
    )


def _decision(
    ctx: RunContext,
    fund: ContractualFund,
    reason: str,
    part: ExtraMonthSettlement | None,
) -> CalculationDecision:
    ccnl = ctx.contract.ccnl
    ruleset = ccnl.ruleset
    amount = None if part is None else sum((e.amount for e in part.entries), _ZERO)
    location = fund.provenance.location
    return CalculationDecision(
        capability=CAPABILITY,
        status=CalculationStatus.FINAL
        if part is not None
        else CalculationStatus.INCOMPLETE,
        reason_code=reason,
        rule=f"ccnl/{ccnl.meta.ccnl_id}" if ruleset is None else ruleset.id,
        rule_version=str(ctx.contract.tctx.competence.year)
        if ruleset is None
        else ruleset.version,
        inputs={"fund": fund.code},
        source=location,
        amount=amount,
    )


def _unknown_issue(funds: tuple[ContractualFund, ...]) -> CalculationIssue:
    names = ", ".join(f.code for f in funds)
    return CalculationIssue(
        code="contractual_funds_unknown",
        message=(
            f"the CCNL owes the funds {names} for this worker, or an elemento "
            "distinto when the employer does not pay them, and the employer "
            "does not state which it pays: nothing is posted; state "
            "EmployerProfile.contractual_funds (an empty set for none)"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=FACT,
        capability=CAPABILITY,
    )
