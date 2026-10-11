"""Independent Art. 12 TUIR family deduction oracle, tax year 2026.

Written from the statutory text, deliberately without importing anything from
``ccnl_engine``.  Given the reddito complessivo of the year, it answers what
the deduction for a full year of dependency is, and prorates it by months.

Text in force, read on Normattiva on 3 October 2026 (vigenza 12-8-2026 al
31-12-2026; the 2025-2026 amendments of notes 241 and 250 touch only c.
4-ter),
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art12!vig=

- c. 1 lett. a), spouse: "1) 800 euro, diminuiti del prodotto tra 110 euro e
  l'importo corrispondente al rapporto fra reddito complessivo e 15.000
  euro, se il reddito complessivo non supera 15.000 euro; 2) 690 euro, se il
  reddito complessivo è superiore a 15.000 euro ma non a 40.000 euro; 3) 690
  euro, se il reddito complessivo è superiore a 40.000 euro ma non a 80.000
  euro. La detrazione spetta per la parte corrispondente al rapporto tra
  l'importo di 80.000 euro, diminuito del reddito complessivo, e 40.000
  euro";
- c. 1 lett. b): "la detrazione spettante ai sensi della lettera a) è
  aumentata di un importo pari a: 1) 10 euro, se il reddito complessivo è
  superiore a 29.000 euro ma non a 29.200 euro; 2) 20 euro, se [...]
  superiore a 29.200 euro ma non a 34.700 euro; 3) 30 euro, se [...]
  superiore a 34.700 euro ma non a 35.000 euro; 4) 20 euro, se [...]
  superiore a 35.000 euro ma non a 35.100 euro; 5) 10 euro, se [...]
  superiore a 35.100 euro ma non a 35.200 euro";
- c. 1 lett. c), children: 950 euro each, "per la parte corrispondente al
  rapporto tra l'importo di 95.000 euro, diminuito del reddito complessivo,
  e 95.000 euro", with 95.000 "aumentato per tutti di 15.000 euro per ogni
  figlio successivo al primo";
- c. 1 lett. d), ascendants: 750 euro each, "per la parte corrispondente al
  rapporto tra l'importo di 80.000 euro, diminuito del reddito complessivo,
  e 80.000 euro";
- c. 3: the deductions "sono rapportate a mese e competono dal mese in cui
  si sono verificate a quello in cui sono cessate le condizioni richieste";
- c. 4: "Se il rapporto di cui al comma 1, lettera a), numero 1), è uguale a
  uno, la detrazione compete nella misura di 690 euro. Se i rapporti di cui
  al comma 1, lettera a), numeri 1) e 3), sono uguali a zero, la detrazione
  non compete. Se i rapporti di cui al comma 1, lettere c) e d), sono pari a
  zero, minori di zero o uguali a uno, le detrazioni non competono. Negli
  altri casi, il risultato dei predetti rapporti si assume nelle prime
  quattro cifre decimali."

Rounding order of the oracle: the ratio is truncated to four decimals, it
multiplies the amount, the full-year amount is multiplied by ``months / 12``
and the share, and the result is rounded half up to the cent once.

Worked examples, spouse, twelve months of dependency:

| Reddito complessivo | Rule | Deduction |
|---:|---|---:|
| 29,100 | 690 + 10 (29,000 < R <= 29,200) | 700 |
| 30,000 | 690 + 20 (29,200 < R <= 34,700) | 710 |
| 34,800 | 690 + 30 (34,700 < R <= 35,000) | 720 |
| 35,050 | 690 + 20 (35,000 < R <= 35,100) | 710 |
| 35,150 | 690 + 10 (35,100 < R <= 35,200) | 700 |
| 50,001 | 690 x 0.7499 (29,999 / 40,000 = 0.749975) | 517.43 |
"""

from __future__ import annotations

from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import NamedTuple

__all__ = [
    "SPOUSE_BAND_EXAMPLES",
    "IncomeBand",
    "ascendant_deduction",
    "child_deduction",
    "spouse_deduction",
]

_CENT = Decimal("0.01")
_RATIO = Decimal("0.0001")
_MONTHS_IN_YEAR = 12
_ZERO = Decimal(0)
_ONE = Decimal(1)


