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
  annual income instead of trusting it.

Worked example, the tredicesima of December 2026 (one minimo of the month):

    gross       2,211.43
    INPS        2,211.43 x 9.49% = 209.8647 -> 209.86
    taxable     2,211.43 - 209.86 = 2,001.57
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

__all__ = ["C3_MINIMUM_FROM_JUNE_2026", "employee_taxable"]

C3_MINIMUM_FROM_JUNE_2026 = Decimal("2211.43")

_CENT = Decimal("0.01")
_EMPLOYEE_INPS_RATE = Decimal("0.0919") + Decimal("0.0030")


def employee_taxable(gross: Decimal) -> Decimal:
    """Return the IRPEF taxable of a run: gross less employee INPS.

    Valid only for a gross below the IVS massimale and with no pension fund.

    Returns:
        ``gross`` less 9.49% of it rounded to the cent.
    """
    inps = (gross * _EMPLOYEE_INPS_RATE).quantize(_CENT, rounding=ROUND_HALF_UP)
    return gross - inps
