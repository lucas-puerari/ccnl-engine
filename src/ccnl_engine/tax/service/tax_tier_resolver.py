"""INPS contribution tier resolution for employer headcount."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from ccnl_engine.shared.domain.errors import DataIntegrityError
from ccnl_engine.tax.domain.contribution_rules import ApprenticeRates, InpsRates

if TYPE_CHECKING:
    from collections.abc import Sequence
    from decimal import Decimal

    from ccnl_engine.tax.domain.contribution_tiers import (
        ApprenticeRawRates,
        InpsRawRates,
    )


class _Tier(Protocol):
    max_employees: int | None
    rate: Decimal
    ivs_rate: Decimal


def _assert_tier_integrity(tiers: Sequence[_Tier], side: str) -> None:
    """Raise DataIntegrityError if the tier list has structural defects.

    Checks (run on the unsorted input):
    - Exactly one open tier (max_employees: null) must be present.
      Zero open tiers would cause silent mis-classification for any
      headcount above the highest bounded tier; more than one would
      cause non-deterministic tier selection.
    - No duplicate max_employees values among bounded tiers (would cause
      silent mis-classification depending on sort stability).

    Raises:
        DataIntegrityError: if the number of open tiers is not exactly one,
            or if any bounded max_employees value appears more than once.
    """
    open_count = sum(1 for t in tiers if t.max_employees is None)
    if open_count != 1:
        msg = (
            f"{side}-rate tiers: exactly one open tier "
            f"(max_employees: null) is required, found {open_count}."
        )
        raise DataIntegrityError(msg)
    seen: set[int] = set()
    for tier in tiers:
        if tier.max_employees is None:
            continue
        if tier.max_employees in seen:
            msg = f"{side}-rate tiers: duplicate max_employees={tier.max_employees}."
            raise DataIntegrityError(msg)
        seen.add(tier.max_employees)


def _resolve_tier[T: _Tier](tiers: list[T], num_employees: int, side: str) -> T:
    """Select the applicable tier for the given employer headcount.

    ``_assert_tier_integrity`` is called first; it guarantees exactly one
    open tier (``max_employees: null``) is present.  After sorting, bounded
    tiers come first ordered by ``max_employees``; the open tier is last and
    serves as the unconditional fallback.

    Returns:
        The narrowest tier that covers ``num_employees``.
    """
    _assert_tier_integrity(tiers, side)
    sorted_tiers = sorted(
        tiers,
        key=lambda t: (t.max_employees is None, t.max_employees or 0),
    )
    for tier in sorted_tiers[:-1]:
        max_e = tier.max_employees
        if max_e is not None and num_employees <= max_e:
            return tier
    return sorted_tiers[-1]


def _resolve_inps(raw: InpsRawRates | None, num_employees: int) -> InpsRates | None:
    """Resolve INPS tiers by headcount; return None for domestic-model sectors.

    Validates that ``employee_additional_rate`` and
    ``employee_additional_threshold`` are both present or both absent.

    Returns:
        Resolved InpsRates for standard sectors; None when raw is None
        (i.e. the sector uses domestic_contributions instead).

    Raises:
        DataIntegrityError: If only one of the additional rate/threshold is set.
    """
    if raw is None:
        return None
    has_rate = raw.employee_additional_rate is not None
    has_threshold = raw.employee_additional_threshold is not None
    if has_rate != has_threshold:
        msg = (
            "employee_additional_rate and employee_additional_threshold "
            "must both be set or both be absent"
        )
        raise DataIntegrityError(msg)
    employer_tier = _resolve_tier(raw.employer_tiers, num_employees, "employer")
    employee_tier = _resolve_tier(raw.employee_tiers, num_employees, "employee")
    return InpsRates(
        employee_rate=employee_tier.rate,
        employee_ivs_rate=employee_tier.ivs_rate,
        employer_rate=employer_tier.rate,
        employer_ivs_rate=employer_tier.ivs_rate,
        ceiling=raw.ceiling,
        employer_rate_by_category=employer_tier.rate_by_category,
        employee_additional_rate=raw.employee_additional_rate,
        employee_additional_threshold=raw.employee_additional_threshold,
    )


def _resolve_apprentice(raw: ApprenticeRawRates, num_employees: int) -> ApprenticeRates:
    """Resolve apprentice rates by firm size.

    Returns:
        ApprenticeRates with employer rates selected for small or large firm.
    """
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
