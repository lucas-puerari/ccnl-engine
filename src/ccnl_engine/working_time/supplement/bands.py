"""Select the in-force supplement band for a worker and work kind."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.working_time.hourly.policies import Unstated
from ccnl_engine.working_time.supplement.models import SupplementWork

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.working_time.hourly.policies import HourlyTerms
    from ccnl_engine.working_time.supplement.models import SupplementBand


def _in_force(
    terms: HourlyTerms, work: SupplementWork, day: date
) -> list[tuple[SupplementBand, Decimal]]:
    """Return the bands of ``work`` for the worker's level in force on ``day``.

    Returns:
        Each band with its rate on ``day``.
    """
    supplements = terms.supplements
    bands = () if supplements is None else supplements.supplement_bands
    found: list[tuple[SupplementBand, Decimal]] = []
    for band in bands:
        period = band.rate.period_at(day)
        if (
            band.work is work
            and (not band.levels or terms.level_code in band.levels)
            and period is not None
            and period.value is not None
        ):
            found.append((band, period.value))
    return found


def band_for(
    terms: HourlyTerms, work: SupplementWork, day: date
) -> tuple[SupplementBand, Decimal] | str | Unstated:
    """Return the band of ``work`` the worker is paid with on ``day``.

    Returns:
        The band and its rate, or the reason none can be chosen.
    """
    found = _in_force(terms, work, day)
    if not found:
        return (
            f"the CCNL ({terms.ruleset}) has no {work.value} supplement band "
            "the engine applies (see its coverage notes)"
        )
    roles = sorted({b.role for b, _ in found if b.role is not None})
    if roles and terms.roles is None:
        return Unstated(
            "Employment.roles",
            f"the CCNL ({terms.ruleset}) pays {work.value} work apart for the "
            f"roles {', '.join(roles)} and Employment.roles is not stated",
        )
    held = terms.roles or frozenset()
    chosen = next(((b, r) for b, r in found if b.role in held), None)
    chosen = chosen or next(((b, r) for b, r in found if b.role is None), None)
    if chosen is None:
        return (
            f"the CCNL ({terms.ruleset}) has a {work.value} supplement band "
            f"only for the roles {', '.join(roles)}"
        )
    return chosen
