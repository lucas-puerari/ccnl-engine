"""Payroll provenance, ruleset identities and trace assembly."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation,
    CalculationTrace,
    InputSnapshot,
    TraceCategory,
    TraceStep,
)
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.trace import build_fiscal_trace
from ccnl_engine.knowledge.version import __version__ as knowledge_version
from ccnl_engine.version import __version__ as engine_version

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
        Level,
        SeniorityIncrements,
        SupplementaryAllowance,
    )
    from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.payroll.service.types import MonthlyPayChain
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay
    from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules

_ZERO = Decimal(0)


def _collect_provenance(
    level: Level,
    as_of: date,
    chain: MonthlyPayChain,
    seniority_increments: SeniorityIncrements,
    *,
    ccnl: CCNL | None = None,
    under_level_code: str | None = None,
) -> tuple[RuleProvenance, ...]:
    """Collect provenance for all rules that contributed to a pay outcome.

    Gathers the effective pay level (plus per-period base-salary override),
    each applied allowance, and the seniority-increment rule.

    For under-classification apprentices, ``level`` is the destination level
    but pay is derived from ``under_level_code``.  When both ``ccnl`` and
    ``under_level_code`` are provided, the effective pay level's provenance
    is recorded instead of the destination level.

    Returns:
        Ordered provenance tuple, one entry per contributing rule.
    """
    out: list[RuleProvenance] = []

    def _add(prov: RuleProvenance | None) -> None:
        if prov is not None:
            out.append(prov)

    effective_level = (
        ccnl.level_by_code(under_level_code)
        if ccnl is not None and under_level_code is not None
        else level
    )
    _add(effective_level.provenance)
    for period in effective_level.base_salary.periods:
        if period.valid_from <= as_of and (
            period.valid_until is None or as_of < period.valid_until
        ):
            _add(period.provenance)
            break
    for allowance, _ in chain.allowances:
        _add(allowance.provenance)
    _add(seniority_increments.provenance)
    return tuple(out)


def _build_trace(
    ccnl_id: str,
    level: Level,
    chain: MonthlyPayChain,
    seniority_count: int,
    ad_personam: Decimal,
    scaled_second_level: list[tuple[Decimal, SupplementaryAllowance]],
    gross_monthly: Decimal,
) -> CalculationTrace:
    """Build the step-by-step gross computation trace, post-scaling.

    All amounts are taken from already-scaled values (part-time and
    apprenticeship percentages already applied), so the trace faithfully
    represents the actual contribution of each component.

    Returns:
        A :class:`CalculationTrace` whose non-GROSS steps sum to ``gross_monthly``.
    """
    steps: list[TraceStep] = [
        TraceStep(
            category=TraceCategory.BASE_SALARY,
            label="Base retributiva",
            amount=chain.base,
            detail=f"{level.code}@{ccnl_id}",
        ),
        TraceStep(
            category=TraceCategory.SENIORITY,
            label="Scatti di anzianità",
            amount=chain.seniority,
            detail=f"scatti={seniority_count}",
        ),
    ]

    for allowance, amount in chain.allowances:
        steps.append(
            TraceStep(
                category=TraceCategory.ALLOWANCE,
                label=allowance.description,
                amount=amount,
                detail=allowance.code,
            )
        )

    if ad_personam > _ZERO:
        steps.append(
            TraceStep(
                category=TraceCategory.AD_PERSONAM,
                label="Ad personam",
                amount=ad_personam,
            )
        )

    for scaled, sl in scaled_second_level:
        if scaled > _ZERO:
            steps.append(
                TraceStep(
                    category=TraceCategory.SECOND_LEVEL,
                    label=sl.description,
                    amount=scaled,
                    detail=sl.code,
                )
            )

    # When a negotiated RAL overrides the component sum (e.g. DestinationRalOverride
    # or a plain RalOverride), the gross_monthly differs from the sum of components.
    # A RAL_OVERRIDE step bridges the gap so the invariant always holds:
    #   sum(non-GROSS steps) == GROSS step amount
    component_sum = money(sum((s.amount for s in steps), _ZERO))
    ral_delta = money(gross_monthly - component_sum)
    if ral_delta != _ZERO:
        steps.append(
            TraceStep(
                category=TraceCategory.RAL_OVERRIDE,
                label="Rettifica RAL concordata",
                amount=ral_delta,
            )
        )

    steps.append(
        TraceStep(
            category=TraceCategory.GROSS,
            label="Lordo mensile",
            amount=gross_monthly,
        )
    )

    return CalculationTrace(steps=tuple(steps))


def _ruleset_versions(
    ccnl: CCNL,
    rules: YearRules,
    surtax: SurtaxRules | None,
    sub_rulesets: dict[str, str] | None = None,
) -> dict[str, str]:
    """Return ``{kind: id@version}`` identities for all consumed rulesets.

    Falls back to the knowledge-base version for rulesets without a recorded
    identity.  Sub-rulesets (e.g. ``sick_pay``, ``variable_pay``) are merged
    in only when provided.

    Returns:
        Mapping of ruleset kind to ``id@version`` string.
    """
    versions: dict[str, str] = {}
    if ccnl.ruleset is not None:
        versions["ccnl"] = str(ccnl.ruleset)
    else:
        versions["ccnl"] = f"{ccnl.meta.ccnl_id}@{knowledge_version}"
    if rules.ruleset is not None:
        versions["tax"] = str(rules.ruleset)
    else:
        versions["tax"] = f"tax/{rules.year}/{ccnl.meta.tax_sector}@{knowledge_version}"
    if rules.inps_ruleset is not None:
        versions["inps"] = str(rules.inps_ruleset)
    if surtax is not None:
        if surtax.ruleset is not None:
            versions["surtax"] = str(surtax.ruleset)
        else:
            versions["surtax"] = f"surtax/{surtax.year}@{knowledge_version}"
    if sub_rulesets:
        versions.update(sub_rulesets)
    return versions


def build_calculation(
    scenario: PayrollScenario,
    ccnl: CCNL,
    rules: YearRules,
    surtax: SurtaxRules | None,
    gross: GrossPay,
    work: WorkRulesPay,
    result: PayrollResult,
) -> Calculation:
    """Attach the input snapshot, ruleset identities and traces to a result.

    Returns:
        The public calculation envelope with the original input captured.
    """
    snapshot = InputSnapshot.capture(
        scenario=scenario,
        ccnl_id=ccnl.meta.ccnl_id,
        tax_sector=ccnl.meta.tax_sector,
        year=rules.year,
        uses_surtax=surtax is not None,
    )

    gross_trace = _build_trace(
        ccnl_id=ccnl.meta.ccnl_id,
        level=gross.level,
        chain=gross.chain,
        seniority_count=gross.count,
        ad_personam=gross.ad_personam,
        scaled_second_level=gross.scaled_second_level,
        gross_monthly=result.gross_monthly,
    )
    # Domestic (colf/badanti) contributions use a flat per-hour rate.
    domestic_inps_formula = (
        "tariffa_oraria_INPS * ore_annuali_contratto"
        if rules.domestic_contributions is not None
        else None
    )
    ivs_ceiling_applies = scenario.employee.ivs_ceiling_applies
    ivs_ceiling = rules.inps.ceiling if rules.inps is not None else None
    fiscal_steps = build_fiscal_trace(
        gross_annual=result.gross_annual,
        contribution_base=gross.contribution_base,
        inps_employee_annual=result.inps_employee_annual,
        inps_employer_annual=result.inps_employer_annual,
        employer_funds_annual=result.employer_funds_annual,
        tfr_annual=result.tfr_annual,
        taxable_income=result.taxable_income,
        irpef_gross=result.irpef_gross,
        work_income_deduction=result.work_income_deduction,
        family_deduction_annual=result.family_deduction_annual,
        art15_deduction_annual=result.art15_deduction_annual,
        irpef_net=result.irpef_net,
        addizionale_regionale_annual=result.addizionale_regionale_annual,
        addizionale_comunale_annual=result.addizionale_comunale_annual,
        trattamento_integrativo=result.trattamento_integrativo,
        net_annual=result.net_annual,
        employer_withholds_irpef=result.employer_withholds_irpef,
        inps_formula=domestic_inps_formula,
        tfr_divisor=rules.tfr.accrual_divisor,
        ivs_ceiling_applies=ivs_ceiling_applies,
        ivs_ceiling=ivs_ceiling,
    )
    return Calculation(
        engine_version=engine_version,
        ruleset_version=_ruleset_versions(ccnl, rules, surtax, work.consumed_rulesets),
        input_snapshot=snapshot,
        result=result,
        trace=CalculationTrace(
            steps=gross_trace.steps,
            supplement_steps=work.supplement_trace,
            fiscal_steps=fiscal_steps,
        ),
    )
