"""Coordination of optional period inputs and variable pay."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.contract.domain.ccnl import WorkKind
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
    from collections.abc import Sequence
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
        OvertimeBand,
    )
    from ccnl_engine.engine.payroll.domain.calculation import (
        TraceStep,
    )
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates
    from ccnl_engine.engine.tax.domain.variable_pay import VariablePayRules

_ZERO = Decimal(0)


def _kind_supported(bands: Sequence[OvertimeBand], *kinds: WorkKind) -> bool:
    """Return True when any band in *bands* applies to at least one of *kinds*.

    Args:
        bands: List of :class:`OvertimeBand` objects from the CCNL schema.
        kinds: One or more :class:`WorkKind` values to match against.

    Returns:
        ``True`` if a matching band exists, ``False`` otherwise.
    """
    return any(k in b.applies_to_kinds for b in bands for k in kinds)


def _warn_missing_kind_bands(
    bands: Sequence[OvertimeBand],
    kind_hours: dict[WorkKind, Decimal],
    warnings: list[str],
) -> None:
    """Append a warning for each work kind that has positive hours but no band.

    Args:
        bands: CCNL overtime bands to check against.
        kind_hours: Map of WorkKind to the declared hours for that kind.
        warnings: Mutable list to which warning messages are appended.
    """
    for kind, hours in kind_hours.items():
        if hours > _ZERO and not _kind_supported(bands, kind):
            warnings.append(f"{kind.value} hours declared but not covered by any band")


# ---------------------------------------------------------------------------
# Private result dataclasses — one per _run_wr_* block
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _SupplementsResult:
    overtime: Decimal
    night: Decimal
    holiday: Decimal
    trace: tuple[TraceStep, ...]
    overtime_supported: bool
    night_supported: bool
    holiday_supported: bool


@dataclass(frozen=True)
class _AbsenceResult:
    deduction: Decimal
    effective_gross: Decimal
    present: bool


@dataclass(frozen=True)
class _LeaveResult:
    accrued: Decimal
    taken: Decimal
    balance: Decimal
    present: bool


@dataclass(frozen=True)
class _SicknessResult:
    sick_days: Decimal
    carenza_days: Decimal
    inps_indemnity: Decimal
    company_integration: Decimal
    present: bool


@dataclass(frozen=True)
class _VariablePayResult:
    fringe_benefit: Decimal
    fringe_benefit_threshold: Decimal
    fringe_benefit_taxable: Decimal
    welfare: Decimal
    bonus: Decimal
    bonus_pdr_flat_tax: Decimal
    bonus_ordinary_taxable: Decimal
    var_pay_rules: VariablePayRules | None


# ---------------------------------------------------------------------------
# Private block runners
# ---------------------------------------------------------------------------


def _run_wr_supplements(
    scenario: PayrollScenario,
    ccnl: CCNL,
    base_monthly_full_time: Decimal,
    hourly_divisor: Decimal,
    as_of: date,
    wr_warnings: list[str],
) -> _SupplementsResult:
    """Run the work-rules time-supplement block.

    Returns:
        :class:`_SupplementsResult` with zero amounts and ``False`` support
        flags when the CCNL has no work-rules schema or no hours were
        supplied. A warning is appended to ``wr_warnings`` in the latter
        case.
    """
    ts_input = scenario.time_supplements
    wr_schema_present = (
        ccnl.work_rules is not None and ccnl.work_rules.time_supplements is not None
    )
    if ts_input is None:
        return _SupplementsResult(
            overtime=_ZERO,
            night=_ZERO,
            holiday=_ZERO,
            trace=(),
            overtime_supported=False,
            night_supported=False,
            holiday_supported=False,
        )
    if not wr_schema_present:
        wr_warnings.append("time_supplements requested but not modelled for this CCNL")
        return _SupplementsResult(
            overtime=_ZERO,
            night=_ZERO,
            holiday=_ZERO,
            trace=(),
            overtime_supported=False,
            night_supported=False,
            holiday_supported=False,
        )
    assert ccnl.work_rules is not None  # narrowing for mypy
    assert ccnl.work_rules.time_supplements is not None
    ts_schema = ccnl.work_rules.time_supplements
    if ts_schema.hourly_base_method == "gross_incl_allowances":
        wr_warnings.append(
            "hourly_base_method='gross_incl_allowances' is not yet"
            " implemented; time supplements cannot be computed"
        )
        return _SupplementsResult(
            overtime=_ZERO,
            night=_ZERO,
            holiday=_ZERO,
            trace=(),
            overtime_supported=False,
            night_supported=False,
            holiday_supported=False,
        )
    bands = ts_schema.overtime_bands
    ts = ts_input
    kind_hours: dict[WorkKind, Decimal] = {
        WorkKind.WEEKDAY: ts.weekday_hours,
        WorkKind.SUPPLEMENTARE: ts.supplementare_hours,
        WorkKind.NIGHT: ts.night_hours,
        WorkKind.HOLIDAY: ts.holiday_hours,
        WorkKind.NIGHT_HOLIDAY: ts.night_holiday_hours,
    }
    _warn_missing_kind_bands(bands, kind_hours, wr_warnings)
    # Support flag: True only when every kind with positive hours
    # has a covering band (schema-level AND per-kind coverage).
    wd_uncovered = ts.weekday_hours > _ZERO and not _kind_supported(
        bands, WorkKind.WEEKDAY
    )
    sl_uncovered = ts.supplementare_hours > _ZERO and not _kind_supported(
        bands, WorkKind.SUPPLEMENTARE
    )
    ho_uncovered = ts.holiday_hours > _ZERO and not _kind_supported(
        bands, WorkKind.HOLIDAY
    )
    nh_uncovered = ts.night_holiday_hours > _ZERO and not _kind_supported(
        bands, WorkKind.NIGHT_HOLIDAY
    )
    overtime_supported = (
        _kind_supported(bands, WorkKind.WEEKDAY, WorkKind.SUPPLEMENTARE)
        and not wd_uncovered
        and not sl_uncovered
    )
    night_supported = _kind_supported(bands, WorkKind.NIGHT)
    holiday_supported = (
        _kind_supported(bands, WorkKind.HOLIDAY, WorkKind.NIGHT_HOLIDAY)
        and not ho_uncovered
        and not nh_uncovered
    )
    overtime, night, holiday, trace = compute_time_supplements(
        supps_input=ts_input,
        supplements_schema=ts_schema,
        base_monthly_full_time=base_monthly_full_time,
        hourly_divisor=hourly_divisor,
        as_of=as_of,
    )
    return _SupplementsResult(
        overtime=overtime,
        night=night,
        holiday=holiday,
        trace=trace,
        overtime_supported=overtime_supported,
        night_supported=night_supported,
        holiday_supported=holiday_supported,
    )


def _run_wr_absence(
    scenario: PayrollScenario,
    ccnl: CCNL,
    gross_monthly: Decimal,
    hourly_rate: Decimal,
    wr_warnings: list[str],
) -> _AbsenceResult:
    """Run the work-rules absence-deduction block.

    Returns:
        :class:`_AbsenceResult` with zero deduction and
        ``effective_gross == gross_monthly`` when no absence is supplied or
        the CCNL has no absence rules. A warning is appended to
        ``wr_warnings`` in the latter case.
    """
    absence_input = scenario.absence_days
    present = ccnl.work_rules is not None and ccnl.work_rules.absence_rules is not None
    deduction = _ZERO
    if absence_input is not None:
        if present:
            assert ccnl.work_rules is not None  # narrowing for mypy
            assert ccnl.work_rules.absence_rules is not None
            deduction = compute_absence_deduction(
                absence_input=absence_input,
                absence_rules=ccnl.work_rules.absence_rules,
                gross_monthly=gross_monthly,
                hourly_rate=hourly_rate,
            )
        else:
            wr_warnings.append("absence_days requested but not modelled for this CCNL")
    return _AbsenceResult(
        deduction=deduction,
        effective_gross=money(gross_monthly - deduction),
        present=present,
    )


def _run_wr_leave(
    scenario: PayrollScenario,
    ccnl: CCNL,
    wr_warnings: list[str],
) -> _LeaveResult:
    """Run the work-rules leave-accrual block.

    Returns:
        :class:`_LeaveResult` with zero day counters when no leave input is
        supplied or the CCNL has no leave rules. A warning is appended to
        ``wr_warnings`` in the latter case.
    """
    leave_input = scenario.leave_input
    present = ccnl.work_rules is not None and ccnl.work_rules.leave_rules is not None
    if leave_input is None:
        return _LeaveResult(accrued=_ZERO, taken=_ZERO, balance=_ZERO, present=present)
    if present:
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
        return _LeaveResult(accrued=accrued, taken=taken, balance=balance, present=True)
    wr_warnings.append("leave_input requested but not modelled for this CCNL")
    return _LeaveResult(accrued=_ZERO, taken=_ZERO, balance=_ZERO, present=present)


def _run_wr_sickness(
    scenario: PayrollScenario,
    ccnl: CCNL,
    sick_pay_rates: InpsSickPayRates,
    gross_monthly: Decimal,
    wr_warnings: list[str],
) -> _SicknessResult:
    """Run the work-rules sickness block.

    Returns:
        :class:`_SicknessResult` with zero amounts when no sick input is
        supplied or the CCNL has no sickness rules. A warning is appended to
        ``wr_warnings`` in the latter case.
    """
    sick_input = scenario.sick_input
    present = ccnl.work_rules is not None and ccnl.work_rules.sickness_rules is not None
    if sick_input is None:
        return _SicknessResult(
            sick_days=_ZERO,
            carenza_days=_ZERO,
            inps_indemnity=_ZERO,
            company_integration=_ZERO,
            present=present,
        )
    if present:
        assert ccnl.work_rules is not None  # narrowing for mypy
        assert ccnl.work_rules.sickness_rules is not None
        sick_days, carenza, inps_indemnity, company_integration = compute_sickness(
            sick_input=sick_input,
            sickness_rules=ccnl.work_rules.sickness_rules,
            sick_pay_rates=sick_pay_rates,
            gross_monthly=gross_monthly,
        )
        return _SicknessResult(
            sick_days=sick_days,
            carenza_days=carenza,
            inps_indemnity=inps_indemnity,
            company_integration=company_integration,
            present=True,
        )
    wr_warnings.append("sick_input requested but not modelled for this CCNL")
    return _SicknessResult(
        sick_days=_ZERO,
        carenza_days=_ZERO,
        inps_indemnity=_ZERO,
        company_integration=_ZERO,
        present=present,
    )


def _run_wr_variable_pay(
    scenario: PayrollScenario,
    gross_annual: Decimal,
    year: int,
    wr_warnings: list[str],
) -> _VariablePayResult:
    """Run the work-rules variable-pay block (fringe benefits, welfare, bonus/PdR).

    Variable-pay rules are statutory (not CCNL-specific): the rules file is
    always present for the fiscal year. Each sub-feature is computed only
    when the caller provides the corresponding input.

    Returns:
        :class:`_VariablePayResult` with zero amounts for unset inputs.
        ``var_pay_rules`` is ``None`` when no variable-pay input is present
        (rules were not loaded), so the caller can extract the ruleset id
        without a second load.
    """
    fb_input = scenario.fringe_benefit_input
    welfare_input = scenario.welfare_input
    bonus_input = scenario.bonus_input
    any_input = (
        fb_input is not None or welfare_input is not None or bonus_input is not None
    )

    if not any_input:
        return _VariablePayResult(
            fringe_benefit=_ZERO,
            fringe_benefit_threshold=_ZERO,
            fringe_benefit_taxable=_ZERO,
            welfare=_ZERO,
            bonus=_ZERO,
            bonus_pdr_flat_tax=_ZERO,
            bonus_ordinary_taxable=_ZERO,
            var_pay_rules=None,
        )

    var_pay_rules = load_variable_pay_rules(year)
    fb_annual = _ZERO
    fb_threshold = _ZERO
    fb_taxable = _ZERO
    welfare_annual = _ZERO
    bonus_annual = _ZERO
    pdr_flat_tax = _ZERO
    bonus_ordinary = _ZERO

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

    return _VariablePayResult(
        fringe_benefit=fb_annual,
        fringe_benefit_threshold=fb_threshold,
        fringe_benefit_taxable=fb_taxable,
        welfare=welfare_annual,
        bonus=bonus_annual,
        bonus_pdr_flat_tax=pdr_flat_tax,
        bonus_ordinary_taxable=bonus_ordinary,
        var_pay_rules=var_pay_rules,
    )


# ---------------------------------------------------------------------------
# Public result and entry point
# ---------------------------------------------------------------------------


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
    wr_overtime_supported: bool
    wr_night_supported: bool
    wr_holiday_supported: bool
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

    supps = _run_wr_supplements(
        scenario=scenario,
        ccnl=ccnl,
        base_monthly_full_time=base_monthly_full_time,
        hourly_divisor=gross.hourly_divisor,
        as_of=scenario.employment.calculation_date,
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
    leave = _run_wr_leave(scenario=scenario, ccnl=ccnl, wr_warnings=wr_warnings)

    sick_pay_rates = load_sick_pay_rates()
    sickness = _run_wr_sickness(
        scenario=scenario,
        ccnl=ccnl,
        sick_pay_rates=sick_pay_rates,
        gross_monthly=gross.gross_monthly,
        wr_warnings=wr_warnings,
    )
    var_pay = _run_wr_variable_pay(
        scenario=scenario,
        gross_annual=gross.gross_annual,
        year=year,
        wr_warnings=wr_warnings,
    )

    consumed: dict[str, str] = {}
    if sickness.present:
        consumed["sick_pay"] = (
            str(sick_pay_rates.ruleset)
            if sick_pay_rates.ruleset is not None
            else f"sick-pay-rates@{_knowledge_version}"
        )
    if var_pay.var_pay_rules is not None:
        ruleset = var_pay.var_pay_rules.ruleset
        consumed["variable_pay"] = (
            str(ruleset)
            if ruleset is not None
            else f"variable-pay-rules/{year}@{_knowledge_version}"
        )

    return WorkRulesPay(
        base_monthly_full_time=base_monthly_full_time,
        overtime_supp=supps.overtime,
        night_supp=supps.night,
        holiday_supp=supps.holiday,
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
        wr_overtime_supported=supps.overtime_supported,
        wr_night_supported=supps.night_supported,
        wr_holiday_supported=supps.holiday_supported,
        wr_absence_present=absence.present,
        wr_leave_present=leave.present,
        wr_sickness_present=sickness.present,
        supplement_trace=supps.trace,
        warnings=tuple(wr_warnings),
        consumed_rulesets=consumed,
    )
