"""The sick days INPS pays an operaio agricolo a tempo determinato.

INPS, Guida alla tutela previdenziale della malattia (September 2024, p.
4): "51 giornate di iscrizione negli elenchi nominativi dell'anno
precedente oppure 51 giornate di iscrizione nell'anno in corso, purché
prima dell'inizio dell'evento di malattia"; "l'indennità è riconosciuta per
un numero di giorni pari a quelli di iscrizione negli elenchi, con un
massimo di 180 giorni nell'anno solare"; "se le 51 giornate sono state
lavorate nell'anno in corso, il numero massimo di giornate indennizzabili è
30".  The days counted are the indemnified ones: the carenza is not.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.sickness.agricultural.inputs import AgriculturalDays
    from ccnl_engine.sickness.indemnity.models import InpsSickPayRates

__all__ = ["AgriculturalLimit", "agricultural_limit"]

_REQUIRED = 51
_CURRENT_YEAR_DAYS = 30


class _YearCounts(Protocol):
    short_term: dict[int, int]


@dataclass(frozen=True)
class AgriculturalLimit:
    """The indemnified days of a calendar year, INPS paying them directly.

    Attributes:
        days: Days of a calendar year INPS pays at most.
        carenza_days: Days of the waiting period, not counted.
        direct_after: Episode day after which INPS pays directly: every one.
    """

    days: int
    carenza_days: int
    direct_after: int = 0

    def allows(self, index: int, day: date, inps: _YearCounts) -> bool:
        """Count ``day`` against the year when it is past the carenza.

        Returns:
            Whether the day is within the days of the year.
        """
        if index <= self.carenza_days:
            return True
        count = inps.short_term.get(day.year, 0)
        if count >= self.days:
            return False
        inps.short_term[day.year] = count + 1
        return True


def agricultural_limit(
    days: AgriculturalDays | None, inps: InpsSickPayRates
) -> AgriculturalLimit | None:
    """Return the days a year INPS pays from the registration days.

    Returns:
        The registration days of the year before, at most the INPS annual
        maximum, when they are 51 or more; else 30 when the current year
        has 51; else none; ``None`` when the days are not stated.
    """
    if days is None:
        return None
    if days.previous_year >= _REQUIRED:
        paid = min(days.previous_year, inps.annual_max_days)
    elif days.current_year >= _REQUIRED:
        paid = _CURRENT_YEAR_DAYS
    else:
        paid = 0
    return AgriculturalLimit(paid, inps.carenza_days)
