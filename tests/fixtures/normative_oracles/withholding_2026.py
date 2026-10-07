"""Independent oracle of three 2026 withholding rules the IRPEF oracle leaves out.

Written from the statutory text, deliberately without importing anything from
``ccnl_engine``; the brackets and the art. 13 formula come from the sibling
oracle :mod:`.irpef_2026`, written the same way.

Sources (read on 7 October 2026):

- Floor of the employment deduction: art. 13 c. 1 lett. a) TUIR, text in
  force on Normattiva
  (https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art13):
  "L'ammontare della detrazione effettivamente spettante non può essere
  inferiore a 690 euro. Per i rapporti di lavoro a tempo determinato,
  l'ammontare della detrazione effettivamente spettante non può essere
  inferiore a 1.380 euro".  Allegato C to the 730/2026 instructions of the
  Agenzia delle Entrate, section on the employment deduction up to 15,000
  EUR: "l'importo della detrazione minima come sopra determinata non deve
  essere rapportata ai giorni di lavoro dipendente"; the deduction due is
  the larger of the floor and the formula proportioned to the days.
- Withholding on an additional month: art. 23 c. 2 lett. b) DPR 600/1973
  (Normattiva): "sulle mensilità aggiuntive e sui compensi della stessa
  natura, con le aliquote dell'imposta sul reddito delle persone fisiche,
  ragguagliando a mese i corrispondenti scaglioni annui di reddito", with
  no deduction, unlike lett. a) for the ordinary pay of the period.
- Trattamento integrativo above 15,000 EUR: D.L. 3/2020 art. 1 c. 1 and
  c. 1-bis (Normattiva): due up to 28,000 EUR of reddito complessivo when
  "la somma delle detrazioni di cui agli articoli 12 e 13, comma 1" (plus
  art. 15 interest on loans taken before 2022 and the other listed
  deductions, none of which the callers here have) "sia di ammontare
  superiore all'imposta lorda", for "un ammontare, comunque non superiore a
  1.200 euro, determinato in misura pari alla differenza tra la somma delle
  detrazioni [...] e l'imposta lorda".
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from tests.fixtures.normative_oracles.irpef_2026 import (
    employment_deduction,
    gross_irpef,
)

__all__ = [
    "EMPLOYMENT_DEDUCTION_FLOOR",
    "FIXED_TERM_EMPLOYMENT_DEDUCTION_FLOOR",
    "extra_month_withholding",
    "trattamento_integrativo_above_15000",
]

#: Art. 13 c. 1 lett. a) TUIR, open-ended employment; not proportioned.
EMPLOYMENT_DEDUCTION_FLOOR = Decimal("690.00")
#: Art. 13 c. 1 lett. a) TUIR, fixed-term employment; not proportioned.
FIXED_TERM_EMPLOYMENT_DEDUCTION_FLOOR = Decimal("1380.00")

_CENT = Decimal("0.01")
_ZERO = Decimal(0)
_MONTHS = 12
_TRATTAMENTO_CAP = Decimal("1200.00")
_TRATTAMENTO_FLOOR_INCOME = Decimal(15_000)
_TRATTAMENTO_CEILING_INCOME = Decimal(28_000)
# (annual upper bound, rate) of the 2026 brackets, art. 11 c. 1 TUIR.
_ANNUAL_BRACKETS: tuple[tuple[Decimal | None, Decimal], ...] = (
    (Decimal(28_000), Decimal("0.23")),
    (Decimal(50_000), Decimal("0.33")),
    (None, Decimal("0.43")),
)


def extra_month_withholding(taxable: Decimal) -> Decimal:
    """Return the IRPEF withheld on an additional month under lett. b).

    The annual brackets are divided by twelve (28,000 / 12 = 2,333.33...)
    and the slices of ``taxable`` taxed at their rate, with no deduction.

    Returns:
        The withholding, rounded to the cent.
    """
    tax = _ZERO
    lower = _ZERO
    for upper, rate in _ANNUAL_BRACKETS:
        top = taxable if upper is None else min(taxable, upper / _MONTHS)
        if top > lower:
            tax += (top - lower) * rate
        if upper is None or taxable <= upper / _MONTHS:
            break
        lower = upper / _MONTHS
    return tax.quantize(_CENT, rounding=ROUND_HALF_UP)


def trattamento_integrativo_above_15000(
    income: Decimal, family_deductions: Decimal
) -> Decimal:
    """Return the trattamento integrativo of c. 1-bis for a full year.

    Args:
        income: Reddito complessivo, employment only, 15,000 to 28,000 EUR.
        family_deductions: Art. 12 TUIR deductions of the year.

    Returns:
        ``min(1,200, art. 12 + art. 13 - imposta lorda)``, zero when the
        deductions do not exceed the gross tax.

    Raises:
        ValueError: When ``income`` is outside the band of c. 1-bis.
    """
    if not _TRATTAMENTO_FLOOR_INCOME < income <= _TRATTAMENTO_CEILING_INCOME:
        msg = f"income {income} is outside the 15,000-28,000 band of c. 1-bis"
        raise ValueError(msg)
    excess = family_deductions + employment_deduction(income) - gross_irpef(income)
    return min(max(excess, _ZERO), _TRATTAMENTO_CAP)