class IncomeBand(NamedTuple):
    """A band of reddito complessivo: above ``floor``, not above ``ceiling``."""

    floor: Decimal
    ceiling: Decimal

    def contains(self, income: Decimal) -> bool:
        """Return whether ``income`` falls in the band.

        Returns:
            ``floor < income <= ceiling``, the "superiore a ... ma non a" form.
        """
        return self.floor < income <= self.ceiling


#: Art. 12 c. 1 lett. b): increase of the spouse deduction per income band.
_INCREASES: tuple[tuple[IncomeBand, Decimal], ...] = (
    (IncomeBand(Decimal(29_000), Decimal(29_200)), Decimal(10)),
    (IncomeBand(Decimal(29_200), Decimal(34_700)), Decimal(20)),
    (IncomeBand(Decimal(34_700), Decimal(35_000)), Decimal(30)),
    (IncomeBand(Decimal(35_000), Decimal(35_100)), Decimal(20)),
    (IncomeBand(Decimal(35_100), Decimal(35_200)), Decimal(10)),
)

#: (reddito complessivo, band of lett. b) it falls in) of the worked examples.
SPOUSE_BAND_EXAMPLES: tuple[tuple[Decimal, IncomeBand], ...] = tuple(
    (income, band)
    for income in (
        Decimal(29_100),
        Decimal(30_000),
        Decimal(34_800),
        Decimal(35_050),
        Decimal(35_150),
    )
    for band, _ in _INCREASES
    if band.contains(income)
)


def _ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
    # Ratio taken to its first four decimals, the rest discarded (c. 4).
    return (numerator / denominator).quantize(_RATIO, rounding=ROUND_DOWN)


def _prorated(annual: Decimal, months: int, share: Decimal) -> Decimal:
    if not 0 <= months <= _MONTHS_IN_YEAR:
        msg = f"months must be in 0-12; got {months}"
        raise ValueError(msg)
    amount = annual * months / _MONTHS_IN_YEAR * share / 100
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def _spouse_annual(income: Decimal) -> Decimal:
    if income <= _ZERO:
        return _ZERO  # c. 4: ratio of number 1) equal to zero
    if income <= 15_000:
        base = Decimal(800) - Decimal(110) * _ratio(income, Decimal(15_000))
    elif income <= 40_000:
        base = Decimal(690)
    elif income < 80_000:
        base = Decimal(690) * _ratio(Decimal(80_000) - income, Decimal(40_000))
    else:
        base = _ZERO
    increase = next(
        (amount for band, amount in _INCREASES if band.contains(income)), _ZERO
    )
    return base + increase


def spouse_deduction(
    income: Decimal, months: int = _MONTHS_IN_YEAR, share: Decimal = Decimal(100)
) -> Decimal:
    """Return the spouse deduction of art. 12 c. 1 lett. a) and b).

    Args:
        income: Reddito complessivo of the year.
        months: Months of the year the spouse is dependent, 0-12.
        share: Percentage of the deduction of the worker.

    Returns:
        The deduction for ``months`` months, rounded to the cent.
    """
    return _prorated(_spouse_annual(income), months, share)


def _phased(amount: Decimal, ceiling: Decimal, income: Decimal) -> Decimal:
    exact = (ceiling - income) / ceiling
    if exact <= _ZERO or exact >= _ONE:
        return _ZERO  # c. 4: zero, below zero or equal to one
    return amount * _ratio(ceiling - income, ceiling)


def child_deduction(
    income: Decimal,
    children: int = 1,
    months: int = _MONTHS_IN_YEAR,
    share: Decimal = Decimal(100),
) -> Decimal:
    """Return the deduction for one child of art. 12 c. 1 lett. c).

    Args:
        income: Reddito complessivo of the year.
        children: Children giving right to the deduction, ``>= 1``.
        months: Months the child gives right to it, 0-12.
        share: Percentage of the deduction of the worker.

    Returns:
        The deduction for ``months`` months, rounded to the cent.
    """
    ceiling = Decimal(95_000) + Decimal(15_000) * (children - 1)
    return _prorated(_phased(Decimal(950), ceiling, income), months, share)


def ascendant_deduction(
    income: Decimal,
    months: int = _MONTHS_IN_YEAR,
    share: Decimal = Decimal(100),
) -> Decimal:
    """Return the deduction for one ascendant of art. 12 c. 1 lett. d).

    Returns:
        The deduction for ``months`` months, rounded to the cent.
    """
    return _prorated(_phased(Decimal(750), Decimal(80_000), income), months, share)
