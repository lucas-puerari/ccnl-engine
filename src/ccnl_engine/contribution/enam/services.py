"""Contribution of a teacher to the Gestione Assistenza Magistrale (ex ENAM).

L. 93/1957 art. 3 c. 1 lett. a: the permanent teachers of the scuola
dell'infanzia and primaria pay 1% of 80% of the stipendio.  The stipendio
the ENAM counts excludes the IIS conglobata, which the retribuzione
tabellare of the CCNL holds since 1 January 2003: the CCNL states it for
each ENAM level (``CCNLParameters.enam_iis_monthly``) and it is taken out
of the minimum, in the same proportion as the minimum of the run.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.employment.inputs import Permanent

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

__all__ = ["enam_stipendio"]


def enam_stipendio(ctx: RunContext) -> Decimal | None:
    """Return the stipendio of a teacher who owes the ENAM.

    Returns:
        The minimum of the pay chain of a permanent worker on a level of
        ``CCNLParameters.enam_levels`` in a year with ENAM rates; ``None``
        otherwise.
    """
    contract = ctx.contract
    inps = contract.year_rules.inps
    owes = (
        inps is not None
        and inps.public_enam is not None
        and contract.level.code in contract.ccnl.parameters.enam_levels
        and isinstance(ctx.request.contract_type, Permanent)
    )
    if not owes:
        return None
    base = ctx.chain.base
    iis = contract.ccnl.parameters.enam_iis_monthly[contract.level.code]
    day = contract.tctx.competence
    full = contract.level.base_salary.value_at(day)
    excluded = iis.value_at(day) * (base / full if full else Decimal(0))
    return max(base - excluded, Decimal(0))
