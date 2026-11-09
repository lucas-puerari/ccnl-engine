"""The national holidays a CCNL holiday target in a sickness covers."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus, IssueCause

if TYPE_CHECKING:
    from ccnl_engine.calendar.holiday.models import NationalHolidays
    from ccnl_engine.employer.inputs import EmployerProfile
    from ccnl_engine.sickness.holiday.models import SicknessHoliday
    from ccnl_engine.sickness.integration.models import SicknessRules

__all__ = [
    "covered_holidays",
    "covered_target_holidays",
    "gross_holiday_boundary",
    "legacy_section_issue",
]

_SUNDAY = 6


def gross_holiday_boundary(
    target: SicknessHoliday | None, holidays: frozenset[date], day: date, previous: date
) -> bool:
    """Keep gross-basis holiday pay separate from adjacent ordinary sick pay.

    Returns:
        Whether a segment must end at this day boundary.
    """
    return bool(
        target and target.gross_basis and (day in holidays or previous in holidays)
    )


def legacy_section_issue(
    target: SicknessHoliday | None,
    calendar: NationalHolidays,
    first: date,
    last: date,
    employer: EmployerProfile | None,
    capability: str,
) -> CalculationIssue | None:
    """Report an unknown legacy-section fact only when a covered holiday overlaps.

    Returns:
        A blocking missing-fact issue, or none if the fact is known or no
        eligible holiday falls during the absence.
    """
    if (
        target is None
        or not target.requires_legacy_section
        or (employer is not None and employer.legacy_section_applicable is not None)
    ):
        return None
    unrestricted = target.model_copy(update={"requires_legacy_section": False})
    days = covered_target_holidays(unrestricted, calendar, last.year, employer)
    if not any(first <= day <= last for day in days):
        return None
    return CalculationIssue(
        code="missing_fact",
        message="The employer's legacy CCNL section is unknown; its holiday top-up "
        "during sickness or injury is withheld.",
        status=CalculationStatus.INCOMPLETE,
        fact="legacy_section_applicable",
        capability=capability,
        cause=IssueCause.FACT,
    )


def covered_holidays(
    rules: SicknessRules,
    calendar: NationalHolidays,
    year: int,
    employer: EmployerProfile | None = None,
) -> frozenset[date]:
    """Return the holidays the target of ``rules`` applies on.

    The weekday holidays of ``year`` and of the two years before, the span
    an episode of the run can reach, but those the clause leaves out; a
    holiday on a Sunday is paid by its own quota (L. 260/1949 art. 5).

    Returns:
        Their dates; none without a holiday target.
    """
    return covered_target_holidays(rules.holiday, calendar, year, employer)


def _eligible_employer(
    target: SicknessHoliday, employer: EmployerProfile | None
) -> bool:
    """Whether the employer qualifies for a restricted holiday target.

    Returns:
        True for an unrestricted target or a confirmed eligible employer.
    """
    return not getattr(target, "requires_legacy_section", False) or (
        employer is not None and employer.legacy_section_applicable is True
    )


def covered_target_holidays(
    target: SicknessHoliday | None,
    calendar: NationalHolidays,
    year: int,
    employer: EmployerProfile | None = None,
) -> frozenset[date]:
    """Return the weekday national holidays eligible for this target.

    Returns:
        The covered dates, or none when no holiday clause is present.
    """
    if target is None or not _eligible_employer(target, employer):
        return frozenset()
    covered = calendar.model_copy(
        update={
            "holidays": tuple(
                h for h in calendar.holidays if h.day not in target.excluded_days
            )
        }
    )
    days = set().union(*(covered.in_year(y) for y in range(year - 2, year + 1)))
    patron = None if employer is None else employer.patron_saint_day
    if target.includes_patron_saint and patron is not None:
        month, day = (int(part) for part in patron.split("-"))
        for y in range(year - 2, year + 1):
            try:
                days.add(date(y, month, day))
            except ValueError:  # 29 February in a non-leap year
                continue
    return frozenset(day for day in days if day.weekday() != _SUNDAY)
