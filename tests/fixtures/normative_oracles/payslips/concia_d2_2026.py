"""Independent full-year payslip oracle: CCNL Concia UNIC, level D2, 2026.

Written from the sources, deliberately without importing anything from
``ccnl_engine``; the IRPEF and surtax figures come from the sibling oracles
:mod:`.irpef_2026` and :mod:`.surtax_2026`, written the same way.  No figure
was read from the engine's output.

Scenario: a full-time worker of level D2, hired on 1 January 2026 by an
industrial tannery with 50 employees, paid twelve regular months and the
tredicesima in 2026, no event, no seniority increment, no dependant,
resident in Alghero (Sardegna), 2025 employment income of 40,000 EUR from an
earlier employer (not imported: it only decides the renewal regime below).

Sources, each with section and effective date:

- Minimo tabellare D2 from 1 January 2026: "Ipotesi di accordo per il
  rinnovo del CCNL Concia" of 7 March 2024 (UNIC, Filctem-CGIL,
  Femca-CISL, Uiltec-UIL), contracting-party PDF
  https://www.filctemcgil.it/images/download/CONTRATTI/concia/240307_CONCIA_RINNOVO%20CCNL%202023-2026.pdf
  (sha256 4988c9f804760f367b02e333503187e4a89d5e74e8db95ee4a7ffc1ad774a117,
  scanned, read by OCR on 4 October 2026).  "Parte economica" (page 13):
  "L'aumento contrattuale è pari a 191,00 euro al livello D2 così erogati:
  euro 96,00 dal 1° marzo 2024, euro 55,00 dal 1° gennaio 2025, euro 40,00
  dal 1° gennaio 2026"; Allegato n. 1 (page 14): minimo D2 1,850.99 at the
  30 June 2023 expiry and 2,041.99 from 1 January 2026.  The oracle adds the
  tranches to the expiry minimo and checks the sum against the table.
- EDR 10.33 EUR a month: the elemento distinto della retribuzione of the
  Protocollo Governo-parti sociali of 31 July 1992, 20,000 lire converted at
  1,936.27 lire per euro.  Not fetched for this oracle, and Allegato n. 1
  has no EDR column: the amount is the one the bundle reads, sourced here
  only to the Protocollo.
- One additional month (tredicesima), no quattordicesima: not stated in the
  rinnovo, which leaves the CCNL text unchanged; the count is the bundle's
  and is not read from a primary source here.
- Employee INPS: FPLD IVS 9.19% (the employee share INPS publishes, not
  fetched) and CIGS 0.30% (D.Lgs. 148/2015 art. 23 c. 1, employee third of
  0.90% for industrial employers above 15 employees, art. 20).  The annual
  gross is under half of the first pensionable-earnings band of 2025 and
  2026, so the additional 1% (L. 438/1992 art. 3-ter) is not due, and far
  under the IVS massimale; neither the band nor the massimale enters a
  figure.  The 2026 values are in INPS circolare n. 6 of 30 January 2026
  (massimale 122,295 EUR), as secondary sources (ecnews.it, Ascom Bologna)
  report it; the circular itself was not fetched.
- TFR quota: art. 2120 c. 1 c.c., the yearly pay divided by 13.5, accrued
  per month here; L. 297/1982 art. 3 (Normattiva, read on 4 October 2026)
  raises the employer IVS rate by 0.50% and has the employer deduct that
  contribution "dall'ammontare della quota del trattamento di fine rapporto
  relativa al periodo di riferimento".
- IRPEF of the year: :func:`.irpef_2026.net_irpef` on the annual taxable
  for 365 days.  No trattamento integrativo: the annual taxable is above
  15,000 EUR and the art. 13 deduction plus the further deduction stay below
  the gross IRPEF (D.L. 3/2020 art. 1 cc. 1 and 1-bis).  No somma esente:
  the income is above 20,000 EUR (L. 207/2024 art. 1 c. 4).  No 5% renewal
  substitute tax: the 2025 employment income is above 33,000 EUR
  (L. 199/2025 art. 1 c. 7).
- Surtaxes of 2026, determined at the December conguaglio and withheld in
  2027: Sardegna 1.23% and Alghero 0.8% (:mod:`.surtax_2026`), balance in
  eleven installments, municipal acconto of 2027 30% in nine.

Worked example:

    monthly gross   2,041.99 + 10.33                    = 2,052.32
    employee INPS   2,052.32 x 9.49% = 194.7652          ->  194.77
    TFR quota       2,052.32 / 13.5  = 152.0237          ->  152.02
    TFR deduction   2,052.32 x 0.50% = 10.2616           ->   10.26
    annual gross    2,052.32 x 13                       = 26,680.16
    annual INPS     194.77 x 13                         =  2,532.01
    annual taxable  26,680.16 - 2,532.01                = 24,148.15
    gross IRPEF     23% of 24,148.15                     =  5,554.07
    art. 13         1,910 + 1,190 x 0.2962 (truncated)   =  2,262.48
    further         L. 207/2024 c. 6 lett. a             =  1,000.00
    net IRPEF       5,554.07 - 2,262.48 - 1,000.00      =  2,291.59
    net pay         26,680.16 - 2,532.01 - 2,291.59     = 21,856.56
    Sardegna        24,148.15 x 1.23% = 297.0222         ->  297.02
    Alghero         24,148.15 x 0.80% = 193.1852         ->  193.19
    acconto 2027    193.19 x 30%      = 57.957           ->   57.96
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from tests.fixtures.normative_oracles.irpef_2026 import net_irpef
from tests.fixtures.normative_oracles.surtax_2026 import (
    municipal_advance,
    municipal_alghero,
    regional_sardegna,
)

__all__ = ["CONCIA_D2_2026", "ConciaYear"]

_CENT = Decimal("0.01")

#: Allegato n. 1, minimo D2 at the expiry of 30 June 2023.
_MINIMUM_AT_EXPIRY = Decimal("1850.99")
#: Parte economica, D2 tranches of 1 March 2024, 1 January 2025 and 2026.
_TRANCHES = (Decimal("96.00"), Decimal("55.00"), Decimal("40.00"))
#: Allegato n. 1, minimo D2 from 1 January 2026.
_TABLE_MINIMUM_2026 = Decimal("2041.99")
_EDR_LIRE = Decimal(20_000)
_LIRE_PER_EURO = Decimal("1936.27")
_MONTHS_PAID = 13
_EMPLOYEE_INPS_RATE = Decimal("0.0919") + Decimal("0.0030")
_TFR_DIVISOR = Decimal("13.5")
_TFR_EXTRA_IVS_RATE = Decimal("0.0050")


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class ConciaYear:
    """The oracle figures of the scenario, in EUR.

    Attributes:
        minimum: Minimo tabellare D2 of every 2026 payment.
        edr: Elemento distinto della retribuzione of every payment.
        monthly_gross: Gross of each of the thirteen payments.
        monthly_inps: Employee INPS of each payment.
        tfr_divisor: Art. 2120 c.c. divisor of the yearly pay.
        tfr_quota: Art. 2120 c.c. TFR quota of each payment.
        tfr_net_of_extra_ivs: The quota less the 0.50% L. 297/1982 deducts.
        payments: Number of payments of the tax year.
        gross: Gross of the year.
        inps: Employee INPS of the year.
        taxable: IRPEF taxable income of the year.
        irpef: Net IRPEF of the year, all withheld by the conguaglio.
        net: Net pay of the year.
        regional: Regional surtax of 2026, withheld in 2027.
        municipal: Municipal surtax of 2026, withheld in 2027.
        municipal_advance: Municipal acconto of 2027.
    """

    minimum: Decimal
    edr: Decimal
    monthly_gross: Decimal
    monthly_inps: Decimal
    tfr_divisor: Decimal
    tfr_quota: Decimal
    tfr_net_of_extra_ivs: Decimal
    payments: int
    gross: Decimal
    inps: Decimal
    taxable: Decimal
    irpef: Decimal
    net: Decimal
    regional: Decimal
    municipal: Decimal
    municipal_advance: Decimal


def _year() -> ConciaYear:
    minimum = _MINIMUM_AT_EXPIRY + sum(_TRANCHES, Decimal(0))
    if minimum != _TABLE_MINIMUM_2026:
        msg = f"tranches give {minimum}, Allegato n. 1 states {_TABLE_MINIMUM_2026}"
        raise ValueError(msg)
    edr = _cents(_EDR_LIRE / _LIRE_PER_EURO)
    monthly_gross = minimum + edr
    monthly_inps = _cents(monthly_gross * _EMPLOYEE_INPS_RATE)
    tfr_quota = _cents(monthly_gross / _TFR_DIVISOR)
    gross = monthly_gross * _MONTHS_PAID
    inps = monthly_inps * _MONTHS_PAID
    taxable = gross - inps
    irpef = net_irpef(taxable)
    municipal = municipal_alghero(taxable, irpef)
    return ConciaYear(
        minimum=minimum,
        edr=edr,
        monthly_gross=monthly_gross,
        monthly_inps=monthly_inps,
        tfr_divisor=_TFR_DIVISOR,
        tfr_quota=tfr_quota,
        tfr_net_of_extra_ivs=tfr_quota - _cents(monthly_gross * _TFR_EXTRA_IVS_RATE),
        payments=_MONTHS_PAID,
        gross=gross,
        inps=inps,
        taxable=taxable,
        irpef=irpef,
        net=gross - inps - irpef,
        regional=regional_sardegna(taxable, irpef),
        municipal=municipal,
        municipal_advance=municipal_advance(municipal),
    )


#: The oracle of the scenario described in the module docstring.
CONCIA_D2_2026 = _year()
