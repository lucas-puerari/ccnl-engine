"""Buckets of paid leave and the unit each one is counted in."""

from __future__ import annotations

from enum import StrEnum

__all__ = ["HALF_MONTH_DAYS", "LeaveBucket", "MonthCredit"]


class LeaveBucket(StrEnum):
    """A bucket of paid leave a CCNL grants every year.

    Attributes:
        FERIE: Annual leave (ferie, art. 2109 c.c. and D.Lgs. 66/2003 art.
            10), counted in working days.
        ROL: Paid hours of the reduction of the working time (riduzione
            dell'orario di lavoro, permessi annui retribuiti), counted in
            hours.  A CCNL that pools the hours of the abolished festivities
            with them (the PAR of the metalmeccanici, the 104 hours of the
            Turismo) keeps the pool here.
        EX_FESTIVITA: Paid hours in place of the festivities abolished by
            L. 54/1977, counted in hours, when the CCNL keeps them apart
            from the ROL.
    """

    FERIE = "ferie"
    ROL = "rol"
    EX_FESTIVITA = "ex_festivita"

    @property
    def unit(self) -> str:
        """Unit the bucket is counted in: ``"days"`` or ``"hours"``."""
        return "days" if self is LeaveBucket.FERIE else "hours"


#: Days of a month above which a month fraction counts as a whole month.
HALF_MONTH_DAYS = 15


class MonthCredit(StrEnum):
    """Which months of service accrue a twelfth of the year.

    Attributes:
        WHOLE_MONTH: Only a month served every day ("per ogni mese intero
            di servizio prestato").
        MORE_THAN_HALF: A month served more than fifteen days counts as a
            whole month, a shorter one accrues nothing ("la frazione di mese
            superiore ai 15 giorni viene considerata come mese intero").
    """

    WHOLE_MONTH = "whole_month"
    MORE_THAN_HALF = "more_than_half"

    def credits(self, served_days: int, month_days: int) -> bool:
        """Return whether a month served ``served_days`` days accrues.

        Returns:
            ``True`` when the month accrues a twelfth of the year.
        """
        if self is MonthCredit.WHOLE_MONTH:
            return served_days >= month_days
        return served_days > HALF_MONTH_DAYS
