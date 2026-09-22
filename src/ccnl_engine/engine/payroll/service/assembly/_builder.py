"""build_calculation — the public assembly entry point."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation,
    CalculationTrace,
    InputSnapshot,
)
from ccnl_engine.engine.payroll.domain.item_producer import build_pay_items
from ccnl_engine.engine.payroll.service import contributions as _contrib
from ccnl_engine.engine.payroll.service.assembly._provenance import _build_trace
from ccnl_engine.engine.payroll.service.assembly._versions import (
    _ruleset_verifications,
    _ruleset_versions,
)
from ccnl_engine.engine.payroll.service.trace import build_fiscal_trace
from ccnl_engine.version import __version__ as engine_version

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
    from ccnl_engine.engine.payroll.domain.ledger import Ledger
    from ccnl_engine.engine.payroll.domain.payroll_result import AnnualEstimate
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules

_ZERO = Decimal(0)


def build_calculation(
    scenario: _InternalScenario,
    ccnl: CCNL,
    rules: YearRules,
    surtax: SurtaxRules | None,
    gross: GrossPay,
    work: WorkRulesPay,
    result: AnnualEstimate,
    fiscal: FiscalPay,
    ledger: Ledger | None = None,
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

    effective_level = (
        ccnl.level_by_code(gross.under_level_code)
        if gross.under_level_code is not None
        else gross.level
    )
    gross_trace = _build_trace(
        ccnl_id=ccnl.meta.ccnl_id,
        level=effective_level,
        chain=gross.chain,
        seniority_count=gross.count,
        ad_personam=gross.ad_personam,
        scaled_second_level=gross.scaled_second_level,
        gross_monthly=result.earnings.gross_monthly,
    )
    # Domestic (colf/badanti) contributions use a flat per-hour rate.
    domestic_inps_formula = (
        "tariffa_oraria_INPS * ore_annuali_contratto"
        if rules.domestic_contributions is not None
        else None
    )
    ivs_ceiling_applies = scenario.employee.ivs_ceiling_applies
    ivs_ceiling = rules.inps.ceiling if rules.inps is not None else None
    # Compute the 1% additional separately so build_fiscal_trace can include
    # it in the employee formula text.  The domestic flat-hour model has no
    # separate additional component (the per-hour tariff is composite).
    inps_employee_additional_annual = (
        _contrib.inps_employee_additional(
            gross.contribution_base,
            rules.inps,
            ivs_ceiling_applies=ivs_ceiling_applies,
        )
        if rules.domestic_contributions is None
        else _ZERO
    )
    fiscal_steps = build_fiscal_trace(
        gross_annual=result.earnings.gross_annual,
        contribution_base=gross.contribution_base,
        inps_employee_annual=result.contributions.inps_employee_annual,
        inps_employer_annual=result.contributions.inps_employer_annual,
        inps_employee_additional_annual=inps_employee_additional_annual,
        employer_funds_annual=result.contributions.employer_funds_annual,
        tfr_annual=result.contributions.tfr_annual,
        taxable_income=result.taxes.taxable_income,
        irpef_gross=result.taxes.irpef_gross,
        work_income_deduction=result.taxes.work_income_deduction,
        ulteriore_detrazione_lavoro=result.taxes.ulteriore_detrazione_lavoro,
        family_deduction_annual=result.taxes.family_deduction_annual,
        art15_deduction_annual=result.taxes.art15_deduction_annual,
        sterilizzazione_clawback=result.taxes.sterilizzazione_clawback_annual,
        bilateral_employee_annual=result.contributions.bilateral_employee_annual,
        irpef_net=result.taxes.irpef_net,
        addizionale_regionale_annual=result.taxes.addizionale_regionale_annual,
        addizionale_comunale_annual=result.taxes.addizionale_comunale_annual,
        trattamento_integrativo=result.taxes.trattamento_integrativo,
        somma_esente=result.taxes.somma_esente,
        net_annual=result.net_annual,
        employer_withholds_irpef=result.taxes.employer_withholds_irpef,
        inps_formula=domestic_inps_formula,
        tfr_divisor=rules.tfr.accrual_divisor,
        ivs_ceiling_applies=ivs_ceiling_applies,
        ivs_ceiling=ivs_ceiling,
    )
    uses_family = scenario.family is not None and scenario.family.has_any_dependent
    uses_art15 = (
        scenario.art15_deductions is not None
        and scenario.art15_deductions.has_any_onere
    )
    as_of = scenario.employment.as_of
    return Calculation(
        engine_version=engine_version,
        ruleset_version=_ruleset_versions(
            ccnl,
            rules,
            surtax,
            work.consumed_rulesets,
            uses_family_deductions=uses_family,
            uses_art15_deductions=uses_art15,
        ),
        ruleset_verification=_ruleset_verifications(ccnl, rules, surtax, work, fiscal),
        input_snapshot=snapshot,
        result=result,
        trace=CalculationTrace(
            steps=gross_trace.steps,
            supplement_steps=work.supplement_trace,
            fiscal_steps=fiscal_steps,
        ),
        ledger_entries=tuple(ledger.entries()) if ledger is not None else (),
        pay_items=build_pay_items(
            gross, work, fiscal, as_of, scenario.extra_monthly_payments
        ),
    )
