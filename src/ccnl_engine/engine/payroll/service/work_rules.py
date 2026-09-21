"""Coordination of optional period inputs and variable pay."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.work_rules_absence import _run_wr_absence
from ccnl_engine.engine.payroll.service.work_rules_leave import _run_wr_leave
from ccnl_engine.engine.payroll.service.work_rules_sickness import _run_wr_sickness
from ccnl_engine.engine.payroll.service.work_rules_supplements import (
    _run_wr_supplements,
)
from ccnl_engine.engine.payroll.service.work_rules_variable_pay import (
    _run_wr_variable_pay,
)
from ccnl_engine.engine.tax.service.loaders import load_sick_pay_rates
from ccnl_engine.knowledge.version import __version__ as _knowledge_version

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.metadata import RulesetIdentity
    from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
    from ccnl_engine.engine.payroll.domain.calculation import TraceStep
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates

_ZERO = Decimal(0)


@dataclass(frozen=True)
class WorkRulesPay:
    """Informational pay components, availability and warnings for the period."""

    base_monthly_full_time: Decimal
    overtime_supp: Decimal
    night_supp: Decimal
    holiday_supp: Decimal
    overtime_hours: Decimal
    night_hours: Decimal
    holiday_hours: Decimal
    time_supplements_monthly: Decimal
    time_supplements_annual_projection: Decimal
    hourly_rate: Decimal
    absence_deduction_monthly: Decimal
    effective_gross_monthly: Decimal
    leave_accrued_days_monthly: Decimal
    leave_taken_days_monthly: Decimal
    leave_balance_days: Decimal
    sick_days_monthly: Decimal
    sick_carenza_days_monthly: Decimal
    sick_inps_indemnity_monthly: Decimal
    sick_company_integration_monthly: Decimal
    fringe_benefit_annual: Decimal
    fringe_benefit_threshold_annual: Decimal
    fringe_benefit_taxable_annual: Decimal
    welfare_annual: Decimal
    bonus_annual: Decimal
    bonus_pdr_flat_tax_annual: Decimal
    bonus_ordinary_taxable_annual: Decimal
    bonus_pdr_missing_prior_year: bool
    wr_overtime_supported: bool
    wr_night_supported: bool
    wr_holiday_supported: bool
    wr_absence_present: bool
    wr_leave_present: bool
    wr_sickness_present: bool
    supplement_trace: tuple[TraceStep, ...]
    warnings: tuple[str, ...]
    consumed_rulesets: dict[str, str]
    consumed_ruleset_ids: tuple[RulesetIdentity | None, ...]
    consumed_verifications: dict[str, str]


def compute_work_rules(
    scenario: _InternalScenario,
    ccnl: CCNL,
    gross: GrossPay,
    year: int,
) -> WorkRulesPay:
    """Compute optional period features without changing the annual net pay.

    Returns:
        Informational amounts, their trace and missing-rule diagnostics.
    """
    base_monthly_full_time = gross.chain_full_time.base
    wr_warnings: list[str] = []

    supps = _run_wr_supplements(
        scenario=scenario,
        ccnl=ccnl,
        base_monthly_full_time=base_monthly_full_time,
        hourly_divisor=gross.hourly_divisor,
        as_of=scenario.employment.as_of,
        wr_warnings=wr_warnings,
    )
    time_supplements_monthly = money(supps.overtime + supps.night + supps.holiday)
    time_supplements_annual_projection = money(
        time_supplements_monthly * gross.additional_months
    )

    hourly_rate = money(gross.gross_monthly / gross.hourly_divisor)
    absence = _run_wr_absence(
        scenario=scenario,
        ccnl=ccnl,
        gross_monthly=gross.gross_monthly,
        hourly_rate=hourly_rate,
        wr_warnings=wr_warnings,
    )
    leave = _run_wr_leave(scenario=scenario, ccnl=ccnl)

    # Load sick-pay rates only when sick days were actually requested AND the
    # CCNL supports the sickness feature, so the ruleset is not registered as
    # consumed for scenarios with no sick input or unsupported CCNLs.
    sick_input = scenario.sick_input
    sickness_supported = (
        ccnl.work_rules is not None and ccnl.work_rules.sickness_rules is not None
    )
    sick_used = (
        sick_input is not None and sick_input.sick_days > _ZERO and sickness_supported
    )
    sick_pay_rates: InpsSickPayRates | None = (
        load_sick_pay_rates() if sick_used else None
    )
    sickness = _run_wr_sickness(
        scenario=scenario,
        ccnl=ccnl,
        sick_pay_rates=sick_pay_rates,
        gross_monthly=gross.gross_monthly,
    )
    var_pay = _run_wr_variable_pay(
        scenario=scenario,
        year=year,
        wr_warnings=wr_warnings,
    )

    consumed: dict[str, str] = {}
    consumed_ids: list[RulesetIdentity | None] = []
    consumed_ver: dict[str, str] = {}
    unverified = "unverified"
    if sick_pay_rates is not None and sickness.present:
        consumed["sick_pay"] = (
            str(sick_pay_rates.ruleset)
            if sick_pay_rates.ruleset is not None
            else f"sick-pay-rates@{_knowledge_version}"
        )
        consumed_ids.append(sick_pay_rates.ruleset)
        consumed_ver["sick_pay"] = (
            sick_pay_rates.ruleset.verification_status.value
            if sick_pay_rates.ruleset is not None
            else unverified
        )
    if var_pay.var_pay_rules is not None:
        ruleset = var_pay.var_pay_rules.ruleset
        consumed["variable_pay"] = (
            str(ruleset)
            if ruleset is not None
            else f"variable-pay-rules/{year}@{_knowledge_version}"
        )
        consumed_ids.append(ruleset)
        consumed_ver["variable_pay"] = (
            ruleset.verification_status.value if ruleset is not None else unverified
        )

    return WorkRulesPay(
        base_monthly_full_time=base_monthly_full_time,
        overtime_supp=supps.overtime,
        night_supp=supps.night,
        holiday_supp=supps.holiday,
        overtime_hours=supps.overtime_hours,
        night_hours=supps.night_hours,
        holiday_hours=supps.holiday_hours,
        time_supplements_monthly=time_supplements_monthly,
        time_supplements_annual_projection=time_supplements_annual_projection,
        hourly_rate=hourly_rate,
        absence_deduction_monthly=absence.deduction,
        effective_gross_monthly=absence.effective_gross,
        leave_accrued_days_monthly=leave.accrued,
        leave_taken_days_monthly=leave.taken,
        leave_balance_days=leave.balance,
        sick_days_monthly=sickness.sick_days,
        sick_carenza_days_monthly=sickness.carenza_days,
        sick_inps_indemnity_monthly=sickness.inps_indemnity,
        sick_company_integration_monthly=sickness.company_integration,
        fringe_benefit_annual=var_pay.fringe_benefit,
        fringe_benefit_threshold_annual=var_pay.fringe_benefit_threshold,
        fringe_benefit_taxable_annual=var_pay.fringe_benefit_taxable,
        welfare_annual=var_pay.welfare,
        bonus_annual=var_pay.bonus,
        bonus_pdr_flat_tax_annual=var_pay.bonus_pdr_flat_tax,
        bonus_ordinary_taxable_annual=var_pay.bonus_ordinary_taxable,
        bonus_pdr_missing_prior_year=var_pay.bonus_pdr_missing_prior_year,
        wr_overtime_supported=supps.overtime_supported,
        wr_night_supported=supps.night_supported,
        wr_holiday_supported=supps.holiday_supported,
        wr_absence_present=absence.present,
        wr_leave_present=leave.present,
        wr_sickness_present=sickness.present,
        supplement_trace=supps.trace,
        warnings=tuple(wr_warnings),
        consumed_rulesets=consumed,
        consumed_ruleset_ids=tuple(consumed_ids),
        consumed_verifications=consumed_ver,
    )
