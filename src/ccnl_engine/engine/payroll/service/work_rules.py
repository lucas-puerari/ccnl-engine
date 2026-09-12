"""Coordination of optional period inputs and variable pay."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.absence import compute_absence_deduction
from ccnl_engine.engine.payroll.service.leave import compute_leave
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.sickness import compute_sickness
from ccnl_engine.engine.payroll.service.supplements import compute_time_supplements
from ccnl_engine.engine.payroll.service.variable_pay import (
    compute_bonus,
    compute_fringe_benefit,
    compute_welfare,
)
from ccnl_engine.engine.tax.service.loaders import (
    load_sick_pay_rates,
    load_variable_pay_rules,
)
from ccnl_engine.knowledge.version import __version__ as _knowledge_version

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
    )
    from ccnl_engine.engine.payroll.domain.calculation import (
        TraceStep,
    )
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates

_ZERO = Decimal(0)


def _run_wr_supplements(
    scenario: PayrollScenario,
    ccnl: CCNL,
    base_monthly_full_time: Decimal,
    hourly_divisor: Decimal,
    as_of: date,
    wr_warnings: list[str],
) -> tuple[Decimal, Decimal, Decimal, tuple[TraceStep, ...], bool]:
    """Run the work-rules time-supplement block and return its outputs.

    Returns:
        A 5-tuple of (overtime_supp, night_supp, holiday_supp, supplement_trace,
        wr_schema_present).  All supplement amounts are zero when the CCNL has no
        work-rules data or no hours were supplied; a warning is appended to
        ``wr_warnings`` in the latter case.
    """
    ts_input = scenario.time_supplements
    wr_schema_present = (
        ccnl.work_rules is not None and ccnl.work_rules.time_supplements is not None
    )
    overtime_supp = _ZERO
    night_supp = _ZERO
    holiday_supp = _ZERO
    supplement_trace: tuple[TraceStep, ...] = ()
    if ts_input is not None:
        if wr_schema_present:
            assert ccnl.work_rules is not None  # narrowing for mypy
            assert ccnl.work_rules.time_supplements is not None
            ts_schema = ccnl.work_rules.time_supplements
            if ts_schema.hourly_base_method == "gross_incl_allowances":
                wr_warnings.append(
                    "hourly_base_method='gross_incl_allowances' is not yet"
                    " implemented; time supplements cannot be computed"
                )
                return _ZERO, _ZERO, _ZERO, (), False
            overtime_supp, night_supp, holiday_supp, supplement_trace = (
                compute_time_supplements(
                    supps_input=ts_input,
                    supplements_schema=ts_schema,
                    base_monthly_full_time=base_monthly_full_time,
                    hourly_divisor=hourly_divisor,
                    as_of=as_of,
                )
            )
        else:
            wr_warnings.append(
                "time_supplements requested but not modelled for this CCNL"
            )
    return overtime_supp, night_supp, holiday_supp, supplement_trace, wr_schema_present


def _run_wr_absence(
    scenario: PayrollScenario,
    ccnl: CCNL,
    gross_monthly: Decimal,
    hourly_rate: Decimal,
    wr_warnings: list[str],
) -> tuple[Decimal, Decimal, bool]:
    """Run the work-rules absence-deduction block and return its outputs.

    Returns:
        A 3-tuple of (absence_deduction_monthly, effective_gross_monthly,
        wr_absence_present).  Both amounts are zero and effective_gross equals
        gross when no absence is supplied or the CCNL has no absence rules; a
        warning is appended to ``wr_warnings`` in the latter case.
    """
    absence_input = scenario.absence_days
    wr_absence_present = (
        ccnl.work_rules is not None and ccnl.work_rules.absence_rules is not None
    )
    absence_deduction_monthly = _ZERO
    if absence_input is not None:
        if wr_absence_present:
            assert ccnl.work_rules is not None  # narrowing for mypy
            assert ccnl.work_rules.absence_rules is not None
            absence_deduction_monthly = compute_absence_deduction(
                absence_input=absence_input,
                absence_rules=ccnl.work_rules.absence_rules,
                gross_monthly=gross_monthly,
                hourly_rate=hourly_rate,
            )
        else:
            wr_warnings.append("absence_days requested but not modelled for this CCNL")
    effective_gross_monthly = money(gross_monthly - absence_deduction_monthly)
    return absence_deduction_monthly, effective_gross_monthly, wr_absence_present


def _run_wr_leave(
    scenario: PayrollScenario,
    ccnl: CCNL,
    wr_warnings: list[str],
) -> tuple[Decimal, Decimal, Decimal, bool]:
    """Run the work-rules leave-accrual block and return its outputs.

    Returns:
        A 4-tuple of (leave_accrued_days_monthly, leave_taken_days_monthly,
        leave_balance_days, wr_leave_present).  All day counters are zero
        when no leave input is supplied or when the CCNL has no leave rules;
        a warning is appended in the latter case.
    """
    leave_input = scenario.leave_input
    wr_leave_present = (
        ccnl.work_rules is not None and ccnl.work_rules.leave_rules is not None
    )
    if leave_input is None:
        return _ZERO, _ZERO, _ZERO, wr_leave_present
    if wr_leave_present:
        assert ccnl.work_rules is not None  # narrowing for mypy
        assert ccnl.work_rules.leave_rules is not None
        service_months = scenario.employee.seniority_months_as_of(
            scenario.employment.calculation_date
        )
        accrued, taken, balance = compute_leave(
            leave_input=leave_input,
            leave_rules=ccnl.work_rules.leave_rules,
            service_months=service_months,
        )
        return accrued, taken, balance, wr_leave_present
    wr_warnings.append("leave_input requested but not modelled for this CCNL")
    return _ZERO, _ZERO, _ZERO, wr_leave_present


def _run_wr_sickness(
    scenario: PayrollScenario,
    ccnl: CCNL,
    sick_pay_rates: InpsSickPayRates,
    gross_monthly: Decimal,
    wr_warnings: list[str],
) -> tuple[Decimal, Decimal, Decimal, Decimal, bool]:
    """Run the work-rules sickness block and return its outputs.

    Returns:
        A 5-tuple of (sick_days_monthly, sick_carenza_days_monthly,
        sick_inps_indemnity_monthly, sick_company_integration_monthly,
        wr_sickness_present).  All amounts are zero when no sick input
        is supplied or when the CCNL has no sickness rules; a warning is
        appended in the latter case.
    """
    sick_input = scenario.sick_input
    wr_sickness_present = (
        ccnl.work_rules is not None and ccnl.work_rules.sickness_rules is not None
    )
    if sick_input is None:
        return _ZERO, _ZERO, _ZERO, _ZERO, wr_sickness_present
    if wr_sickness_present:
        assert ccnl.work_rules is not None  # narrowing for mypy
        assert ccnl.work_rules.sickness_rules is not None
        sick_days, carenza, inps_indemnity, company_integration = compute_sickness(
            sick_input=sick_input,
            sickness_rules=ccnl.work_rules.sickness_rules,
            sick_pay_rates=sick_pay_rates,
            gross_monthly=gross_monthly,
        )
        return sick_days, carenza, inps_indemnity, company_integration, True
    wr_warnings.append("sick_input requested but not modelled for this CCNL")
    return _ZERO, _ZERO, _ZERO, _ZERO, wr_sickness_present


def _run_wr_variable_pay(
    scenario: PayrollScenario,
    gross_annual: Decimal,
    year: int,
    wr_warnings: list[str],
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
    """Run the work-rules variable-pay block (fringe benefits, welfare, bonus/PdR).

    Variable-pay rules are statutory (not CCNL-specific): the rules file is
    always present for the fiscal year.  Each sub-feature is computed only
    when the caller provides the corresponding input.

    Returns:
        A 7-tuple of (fringe_benefit_annual, fringe_benefit_threshold_annual,
        fringe_benefit_taxable_annual, welfare_annual, bonus_annual,
        bonus_pdr_flat_tax_annual, bonus_ordinary_taxable_annual).
        Any unset input yields zeros for its slot.
    """
    fb_input = scenario.fringe_benefit_input
    welfare_input = scenario.welfare_input
    bonus_input = scenario.bonus_input

    any_input = (
        fb_input is not None or welfare_input is not None or bonus_input is not None
    )
    fb_annual = _ZERO
    fb_threshold = _ZERO
    fb_taxable = _ZERO
    welfare_annual = _ZERO
    bonus_annual = _ZERO
    pdr_flat_tax = _ZERO
    bonus_ordinary = _ZERO

    if not any_input:
        return (
            fb_annual,
            fb_threshold,
            fb_taxable,
            welfare_annual,
            bonus_annual,
            pdr_flat_tax,
            bonus_ordinary,
        )

    var_pay_rules = load_variable_pay_rules(year)

    if fb_input is not None:
        fb_annual, fb_threshold, fb_taxable = compute_fringe_benefit(
            fb_input, var_pay_rules.fringe_benefit
        )

    if welfare_input is not None:
        welfare_annual = compute_welfare(welfare_input)

    if bonus_input is not None:
        bonus_annual, pdr_flat_tax, bonus_ordinary = compute_bonus(
            bonus_input, var_pay_rules.pdr, gross_annual, wr_warnings
        )

    return (
        fb_annual,
        fb_threshold,
        fb_taxable,
        welfare_annual,
        bonus_annual,
        pdr_flat_tax,
        bonus_ordinary,
    )


@dataclass(frozen=True)
class WorkRulesPay:
    """Informational pay components, availability and warnings for the period."""

    base_monthly_full_time: Decimal
    overtime_supp: Decimal
    night_supp: Decimal
    holiday_supp: Decimal
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
    wr_schema_present: bool
    wr_absence_present: bool
    wr_leave_present: bool
    wr_sickness_present: bool
    supplement_trace: tuple[TraceStep, ...]
    warnings: tuple[str, ...]
    consumed_rulesets: dict[str, str]


def compute_work_rules(
    scenario: PayrollScenario,
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
    overtime_supp, night_supp, holiday_supp, supplement_trace, wr_schema_present = (
        _run_wr_supplements(
            scenario=scenario,
            ccnl=ccnl,
            base_monthly_full_time=base_monthly_full_time,
            hourly_divisor=gross.hourly_divisor,
            as_of=scenario.employment.calculation_date,
            wr_warnings=wr_warnings,
        )
    )

    time_supplements_monthly = money(overtime_supp + night_supp + holiday_supp)
    time_supplements_annual_projection = money(
        time_supplements_monthly * gross.additional_months
    )

    hourly_rate = money(gross.gross_monthly / gross.hourly_divisor)
    absence_deduction_monthly, effective_gross_monthly, wr_absence_present = (
        _run_wr_absence(
            scenario=scenario,
            ccnl=ccnl,
            gross_monthly=gross.gross_monthly,
            hourly_rate=hourly_rate,
            wr_warnings=wr_warnings,
        )
    )

    (
        leave_accrued_days_monthly,
        leave_taken_days_monthly,
        leave_balance_days,
        wr_leave_present,
    ) = _run_wr_leave(scenario=scenario, ccnl=ccnl, wr_warnings=wr_warnings)

    sick_pay_rates = load_sick_pay_rates()
    (
        sick_days_monthly,
        sick_carenza_days_monthly,
        sick_inps_indemnity_monthly,
        sick_company_integration_monthly,
        wr_sickness_present,
    ) = _run_wr_sickness(
        scenario=scenario,
        ccnl=ccnl,
        sick_pay_rates=sick_pay_rates,
        gross_monthly=gross.gross_monthly,
        wr_warnings=wr_warnings,
    )

    (
        fringe_benefit_annual,
        fringe_benefit_threshold_annual,
        fringe_benefit_taxable_annual,
        welfare_annual,
        bonus_annual,
        bonus_pdr_flat_tax_annual,
        bonus_ordinary_taxable_annual,
    ) = _run_wr_variable_pay(
        scenario=scenario,
        gross_annual=gross.gross_annual,
        year=year,
        wr_warnings=wr_warnings,
    )
    warnings = tuple(wr_warnings)

    consumed: dict[str, str] = {}
    if wr_sickness_present:
        consumed["sick_pay"] = (
            str(sick_pay_rates.ruleset)
            if sick_pay_rates.ruleset is not None
            else f"sick-pay-rates@{_knowledge_version}"
        )
    has_var_input = (
        scenario.fringe_benefit_input is not None
        or scenario.welfare_input is not None
        or scenario.bonus_input is not None
    )
    if has_var_input:
        var_pay_id = load_variable_pay_rules(year).ruleset
        consumed["variable_pay"] = (
            str(var_pay_id)
            if var_pay_id is not None
            else f"variable-pay-rules/{year}@{_knowledge_version}"
        )

    return WorkRulesPay(
        base_monthly_full_time=base_monthly_full_time,
        overtime_supp=overtime_supp,
        night_supp=night_supp,
        holiday_supp=holiday_supp,
        time_supplements_monthly=time_supplements_monthly,
        time_supplements_annual_projection=time_supplements_annual_projection,
        hourly_rate=hourly_rate,
        absence_deduction_monthly=absence_deduction_monthly,
        effective_gross_monthly=effective_gross_monthly,
        leave_accrued_days_monthly=leave_accrued_days_monthly,
        leave_taken_days_monthly=leave_taken_days_monthly,
        leave_balance_days=leave_balance_days,
        sick_days_monthly=sick_days_monthly,
        sick_carenza_days_monthly=sick_carenza_days_monthly,
        sick_inps_indemnity_monthly=sick_inps_indemnity_monthly,
        sick_company_integration_monthly=sick_company_integration_monthly,
        fringe_benefit_annual=fringe_benefit_annual,
        fringe_benefit_threshold_annual=fringe_benefit_threshold_annual,
        fringe_benefit_taxable_annual=fringe_benefit_taxable_annual,
        welfare_annual=welfare_annual,
        bonus_annual=bonus_annual,
        bonus_pdr_flat_tax_annual=bonus_pdr_flat_tax_annual,
        bonus_ordinary_taxable_annual=bonus_ordinary_taxable_annual,
        wr_schema_present=wr_schema_present,
        wr_absence_present=wr_absence_present,
        wr_leave_present=wr_leave_present,
        wr_sickness_present=wr_sickness_present,
        supplement_trace=supplement_trace,
        warnings=warnings,
        consumed_rulesets=consumed,
    )
