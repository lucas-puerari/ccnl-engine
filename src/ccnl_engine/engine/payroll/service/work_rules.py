"""Coordination of optional period inputs and variable pay."""

from __future__ import annotations

from collections import defaultdict
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
    from ccnl_engine.engine.metadata import RulesetIdentity
    from ccnl_engine.engine.payroll.domain.calculation import (
        TraceStep,
    )
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario
    from ccnl_engine.engine.payroll.domain.supplements import OvertimeHours
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


def _kinds_with_tiered_weekly_bands(
    bands: Sequence[OvertimeBand],
) -> set[WorkKind]:
    """Return kinds that have more than one band for the same work kind.

    A kind has tiered weekly bands when the CCNL partitions it by
    ``hour_threshold_per_week`` (e.g. first 4 h/week at one rate, the
    rest at a higher rate).  Without a per-week breakdown the engine
    treats the monthly total as a single week, which may overstate the
    higher band.

    Args:
        bands: All overtime bands from the CCNL schema.

    Returns:
        Set of :class:`WorkKind` values that have two or more bands.
    """
    kind_count: dict[WorkKind, int] = defaultdict(int)
    for band in bands:
        for kind in band.applies_to_kinds:
            kind_count[kind] += 1
    return {k for k, n in kind_count.items() if n > 1}


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


