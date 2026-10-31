"""The notice period of a termination, from the act and the CCNL band."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.termination.notice.models import NoticeBand

__all__ = ["NoticePeriod", "notice_period"]

_DAY = timedelta(days=1)


def _add_months(day: date, months: int) -> date:
    year, month = divmod(day.month - 1 + months, 12)
    year, month = day.year + year, month + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


@dataclass(frozen=True)
class NoticePeriod:
    """The notice an act of termination opens.

    Attributes:
        first_day: First day of notice, the day after the act is received.
        last_day: Last day of notice.
        band: The CCNL band it comes from.
    """

    first_day: date
    last_day: date
    band: NoticeBand

    @property
    def days(self) -> int:
        """Calendar days of notice."""
        return (self.last_day - self.first_day).days + 1

    def unworked_days(self, ended_on: date) -> int:
        """Return the days of notice after the last day of employment.

        Returns:
            Zero when the employment lasts the whole notice.
        """
        start = max(ended_on + _DAY, self.first_day)
        return max((self.last_day - start).days + 1, 0)


def notice_period(band: NoticeBand, received_on: date) -> NoticePeriod:
    """Return the notice ``band`` opens on an act received on ``received_on``.

    The notice is a term of the obligation, computed as art. 1187 c.c.
    says, by art. 2963 c.c.: the day of receipt is not counted, a term of
    months ends on the day of the last month corresponding to the day of
    receipt, or on the last day of a month without it; the days of the band
    follow.  A notice of one month on an act of 28 February ends on 28
    March, one of 31 January on 28 February.  The extension of a term
    ending on a holiday (art. 2963 c. 3) concerns the act owed at the
    term, not the length of the notice, and is not applied.

    Returns:
        The first and last day of notice.
    """
    last = _add_months(received_on, band.months) + timedelta(days=band.days)
    return NoticePeriod(received_on + _DAY, last, band)
