"""Contributions stage: INPS, bilateral funds, employer funds, TFR."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.payroll.domain.bilateral_funds import (
    BilateralFundInput,
    FlatMonthlyFund,
)
from ccnl_engine.engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.engine.payroll.service import contributions as _contrib
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import CCNL, LevelCategory
    from ccnl_engine.engine.payroll.domain.employment import Permanent
    from ccnl_engine.engine.tax.domain.rules import DomesticInpsRates, YearRules

_ZERO = Decimal(0)
_TWELVE = Decimal(12)


def _inps_domestic(
    dc: DomesticInpsRates,
    contract: Permanent | FixedTerm | Apprentice,
    gross_monthly: Decimal,
    weekly_hours: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return (employee_annual, employer_annual) via the flat per-hour model.

    Returns:
        Rounded annual INPS contributions for both parties.
    """
    annual_rate = gross_monthly * Decimal(12) / (weekly_hours * Decimal(52))
    hourly_rate_for_bracket = money(annual_rate)
    is_fixed_term = isinstance(contract, FixedTerm)
    emp_ph, er_ph = _contrib.resolve_domestic_inps_rate(
        dc,
        hourly_rate_for_bracket,
        weekly_hours,
        is_fixed_term=is_fixed_term,
    )
    annual_hours = weekly_hours * 52
    return money(emp_ph * annual_hours), money(er_ph * annual_hours)


def _inps_standard(
    rules: YearRules,
    contract: Permanent | FixedTerm | Apprentice,
    contribution_base: Decimal,
    worker_category: LevelCategory | None,
    *,
    ivs_ceiling_applies: bool,
) -> tuple[Decimal, Decimal, Decimal]:
    """Return ``(employee, employer, additional)`` via the standard percentage model.

    Returns:
        A 3-tuple of (employee INPS, employer INPS, employee 1% additional),
        all rounded to two decimal places.
    """
    rates = _contrib.resolve_rates(rules, contract, worker_category)
    employee_inps = _contrib.inps_contribution(
        contribution_base,
        rates.employee_rate,
        rates.employee_ivs_rate,
        rules,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
    additional = _contrib.inps_employee_additional(
        contribution_base,
        rules.inps,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
    employee_inps = money(employee_inps + additional)
    employer_inps = _contrib.inps_contribution(
        contribution_base,
        rates.employer_rate,
        rates.employer_ivs_rate,
        rules,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
    return employee_inps, employer_inps, additional


def _inps_contributions(
    rules: YearRules,
    contract: Permanent | FixedTerm | Apprentice,
    gross_monthly: Decimal,
    contribution_base: Decimal,
    worker_category: LevelCategory | None,
    *,
    weekly_hours: Decimal | None,
    ivs_ceiling_applies: bool,
) -> tuple[Decimal, Decimal, Decimal]:
    """Return (inps_employee_annual, inps_employer_annual, additional_annual).

    Routes to the flat per-hour domestic model when
    ``rules.domestic_contributions`` is set, otherwise uses the standard
    percentage model.

    Returns:
        A 3-tuple of (employee INPS, employer INPS, employee 1% additional),
        all rounded to two decimal places.

    Raises:
        InvalidInputError: If domestic model is active and ``weekly_hours`` is None.
    """
    if rules.domestic_contributions is not None:
        if weekly_hours is None:
            msg = "weekly_hours is required when rules.domestic_contributions is set"
            remediation = (
                "Set PayrollScenario.employee.weekly_hours when using the "
                "domestic contributions model."
            )
            raise InvalidInputError(
                msg,
                feature="domestic_contributions",
                remediation=remediation,
            )
        emp, er = _inps_domestic(
            rules.domestic_contributions,
            contract,
            gross_monthly,
            weekly_hours,
        )
        return emp, er, _ZERO
    return _inps_standard(
        rules,
        contract,
        contribution_base,
        worker_category,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )


def _compute_bilateral_funds(
    bilateral_funds: tuple[BilateralFundInput, ...],
    tfr_base: Decimal,
    gross_annual: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return (bilateral_employee_annual, bilateral_employer_annual).

    Returns:
        A 2-tuple of (employee_annual, employer_annual).
    """
    employee_total = _ZERO
    employer_total = _ZERO
    for fund in bilateral_funds:
        if isinstance(fund, FlatMonthlyFund):
            employee_total += money(fund.employee_monthly * _TWELVE)
            employer_total += money(fund.employer_monthly * _TWELVE)
        else:
            # RateFund
            base = tfr_base if fund.base == "tfr_base" else gross_annual
            employee_total += money(base * fund.employee_rate)
            employer_total += money(base * fund.employer_rate)
    return money(employee_total), money(employer_total)


def _employer_funds(
    ccnl: CCNL,
    category: LevelCategory | None,
    contribution_base: Decimal,
    as_of: date,
) -> Decimal:
    total = _ZERO
    for fund in ccnl.parameters.employer_funds:
        if _contrib.fund_applies_to(fund, category):
            total += money(contribution_base * fund.rate.value_at(as_of))
    return money(total)
