"""Tax year rules loader."""

from __future__ import annotations

import importlib.resources
from typing import TYPE_CHECKING, Protocol

from ccnl_engine.tax.models import (
    ApprenticeRates,
    InpsRates,
    YearRules,
    _ApprenticeRawRates,
    _InpsRawRates,
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

    INPS contribution rates are tiered by company size. This function selects
    the correct tier for ``num_employees`` and returns a flat ``YearRules``
    with the resolved rates — callers do not need to handle tier logic.

    Args:
        year: Tax year (e.g. ``2026``). A matching data file must exist in the
            package bundle (``ccnl_engine/tax/data/<year>-<sector>.json``).
        sector: INPS sector classification, taken from ``CCNL.meta.tax_sector``.
        num_employees: Headcount used to select the INPS contribution-rate tier.
            Use the employer's total headcount, not just the contract's.

    Returns:
        A ``YearRules`` instance with INPS rates already resolved for the given
        headcount. The ``inps`` field is ``None`` for domestic-work sectors,
        which use ``domestic_contributions`` instead.
    """
    filename = f"{year}-{sector.value}.json"
    raw_text = (
        importlib.resources
        .files("ccnl_engine.tax.data")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )
    raw = _YearRulesRaw.model_validate_json(raw_text)
    inps = _resolve_inps(raw.inps, num_employees)
    apprentice = (
        _resolve_apprentice(raw.apprentice, num_employees)
        if raw.apprentice is not None
        else None
    )
    return YearRules(
        year=raw.year,
        irpef_brackets=raw.irpef_brackets,
        work_deduction_breakpoints=raw.work_deduction_breakpoints,
        fixed_term_additional_rate=raw.fixed_term_additional_rate,
        inps=inps,
        apprentice=apprentice,
        domestic_contributions=raw.domestic_contributions,
        tfr=raw.tfr,
        trattamento_integrativo=raw.trattamento_integrativo,
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


def _resolve_inps(raw: _InpsRawRates | None, num_employees: int) -> InpsRates | None:
    """Resolve INPS tiers by headcount; return None for domestic-model sectors.

    Returns:
        Resolved InpsRates for standard sectors; None when raw is None
        (i.e. the tax file uses domestic_contributions instead).
    """
    if raw is None:
        return None
    employer_tier = _resolve_tier(raw.employer_tiers, num_employees, "employer")
    employee_tier = _resolve_tier(raw.employee_tiers, num_employees, "employee")
    return InpsRates(
        employee_rate=employee_tier.rate,
        employee_ivs_rate=employee_tier.ivs_rate,
        employer_rate=employer_tier.rate,
        employer_ivs_rate=employer_tier.ivs_rate,
        ceiling=raw.ceiling,
        employer_rate_by_category=employer_tier.rate_by_category,
    )


def _resolve_apprentice(
    raw: _ApprenticeRawRates, num_employees: int
) -> ApprenticeRates:
    small_firm = num_employees <= raw.small_firm_max_employees
    return ApprenticeRates(
        employee_rate=raw.employee_rate,
        employee_ivs_rate=raw.employee_ivs_rate,
        employer_rate_months_0_11=(
            raw.small_firm_employer_rate_months_0_11
            if small_firm
            else raw.employer_rate
        ),
        employer_ivs_rate_months_0_11=(
            raw.small_firm_employer_ivs_rate_months_0_11
            if small_firm
            else raw.employer_ivs_rate
        ),
        employer_rate_months_12_23=(
            raw.small_firm_employer_rate_months_12_23
            if small_firm
            else raw.employer_rate
        ),
        employer_ivs_rate_months_12_23=(
            raw.small_firm_employer_ivs_rate_months_12_23
            if small_firm
            else raw.employer_ivs_rate
        ),
        employer_rate_after=raw.employer_rate,
        employer_ivs_rate_after=raw.employer_ivs_rate,
    )
