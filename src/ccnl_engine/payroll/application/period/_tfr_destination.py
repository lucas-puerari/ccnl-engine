"""Whether the TFR of a run goes to the Fondo Tesoreria INPS.

L. 296/2006 art. 1 c. 756 has employers of the private sector with at
least 50 employees pay the TFR not destined to a complementary pension
fund to the Fondo of c. 755, managed by INPS.  The size is not the
headcount of the run: it is the yearly average of 2006, or of the year the
activity started (DM 30 gennaio 2007 art. 1 c. 6), and from 2026 of the year
before for an employer that reaches it later, with at least 60 employees in
2026 and 2027 (c. 756 as in force from 12 August 2026).  Some workers are
excluded (art. 1 c. 8).  The request states the outcome as
``Employment.tfr_treasury_fund``; the engine only rules out the sectors the
Fondo never covers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext

__all__ = ["tfr_treasury_fund"]

#: Sectors outside the Fondo Tesoreria: domestic employers (DM 30 gennaio
#: 2007 art. 1 c. 5) and the public administrations of D.Lgs. 165/2001 art.
#: 1 c. 2 (INPS circ. 70/2007, par. 2 lett. a).
_EXCLUDED = frozenset({TaxSector.LAVORO_DOMESTICO, TaxSector.PUBBLICA_AMMINISTRAZIONE})


def tfr_treasury_fund(ctx: RunContext) -> bool | None:
    """Return whether the TFR not paid to a pension fund goes to the Fondo.

    Returns:
        ``False`` in a sector the Fondo excludes; otherwise the stated
        ``Employment.tfr_treasury_fund``, ``None`` when not stated.

    Raises:
        InvalidInputError: When the request routes to the Fondo the TFR of
            a sector it excludes.
    """
    stated = ctx.request.tfr_treasury_fund
    sector = ctx.contract.ccnl.meta.tax_sector
    if sector not in _EXCLUDED:
        return stated
    if stated:
        msg = (
            f"Employment.tfr_treasury_fund is True, but the Fondo Tesoreria "
            f"(L. 296/2006 art. 1 c. 756) does not cover the {sector.value} "
            "sector: domestic employers and public administrations are excluded"
        )
        raise InvalidInputError(
            msg, field="Employment.tfr_treasury_fund", feature="tfr"
        )
    return False
