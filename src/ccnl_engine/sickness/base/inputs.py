"""The pay history the INPS daily base of a sickness episode is computed from.

INPS pays its share of a sick day on the *retribuzione media globale
giornaliera* (RMGG) of the month immediately before the illness starts
(INPS circ. 134368 A.G.O. 14 of 28 January 1981, point 11; circ. 55 of 4
April 2024, Allegato 1): the pay of that month and the monthly share of the
recurring payments outside it, divided by 30 for an impiegato and by the
days worked or paid for an operaio.  That pay is a fact of the payroll
history, the *retribuzione teorica* the employer declared in the UniEmens
flow of that month; the engine computes the base from it
(:mod:`ccnl_engine.sickness.base.rules`).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.validators import require_decimal, require_int

__all__ = ["InpsSicknessBase", "SpettacoloSicknessBase"]

_FEATURE = "sickness"
_OWNER = "InpsSicknessBase"


@dataclass(frozen=True, slots=True)
class InpsSicknessBase:
    """The pay of the month before a sickness episode, as INPS reads it.

    Attributes:
        theoretical_pay: Gross pay of the month immediately before the first
            day of illness, the *retribuzione teorica* of its UniEmens
            flow: the monthly pay and the components normally in it
            (contractual overtime, shift allowances, in their monthly
            share), without overtime that is not contractual, amounts
            monetised whatever the illness (holidays not taken), the notice
            indemnity and the employer's integration of an earlier sickness
            (circ. 134368/1981 point 11.1; circ. 55/2024 Allegato 1).
        paid_days: Days worked or paid in that month (paid holidays and
            leave, the sixth day of a short week; never the sick days), which
            the base of an operaio divides by (point 11.3), and that of an
            impiegato who did not work the whole month, Sundays and paid
            holidays included (point 11.2 letters d-f).  ``None`` for an
            impiegato who worked the whole month.
        recurring_annual: Recurring payments of the year that are neither
            part of the monthly pay nor an additional month of the CCNL
            (annual or periodic bonuses, point 11.2 letter b); the engine
            adds the additional months of the CCNL itself.  ``0`` when there
            are none.
        full_month_pay: Monthly pay of a whole month of the employment in
            that month, when the worker was not employed all of it (a hire
            during the month): the additional months accrue on it, not on
            the pay of the days (point 11.2 letter e).  Required for an
            impiegato who did not work the whole month; ``None`` when the
            month was worked in full.

    Raises:
        InvalidInputError: When ``theoretical_pay``, ``recurring_annual``
            or ``full_month_pay`` is not a non-negative ``Decimal``, or
            ``paid_days`` is not an int in [1, 31].
    """

    theoretical_pay: Decimal
    recurring_annual: Decimal
    paid_days: int | None = None
    full_month_pay: Decimal | None = None

    def __post_init__(self) -> None:  # noqa: D105
        require_decimal(
            self.full_month_pay,
            f"{_OWNER}.full_month_pay",
            feature=_FEATURE,
            minimum=Decimal(0),
            optional=True,
        )
        for name in ("theoretical_pay", "recurring_annual"):
            require_decimal(
                getattr(self, name),
                f"{_OWNER}.{name}",
                feature=_FEATURE,
                minimum=Decimal(0),
            )
        require_int(
            self.paid_days,
            f"{_OWNER}.paid_days",
            feature=_FEATURE,
            minimum=1,
            maximum=31,
            optional=True,
        )


@dataclass(frozen=True, slots=True)
class SpettacoloSicknessBase:
    """The pay of the last daily contributions of a lavoratore dello spettacolo.

    The indemnity of a worker insured with the Fondo pensioni lavoratori
    dello spettacolo is computed on the average pay of the last 40 daily
    contributions in the sector, the 13th and the other contributed
    payments included (art. 13 D.Lgs. C.P.S. 708/1947 as amended by art. 66
    D.L. 73/2021; INPS circ. 132/2021 par. 2.4).

    Attributes:
        pay: Gross pay of those contributions, the rateo of the 13th and the
            bonuses subject to contributions included.
        contributions: Number of daily contributions the pay covers, every
            employer of the sector counted.

    Raises:
        InvalidInputError: When ``pay`` is not a non-negative ``Decimal`` or
            ``contributions`` is not an int in [1, 366].
    """

    pay: Decimal
    contributions: int

    def __post_init__(self) -> None:  # noqa: D105
        owner = "SpettacoloSicknessBase"
        require_decimal(self.pay, f"{owner}.pay", feature=_FEATURE, minimum=Decimal(0))
        require_int(
            self.contributions,
            f"{owner}.contributions",
            feature=_FEATURE,
            minimum=1,
            maximum=366,
        )
