"""Decisions of the base stages every run executes.

One decision per stage: the pay chain (``base_salary``), the INPS
contributions of the worker and of the employer, the TFR accrual and the
ordinary IRPEF withholding.  Each names the payable rule it read, as listed
by :mod:`~ccnl_engine.payroll.application.period._rule_lookup`, and its
source when the rule records one.  The decisions other capabilities take on
the same amounts (apprenticeship scaling, seniority, credits, surtax, the
withholding cap) are referenced by capability, not repeated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._inps_decisions import inps_decisions
from ccnl_engine.payroll.application.period._rule_lookup import (
    contract_rules,
    tax_rules,
)
from ccnl_engine.payroll.application.period._run_decisions import _ccnl_rule
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.provenance.domain.chain import RuleProvenance

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.handlers._totals import _EventTotals
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.period._pipeline import RunAmounts
    from ccnl_engine.payroll.application.period._rule_lookup import Rule
    from ccnl_engine.tax.domain.ruleset import YearRules

__all__ = ["base_stage_decisions"]

_NONE = "none"

#: Credit and tax decisions the IRPEF of the run is netted with.
_IRPEF_REFERENCES = (
    "family_deductions",
    "ulteriore_detrazione_lavoro",
    "trattamento_integrativo",
    "foreign_tax_credit",
)


def _decision(
    capability: str,
    reason_code: str,
    rule: Rule,
    version: str,
    inputs: dict[str, Decimal | str],
    amount: Decimal | None,
    status: CalculationStatus = CalculationStatus.FINAL,
) -> CalculationDecision:
    rule_id, provenance = rule
    return CalculationDecision(
        capability=capability,
        status=status,
        reason_code=reason_code,
        rule=rule_id,
        rule_version=version,
        inputs=inputs,
        source=(
            provenance.location if isinstance(provenance, RuleProvenance) else None
        ),
        amount=amount,
    )


def _tax_version(rules: YearRules) -> str:
    return str(rules.year) if rules.ruleset is None else rules.ruleset.version


def _base_salary(ctx: RunContext) -> CalculationDecision:
    """Return the decision of the pay chain of the run.

    The rule is the base salary period of the level in force on the
    competence date; the allowances and the additional months the chain
    also reads are listed with their provenance in the capability report.

    The regular run of a partly employed month records its employed span
    and payable days; without a CCNL partial-month rule it is provisional
    and carries no amount.

    Returns:
        A decision with reason ``pay_chain_applied``, ``pay_chain_prorated``
        or ``partial_month_rule_missing``, and the chain gross.
    """
    contract, chain, proration = ctx.contract, ctx.chain, ctx.proration
    rules = contract_rules(ctx)["base_salary"]
    rule = next(
        (r for r in rules if ".base_salary[" in r[0]),
        (_ccnl_rule(contract.ccnl, contract.tctx.competence.year)[0], None),
    )
    codes = ",".join(allowance.code for allowance, _ in chain.allowances)
    return _decision(
        "base_salary",
        proration.reason or "pay_chain_applied",
        rule,
        _ccnl_rule(contract.ccnl, contract.tctx.competence.year)[1],
        {
            "level": contract.level.code,
            "run_kind": ctx.run_kind.value,
            "minimum": chain.base,
            "seniority": chain.seniority,
            "allowances": chain.allowances_total,
            "allowance_codes": codes or _NONE,
            "apprenticeship": (
                _NONE if ctx.apprenticeship is None else "apprenticeship_scaling"
            ),
            **proration.inputs(),
        },
        None if proration.missing else ctx.monthly_gross,
        CalculationStatus.PROVISIONAL if proration.missing else CalculationStatus.FINAL,
    )


def _tfr(
    ctx: RunContext, totals: _EventTotals, amounts: RunAmounts
) -> CalculationDecision:
    """Return the decision of the TFR accrued on the run.

    Returns:
        A decision with reason ``accrued``, the account the TFR goes to
        (the company accrual, the Fondo Tesoreria or the pension fund) and
        the art. 2120 c.c. quota with the additional IVS of L. 297/1982
        deducted from it.
    """
    year_rules = ctx.contract.year_rules
    tfr = amounts.amounts.tfr
    treasury = tfr.treasury_fund
    return _decision(
        "tfr",
        "accrued",
        tax_rules(ctx)["tfr"][0],
        _tax_version(year_rules),
        {
            "base": ctx.monthly_gross + ctx.chain.in_kind_total + totals.tfr_base,
            "in_kind": ctx.chain.in_kind_total,
            "accrual_divisor": year_rules.tfr.accrual_divisor,
            "quota": tfr.quota,
            "additional_ivs_base": tfr.ivs_base,
            "additional_ivs_rate": tfr.ivs_rate,
            "additional_ivs_deduction": tfr.deduction,
            "treasury_fund": "unknown" if treasury is None else str(treasury).lower(),
            "account": tfr.destination,
        },
        tfr.amount,
    )


def _irpef(ctx: RunContext, amounts: RunAmounts) -> CalculationDecision:
    """Return the decision of the ordinary IRPEF of the run.

    The amount is the withholding the conguaglio YTD computed for the run,
    before the pay cap: a ``withholding_shortfall`` decision records what
    the cap carried to the next runs.  A negative amount is a refund.

    Returns:
        A decision with reason ``withheld``, ``refunded`` or ``nothing_due``,
        the annual components of the tax and the credit decisions it is
        netted with.
    """
    computation = amounts.tax_computation
    ordinary = computation.ordinary_tax
    reason = "withheld" if ordinary > 0 else "refunded" if ordinary < 0 else ""
    taken = {d.capability for d in amounts.amounts.decisions}
    references = ",".join(c for c in _IRPEF_REFERENCES if c in taken)
    projected = amounts.amounts.projected_taxable
    inputs: dict[str, Decimal | str] = {
        "projected_taxable": _NONE if projected is None else projected,
        **{component.name: component.amount for component in computation.components},
        "withholding_due": computation.withholding_due,
        "withholding_slots": str(ctx.withholding_schedule.run_count.value),
        "decisions": references or _NONE,
    }
    return _decision(
        "irpef",
        reason or "nothing_due",
        tax_rules(ctx)["irpef"][0],
        _tax_version(ctx.contract.year_rules),
        inputs,
        ordinary,
    )


def base_stage_decisions(
    ctx: RunContext, totals: _EventTotals, amounts: RunAmounts
) -> tuple[CalculationDecision, ...]:
    """Return the decisions of the base stages of the run.

    An employer that is not a withholding agent computes no IRPEF: its
    ``irpef`` capability keeps the not-applicable decision of
    :mod:`~ccnl_engine.payroll.service.withholding_agent`.

    Returns:
        The ``base_salary``, ``inps_employee``, ``inps_employer`` and
        ``tfr`` decisions, then ``irpef`` for a withholding agent.
    """
    decisions = (
        _base_salary(ctx),
        *inps_decisions(ctx, totals, amounts),
        _tfr(ctx, totals, amounts),
    )
    if not ctx.withholding_agent:
        return decisions
    return (*decisions, _irpef(ctx, amounts))
