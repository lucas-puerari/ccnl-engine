"""Independent oracle of four 2026 INPS rules on the contribution base.

Written from the sources, deliberately without importing anything from
``ccnl_engine``.

Sources:

- INPS circolare n. 6 of 30 January 2026, read on 7 October 2026 in the copy
  attached to circolare 23/26 of Ascom Bologna
  (https://ascom.bo.it/wp-content/uploads/2026/02/Allegato-1-CIRCO-23-26_Circolare-INPS-n.-6-del-30-01-2026.pdf,
  sha256 ec8fce75b98095d5b7de3d7ba725a403e1c487e1c75512567066650b88118992);
  the INPS news page of February 2026 on the circular gives the same
  figures.
  - Section 1: "Minimale di retribuzione giornaliera (9,5%) 58,13", the
    floor of art. 7 c. 1 D.L. 463/1983 to which every daily pay is raised.
  - Section 4: the hourly floor of a 40-hour week is "58,13 euro x 6/40 =
    8,72 euro", so a full-time week holds six daily floors; for the 36 hours
    on five days of the Gestione pubblica "58,13 euro x 5/36 = 8,07 euro".
    A month of a monthly-paid full-time worker holds 6 x 52 / 12 = 26 of
    them, the 26 days INPS uses for monthly pay: 58.13 x 26 = 1,511.38 EUR.
    This monthly reading is derived here, not quoted from the circular.
  - Section 5: the additional 1% of art. 3-ter D.L. 384/1992, charged to
    the worker on the pay above the first pensionable band, "rapportato a
    dodici mesi, è pari a 4.685,00 euro [...] deve essere osservato il
    criterio della mensilizzazione", with a conguaglio at year end.
- D.L. 463/1983 art. 7, Normattiva, read on 7 October 2026: c. 5 "Le
  disposizioni di cui ai commi 1, 2, 3 e 4 del presente articolo non si
  applicano ai lavoratori addetti ai servizi domestici e familiari, agli
  operai agricoli, agli apprendisti".
- L. 92/2012 art. 2, Normattiva, read on 7 October 2026: c. 28 charges the
  employer "un contributo addizionale [...] pari all'1,4 per cento della
  retribuzione imponibile" on every non-permanent employment; c. 3: "Le
  disposizioni di cui al presente articolo non si applicano nei confronti
  degli operai agricoli a tempo determinato o indeterminato", so the
  surcharge of c. 28, a provision of the same article, is not due for them.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

__all__ = [
    "ADDITIONAL_IVS_MONTHLY_THRESHOLD",
    "DAILY_CONTRIBUTION_FLOOR",
    "FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR",
    "HOURLY_FLOOR_40_HOURS",
    "HOURLY_FLOOR_PUBLIC_36_HOURS",
    "additional_ivs",
]

#: Circolare INPS 6/2026 section 1.
DAILY_CONTRIBUTION_FLOOR = Decimal("58.13")
#: Section 4 reading: 26 daily floors in a month of a 40-hour, six-day week.
FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR = DAILY_CONTRIBUTION_FLOOR * 26
#: Section 4: 58.13 x 6 / 40 = 8.7195, published as 8.72.
HOURLY_FLOOR_40_HOURS = Decimal("8.72")
#: Section 4: 58.13 x 5 / 36 = 8.0736, published as 8.07.
HOURLY_FLOOR_PUBLIC_36_HOURS = Decimal("8.07")
#: Circolare INPS 6/2026 section 5: 56,224 EUR over twelve months.
ADDITIONAL_IVS_MONTHLY_THRESHOLD = Decimal("4685.00")

_CENT = Decimal("0.01")
_ADDITIONAL_RATE = Decimal("0.01")
_ZERO = Decimal(0)


def additional_ivs(monthly_base: Decimal) -> Decimal:
    """Return the additional 1% of one month under the monthly threshold.

    Valid for a month whose year-to-date base stays under the IVS massimale
    (122,295 EUR for 2026, same circular, section 6).

    Returns:
        1% of the base above 4,685 EUR, rounded to the cent; zero below it.
    """
    excess = max(monthly_base - ADDITIONAL_IVS_MONTHLY_THRESHOLD, _ZERO)
    return (excess * _ADDITIONAL_RATE).quantize(_CENT, rounding=ROUND_HALF_UP)