def _warn_tiered_bands_without_weeks(
    bands: Sequence[OvertimeBand],
    ts: OvertimeHours,
    kind_hours: dict[WorkKind, Decimal],
    wr_warnings: list[str],
) -> None:
    """Append a warning when tiered per-week bands exist but no weeks supplied.

    When the CCNL defines multiple overtime bands for the same kind (tiered
    weekly thresholds) and the caller passed only monthly totals, the engine
    treats the entire month as a single week, which overstates the higher
    band's contribution.  This warning nudges the caller to supply weekly
    data via :attr:`OvertimeHours.weeks`.
    """
    if ts.weeks:
        return
    tiered = _kinds_with_tiered_weekly_bands(bands)
    active_tiered = {k for k in tiered if kind_hours.get(k, _ZERO) > _ZERO}
    if not active_tiered:
        return
    names = ", ".join(sorted(k.value for k in active_tiered))
    wr_warnings.append(
        f"CCNL defines tiered weekly thresholds for {names}; "
        "provide OvertimeHours.weeks for accurate per-week "
        "band partitioning"
    )


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

    Raises:
        RuntimeError: If ``work_rules`` or ``time_supplements`` is ``None``
            despite ``wr_schema_present=True`` (indicates a data bug).
    """
    ts_input = scenario.time_supplements
    wr_schema_present = (
        ccnl.work_rules is not None and ccnl.work_rules.time_supplements is not None
    )
    zero_result = _SupplementsResult(
        overtime=_ZERO,
        night=_ZERO,
        holiday=_ZERO,
        trace=(),
        overtime_supported=False,
        night_supported=False,
        holiday_supported=False,
    )
    if ts_input is None:
        return zero_result
    # Treat a zero-hours supplement object the same as None: no hours were
    # actually requested, so no warning is warranted even when the CCNL has no
    # time-supplement schema.  This keeps the "requested but not modelled"
    # warning consistent with the scope predicate (ot_hours > 0 etc.).
    if (
        ts_input.weekday_hours
        + ts_input.supplementare_hours
        + ts_input.night_hours
        + ts_input.holiday_hours
        + ts_input.night_holiday_hours
    ) == _ZERO:
        return zero_result
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
    work_rules_ts = ccnl.work_rules
    if (  # pragma: no cover
        work_rules_ts is None or work_rules_ts.time_supplements is None
    ):
        msg = "time_supplements is None despite wr_schema_present=True"
        raise RuntimeError(msg)
    ts_schema = work_rules_ts.time_supplements
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
    _warn_tiered_bands_without_weeks(bands, ts, kind_hours, wr_warnings)
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

    Raises:
        RuntimeError: If ``work_rules`` or ``absence_rules`` is ``None``
            despite ``present=True`` (indicates a data bug).
    """
    absence_input = scenario.absence_days
    present = ccnl.work_rules is not None and ccnl.work_rules.absence_rules is not None
    deduction = _ZERO
    # A zero-day absence object is treated the same as None: no days were
    # actually taken, so computing or warning is unnecessary.  This keeps the
    # "requested but not modelled" warning consistent with the scope predicate
    # (unpaid_days != 0).
    if absence_input is not None and absence_input.unpaid_days != _ZERO:
        if present:
            work_rules_ab = ccnl.work_rules
            if (  # pragma: no cover
                work_rules_ab is None or work_rules_ab.absence_rules is None
            ):
                msg = "absence_rules is None despite present=True"
                raise RuntimeError(msg)
            deduction = compute_absence_deduction(
                absence_input=absence_input,
                absence_rules=work_rules_ab.absence_rules,
                gross_monthly=gross_monthly,
                hourly_rate=hourly_rate,
            )
            # Cap the deduction so effective_gross_monthly cannot go negative.
            if deduction > gross_monthly:
                wr_warnings.append(
                    "absence_deduction exceeds gross_monthly: capped to gross_monthly"
                )
                deduction = gross_monthly
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

    Raises:
        RuntimeError: If ``work_rules`` or ``leave_rules`` is ``None``
            despite ``present=True`` (indicates a data bug).
    """
    leave_input = scenario.leave_input
    present = ccnl.work_rules is not None and ccnl.work_rules.leave_rules is not None
    if leave_input is None:
        return _LeaveResult(accrued=_ZERO, taken=_ZERO, balance=_ZERO, present=present)
    if present:
        work_rules_lv = ccnl.work_rules
        if (  # pragma: no cover
            work_rules_lv is None or work_rules_lv.leave_rules is None
        ):
            msg = "leave_rules is None despite present=True"
            raise RuntimeError(msg)
        service_months = scenario.employee.seniority_months_as_of(
            scenario.employment.calculation_date
        )
        accrued, taken, balance = compute_leave(
            leave_input=leave_input,
            leave_rules=work_rules_lv.leave_rules,
            service_months=service_months,
        )
        return _LeaveResult(accrued=accrued, taken=taken, balance=balance, present=True)
    wr_warnings.append("leave_input requested but not modelled for this CCNL")
    return _LeaveResult(accrued=_ZERO, taken=_ZERO, balance=_ZERO, present=present)


def _run_wr_sickness(
    scenario: PayrollScenario,
    ccnl: CCNL,
    sick_pay_rates: InpsSickPayRates | None,
    gross_monthly: Decimal,
    wr_warnings: list[str],
) -> _SicknessResult:
    """Run the work-rules sickness block.

    ``sick_pay_rates`` must be non-``None`` when ``sick_input.sick_days > 0``;
    it is ``None`` when the caller skipped loading (zero or absent sick input).

    Returns:
        :class:`_SicknessResult` with zero amounts when sick input is absent
        or ``sick_days == 0``.  A warning is appended to ``wr_warnings`` when
        ``sick_days > 0`` but the CCNL has no sickness schema.

    Raises:
        RuntimeError: If ``work_rules`` or ``sickness_rules`` is ``None``
            despite ``present=True``, or if ``sick_pay_rates`` is ``None``
            when sickness computation is attempted (indicates a caller bug).
    """
    sick_input = scenario.sick_input
    present = ccnl.work_rules is not None and ccnl.work_rules.sickness_rules is not None
    # A zero-day sickness object is treated the same as None: no sick days were
    # taken, so loading rates, computing or warning is unnecessary.  This
    # mirrors the predicates already used for OvertimeHours and AbsenceDays.
    if sick_input is None or sick_input.sick_days == _ZERO:
        return _SicknessResult(
            sick_days=_ZERO,
            carenza_days=_ZERO,
            inps_indemnity=_ZERO,
            company_integration=_ZERO,
            present=present,
        )
    if present:
        work_rules_sk = ccnl.work_rules
        if (  # pragma: no cover
            work_rules_sk is None or work_rules_sk.sickness_rules is None
        ):
            msg = "sickness_rules is None despite present=True"
            raise RuntimeError(msg)
        if sick_pay_rates is None:  # pragma: no cover
            msg = "sick_pay_rates is None despite sick_days > 0"
            raise RuntimeError(msg)
        sick_days, carenza, inps_indemnity, company_integration = compute_sickness(
            sick_input=sick_input,
            sickness_rules=work_rules_sk.sickness_rules,
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
        ``var_pay_rules`` is ``None`` when no fringe-benefit or bonus/PdR
        input is present (rules were not loaded).  Welfare is computed from
        the input alone and does not require the variable-pay rules file.
    """
    fb_input = scenario.fringe_benefit_input
    welfare_input = scenario.welfare_input
    bonus_input = scenario.bonus_input
    any_input = (
        fb_input is not None or welfare_input is not None or bonus_input is not None
    )
    # Welfare is a statutory flat exemption and does not use the variable-pay
    # rules file.  Load only when fringe-benefit or bonus/PdR computation is
    # actually needed, so the ruleset is not registered as consumed for a
    # welfare-only scenario.
    rules_needed = fb_input is not None or bonus_input is not None

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

    fb_annual = _ZERO
    fb_threshold = _ZERO
    fb_taxable = _ZERO
    welfare_annual = _ZERO
    bonus_annual = _ZERO
    pdr_flat_tax = _ZERO
    bonus_ordinary = _ZERO
    var_pay_rules: VariablePayRules | None

    if rules_needed:
        var_pay_rules = load_variable_pay_rules(year)
        if fb_input is not None:
            fb_annual, fb_threshold, fb_taxable = compute_fringe_benefit(
                fb_input, var_pay_rules.fringe_benefit
            )
        if bonus_input is not None:
            bonus_annual, pdr_flat_tax, bonus_ordinary = compute_bonus(
                bonus_input, var_pay_rules.pdr, gross_annual, wr_warnings
            )
    else:
        var_pay_rules = None
    if welfare_input is not None:
        welfare_annual = compute_welfare(welfare_input)

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
    consumed_ruleset_ids: tuple[RulesetIdentity | None, ...]


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
        wr_warnings=wr_warnings,
    )
    var_pay = _run_wr_variable_pay(
        scenario=scenario,
        gross_annual=gross.gross_annual,
        year=year,
        wr_warnings=wr_warnings,
    )

    consumed: dict[str, str] = {}
    consumed_ids: list[RulesetIdentity | None] = []
    # Register sick-pay rates only when sickness was computed (sick_days > 0
    # and the CCNL supports it).  Always append the identity, including None,
    # so compute_confidence sees an unverified entry when identity is absent.
    if sick_pay_rates is not None and sickness.present:
        consumed["sick_pay"] = (
            str(sick_pay_rates.ruleset)
            if sick_pay_rates.ruleset is not None
            else f"sick-pay-rates@{_knowledge_version}"
        )
        consumed_ids.append(sick_pay_rates.ruleset)
    if var_pay.var_pay_rules is not None:
        ruleset = var_pay.var_pay_rules.ruleset
        consumed["variable_pay"] = (
            str(ruleset)
            if ruleset is not None
            else f"variable-pay-rules/{year}@{_knowledge_version}"
        )
        consumed_ids.append(ruleset)

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
        consumed_ruleset_ids=tuple(consumed_ids),
    )
