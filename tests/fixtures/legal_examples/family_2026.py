"""Independent Art. 12 TUIR spouse deduction oracle, tax year 2026.

Written from the statutory text, deliberately without importing anything from
``ccnl_engine``.  It answers one question: given the reddito complessivo of
the year and the months of dependency, what is the spouse deduction?

Scope (anything outside raises :class:`ValueError`): reddito complessivo
above 15,000 EUR and not above 40,000 EUR, the flat band of lett. a), where
no ratio and so no truncation rule is involved.

Text in force, read on Normattiva on 3 October 2026,
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art12!vig=

- art. 12 c. 1 lett. a): "690 euro, se il reddito complessivo è superiore a
  15.000 euro ma non a 40.000 euro";
- art. 12 c. 1 lett. b): "la detrazione spettante ai sensi della lettera a)
  è aumentata di un importo pari a: 1) 10 euro, se il reddito complessivo è
  superiore a 29.000 euro ma non a 29.200 euro; 2) 20 euro, se il reddito
  complessivo è superiore a 29.200 euro ma non a 34.700 euro; 3) 30 euro,
  se il reddito complessivo è superiore a 34.700 euro ma non a 35.000 euro;
  4) 20 euro, se il reddito complessivo è superiore a 35.000 euro ma non a
  35.100 euro; 5) 10 euro, se il reddito complessivo è superiore a 35.100
  euro ma non a 35.200 euro";
- art. 12 c. 3: the deductions "sono rapportate a mese e competono dal mese
  in cui si sono verificate a quello in cui sono cessate le condizioni
  richieste".  The oracle multiplies by ``months / 12`` and rounds to cents.

Worked examples, twelve months of dependency:

| Reddito complessivo | Base | Increase | Deduction |
|---:|---:|---:|---:|
| 29,100 | 690 | 10 (29,000 < R <= 29,200) | 700 |
| 30,000 | 690 | 20 (29,200 < R <= 34,700) | 710 |
| 34,800 | 690 | 30 (34,700 < R <= 35,000) | 720 |
| 35,050 | 690 | 20 (35,000 < R <= 35,100) | 710 |
| 35,150 | 690 | 10 (35,100 < R <= 35,200) | 700 |
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import NamedTuple

__all__ = ["SPOUSE_BAND_EXAMPLES", "IncomeBand", "spouse_deduction"]

_CENT = Decimal("0.01")
_MONTHS_IN_YEAR = 12
_FLAT_FLOOR = Decimal(15_000)
_FLAT_CEILING = Decimal(40_000)
_FLAT_DEDUCTION = Decimal(690)


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


def spouse_deduction(income: Decimal, months: int = _MONTHS_IN_YEAR) -> Decimal:
    """Return the annual spouse deduction of art. 12 c. 1 lett. a) and b).

    Args:
        income: Reddito complessivo of the year.
        months: Months of the year the spouse is dependent, 1-12.

    Returns:
        The deduction for ``months`` months, rounded to the cent.

    Raises:
        ValueError: When ``income`` is outside the flat band of lett. a) or
            ``months`` is outside 1-12.
    """
    if not IncomeBand(_FLAT_FLOOR, _FLAT_CEILING).contains(income):
        msg = f"income {income} outside the flat band 15,000-40,000"
        raise ValueError(msg)
    if not 1 <= months <= _MONTHS_IN_YEAR:
        msg = f"months must be in 1-12; got {months}"
        raise ValueError(msg)
    increase = next(
        (amount for band, amount in _INCREASES if band.contains(income)),
        Decimal(0),
    )
    annual = _FLAT_DEDUCTION + increase
    return (annual * months / _MONTHS_IN_YEAR).quantize(_CENT, rounding=ROUND_HALF_UP)
