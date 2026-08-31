"""Gross-to-net and employer cost computation."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine import contributions as _contrib
from ccnl_engine.engine import irpef as _irpef
from ccnl_engine.engine.result import ComputationResult
from ccnl_engine.engine.rounding import money
from ccnl_engine.models.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.models.employment import Apprentice, FixedTerm

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.models.ccnl import CCNL, Level
    from ccnl_engine.models.employment import Employment
    from ccnl_engine.tax.models import YearRules

_ONE = Decimal(1)
_ZERO = Decimal(0)


def compute(
    ccnl: CCNL,
    level_code: str,
    as_of: date,
    rules: YearRules,
    employment: Employment,
    part_time_pct: Decimal = _ONE,
    seniority_count: int = 0,
    negotiated_ral: Decimal | None = None,
) -> ComputationResult:
    """Compute gross-to-net salary and employer cost for a given scenario."""
    if not (_ZERO < part_time_pct <= _ONE):
        msg = f"part_time_pct must be in (0, 1], got {part_time_pct}"
        raise ValueError(msg)
    if seniority_count < 0:
        msg = f"seniority_count must be >= 0, got {seniority_count}"
        raise ValueError(msg)

    level = _resolve_level(ccnl, level_code)
    base_monthly, seniority_monthly, allowances_monthly, gross_monthly = (
        _build_salary_chain(level, ccnl, seniority_count, part_time_pct, as_of)
    )
    additional_months = ccnl.parameters.additional_months.value_at(as_of)

    if isinstance(employment, Apprentice):
        gross_annual, apprenticeship_pct, apprenticeship_under_level_code = (
            _compute_apprentice_annual(
                employment,
                ccnl,
                gross_monthly,
                additional_months,
                negotiated_ral,
                part_time_pct,
                as_of,
            )
        )
    else:
        gross_annual = negotiated_ral or money(gross_monthly * additional_months)
        apprenticeship_pct = None
        apprenticeship_under_level_code = None

    is_fixed_term = isinstance(employment, FixedTerm)
    inps_employee_annual = _contrib.inps_employee(gross_annual, rules)
    inps_employer_annual = _contrib.inps_employer(
        gross_annual, rules, fixed_term=is_fixed_term
    )
    tfr_annual = _contrib.tfr(gross_annual, rules)

    # SIMPLIFICATION: no addizionali regionali/comunali; no detrazioni per
    # carichi di famiglia; no sterilization mechanism for incomes > EUR 200k
    # (Art. 1 c. 3-4 L. 199/2025).
    taxable_income = money(gross_annual - inps_employee_annual)
    irpef_gross_val = _irpef.irpef_gross(taxable_income, rules)
    work_income_deduction_val = _irpef.work_income_deduction(gross_annual, rules)
    irpef_net = money(max(_ZERO, irpef_gross_val - work_income_deduction_val))

    net_annual = money(gross_annual - inps_employee_annual - irpef_net)
    net_monthly = money(net_annual / additional_months)
    employer_cost_annual = money(gross_annual + inps_employer_annual + tfr_annual)

    return ComputationResult(
        ccnl_id=ccnl.ccnl.id,
        level_code=level_code,
        employment_type=employment.type,
        part_time_pct=part_time_pct,
        as_of=as_of,
        year=as_of.year,
        base_monthly=base_monthly,
        seniority_monthly=seniority_monthly,
        allowances_monthly=allowances_monthly,
        gross_monthly=gross_monthly,
        gross_annual=gross_annual,
        apprenticeship_pct=apprenticeship_pct,
        apprenticeship_under_level_code=apprenticeship_under_level_code,
        inps_employee_annual=inps_employee_annual,
        inps_employer_annual=inps_employer_annual,
        tfr_annual=tfr_annual,
        taxable_income=taxable_income,
        irpef_gross=irpef_gross_val,
        work_income_deduction=work_income_deduction_val,
        irpef_net=irpef_net,
        net_annual=net_annual,
        net_monthly=net_monthly,
        employer_cost_annual=employer_cost_annual,
    )


def _resolve_level(ccnl: CCNL, level_code: str) -> Level:
    try:
        return next(lv for lv in ccnl.levels if lv.code == level_code)
    except StopIteration:
        msg = f"level_code {level_code!r} not found in CCNL {ccnl.ccnl.id!r}"
        raise KeyError(msg) from None


def _build_salary_chain(
    level: Level,
    ccnl: CCNL,
    seniority_count: int,
    part_time_pct: Decimal,
    as_of: date,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    base_monthly_ft = level.base_salary.value_at(as_of)
    seniority_increment = _ZERO
    amount_by_level = ccnl.parameters.seniority_increments.amount_by_level
    if level.code in amount_by_level:
        seniority_increment = amount_by_level[level.code].value_at(as_of)
    seniority_monthly = money(seniority_increment * seniority_count)
    allowances_monthly = money(
        sum(
            (a.monthly.value_at(as_of) for a in level.fixed_allowances),
            _ZERO,
        )
    )
    gross_monthly_ft = money(base_monthly_ft + seniority_monthly + allowances_monthly)
    gross_monthly = money(gross_monthly_ft * part_time_pct)
    return base_monthly_ft, seniority_monthly, allowances_monthly, gross_monthly


def _compute_apprentice_annual(
    employment: Apprentice,
    ccnl: CCNL,
    gross_monthly: Decimal,
    additional_months: Decimal,
    negotiated_ral: Decimal | None,
    part_time_pct: Decimal,
    as_of: date,
) -> tuple[Decimal, Decimal | None, str | None]:
    app = ccnl.apprenticeship
    if isinstance(app, ApprenticeshipPercentage):
        pct = _find_apprenticeship_percentage(app, employment.months_elapsed)
        base_gross = negotiated_ral or money(gross_monthly * additional_months)
        return money(base_gross * pct), pct, None
    assert isinstance(app, ApprenticeshipUnderClassification)
    pay_code = _find_under_classification_code(app, employment.months_elapsed)
    pay_level = next(lv for lv in ccnl.levels if lv.code == pay_code)
    pay_base = pay_level.base_salary.value_at(as_of)
    pay_allowances = money(
        sum(
            (a.monthly.value_at(as_of) for a in pay_level.fixed_allowances),
            _ZERO,
        )
    )
    pay_gross_monthly = money(money(pay_base + pay_allowances) * part_time_pct)
    gross_annual = negotiated_ral or money(pay_gross_monthly * additional_months)
    return gross_annual, None, pay_code


def _find_apprenticeship_percentage(
    app: ApprenticeshipPercentage, months_elapsed: int
) -> Decimal:
    for period in app.periods:
        if period.months_from <= months_elapsed and (
            period.months_until is None or months_elapsed < period.months_until
        ):
            return period.percentage
    msg = f"no apprenticeship period covers months_elapsed={months_elapsed}"
    raise ValueError(msg)


def _find_under_classification_code(
    app: ApprenticeshipUnderClassification, months_elapsed: int
) -> str:
    for period in app.periods:
        if period.months_from <= months_elapsed and (
            period.months_until is None or months_elapsed < period.months_until
        ):
            return period.pay_level_code
    msg = f"no apprenticeship period covers months_elapsed={months_elapsed}"
    raise ValueError(msg)
