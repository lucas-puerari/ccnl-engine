"""Ordinary wage integration contributions selected by employer activity.

INPS circular 76/2022, p. 7, reproduces D.Lgs. 148/2015 art. 13(1):
construction operai 4.70%, stone-working operai 3.30%, and the impiegati
and quadri of either activity 1.70% through 50 employees and 2.00% above.
The same circular applies these rates to apprentices. The sector tables
already contain the general industrial CIGO and any CIGS; only the CIGO
difference is added here, leaving every other contribution intact.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.regime.models import EmployerActivity
from ccnl_engine.sector.models import YearRules

_OPERAI_CIGO = {
    EmployerActivity.CONSTRUCTION: Decimal("0.047"),
    EmployerActivity.STONE_WORKING: Decimal("0.033"),
}


def with_activity_cigo(
    rules: YearRules,
    sector: TaxSector,
    activity: EmployerActivity,
    headcount: int,
) -> YearRules:
    """Replace the sector's CIGO with the rate for the employer's activity.

    The generic industria rate is already included in both permanent and
    apprentice rates; artigianato includes no CIGO. CIGS and all IVS rates
    remain unchanged. The apprentice rate is that of an operaio, as in the
    INPS circular's apprenticeship provision.

    Returns:
        Rates with only the employer's activity-dependent CIGO adjusted.
    """
    inps = rules.inps
    if inps is None or activity not in _OPERAI_CIGO:
        return rules
    if sector not in {TaxSector.INDUSTRIA, TaxSector.ARTIGIANATO}:
        return rules
    general = (
        (Decimal("0.017") if headcount <= 50 else Decimal("0.020"))
        if sector is TaxSector.INDUSTRIA
        else Decimal(0)
    )
    office = Decimal("0.017") if headcount <= 50 else Decimal("0.020")
    operai_delta = _OPERAI_CIGO[activity] - general
    office_delta = office - general
    by_category = dict(inps.employer_rate_by_category)
    for category in (WorkerCategory.IMPIEGATO, WorkerCategory.QUADRO):
        by_category[category] = (
            inps.employer_rate_by_category.get(category, inps.employer_rate)
            + office_delta
        )
        # Artisan sector tiers differ between operai and office workers;
        # their base category rates must not receive the operaio increment.
    updated = inps.model_copy(
        update={
            "employer_rate": inps.employer_rate + operai_delta,
            "employer_rate_by_category": by_category,
            "wage_integration_employer_rate": (
                inps.wage_integration_employer_rate + operai_delta
            ),
        }
    )
    apprentice = rules.apprentice
    if apprentice is not None:
        apprentice = apprentice.model_copy(
            update={
                "employer_rate_months_0_11": (
                    apprentice.employer_rate_months_0_11 + operai_delta
                ),
                "employer_rate_months_12_23": (
                    apprentice.employer_rate_months_12_23 + operai_delta
                ),
                "employer_rate_after": apprentice.employer_rate_after + operai_delta,
            }
        )
    return rules.model_copy(update={"inps": updated, "apprentice": apprentice})
