"""The hourly divisor of the normal week of the employment.

A CCNL may set one divisor for each normal week of its staff (Commercio and
Terziario Confesercenti art. 211, DMO art. 194: "168, per il personale la
cui durata normale di lavoro è di 40 ore settimanali; 182, [...] di 42 ore;
195, [...] di 45 ore").  The hourly quota of the retribuzione, "sia normale
che di fatto", is then the monthly pay over the divisor of the worker's
normal week: :func:`with_week_divisor` swaps it into the CCNL of the run,
so the overtime, the supplements, the permits and the absences read the
same divisor.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.employment.fact.inputs import WeeklyHours

__all__ = ["with_week_divisor"]


def with_week_divisor(ccnl: CCNL, full_time: WeeklyHours | None) -> CCNL:
    """Return ``ccnl`` with the hourly divisor of the full-time week stated.

    Args:
        ccnl: The CCNL of the run.
        full_time: ``Employment.full_time_weekly_hours``, the normal week of
            the employment; ``None`` when not stated.

    Returns:
        ``ccnl`` whose ``parameters.hourly_divisor`` is, in every period
        with a divisor, the one the CCNL sets for that week, and whose
        ``hourly_divisor_weekly_hours`` is that week; ``ccnl`` unchanged
        without a stated week or a divisor of the CCNL for it.
    """
    rules = ccnl.work_rules
    supplements = None if rules is None else rules.time_supplements
    if rules is None or supplements is None or full_time is None:
        return ccnl
    week = next(
        (
            w
            for w in supplements.week_divisors
            if Decimal(w.weekly_hours) == full_time.value
        ),
        None,
    )
    if week is None:
        return ccnl
    params = ccnl.parameters
    periods = tuple(
        p
        if p.value is None
        else p.model_copy(update={"value": week.divisor, "provenance": week.provenance})
        for p in params.hourly_divisor.periods
    )
    divisor = params.hourly_divisor.model_copy(update={"periods": periods})
    supplements = supplements.model_copy(
        update={"hourly_divisor_weekly_hours": week.weekly_hours}
    )
    return ccnl.model_copy(
        update={
            "parameters": params.model_copy(update={"hourly_divisor": divisor}),
            "work_rules": rules.model_copy(update={"time_supplements": supplements}),
        }
    )
