"""Decisions of the INPS contributions of the worker and of the employer.

Both read the INPS rules of the year (or the flat hourly contributions of
a domestic CCNL) and record the base the contributions were computed on:
the pay chain and events of the run raised to the minimum base
(:mod:`~ccnl_engine.payroll.service.minimum_base`), the year-to-date base
and how the IVS massimale entered.  They carry no amount while the
massimale or the minimum base is undetermined.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._naspi import with_naspi
from ccnl_engine.payroll.application.period._rule_lookup import contract_rules
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.service._contributions_rates import resolve_rates
from ccnl_engine.provenance.source.models_chain import RuleProvenance

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.handlers._totals import _EventTotals
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.period._ivs_ceiling import IvsCeiling
    from ccnl_engine.payroll.application.period._pipeline import RunAmounts
    from ccnl_engine.payroll.application.period._rule_lookup import Rule
    from ccnl_engine.payroll.domain.minimum_base import MinimumBase

__all__ = ["inps_decisions"]

_NONE = "none"
_SIDES = ("inps_employee", "inps_employer")

type _Inputs = dict[str, Decimal | str]


def _pair(
    ctx: RunContext,
    reason_code: str,
    rule: Rule,
    inputs: tuple[_Inputs, _Inputs],
    amounts: tuple[Decimal | None, Decimal | None],
    status: CalculationStatus = CalculationStatus.FINAL,
) -> tuple[CalculationDecision, CalculationDecision]:
    """Return the ``inps_employee`` and ``inps_employer`` decisions.

    Returns:
        The two decisions on the same rule, reason and status.
    """
    rules = ctx.contract.year_rules
    ruleset = rules.inps_ruleset
    rule_id, provenance = rule
    source = provenance.location if isinstance(provenance, RuleProvenance) else None
    employee, employer = (
        CalculationDecision(
            capability=capability,
            status=status,
            reason_code=reason_code,
            rule=rule_id,
            rule_version=str(rules.year) if ruleset is None else ruleset.version,
            inputs=side_inputs,
            source=source,
            amount=amount,
        )
        for capability, side_inputs, amount in zip(_SIDES, inputs, amounts, strict=True)
    )
    return employee, employer


def _minimum_inputs(actual: Decimal, minimum: MinimumBase | None) -> _Inputs:
    """Return the decision inputs of the minimum INPS base of the run.

    Returns:
        The base before the minimum, the minimum (``none`` when not fixed),
        the highest minimum of the month and how the minimum entered the
        base; ``not_modelled`` without a rule.
    """
    if minimum is None:
        return {"minimum_base": "not_modelled"}
    return {
        "actual_base": actual,
        "minimum_base": _NONE if minimum.minimum is None else minimum.minimum,
        "minimum_base_bound": minimum.bound,
        "minimum_base_reason": minimum.reason.value,
    }


def _ivs_ceiling_state(ivs: IvsCeiling | None) -> str:
    """Return how the IVS massimale entered the contributions of the run.

    Returns:
        ``applied``, ``not_applied``, or ``undetermined`` when it depends
        on a missing contribution history; the ``ivs_ceiling_eligibility``
        decision says why.
    """
    if ivs is None:
        return "not_applied"
    if ivs.undetermined:
        return "undetermined"
    return "applied" if ivs.applies else "not_applied"


def inps_decisions(
    ctx: RunContext, totals: _EventTotals, amounts: RunAmounts
) -> tuple[CalculationDecision, CalculationDecision]:
    """Return the INPS decisions of the worker and of the employer.

    Returns:
        The ``inps_employee`` and ``inps_employer`` decisions, with reason
        ``rates_applied`` for the ordinary rates of the contract,
        ``minimum_base_undetermined`` when the base may be below a minimum
        the bundle cannot fix, or ``domestic_hourly_rates`` for the flat
        hourly contributions of a domestic CCNL.  The employer decision
        records the NASpI surcharge, and is incomplete while it is
        undetermined.
    """
    year_rules = ctx.contract.year_rules
    rules = contract_rules(ctx)["inps_employee"]
    actual = ctx.monthly_gross + totals.inps_base
    base = amounts.inps_base(actual)
    breakdown = amounts.contribution_breakdown
    sides = (breakdown.employee, breakdown.employer)
    if year_rules.inps is None:
        domestic: _Inputs = {"base": base}
        employee, employer = _pair(
            ctx, "domestic_hourly_rates", rules[1], (domestic, domestic), sides
        )
        return employee, with_naspi(ctx, employer)
    rates = resolve_rates(year_rules, ctx.request.contract_type, ctx.worker_category)
    ivs, minimum = amounts.ivs_ceiling, amounts.minimum_base
    below_minimum = minimum is not None and minimum.undetermined
    undetermined = below_minimum or (ivs is not None and ivs.undetermined)
    common: _Inputs = {
        "base": base,
        "ytd_base": ctx.ytd_inps_base,
        "ivs_ceiling": _ivs_ceiling_state(ivs),
        **_minimum_inputs(actual, minimum),
    }
    employee, employer = _pair(
        ctx,
        "minimum_base_undetermined" if below_minimum else "rates_applied",
        rules[0],
        (
            {**common, "rate": rates.employee_rate},
            {**common, "rate": rates.employer_rate},
        ),
        (None, None) if undetermined else sides,
        CalculationStatus.INCOMPLETE if undetermined else CalculationStatus.FINAL,
    )
    return employee, with_naspi(ctx, employer)
