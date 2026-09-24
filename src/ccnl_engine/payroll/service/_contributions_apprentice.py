"""Apprentice INPS rate selection (L. 296/2006 art. 1 c. 773)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.engine.tax.domain.rules import ApprenticeRates

_APPRENTICE_STEP_1: int = 12
_APPRENTICE_STEP_2: int = 24


def apprentice_employer_rate(rates: ApprenticeRates, months_elapsed: int) -> Decimal:
    """Return the employer rate in force at ``months_elapsed``.

    Returns:
        The employer contribution rate applicable at the given month.
    """
    if months_elapsed < _APPRENTICE_STEP_1:
        return rates.employer_rate_months_0_11
    if months_elapsed < _APPRENTICE_STEP_2:
        return rates.employer_rate_months_12_23
    return rates.employer_rate_after


def apprentice_employer_ivs_rate(
    rates: ApprenticeRates, months_elapsed: int
) -> Decimal:
    """Return the IVS-only employer rate in force at ``months_elapsed``.

    Returns:
        The IVS portion of the employer rate applicable at the given month.
    """
    if months_elapsed < _APPRENTICE_STEP_1:
        return rates.employer_ivs_rate_months_0_11
    if months_elapsed < _APPRENTICE_STEP_2:
        return rates.employer_ivs_rate_months_12_23
    return rates.employer_ivs_rate_after
