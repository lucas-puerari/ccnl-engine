"""Comporto rules of a CCNL: the sick days the job is kept for."""

import itertools
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ComportoBand",
    "ComportoWindow",
    "HospitalComportoRule",
    "check_windows",
    "window_of",
]


class HospitalComportoRule(BaseModel):
    """Hospital stays left out of the comporto count.

    Concia art. 60 B: "non saranno tenuti in considerazione i periodi di
    ricovero ospedaliero di durata superiore a 5 giorni [...] continuativi
    di calendario fino ad un massimo di 60 complessivi".

    Attributes:
        more_than_days: A stay counts when it lasts more than these
            consecutive days.
        max_days: Days of such stays left out at most, over the window.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    more_than_days: int = Field(ge=0)
    max_days: int = Field(ge=1)


class ComportoBand(BaseModel):
    """Comporto of one illness for the workers of one seniority band.

    ABI Art. 66 c. 1: "l'impresa conserva il posto e l'intero trattamento
    economico [...] per" 6, 8, 12, 15, 18, 22 months by seniority up to 5,
    10, 15, 20, 25 years and over.

    Attributes:
        seniority_months_from: Completed months of seniority from which the
            band applies; ``0`` for the first.
        comporto_days: Sick days of the illness and the relapses it
            continues the job is kept for; a day past them is outside what
            the CCNL integrates.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    seniority_months_from: int = Field(ge=0)
    comporto_days: int = Field(ge=1)


class ComportoWindow(ComportoBand):
    """Comporto summed over the sick days of the months that end on the day.

    A per-episode CCNL may pay each illness on its own and still end the
    job past a total of sick days over a window: Edilizia ANCE Art. 26,
    "Nel caso di più malattie o ricadute nella stessa malattia, l'operaio
    ha diritto alla conservazione del posto per un periodo massimo
    complessivo di nove mesi nell'arco di 20 mesi consecutivi", 12 months
    in 24 above three and a half years of seniority.

    Attributes:
        window_months: Months ending on the day whose sick days are summed,
            against the ``comporto_days`` of the band.
    """

    window_months: int = Field(ge=1)


def check_windows(windows: Sequence[ComportoBand]) -> None:
    """Check that bands or ``windows`` start at 0 months and increase.

    Raises:
        ValueError: When they do not.
    """
    starts = [w.seniority_months_from for w in windows]
    increasing = all(b > a for a, b in itertools.pairwise(starts))
    if starts and (starts[0] != 0 or not increasing):
        msg = f"comporto windows must start at 0 months and increase; got {starts}"
        raise ValueError(msg)


def window_of[Band: ComportoBand](windows: Sequence[Band], months: int) -> Band | None:
    """Return the band or window of a seniority of ``months`` completed months.

    Returns:
        The last one whose start is at most ``months``, ``None`` without
        any.
    """
    held = [w for w in windows if w.seniority_months_from <= months]
    return held[-1] if held else None
