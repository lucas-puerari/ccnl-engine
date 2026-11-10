"""The span of an employment and how it ends."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date

from ccnl_engine.employment.period.causes import (
    _CASE_CAUSE,
    _JUST_CAUSE,
    NaspiCase,
    TerminationCause,
)
from ccnl_engine.employment.period.collective import CollectiveDismissal
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import parse_enum, require_bool, require_date

__all__ = ["CollectiveDismissal", "EmploymentPeriod", "NaspiCase", "TerminationCause"]

FEATURE = "employment_facts"


@dataclass(frozen=True, slots=True)
class EmploymentPeriod:
    """Start and optional end of the employment relationship.

    Attributes:
        started_on: First day of employment.
        uninterrupted_service_started_on: First day of the current uninterrupted
            actual service counted for service-gated awards. State the date from
            employer records when it differs from the hire date (for example,
            after a break or on a group transfer). It must exclude conventional
            seniority that is not actual service. ``None`` uses ``started_on``.
        ended_on: Last day of employment, or ``None`` for an open-ended
            relationship.  Must not precede ``started_on``.
        ended_by: How the employment ends, with ``ended_on``; ``None`` when
            not stated (a run that needs it reports the missing fact).
        just_cause: Whether a dismissal or a resignation has a just cause
            (art. 2119 c.c.); ``None`` when not stated or not either.
        disciplinary_dismissal: Whether a dismissal is for disciplinary reasons;
            distinct from just cause. ``None`` when not stated.
        naspi_case: The case of the end that changes the NASpI contribution,
            a collective dismissal or ``NaspiCase.ORDINARY``; ``None`` when
            not stated (the contribution carries a limitation).
        probation_until: Last day of the periodo di prova, read by a fund
            that leaves out the workers on probation (FASDA, Igiene
            ambientale art. 65 lett. B); ``None`` when there is none or it
            is not stated.

    Raises:
        InvalidInputError: When a date is not a ``date``, ``ended_on`` or
            ``probation_until`` is before ``started_on``, the service start
            is after ``ended_on``, ``ended_by``
            comes without ``ended_on``,
            ``just_cause`` with a cause other than a dismissal or a
            resignation, ``disciplinary_dismissal`` without a dismissal,
            or ``naspi_case`` without its own cause.
    """

    started_on: date
    ended_on: date | None = None
    ended_by: TerminationCause | None = None
    just_cause: bool | None = None
    naspi_case: NaspiCase | CollectiveDismissal | None = None
    probation_until: date | None = None
    uninterrupted_service_started_on: date | None = None
    disciplinary_dismissal: bool | None = None

    def __post_init__(self) -> None:  # noqa: D105
        require_date(self.started_on, "EmploymentPeriod.started_on", feature=FEATURE)
        require_date(
            self.uninterrupted_service_started_on,
            "EmploymentPeriod.uninterrupted_service_started_on",
            feature=FEATURE,
            optional=True,
        )
        require_date(
            self.probation_until,
            "EmploymentPeriod.probation_until",
            feature=FEATURE,
            optional=True,
        )
        if self.probation_until is not None and self.probation_until < self.started_on:
            msg = (
                f"probation_until ({self.probation_until}) must not precede "
                f"started_on ({self.started_on})"
            )
            raise InvalidInputError(
                msg,
                field="EmploymentPeriod.probation_until",
                feature=FEATURE,
            )
        require_date(
            self.ended_on, "EmploymentPeriod.ended_on", feature=FEATURE, optional=True
        )
        if self.ended_on is not None and self.ended_on < self.started_on:
            msg = (
                f"ended_on ({self.ended_on}) must not precede "
                f"started_on ({self.started_on})"
            )
            raise InvalidInputError(
                msg, field="EmploymentPeriod.ended_on", feature=FEATURE
            )
        if (
            self.ended_on is not None
            and self.uninterrupted_service_started_on is not None
            and self.uninterrupted_service_started_on > self.ended_on
        ):
            msg = "uninterrupted service cannot start after employment ends"
            raise InvalidInputError(
                msg,
                field="EmploymentPeriod.uninterrupted_service_started_on",
                feature=FEATURE,
            )
        if self.ended_by is not None:
            object.__setattr__(self, "ended_by", self._cause())
        self._check_just_cause()
        if self.disciplinary_dismissal is not None:
            path = "EmploymentPeriod.disciplinary_dismissal"
            require_bool(self.disciplinary_dismissal, path, feature=FEATURE)
            if self.ended_by is not TerminationCause.DISMISSAL:
                msg = f"{path} applies only to a dismissal"
                raise InvalidInputError(msg, field=path, feature=FEATURE)
        if self.naspi_case is not None:
            object.__setattr__(self, "naspi_case", self._naspi_case())

    def _naspi_case(self) -> NaspiCase | CollectiveDismissal:
        path = "EmploymentPeriod.naspi_case"
        case = self.naspi_case
        if isinstance(case, CollectiveDismissal):
            cause: TerminationCause | None = TerminationCause.DISMISSAL
        else:
            case = parse_enum(case, NaspiCase, path, feature=FEATURE)
            cause = _CASE_CAUSE.get(case)
        if self.ended_by is None or cause not in {None, self.ended_by}:
            msg = f"{path} {case!r} does not fit the end {self.ended_by!r}"
            raise InvalidInputError(msg, field=path, feature=FEATURE)
        return case

    def _cause(self) -> TerminationCause:
        cause = parse_enum(
            self.ended_by,
            TerminationCause,
            "EmploymentPeriod.ended_by",
            feature=FEATURE,
        )
        if self.ended_on is None:
            msg = "EmploymentPeriod.ended_by needs ended_on"
            raise InvalidInputError(
                msg, field="EmploymentPeriod.ended_by", feature=FEATURE
            )
        return cause

    def _check_just_cause(self) -> None:
        if self.just_cause is None:
            return
        require_bool(self.just_cause, "EmploymentPeriod.just_cause", feature=FEATURE)
        if self.ended_by not in _JUST_CAUSE:
            msg = "EmploymentPeriod.just_cause applies to a dismissal or a resignation"
            raise InvalidInputError(
                msg, field="EmploymentPeriod.just_cause", feature=FEATURE
            )

    @classmethod
    def from_dates(
        cls, started_on: date | None, ended_on: date | None
    ) -> EmploymentPeriod | None:
        """Build a period from optional dates, as supplied by callers.

        Returns:
            ``None`` when neither date is given, otherwise the validated period.

        Raises:
            InvalidInputError: When only ``ended_on`` is given, or when
                ``ended_on`` precedes ``started_on``.
        """
        if started_on is None:
            if ended_on is not None:
                msg = f"ended_on ({ended_on}) requires started_on"
                raise InvalidInputError(msg, feature=FEATURE)
            return None
        return cls(started_on=started_on, ended_on=ended_on)

    def overlaps_month(self, year: int, month: int) -> bool:
        """Return whether the employment covers at least one day of a month.

        Args:
            year: Calendar year of the month.
            month: Calendar month, 1-12.

        Returns:
            ``True`` when the month has at least one employed day.
        """
        first, last = _month_bounds(year, month)
        return self.started_on <= last and (
            self.ended_on is None or self.ended_on >= first
        )

    def covers_month(self, year: int, month: int) -> bool:
        """Return whether the employment covers every day of a month.

        Args:
            year: Calendar year of the month.
            month: Calendar month, 1-12.

        Returns:
            ``True`` when the employment starts on or before the first day
            and does not end before the last day of the month.
        """
        first, last = _month_bounds(year, month)
        return self.started_on <= first and (
            self.ended_on is None or self.ended_on >= last
        )

    def span_in_month(self, year: int, month: int) -> tuple[date, date] | None:
        """Return the first and last employed day of a calendar month.

        Args:
            year: Calendar year of the month.
            month: Calendar month, 1-12.

        Returns:
            ``(first, last)`` employed days of the month, inclusive; ``None``
            when the employment has no day in it.
        """
        first, last = _month_bounds(year, month)
        first = max(first, self.started_on)
        if self.ended_on is not None:
            last = min(last, self.ended_on)
        return None if last < first else (first, last)

    def clip_start(self, day: date) -> date:
        """Return ``day``, or the hire date when ``day`` precedes it.

        Args:
            day: A date, typically the first day of an accrual window.

        Returns:
            ``max(day, started_on)``.
        """
        return max(day, self.started_on)


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    """Return the first and last day of a calendar month.

    Returns:
        ``(first, last)`` dates of ``month`` in ``year``.
    """
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])
    return first, last
