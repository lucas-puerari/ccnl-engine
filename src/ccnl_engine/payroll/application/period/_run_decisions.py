"""Calculation decisions of the contract and tax capabilities of one run.

Each builder returns the decision a capability took in the run, or ``None``
when the capability did not run, so the capability trace can tell a
capability that decided (even a zero amount, with its reason) from one that
never executed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.category import parse_worker_category
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.contract.domain.compensation import Level
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.service.types import ApprenticeshipScaling
    from ccnl_engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.tax.domain.variable_pay import PdRRules

_NONE = "none"


def _final(
    capability: str,
    reason_code: str,
    rule: tuple[str, str],
    inputs: dict[str, Decimal | str],
    amount: Decimal | None = None,
) -> CalculationDecision:
    rule_id, rule_version = rule
    return CalculationDecision(
        capability=capability,
        status=CalculationStatus.FINAL,
        reason_code=reason_code,
        rule=rule_id,
        rule_version=rule_version,
        inputs=inputs,
        amount=amount,
    )


def _ccnl_rule(ccnl: CCNL, year: int) -> tuple[str, str]:
    """Return the rule identity of a CCNL: its ruleset, or its slug and year.

    Returns:
        ``(rule, rule_version)`` of ``ccnl``.
    """
    if ccnl.ruleset is not None:
        return ccnl.ruleset.id, ccnl.ruleset.version
    return f"ccnl/{ccnl.meta.ccnl_id}", str(year)


def worker_category_decision(
    ccnl: CCNL,
    level: Level,
    declared: WorkerCategory | str | None,
    category: WorkerCategory | None,
    year: int,
) -> CalculationDecision | None:
    """Return the decision recording the worker category used in the run.

    Args:
        ccnl: The applicable CCNL.
        level: The worker's level within ``ccnl``.
        declared: Category declared on the employment, or ``None``.
        category: Category resolved for pay and contributions.
        year: Competence year, the rule version when the CCNL has no ruleset.

    Returns:
        A decision with reason ``fixed_by_level`` when the level admits a
        single category, ``declared`` when the employment gave it; ``None``
        when no category was used.
    """
    if category is None:
        return None
    declared_category = parse_worker_category(declared)
    return _final(
        "worker_category",
        "fixed_by_level" if level.category is not None else "declared",
        _ccnl_rule(ccnl, year),
        {
            "category": category.value,
            "declared": _NONE if declared_category is None else declared_category.value,
            "level": level.code,
        },
    )


def apprenticeship_scaling_decision(
    ccnl: CCNL,
    scaling: ApprenticeshipScaling | None,
    year: int,
) -> CalculationDecision | None:
    """Return the decision recording the apprenticeship percentage of the run.

    Args:
        ccnl: The applicable CCNL.
        scaling: Percentage and components of a percentage apprenticeship.
        year: Competence year, the rule version when the CCNL has no ruleset.

    Returns:
        A decision with reason ``percentage_applied``, the percentage and the
        comma-separated codes of the scaled and unscaled components;
        ``None`` when no percentage apprenticeship applies.
    """
    if scaling is None:
        return None
    return _final(
        "apprenticeship_scaling",
        "percentage_applied",
        _ccnl_rule(ccnl, year),
        {
            "percentage": scaling.percentage,
            "scaled": ",".join(scaling.scaled),
            "unscaled": ",".join(scaling.unscaled) or _NONE,
        },
    )


def family_deduction_decision(
    total: Decimal, rules: FamilyDeductionRules | None
) -> CalculationDecision | None:
    """Return the decision recording the annual Art. 12 TUIR deductions.

    Args:
        total: Annual family deductions computed for the run.
        rules: Family deduction rules, ``None`` when no family composition
            was given and the deductions were not computed.

    Returns:
        A decision with reason ``deductions_applied`` or ``no_deduction_due``
        and the annual amount; ``None`` when the deductions were not computed.
    """
    if rules is None:
        return None
    return _final(
        "family_deductions",
        "deductions_applied" if total else "no_deduction_due",
        ("art12-tuir", str(rules.year)),
        {},
        total,
    )


def pdr_decision(
    substitute_base: Decimal,
    eligible: Decimal,
    substitute_tax: Decimal,
    rules: PdRRules,
    year: int,
) -> CalculationDecision | None:
    """Return the decision recording the PdR substitute tax of the run.

    Args:
        substitute_base: Bonus amount routed to the PdR substitute tax.
        eligible: Part of it within the annual limit still available.
        substitute_tax: Substitute tax on ``eligible``.
        rules: PdR rules of the year.
        year: Tax year, the rule version when the rules have no ruleset.

    Returns:
        A decision with reason ``substitute_tax_applied``, or
        ``annual_limit_reached`` when nothing is left of the annual limit,
        and the substitute tax as amount; ``None`` when no bonus was routed
        to the substitute tax.
    """
    if not substitute_base:
        return None
    rule = (
        ("pdr", str(year))
        if rules.ruleset is None
        else (rules.ruleset.id, rules.ruleset.version)
    )
    return _final(
        "bonus_pdr",
        "substitute_tax_applied" if eligible else "annual_limit_reached",
        rule,
        {"eligible_amount": eligible, "ordinary_amount": substitute_base - eligible},
        substitute_tax,
    )


def contract_decisions(
    ccnl: CCNL,
    level: Level,
    declared: WorkerCategory | str | None,
    category: WorkerCategory | None,
    seniority: CalculationDecision,
    year: int,
    apprenticeship: ApprenticeshipScaling | None = None,
) -> tuple[CalculationDecision, ...]:
    """Return the worker category, seniority and apprenticeship decisions.

    Args:
        ccnl: The applicable CCNL.
        level: The worker's level within ``ccnl``.
        declared: Category declared on the employment, or ``None``.
        category: Category resolved for pay and contributions.
        seniority: The seniority decision of the run, always taken.
        year: Competence year, the rule version when the CCNL has no ruleset.
        apprenticeship: Percentage scaling of a percentage apprenticeship.

    Returns:
        The decisions of :func:`worker_category_decision`, the seniority
        and :func:`apprenticeship_scaling_decision` that were taken, in that
        order.
    """
    taken = (
        worker_category_decision(ccnl, level, declared, category, year),
        seniority,
        apprenticeship_scaling_decision(ccnl, apprenticeship, year),
    )
    return tuple(d for d in taken if d is not None)
