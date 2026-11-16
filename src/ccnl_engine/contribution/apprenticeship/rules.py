"""Apprentice INPS rate selection (L. 296/2006 art. 1 c. 773)."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.contribution.rate.models import ApprenticeRates

_APPRENTICE_STEP_1: int = 12
_APPRENTICE_STEP_2: int = 24
#: Employer rate of a first-level apprentice: D.Lgs. 150/2015 art. 32 c. 1
#: lett. b, made structural by L. 205/2017 art. 1 c. 110 (INPS circ.
#: 108/2018 par. 3.4): "l'aliquota contributiva del 10% [...] è ridotta
#: alla misura del 5%", with no NASpI (1.31%) nor 0.30% (lett. c); the
#: reduced rates of a firm with up to nine employees in the first two years
#: stay when lower.
FIRST_LEVEL_EMPLOYER_RATE = Decimal("0.05")


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


def first_level_employer_rate(rates: ApprenticeRates, months_elapsed: int) -> Decimal:
    """Return the employer rate of a first-level apprentice at ``months_elapsed``.

    Returns:
        The IVS rate of the apprentice capped at 5%: the 1.5% and 3% of a
        firm with up to nine employees in the first two years, 5% otherwise;
        no NASpI and no 0.30% are added.
    """
    return min(
        apprentice_employer_ivs_rate(rates, months_elapsed), FIRST_LEVEL_EMPLOYER_RATE
    )
