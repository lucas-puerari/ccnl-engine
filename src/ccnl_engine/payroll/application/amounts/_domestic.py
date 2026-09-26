"""Flat per-hour INPS contributions of domestic CCNLs (colf and badanti)."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.domain.contributions import (
    ContributionBreakdown,
    ContributionComponent,
)
from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.shared.domain.errors import (
    DataIntegrityError,
    MissingRequiredFactError,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.tax.domain.domestic_contribution_rules import DomesticInpsRates
    from ccnl_engine.tax.domain.ruleset import YearRules


def _pick_domestic_per_hour(
    dc: DomesticInpsRates,
    weekly_hours: int,
    domestic_hourly_rate: Decimal,
    contract_type: Permanent | FixedTerm | Apprentice,
) -> tuple[Decimal, Decimal]:
    """Return (employee_per_hour, employer_per_hour) for a domestic CCNL bracket.

    Returns:
        ``(emp_ph, empr_ph)`` flat rates to multiply by contributable hours.
    """
    if weekly_hours > dc.weekly_hours_threshold:
        emp_ph = dc.hours_bracket.employee_per_hour
        empr_ph = (
            dc.hours_bracket.employer_per_hour_fixed_term
            if isinstance(contract_type, FixedTerm)
            else dc.hours_bracket.employer_per_hour
        )
    else:
        emp_ph = _ZERO
        empr_ph = _ZERO
        for wb in dc.wage_brackets:  # pragma: no branch
            if (  # pragma: no branch
                wb.hourly_rate_up_to is None
                or domestic_hourly_rate <= wb.hourly_rate_up_to
            ):
                emp_ph = wb.employee_per_hour
                empr_ph = (
                    wb.employer_per_hour_fixed_term
                    if isinstance(contract_type, FixedTerm)
                    else wb.employer_per_hour
                )
                break
    return emp_ph, empr_ph


def compute_domestic_breakdown(
    rules: YearRules,
    weekly_hours: int | None,
    contributable_hours: Decimal | None,
    domestic_hourly_rate: Decimal | None,
    contract_type: Permanent | FixedTerm | Apprentice,
) -> ContributionBreakdown:
    """Compute domestic flat-rate INPS contributions.

    Returns:
        :class:`~ccnl_engine.payroll.domain.contributions.ContributionBreakdown`
        with employee and employer flat-rate contributions and per-component audit.

    Raises:
        MissingRequiredFactError: When ``weekly_hours`` or ``contributable_hours``
            is ``None``.
        DataIntegrityError: When ``domestic_contributions`` is unexpectedly absent.
    """
    dc = rules.domestic_contributions
    if dc is None:  # pragma: no cover
        msg = "YearRules has no domestic_contributions despite inps=None"
        raise DataIntegrityError(msg)
    if weekly_hours is None:
        msg = (
            "domestic CCNL requires Employment.weekly_hours "
            "to select the INPS contribution bracket"
        )
        raise MissingRequiredFactError(msg, feature="domestic_contributions")
    if contributable_hours is None:
        msg = (
            "domestic CCNL requires PeriodFacts.contributable_hours "
            "to compute INPS contributions"
        )
        raise MissingRequiredFactError(msg, feature="domestic_contributions")
    emp_ph, empr_ph = _pick_domestic_per_hour(
        dc, weekly_hours, domestic_hourly_rate or _ZERO, contract_type
    )
    employee_contribution = money(emp_ph * contributable_hours)
    employer_contribution = money(empr_ph * contributable_hours)
    return ContributionBreakdown(
        employee=employee_contribution,
        employer=employer_contribution,
        components=(
            ContributionComponent(
                name="domestic_employee_per_hour",
                base=contributable_hours,
                rate=emp_ph,
                amount=employee_contribution,
            ),
            ContributionComponent(
                name="domestic_employer_per_hour",
                base=contributable_hours,
                rate=empr_ph,
                amount=employer_contribution,
            ),
        ),
    )


def _domestic_hourly_rate(
    ccnl: CCNL,
    year_rules: YearRules,
    monthly_gross: Decimal,
    as_of: date,
) -> Decimal | None:
    """Return the derived domestic hourly rate, or ``None`` for non-domestic CCNLs.

    Returns:
        Hourly rate in EUR for domestic CCNLs (``monthly_gross / hourly_divisor``),
        or ``None`` when the CCNL uses standard INPS rates.
    """
    if year_rules.domestic_contributions is None:
        return None
    hourly_divisor = Decimal(str(ccnl.parameters.hourly_divisor.value_at(as_of)))
    return money(monthly_gross / hourly_divisor) if monthly_gross > _ZERO else _ZERO
