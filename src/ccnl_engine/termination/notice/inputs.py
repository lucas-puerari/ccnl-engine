"""The notice not given at the end of an open-ended employment.

Pass the event to the run that pays the month of the last day of the
employment (``Employment.employment_period.ended_on``).  How the employment
ends is a fact of the employment (``EmploymentPeriod.ended_by`` and
``just_cause``): the employer owes the indemnity in place of the notice not
worked on a dismissal without just cause and on a death (art. 2118 c.c.),
on a resignation for just cause (art. 2119 c. 1).  A dismissal for just
cause and a mutual agreement owe none: the run records a nil decision.  No
notice is owed during a trial period (art. 2096 c.c.), which the facts do
not state: do not pass the event then.  A resignation without just cause
makes the worker owe the indemnity, which the engine does not compute (an
``incomplete`` issue).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.validators import require_date

if TYPE_CHECKING:
    from datetime import date

__all__ = ["NoticeIndemnityEvent", "employer_owes"]

_NOTICE = "termination_notice"


@dataclass(frozen=True, slots=True)
class NoticeIndemnityEvent:
    """The act that ends the employment, for the notice it opens.

    Attributes:
        received_on: Day the act of dismissal or resignation was received,
            or the day of death; the notice runs from the day after.

    Raises:
        InvalidInputError: When ``received_on`` is not a date.
    """

    received_on: date

    def __post_init__(self) -> None:  # noqa: D105
        require_date(
            self.received_on, "NoticeIndemnityEvent.received_on", feature=_NOTICE
        )

    @property
    def event_date(self) -> date:
        """Day the act was received."""
        return self.received_on


def employer_owes(cause: TerminationCause, just_cause: bool | None) -> bool:
    """Return whether the employer owes the indemnity of the notice not given.

    Returns:
        ``True`` on a dismissal without just cause, a resignation for just
        cause (art. 2119 c. 1 c.c.) or a death (art. 2118 c. 3).
    """
    if cause is TerminationCause.DISMISSAL:
        return just_cause is False
    if cause is TerminationCause.RESIGNATION:
        return just_cause is True
    return cause is TerminationCause.DEATH
