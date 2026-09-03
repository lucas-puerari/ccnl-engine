"""Tax year rules loader."""

from __future__ import annotations

import importlib.resources
from typing import TYPE_CHECKING, Protocol

from ccnl_engine.tax.models import (
    ApprenticeRates,
    InpsRates,
    YearRules,
    _ApprenticeRawRates,
    _YearRulesRaw,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from decimal import Decimal

    from ccnl_engine.models.ccnl import TaxSector


class _Tier(Protocol):
    max_employees: int | None
    rate: Decimal
    ivs_rate: Decimal


def load_year_rules(
    year: int,
    sector: TaxSector,
    num_employees: int,
) -> YearRules:
    """Load and validate tax year rules, resolving INPS rates by headcount.

    Returns:
        The validated YearRules instance with rates resolved for num_employees.
    """
    filename = f"{year}-{sector.value}.json"
    raw_text = (
        importlib.resources
        .files("ccnl_engine.tax.data")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )
    raw = _YearRulesRaw.model_validate_json(raw_text)
    employer_tier = _resolve_tier(raw.inps.employer_tiers, num_employees, "employer")
    employee_tier = _resolve_tier(raw.inps.employee_tiers, num_employees, "employee")
    return YearRules(
        year=raw.year,
        irpef_brackets=raw.irpef_brackets,
        work_deduction_breakpoints=raw.work_deduction_breakpoints,
        fixed_term_additional_rate=raw.fixed_term_additional_rate,
        inps=InpsRates(
            employee_rate=employee_tier.rate,
            employee_ivs_rate=employee_tier.ivs_rate,
            employer_rate=employer_tier.rate,
            employer_ivs_rate=employer_tier.ivs_rate,
            ceiling=raw.inps.ceiling,
            employer_rate_by_category=employer_tier.rate_by_category,
        ),
        apprentice=_resolve_apprentice(raw.apprentice, num_employees),
        tfr=raw.tfr,
        notes=raw.notes,
    )


def _resolve_tier[T: _Tier](tiers: list[T], num_employees: int, side: str) -> T:
    _assert_tier_integrity(tiers, side)
    sorted_tiers = sorted(
        tiers,
        key=lambda t: (t.max_employees is None, t.max_employees or 0),
    )
    for tier in sorted_tiers:
        if tier.max_employees is None or num_employees <= tier.max_employees:
            return tier
    msg = (
        f"No {side}-rate tier covers {num_employees} employees. "
        "Check that the tax data file has an open tier (max_employees: null)."
    )
    raise ValueError(msg)


def _assert_tier_integrity(tiers: Sequence[_Tier], side: str) -> None:
    """Raise ValueError if the tier list has structural defects.

    Checks (run on the unsorted input):
    - At most one open tier (max_employees: null); multiple open tiers
      would cause non-deterministic tier selection.
    - No duplicate max_employees values among bounded tiers (would cause
      silent mis-classification depending on sort stability).

    Raises:
        ValueError: if more than one open tier exists, or if any bounded
            max_employees value appears more than once.
    """
    open_count = sum(1 for t in tiers if t.max_employees is None)
    if open_count > 1:
        msg = (
            f"{side}-rate tiers: {open_count} open tiers "
            "(max_employees: null) found; at most one is allowed."
        )
        raise ValueError(msg)
    seen: set[int] = set()
    for tier in tiers:
        if tier.max_employees is None:
            continue
        if tier.max_employees in seen:
            msg = f"{side}-rate tiers: duplicate max_employees={tier.max_employees}."
            raise ValueError(msg)
        seen.add(tier.max_employees)


def _resolve_apprentice(
    raw: _ApprenticeRawRates, num_employees: int
) -> ApprenticeRates:
    small_firm = num_employees <= raw.small_firm_max_employees
    return ApprenticeRates(
        employee_rate=raw.employee_rate,
        employer_rate_months_0_11=(
            raw.small_firm_employer_rate_months_0_11
            if small_firm
            else raw.employer_rate
        ),
        employer_rate_months_12_23=(
            raw.small_firm_employer_rate_months_12_23
            if small_firm
            else raw.employer_rate
        ),
        employer_rate_after=raw.employer_rate,
    )
