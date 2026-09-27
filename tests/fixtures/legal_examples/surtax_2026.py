"""Independent surtax oracle: Sardegna and Sassari, installments and acconto.

Written from the statutory text and the MEF tables, deliberately without
importing anything from ``ccnl_engine``.  Given the annual taxable income
of the conguaglio, it answers what the conguaglio determines and how it is
withheld in the next year.

Rates, read on the MEF Dipartimento delle Finanze on 27 September 2026:

- Regione Sardegna, anno d'imposta 2026: "Aliquota Unica" 1.23% (D.L.
  201/2011 art. 28; L.R. 48/2018 art. 2),
  https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/fiscalitalocale/addregirpef/addregirpef.php?reg=15
  ; the deduction of 200 EUR per minor child is out of scope (no
  dependants here);
- Comune di Sassari (I452), anno d'imposta 2025: 0.8%, "soglia di
  esenzione" 15,000 EUR of taxable income (delibera n. 13 of 9 April 2014,
  published 20 December 2025); no 2026 row was published.  Above the
  threshold the rate applies to the whole taxable income,
  https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/fiscalitalocale/nuova_addcomirpef/risultato.htm?anno=9999&cm=&pr=SS&cc=I452&r=1
  .

Rules:

- both surtaxes are due only when the net IRPEF of the year is due
  (D.Lgs. 446/1997 art. 50 c. 2; D.Lgs. 360/1998 art. 1 c. 4);
- acconto: "30 per cento dell'addizionale ottenuta applicando le aliquote
  ... al reddito imponibile dell'anno precedente", with the rate and
  threshold "nella misura vigente nell'anno precedente" (art. 1 c. 4);
- installments: at most eleven for the regional surtax and the municipal
  saldo, from the pay period after the conguaglio and not beyond the one
  whose withholding is remitted in December (art. 50 c. 4; art. 1 c. 5),
  so January to November after a December conguaglio; at most nine for
  the acconto, "a partire dal mese di marzo" (art. 1 c. 5), so March to
  November.  The oracle uses the maximum count with equal installments
  rounded to the cent, the last taking the residual.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

__all__ = [
    "ADVANCE_MONTHS",
    "BALANCE_MONTHS",
    "installments",
    "municipal_advance",
    "municipal_sassari",
    "regional_sardegna",
]

_CENT = Decimal("0.01")
_ZERO = Decimal(0)
_SARDEGNA_RATE = Decimal("0.0123")
_SASSARI_RATE = Decimal("0.008")
_SASSARI_THRESHOLD = Decimal(15_000)
_ADVANCE_SHARE = Decimal("0.30")

#: Months of the eleven balance installments after a December conguaglio.
BALANCE_MONTHS: tuple[int, ...] = tuple(range(1, 12))
#: Months of the nine acconto installments.
ADVANCE_MONTHS: tuple[int, ...] = tuple(range(3, 12))


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def regional_sardegna(taxable: Decimal, net_irpef: Decimal) -> Decimal:
    """Return the regional surtax of Sardegna on ``taxable``.

    Returns:
        1.23% of the taxable income, zero without net IRPEF due.
    """
    if net_irpef <= _ZERO:
        return _ZERO
    return _cents(taxable * _SARDEGNA_RATE)


def municipal_sassari(taxable: Decimal, net_irpef: Decimal) -> Decimal:
    """Return the municipal surtax of Sassari on ``taxable``.

    Returns:
        0.8% of the whole taxable income above the 15,000 EUR threshold,
        zero at or below it or without net IRPEF due.
    """
    if net_irpef <= _ZERO or taxable <= _SASSARI_THRESHOLD:
        return _ZERO
    return _cents(taxable * _SASSARI_RATE)


def municipal_advance(municipal: Decimal) -> Decimal:
    """Return the acconto of the next year: 30% of the municipal surtax.

    Returns:
        The acconto, rounded to the cent.
    """
    return _cents(municipal * _ADVANCE_SHARE)


def installments(amount: Decimal, months: tuple[int, ...]) -> dict[int, Decimal]:
    """Split ``amount`` over ``months``: equal cents, the last the residual.

    Returns:
        Amount due by month.
    """
    share = _cents(amount / len(months))
    split = dict.fromkeys(months[:-1], share)
    split[months[-1]] = amount - share * (len(months) - 1)
    return split
