"""Regional and municipal surtax withheld on one run."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.withholding._plan import slot_share
from ccnl_engine.payroll.service.fiscal_surtax import SurtaxOutcome, compute_surtax

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.amounts._types import _AmountsInput


def run_surtax(
    inp: _AmountsInput, taxable: Decimal, irpef_due: Decimal
) -> tuple[SurtaxOutcome, Decimal]:
    """Return the annual surtax and the part withheld on the run.

    D.Lgs. 446/1997 art. 50 c. 2 and D.Lgs. 360/1998 art. 1 c. 4: the
    surtax is due only when the IRPEF net of its deductions is due.

    Returns:
        ``(surtax, period_surtax)``: the annual outcome, empty without surtax
        rules, and its slot share plus the surtax carried from earlier runs.
    """
    surtax = (
        compute_surtax(
            taxable,
            inp.surtax_rules,
            regione=inp.regione,
            comune_belfiore=inp.comune_belfiore,
            irpef_due=irpef_due,
        )
        if inp.surtax_rules is not None
        else SurtaxOutcome()
    )
    period_surtax = (
        slot_share(surtax.total, inp.withholding_schedule)
        + inp.opening.shortfall.surtax
    )
    return surtax, period_surtax
