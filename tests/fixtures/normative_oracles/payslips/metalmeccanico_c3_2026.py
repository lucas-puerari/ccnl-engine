"""Metalmeccanico C3 pay of 2026 from the published table and the INPS rates.

Written from the sources, deliberately without importing anything from
``ccnl_engine``.

- Minimo tabellare of level C3, CCNL Metalmeccanici Federmeccanica-Assistal,
  read on https://www.contratticcnl.it/metalmeccanici/tabelle-retributive/
  on 3 October 2026: 2,211.43 EUR from June 2026.  This aggregator is the
  bundle's own source; the figure is not cross-checked against the signed
  agreement.  A worker of level C3 with no allowance, no seniority and no event
  is paid exactly the minimo for a full month.
- Employee INPS rates of an industrial employer with 50 employees: IVS
  9.19% and CIGS 0.30%, 9.49% in all, on the whole gross below the IVS
  massimale (122,295 EUR for 2026, INPS news of February 2026).  The rates
  are not linked to a circolare; the test using them guards the resulting
  annual income instead of trusting it.  The base is the gross to the whole
  euro, "da 50 centesimi in poi si arrotonda all'unità di Euro superiore"
  (INPS circ. 208/2001), and each share is rounded to the cent on its own.

Worked example, the tredicesima of December 2026 (one minimo of the month):

    gross       2,211.43
    INPS base   2,211
    IVS         2,211 x 9.19% = 203.1909 -> 203.19
    CIGS        2,211 x 0.30% = 6.633    ->   6.63
    taxable     2,211.43 - 209.82 = 2,001.61
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

__all__ = ["C3_MINIMUM_FROM_JUNE_2026", "employee_taxable"]

C3_MINIMUM_FROM_JUNE_2026 = Decimal("2211.43")

_CENT = Decimal("0.01")
_EMPLOYEE_SHARES = (Decimal("0.0919"), Decimal("0.0030"))


def employee_taxable(gross: Decimal) -> Decimal:
    """Return the IRPEF taxable of a run: gross less employee INPS.

    Valid only for a gross below the IVS massimale and with no pension fund.

    Returns:
        ``gross`` less the IVS and CIGS shares of its whole-euro base.
    """
    base = gross.quantize(Decimal(1), rounding=ROUND_HALF_UP)
    inps = sum(
        (
            (base * share).quantize(_CENT, rounding=ROUND_HALF_UP)
            for share in _EMPLOYEE_SHARES
        ),
        Decimal(0),
    )
    return gross - inps
