"""The ferie days of the rota of a security guard.

A CCNL may set the ferie of a year by the rota the guard works (FEDERDAT
art. 89: 25 days on 5+1, 23 on 6+1+1, 22 on 5+2): :func:`with_rota` swaps
the days of the rota stated into the leave rules of the run.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.employment.rota.inputs import Rota

__all__ = ["with_rota"]


def with_rota(ccnl: CCNL, rota: Rota | None) -> CCNL:
    """Return ``ccnl`` with the ferie days of ``rota``.

    Args:
        ccnl: The CCNL of the run.
        rota: ``Employment.rota``; ``None`` when not stated.

    Returns:
        ``ccnl`` whose ``default_annual_days`` are those the CCNL sets for
        ``rota``; ``ccnl`` unchanged without a stated rota or days for it.
    """
    rules = ccnl.work_rules
    leave = None if rules is None else rules.leave_rules
    if rules is None or leave is None or rota is None:
        return ccnl
    days = next((r for r in leave.rota_annual_days if r.rota is rota), None)
    if days is None:
        return ccnl
    leave = leave.model_copy(
        update={"default_annual_days": days.annual_days, "provenance": days.provenance}
    )
    return ccnl.model_copy(
        update={"work_rules": rules.model_copy(update={"leave_rules": leave})}
    )
