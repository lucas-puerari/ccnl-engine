"""Payable rules each capability of a run reads, with their provenance.

Rule identifiers are ``<ruleset id>:<location in the data file>``.
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.handlers._overtime_rate import (
    CCNLOvertimeBands,
    resolve_overtime_rate,
)
from ccnl_engine.payroll.application.period._accrual_decisions import accrual_rules
from ccnl_engine.payroll.application.period._additional_ivs import additional_ivs_rules
from ccnl_engine.payroll.application.period._sickness import sickness_rules
from ccnl_engine.payroll.application.period._tfr_rules import (
    revaluation_rules,
    tfr_rules,
)
from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.payroll.domain.events import OvertimeEvent
from ccnl_engine.payroll.domain.jurisdiction import region_table_name

if TYPE_CHECKING:
    from collections.abc import Callable

    from ccnl_engine.contract.domain.validity import ValidityPeriod
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.provenance.domain.chain import ProvenanceStatus, RuleProvenance
    from ccnl_engine.provenance.domain.ruleset_identity import RulesetIdentity

#: A rule the run read: its identifier and its provenance, if recorded.
type Rule = tuple[str, RuleProvenance | ProvenanceStatus | None]


def _name(ruleset: RulesetIdentity | None, fallback: str) -> str:
    return fallback if ruleset is None else ruleset.id


def _salary_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the salary, allowance and extra-month rules of the run.

    Returns:
        The base salary period, each allowance of the pay chain, the
        additional-months period in force on the competence date, the
        accrual rule when its threshold decided a rateo of the run and the
        partial-month rules when the run pays part of its month.
    """
    ccnl, level = ctx.contract.ccnl, ctx.contract.level
    day = ctx.contract.tctx.competence
    name = _name(ccnl.ruleset, f"ccnl/{ccnl.meta.ccnl_id}")
    prefix = f"{name}:levels[{level.code}]"
    rules: list[Rule] = [
        (
            f"{prefix}.base_salary[{period.valid_from}]",
            period.provenance or level.provenance,
        )
        for period in _in_force(level.base_salary.period_at(day))
    ]
    rules.extend(
        (
            f"{prefix}.fixed_allowances[{allowance.code}]",
            allowance.provenance or level.provenance,
        )
        for allowance, _amount in ctx.chain.allowances
    )
    rules.extend(
        (f"{name}:additional_months[{period.valid_from}]", period.provenance)
        for period in _in_force(ccnl.parameters.additional_months.period_at(day))
    )
    rules.extend(accrual_rules(ctx))
    rules.extend(ctx.proration.rules)
    return tuple(rules)


def _in_force(period: ValidityPeriod | None) -> tuple[ValidityPeriod, ...]:
    return () if period is None else (period,)


def contract_rules(ctx: RunContext) -> dict[str, tuple[Rule, ...]]:
    """Return the CCNL and INPS rules of the run by capability.

    Returns:
        Rules of ``base_salary``, ``seniority``, ``inps_employee``,
        ``inps_employer`` and ``ivs_ceiling_eligibility`` (the massimale).
    """
    ccnl = ctx.contract.ccnl
    name = _name(ccnl.ruleset, f"ccnl/{ccnl.meta.ccnl_id}")
    rules = ctx.contract.year_rules
    inps_name = _name(rules.inps_ruleset, f"inps/{rules.year}")
    contract = ctx.request.contract_type
    rates = (
        ("apprentice", _provenance(rules.apprentice))
        if isinstance(contract, Apprentice)
        else ("inps", _provenance(rules.inps))
    )
    inps: tuple[Rule, ...] = (
        (f"{inps_name}:{rates[0]}", rates[1]),
        (
            f"{inps_name}:domestic_contributions",
            _provenance(rules.domestic_contributions),
        ),
    )
    tax_name = _name(rules.ruleset, f"tax/{rules.year}")
    fixed_term: tuple[Rule, ...] = (
        (
            (
                f"{tax_name}:fixed_term_additional_rate",
                rules.fixed_term_additional_rate_provenance,
            ),
        )
        if isinstance(contract, FixedTerm)
        else ()
    )
    return {
        "base_salary": _salary_rules(ctx),
        "seniority": (
            (
                f"{name}:seniority_increments",
                ccnl.parameters.seniority_increments.provenance,
            ),
        ),
        "inps_employee": inps + additional_ivs_rules(inps_name, rules.inps),
        "inps_employer": inps + fixed_term,
        "ivs_ceiling_eligibility": (
            (f"{inps_name}:inps.ceiling", _provenance(rules.inps)),
        ),
    }


