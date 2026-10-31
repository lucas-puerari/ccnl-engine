"""The notice not given at the end of an open-ended employment.

Pass the event to the run that pays the month of the last day of the
employment (``Employment.employment_period.ended_on``).  The employer owes
the indemnity in place of the notice not worked: on a dismissal without
just cause and on a death (art. 2118 c.c.), on a resignation for just
cause (art. 2119 c. 1).  No notice is owed on a dismissal for just cause or
a mutual agreement, nor during a trial period (art. 2096): do not pass the
event then.  A resignation without just cause makes the worker owe the
indemnity, which the engine does not compute.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ccnl_engine.termination.notice.models import TerminationCause
from ccnl_engine.validators import parse_enum, require_bool, require_date

__all__ = ["NoticeIndemnityEvent"]

_NOTICE = "termination_notice"


@dataclass(frozen=True, slots=True)
class NoticeIndemnityEvent:
    """The act that ends the employment and whether it has a just cause.

    Attributes:
        received_on: Day the act of dismissal or resignation was received,
            or the day of death; the notice runs from the day after.
        cause: How the employment ends.
        just_cause: Whether the act has a just cause (art. 2119 c.c.).  No
            default: a dismissal taken for one without just cause would pay
            an indemnity the employer does not owe, and the other way round.

    Raises:
        InvalidInputError: When a field is of the wrong type.
    """

    received_on: date
    cause: TerminationCause
    just_cause: bool

    def __post_init__(self) -> None:  # noqa: D105
        require_date(
            self.received_on, "NoticeIndemnityEvent.received_on", feature=_NOTICE
        )
        object.__setattr__(
            self,
            "cause",
            parse_enum(
                self.cause,
                TerminationCause,
                "NoticeIndemnityEvent.cause",
                feature=_NOTICE,
            ),
        )
        require_bool(
            self.just_cause, "NoticeIndemnityEvent.just_cause", feature=_NOTICE
        )

    @property
    def event_date(self) -> date:
        """Day the act was received."""
        return self.received_on

    @property
    def employer_owes(self) -> bool:
        """Whether the employer owes the indemnity for the notice not given."""
        cause = self.cause
        if cause is TerminationCause.DISMISSAL:
            return not self.just_cause
        if cause is TerminationCause.RESIGNATION:
            return self.just_cause
        return cause is TerminationCause.DEATH
