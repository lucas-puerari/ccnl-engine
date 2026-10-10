"""RunKind: the kind of a payroll run and the checks shared by run identities."""

from __future__ import annotations

from enum import StrEnum

from ccnl_engine.validation import parse_enum, require_int

__all__ = ["RunKind", "check_year_month", "run_kind"]

_MIN_YEAR = 1970
#: The last year whose next year is still a calendar date (``date`` ends in 9999).
_MAX_YEAR = 9998
_FEATURE = "payroll_run"


class RunKind(StrEnum):
    """Classification of a payroll run.

    Members compare equal to their string values, so ``RunKind.REGULAR == "regular"``
    is ``True`` and existing comparisons with plain strings continue to work.
    """

    REGULAR = "regular"
    THIRTEENTH = "thirteenth"
    FOURTEENTH = "fourteenth"
    ADJUSTMENT = "adjustment"
    TERMINATION = "termination"

    @property
    def consumes_withholding_slot(self) -> bool:
        """Whether a run of this kind takes one IRPEF withholding slot.

        Every payslip does, except an adjustment run, which corrects a run
        already closed without opening a new withholding instalment.
        """
        return self is not RunKind.ADJUSTMENT

    @property
    def rank_in_month(self) -> int:
        """Position of a run of this kind among the runs of its month.

        The regular payslip comes first, the extra months follow it
        (:meth:`~ccnl_engine.payroll.year.models_schedule.PayrollSchedule\
.from_calendar`), a termination run closes the month.  An adjustment run
        corrects a run already closed and is not ordered.
        """
        return _RANK_IN_MONTH[self]

    @property
    def repeats_in_month(self) -> bool:
        """Whether a month can hold several runs of this kind.

        Only an adjustment run can: each corrects a run already closed, so
        a second correction of the same month is a new run with the next
        sequence number.  Every other kind closes once.
        """
        return self is RunKind.ADJUSTMENT


_RANK_IN_MONTH: dict[RunKind, int] = {
    RunKind.REGULAR: 0,
    RunKind.THIRTEENTH: 1,
    RunKind.FOURTEENTH: 1,
    RunKind.TERMINATION: 2,
    RunKind.ADJUSTMENT: 3,
}


def check_year_month(owner: str, year: object, month: object) -> None:
    """Reject a month outside 1-12 or a year outside 1970-9998."""
    require_int(month, f"{owner}.month", feature=_FEATURE, minimum=1, maximum=12)
    require_int(
        year, f"{owner}.year", feature=_FEATURE, minimum=_MIN_YEAR, maximum=_MAX_YEAR
    )


def run_kind(value: object, path: str) -> RunKind:
    """Return ``value`` as a :class:`RunKind`.

    Returns:
        The run kind named by ``value``.
    """
    return parse_enum(value, RunKind, path, feature=_FEATURE)