def tax_rules(ctx: RunContext) -> dict[str, tuple[Rule, ...]]:
    """Return the tax-file and variable-pay rules of the run by capability.

    Returns:
        Rules of the IRPEF, TFR, TFR revaluation, credit and variable-pay
        capabilities.
    """
    rules, var = ctx.contract.year_rules, ctx.var_pay_rules
    name = _name(rules.ruleset, f"tax/{rules.year}")
    var_name = _name(var.ruleset, f"tax/variable-pay-rules/{var.year}")
    return {
        "irpef": (
            (f"{name}:irpef_brackets", rules.irpef_brackets_provenance),
            (f"{name}:work_deduction", rules.work_deduction.provenance),
            (
                f"{name}:work_deduction.minimum",
                rules.work_deduction.minimum.provenance,
            ),
            (
                f"{name}:sterilizzazione_detrazioni",
                _provenance(rules.sterilizzazione_detrazioni),
            ),
        ),
        "tfr": tfr_rules(name, rules.tfr),
        "tfr_revaluation": revaluation_rules(
            rules.tfr_revaluation, ctx.contract.tctx.competence.year
        ),
        "trattamento_integrativo": (
            (
                f"{name}:trattamento_integrativo",
                _provenance(rules.trattamento_integrativo),
            ),
        ),
        "ulteriore_detrazione_lavoro": (
            (f"{name}:ulteriore_detrazione", _provenance(rules.ulteriore_detrazione)),
        ),
        "somma_esente": ((f"{name}:somma_esente", _provenance(rules.somma_esente)),),
        "fringe_benefit": (
            (f"{var_name}:fringe_benefit", var.fringe_benefit.provenance),
        ),
        "bonus_pdr": ((f"{var_name}:pdr", var.pdr.provenance),),
        "rinnovo_substitute_tax": ((f"{var_name}:rinnovo", var.rinnovo.source_status),),
        "notte_festivi_turni_substitute_tax": (
            (
                f"{var_name}:notte_festivi_turni",
                var.notte_festivi_turni.source_status,
            ),
        ),
    }


def _provenance(block: object) -> RuleProvenance | None:
    provenance: RuleProvenance | None = getattr(block, "provenance", None)
    return provenance


def _surtax_rules(ctx: RunContext, *, regional: bool) -> tuple[Rule, ...]:
    """Return the surtax table rule of the run for one jurisdiction.

    An entry of the table may carry its own record; otherwise the record of
    the table applies.

    Returns:
        The rule of the jurisdiction, empty when no table was loaded.
    """
    surtax = ctx.repo.load_surtax_rules(ctx.fiscal_year)
    if surtax is None:
        return ()
    request = ctx.request
    if regional:
        key = region_table_name(request.regione or "") or ""
        entry: object = surtax.regionale.get(key)
        table, ruleset = surtax.regional_provenance, surtax.regional_ruleset
        fallback = f"surtax/{surtax.year}/regionale"
    else:
        key = request.comune_belfiore or ""
        entry = surtax.comunale.get(key)
        table, ruleset = surtax.municipal_provenance, surtax.municipal_ruleset
        fallback = f"surtax/{surtax.year}/comunale"
    return ((f"{_name(ruleset, fallback)}:rates[{key}]", _provenance(entry) or table),)


def _family_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the Art. 12 TUIR family deduction rules of the run.

    Returns:
        The spouse, spouse increase, children and other-dependent rules.
    """
    rules = ctx.repo.load_family_deduction_rules(ctx.fiscal_year)
    name = _name(rules.ruleset, f"tax/{rules.year}/family-deductions")
    return (
        (f"{name}:spouse", rules.spouse.provenance),
        (f"{name}:spouse_increases", rules.spouse_increases.provenance),
        (f"{name}:children", rules.children.provenance),
        (f"{name}:other_dependents", rules.other_dependents.provenance),
    )


def _pension_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the fund rates and the statutory pension rules of the run.

    Only called when the worker is enrolled: the fund was resolved by the
    run.  A rate period without its own record takes the one of its fund.

    Returns:
        The employer rate and employee minimum in force, then the deduction
        cap and solidarity rate of the tax year.
    """
    ccnl = ctx.contract.ccnl
    code = ctx.request.pension_fund.fund_code if ctx.request.pension_fund else ""
    fund = next(f for f in ccnl.parameters.employer_funds if f.code == code)
    day = ctx.contract.tctx.competence
    prefix = f"{_name(ccnl.ruleset, f'ccnl/{ccnl.meta.ccnl_id}')}:employer_funds"
    rules: list[Rule] = [
        (
            f"{prefix}[{code}].{key}[{period.valid_from}]",
            period.provenance or fund.provenance,
        )
        for key, series in (
            ("rate", fund.rate),
            ("employee_min_rate", fund.employee_min_rate),
        )
        if series is not None
        for period in _in_force(series.period_at(day))
    ]
    year_rules = ctx.contract.year_rules
    tax_name = _name(year_rules.ruleset, f"tax/{year_rules.year}")
    rules.append((
        f"{tax_name}:complementary_pension",
        _provenance(year_rules.complementary_pension),
    ))
    return tuple(rules)


def _overtime_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the CCNL overtime bands the multipliers of the run came from.

    Returns:
        One entry per distinct band an overtime event without a caller
        multiplier was paid with; empty when every multiplier is the caller's.
    """
    contract = ctx.contract
    bands = CCNLOvertimeBands.of(contract.ccnl, contract.tctx.competence.year)
    rules: dict[str, Rule] = {}
    events = ctx.request.events
    for event in (e for e in events if isinstance(e, OvertimeEvent)):
        band = resolve_overtime_rate(event, bands).derived_band
        if band is not None:
            rule = bands.rule_of(band)
            rules.setdefault(rule, (rule, band.provenance))
    return tuple(rules.values())


#: Capabilities whose rules need a load, done only when the capability ran.
LOADED: dict[str, Callable[[RunContext], tuple[Rule, ...]]] = {
    "overtime": _overtime_rules,
    "addizionale_regionale": partial(_surtax_rules, regional=True),
    "addizionale_comunale": partial(_surtax_rules, regional=False),
    "family_deductions": _family_rules,
    "pension_fund_contribution": _pension_rules,
    "sickness": sickness_rules,
}
