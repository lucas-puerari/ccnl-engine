"""Recognised seniority of the worker, a fact as of a date."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from ccnl_engine.payroll.domain.employment_facts import FEATURE, require_int
from ccnl_engine.shared.domain.errors import InvalidInputError

__all__ = ["SeniorityFact", "SenioritySource"]

_REMEDIATION = "Compute only runs from the start of the recognised service."


class SenioritySource(StrEnum):
    """Where the caller read the recognised seniority from.

    Attributes:
        EMPLOYER_RECORDS: The personnel file or the libro unico del lavoro.
        PAYSLIP: A previous payslip of the same employment.
        EMPLOYMENT_CONTRACT: The letter of hire, for a seniority recognised
            on hiring (anzianita convenzionale).
    """

    EMPLOYER_RECORDS = "employer_records"
    PAYSLIP = "payslip"
    EMPLOYMENT_CONTRACT = "employment_contract"


@dataclass(frozen=True, slots=True)
class SeniorityFact:
    """Recognised seniority of the worker, for seniority increments.

    The seniority is a fact as of a date: the engine ages it to each run.
    The increments and the service-gated allowances of a run use the
    months of service completed by the first day of its competence month,
    so an increment matured during a month is paid from the next one, and
    service starting within the month counts zero months (see
    :meth:`months_in_month`).  A month is complete on the same day of the
    following month.

    Use :meth:`since` when the caller knows the date the recognised
    seniority starts from instead of a count of months.

    Attributes:
        months: Completed months of recognised service on ``as_of``,
            ``>= 0``.
        as_of: Date the months are counted at.
        source: Where the seniority was read from; a string value of
            :class:`SenioritySource` is accepted and normalized.

    Raises:
        InvalidInputError: When ``months`` is not a non-negative int,
            ``as_of`` is not a date or ``source`` names no source.
    """

    months: int
    as_of: date
    source: SenioritySource

    def __post_init__(self) -> None:  # noqa: D105
        require_int(self.months, "seniority.months")
        if self.months < 0:
            msg = f"seniority.months must be >= 0; got {self.months}"
            raise InvalidInputError(msg, feature=FEATURE)
        if isinstance(self.as_of, datetime) or not isinstance(self.as_of, date):
            msg = f"seniority.as_of must be a date; got {self.as_of!r}"
            raise InvalidInputError(msg, feature=FEATURE)
        object.__setattr__(self, "source", _seniority_source(self.source))

    @classmethod
    def since(cls, recognised_from: date, source: SenioritySource) -> SeniorityFact:
        """Return the seniority that starts on ``recognised_from``.

        Args:
            recognised_from: First day of recognised service, which may
                precede the hire date when the employer recognises earlier
                service.
            source: Where the date was read from.

        Returns:
            Zero months as of ``recognised_from``.
        """
        return cls(months=0, as_of=recognised_from, source=source)

    def months_at(self, day: date) -> int:
        """Return the completed months of recognised service on ``day``.

        Args:
            day: The date to age the seniority to; it may precede
                ``as_of``.

        Returns:
            ``months`` plus the whole months from ``as_of`` to ``day``,
            minus them when ``day`` precedes ``as_of``.

        Raises:
            InvalidInputError: When ``day`` precedes the start of the
                recognised service.
        """
        months = self._aged(day)
        if months < 0:
            raise InvalidInputError(
                self._before_service(day), feature=FEATURE, remediation=_REMEDIATION
            )
        return months

    def months_in_month(self, year: int, month: int) -> int:
        """Return the months of service a run of a month counts.

        A run counts the months completed by the first day of its month.
        Service that starts within the month counts zero months: the hire
        month of a worker whose seniority is recognised from the hire date.

        Args:
            year: Year of the competence month.
            month: Competence month, 1-12.

        Returns:
            The completed months on the first day of the month, at least 0.

        Raises:
            InvalidInputError: When the recognised service starts after the
                last day of the month.
        """
        last = date(year, month, calendar.monthrange(year, month)[1])
        if self._aged(last) < 0:
            raise InvalidInputError(
                self._before_service(last), feature=FEATURE, remediation=_REMEDIATION
            )
        return max(0, self._aged(date(year, month, 1)))

    def _aged(self, day: date) -> int:
        elapsed = (day.year - self.as_of.year) * 12 + day.month - self.as_of.month
        if day.day < self.as_of.day:
            elapsed -= 1
        return self.months + elapsed

    def _before_service(self, day: date) -> str:
        return f"seniority of {self.months} months on {self.as_of} starts after {day}"


def _seniority_source(value: object) -> SenioritySource:
    """Return ``value`` as a :class:`SenioritySource`.

    Returns:
        The source named by ``value``.

    Raises:
        InvalidInputError: When ``value`` names no source.
    """
    try:
        return SenioritySource(str(value))
    except ValueError:
        valid = [s.value for s in SenioritySource]
        msg = f"seniority.source must be one of {valid}; got {value!r}"
        raise InvalidInputError(msg, feature=FEATURE) from None
