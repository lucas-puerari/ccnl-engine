"""The rota of a security guard: working days, rest days.

FEDERDAT art. 89: "25 giorni di lavoro quando si applica il sistema 5 + 1
(cinque giorni di lavoro e un giorno di riposo); 23 giorni di lavoro quando
si applica il sistema 6 + 1 + 1 [...]; 22 giorni [...] 5 + 2".
"""

from __future__ import annotations

from enum import StrEnum

from ccnl_engine.validators import parse_enum

__all__ = ["Rota", "check_rota"]

_PATH = "Employment.rota"
_FEATURE = "employment_facts"


class Rota(StrEnum):
    """Days of work and of rest a rota repeats."""

    FIVE_ONE = "5+1"
    SIX_ONE_ONE = "6+1+1"
    FIVE_TWO = "5+2"


def check_rota(value: object) -> Rota | None:
    """Return the rota, parsed.

    Returns:
        The rota, ``None`` when not stated.
    """
    if value is None:
        return None
    return parse_enum(value, Rota, _PATH, feature=_FEATURE)
