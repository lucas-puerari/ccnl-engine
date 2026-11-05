"""The hourly divisor of the normal week of the employment.

A CCNL may set one divisor for each normal week of its staff (Commercio and
Terziario Confesercenti art. 211, DMO art. 194: "168, per il personale la
cui durata normale di lavoro è di 40 ore settimanali; 182, [...] di 42 ore;
195, [...] di 45 ore").  The hourly quota of the retribuzione, "sia normale
che di fatto", is then the monthly pay over the divisor of the worker's
normal week: :func:`with_week_divisor` swaps it into the CCNL of the run,
so the overtime, the supplements, the permits and the absences read the
same divisor.

A CCNL may also set the daily divisor by the working days of the full-time
week (Pulizia artigianato art. 34: 22 "nel caso di settimana corta", 26
"su sei giorni"): :func:`with_week_days` swaps the absence method, the
divisor of the holiday clause and the ferie days of a year (Studi art. 99:
22 or 26) for the days stated, so the absences, the proration, a change of
level, the sick days, the holidays and the leave accrual read the same.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

from ccnl_engine.leave.permit.models import PermitHours

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL, CCNLWorkRules
    from ccnl_engine.employment.fact.inputs import WeeklyHours
    from ccnl_engine.leave.models import LeaveRules, WeekDaysLeave

__all__ = ["with_week_days", "with_week_divisor"]


class _OfDays(Protocol):
    """A rule of the CCNL for a full-time week of ``days`` working days."""

    @property
    def days(self) -> int: ...


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


def with_week_days(ccnl: CCNL, days: int | None) -> CCNL:
    """Return ``ccnl`` with the daily divisors of a full-time week of ``days``.

    Args:
        ccnl: The CCNL of the run.
        days: ``Employment.full_time_week_days``; ``None`` when not stated.

    Returns:
        ``ccnl`` whose absence method (with its provenance), holiday
        clause divisor and ferie days are the ones the CCNL sets for
        ``days``; ``ccnl``
        unchanged without a stated week or a divisor of the CCNL for it.
    """
    rules = ccnl.work_rules
    if rules is None or days is None:
        return ccnl
    update = _week_days_update(rules, days)
    if not update:
        return ccnl
    return ccnl.model_copy(update={"work_rules": rules.model_copy(update=update)})


def _week_days_update(rules: CCNLWorkRules, days: int) -> dict[str, object]:
    """Return the work rules ``days`` replaces, by field name.

    Returns:
        The absence rules, holiday clause and leave rules with the values
        the CCNL sets for ``days``; only those it sets.
    """
    update: dict[str, object] = {}
    absence = rules.absence_rules
    if (
        absence is not None
        and (method := _of_days(absence.week_days_methods, days)) is not None
    ):
        update["absence_rules"] = absence.model_copy(
            update={
                "daily_divisor_method": method.method,
                "provenance": method.provenance,
            }
        )
    clause = rules.sunday_holidays
    if (
        clause is not None
        and (divisor := _of_days(clause.week_days_divisors, days)) is not None
    ):
        update["sunday_holidays"] = clause.model_copy(
            update={"divisor": divisor.divisor}
        )
    leave = rules.leave_rules
    if (
        leave is not None
        and (ferie := _of_days(leave.week_days_annual_days, days)) is not None
    ):
        update["leave_rules"] = _leave_of_days(leave, ferie)
    return update


def _leave_of_days(leave: LeaveRules, ferie: WeekDaysLeave) -> LeaveRules:
    """Return ``leave`` with the ferie days, divisor and permits of ``ferie``.

    Returns:
        ``leave`` whose ``default_annual_days`` are those of the week, whose
        termination divisor is the week's when ``ferie`` sets one, and whose
        permit buckets named by ``ferie`` take the hours of the week.
    """
    termination = leave.termination
    if termination is not None and ferie.ferie_divisor is not None:
        termination = termination.model_copy(
            update={"ferie_divisor": ferie.ferie_divisor}
        )
    hours = {p.bucket: p for p in ferie.permit_hours}
    permits = tuple(
        permit
        if permit.bucket not in hours
        else permit.model_copy(
            update={
                "annual_hours": (PermitHours(hours=hours[permit.bucket].hours),),
                "provenance": hours[permit.bucket].provenance,
            }
        )
        for permit in leave.permits
    )
    return leave.model_copy(
        update={
            "default_annual_days": ferie.annual_days,
            "termination": termination,
            "permits": permits,
        }
    )


def _of_days[T: _OfDays](items: tuple[T, ...], days: int) -> T | None:
    """Return the item of ``items`` for a week of ``days``.

    Returns:
        The first item whose ``days`` is ``days``, ``None`` if none.
    """
    return next((item for item in items if item.days == days), None)
