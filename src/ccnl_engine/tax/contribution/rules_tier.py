"""INPS contribution tier resolution for employer headcount."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.tax.contribution.models import ApprenticeRates, InpsRates

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ccnl_engine.tax.contribution.models_tier import (
        ApprenticeRawRates,
        InpsRawRates,
    )


class _Tier(Protocol):
    max_employees: int | None


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

    Returns:
        Resolved InpsRates for standard sectors; None when raw is None
        (i.e. the sector uses domestic_contributions instead).
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
        employee_additional=raw.employee_additional,
        minimum_base=raw.minimum_base,
        provenance=raw.provenance,
        public_funds=raw.public_funds,
        end_of_service=raw.end_of_service,
        public_credit=raw.public_credit,
        public_life_insurance=raw.public_life_insurance,
        public_enam=raw.public_enam,
        ceiling_provenance=raw.ceiling_provenance,
        fis_reduction=raw.fis_reduction,
        base_whole_euro=raw.base_whole_euro,
    )


def _apprentice_shares(
    raw: ApprenticeRawRates, num_employees: int
) -> tuple[Decimal, Decimal]:
    """Return the employer and employee wage-integration shares of the headcount.

    Returns:
        ``(employer, employee)`` of the tier that covers ``num_employees``;
        zero when the block has no headcount shares.
    """
    if not raw.headcount_shares:
        return Decimal(0), Decimal(0)
    share = _resolve_tier(raw.headcount_shares, num_employees, "apprentice share")
    return share.employer_rate, share.employee_rate


def _resolve_apprentice(raw: ApprenticeRawRates, num_employees: int) -> ApprenticeRates:
    """Resolve apprentice rates by firm size.

    The headcount share (CIGO, CIGS or FIS) is added to every employer
    period and to the employee rate; the IVS portions are unchanged.

    Returns:
        ApprenticeRates with employer rates selected for small or large firm.
    """
    small_firm = num_employees <= raw.small_firm_max_employees
    employer_share, employee_share = _apprentice_shares(raw, num_employees)
    return ApprenticeRates(
        employee_rate=raw.employee_rate + employee_share,
        employee_ivs_rate=raw.employee_ivs_rate,
        employer_rate_months_0_11=employer_share
        + (
            raw.small_firm_employer_rate_months_0_11
            if small_firm
            else raw.employer_rate
        ),
        employer_ivs_rate_months_0_11=(
            raw.small_firm_employer_ivs_rate_months_0_11
            if small_firm
            else raw.employer_ivs_rate
        ),
        employer_rate_months_12_23=employer_share
        + (
            raw.small_firm_employer_rate_months_12_23
            if small_firm
            else raw.employer_rate
        ),
        employer_ivs_rate_months_12_23=(
            raw.small_firm_employer_ivs_rate_months_12_23
            if small_firm
            else raw.employer_ivs_rate
        ),
        employer_rate_after=raw.employer_rate + employer_share,
        employer_ivs_rate_after=raw.employer_ivs_rate,
        provenance=raw.provenance,
    )
