"""Contribution of a teacher to the Gestione Assistenza Magistrale (ex ENAM).

L. 93/1957 art. 3 c. 1 lett. a: the permanent teachers of the scuola
dell'infanzia and primaria pay 1% of 80% of the stipendio.  The stipendio
the ENAM counts excludes the IIS conglobata, which the retribuzione
tabellare of the CCNL holds; the bundle does not give it apart, so a run
that owes the ENAM traverses the open limitation ``enam_base`` the CCNL
declares, and the contribution is computed on the whole minimum.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.employment.inputs import Permanent

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.period.services_run_context import RunContext

__all__ = ["ENAM_BASE_VARIANT", "enam_paths", "enam_stipendio"]

#: Variant of the CCNL limitation of the ENAM base.
ENAM_BASE_VARIANT = "enam_base"


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
    return ctx.chain.base if owes else None


def enam_paths(ctx: RunContext) -> frozenset[str]:
    """Return the limitation path of a run that owes the ENAM.

    Returns:
        The ``enam_base`` path of the CCNL, empty when no ENAM is owed.
    """
    if enam_stipendio(ctx) is None:
        return frozenset()
    return frozenset({f"{ctx.contract.ccnl.meta.ccnl_id}/{ENAM_BASE_VARIANT}"})
