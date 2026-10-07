"""Independent oracle of two 2026 withholding rules the IRPEF oracle leaves out.

Written from the statutory text, deliberately without importing anything from
``ccnl_engine``; the brackets and the art. 13 formula come from the sibling
oracle :mod:`.irpef_2026`, written the same way.

Sources:

- Withholding on the pay of a month: art. 23 c. 2 lett. a) DPR 600/1973
  (Normattiva, text in force from 21 May 2022 to 31 December 2026, read on
  7 October 2026): on the pay "corrisposti in ciascun periodo di paga, con
  le aliquote dell'imposta sul reddito delle persone fisiche, ragguagliando
  al periodo di paga i corrispondenti scaglioni annui di reddito, ed
  effettuando le detrazioni previste negli articoli 12 e 13 del citato
  testo unico, rapportate al periodo stesso".  AdE circ. 15/E/2007 par.
  2.1 measures the deductions on the employment income the employer pays
  in the year; par. 1.5.1 counts the days of the deduction on a year of
  365.  The further deduction of L. 207/2024 art. 1 c. 6 is "rapportata
  al periodo di lavoro" and recognized "all'atto dell'erogazione delle
  retribuzioni" (c. 7, text in force for 2026); it is taken here, like
  art. 13, for the days of the month over the days of employment.
- Withholding on an additional month: art. 23 c. 2 lett. b) DPR 600/1973
  (Normattiva, copy of the page saved for the review of 6 October 2026,
  https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art23):
  "sulle mensilità aggiuntive e sui
  compensi della stessa natura, con le aliquote dell'imposta sul reddito
  delle persone fisiche, ragguagliando a mese i corrispondenti scaglioni
  annui di reddito", with no deduction, unlike lett. a) for the ordinary
  pay of the period.
- Trattamento integrativo above 15,000 EUR: D.L. 3/2020 art. 1 c. 1, second
  and third periods, Normattiva, read on 7 October 2026
  (https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2020-02-05;3~art1):
  due "se il reddito complessivo è superiore a 15.000 euro ma non a 28.000
  euro, a condizione che la somma delle detrazioni di cui agli articoli 12 e
  13, comma 1" (plus art. 15 interest on loans taken until 2021 and the
  other listed deductions, none of which the callers here have) "sia di
  ammontare superiore all'imposta lorda", and then "per un ammontare,
  comunque non superiore a 1.200 euro, determinato in misura pari alla
  differenza tra la somma delle detrazioni ivi elencate e l'imposta lorda".
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from tests.fixtures.normative_oracles.irpef_2026 import (
    employment_deduction,
    further_deduction,
    gross_irpef,
)

__all__ = [
    "extra_month_withholding",
    "regular_month_withholding",
    "trattamento_integrativo_above_15000",
]

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


def regular_month_withholding(
    taxable: Decimal,
    annual_income: Decimal,
    days: int,
    *,
    employment_days: int = 365,
    family: Decimal = _ZERO,
) -> Decimal:
    """Return the IRPEF withheld on the pay of a month under lett. a).

    Args:
        taxable: Taxable income of the month.
        annual_income: Employment income of the year the deductions are
            measured on.
        days: Days of employment in the month.
        employment_days: Days of employment in the year.
        family: Art. 12 TUIR deductions of the month.

    Returns:
        The tax of :func:`extra_month_withholding` less the art. 13 and the
        further deduction of the year times ``days / employment_days``, each
        rounded to the cent, less ``family``; at least zero.
    """
    share = Decimal(days) / Decimal(employment_days)
    work = employment_deduction(annual_income, employment_days) * share
    further = further_deduction(annual_income, employment_days) * share
    deductions = work.quantize(_CENT, rounding=ROUND_HALF_UP) + further.quantize(
        _CENT, rounding=ROUND_HALF_UP
    )
    return max(extra_month_withholding(taxable) - deductions - family, _ZERO)


def trattamento_integrativo_above_15000(
    income: Decimal, family_deductions: Decimal
) -> Decimal:
    """Return the trattamento integrativo of c. 1 above 15,000 EUR for a full year.

    Args:
        income: Reddito complessivo, employment only, 15,000 to 28,000 EUR.
        family_deductions: Art. 12 TUIR deductions of the year.

    Returns:
        ``min(1,200, art. 12 + art. 13 - imposta lorda)``, zero when the
        deductions do not exceed the gross tax.

    Raises:
        ValueError: When ``income`` is outside the 15,000-28,000 EUR band of c. 1.
    """
    if not _TRATTAMENTO_FLOOR_INCOME < income <= _TRATTAMENTO_CEILING_INCOME:
        msg = f"income {income} is outside the 15,000-28,000 band of c. 1"
        raise ValueError(msg)
    excess = family_deductions + employment_deduction(income) - gross_irpef(income)
    return min(max(excess, _ZERO), _TRATTAMENTO_CAP)
