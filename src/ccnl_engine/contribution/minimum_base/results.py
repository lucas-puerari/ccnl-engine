"""Result of the minimum INPS base of a run: the reason and the base.

The rule is in :mod:`~ccnl_engine.contribution.minimum_base.models`, its
reading in :mod:`~ccnl_engine.contribution.minimum_base.rules`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.provenance.source.models import SourceLocation

__all__ = ["UNDETERMINED", "MinimumBase", "MinimumBaseReason"]


class MinimumBaseReason(StrEnum):
    """How the minimum entered the INPS base of a run.

    Attributes:
        ABOVE_MINIMUM: The base reaches the minimum: it is kept.
        RAISED_TO_MINIMUM: The base was raised to the minimum.
        APPRENTICE: Art. 7 c. 5 excludes apprentices.
        CATEGORY_UNKNOWN: A category of the sector has a lower daily
            minimum and the worker's is not known.
        PARTIAL_MONTH: The run pays part of its month.
        ABSENCE_IN_MONTH: An absence or a sick leave reduced the pay.
        PAY_ADDED_TO_MONTH: The run adds pay to a month posted by another
            run (an extra month, an adjustment, a termination), or settles
            the extra-month ratei with the pay of its month.
        MONTHLY_DAYS_UNSOURCED: The sector has no sourced monthly day count.
        PRESENCE_DAYS_UNKNOWN: A worker of a category paid by the day,
            paid by the hour, states no days of presence.
        HOURLY_MINIMUM_UNSOURCED: No hourly minimum is published for the
            full-time weekly hours of the part-time worker.
        MONTH_NOT_WORKED: The run would post the pay of a month the
            vertical part time does not work: no hour is paid, so the
            hourly minimum of D.Lgs. 81/2015 art. 11 c. 1 gives none.
        INDEMNIFIED_MONTH: Every employed day of the month is a maternity
            leave or a work-injury inability an insurer indemnifies: the
            days are credited with figurative contributions and the
            employer pays no day the daily minimum is counted on.
    """

    ABOVE_MINIMUM = "above_minimum"
    RAISED_TO_MINIMUM = "raised_to_minimum"
    APPRENTICE = "apprentice_excluded"
    CATEGORY_UNKNOWN = "category_unknown"
    PARTIAL_MONTH = "partial_month"
    ABSENCE_IN_MONTH = "absence_in_month"
    PAY_ADDED_TO_MONTH = "pay_added_to_month"
    MONTHLY_DAYS_UNSOURCED = "monthly_days_unsourced"
    HOURLY_MINIMUM_UNSOURCED = "hourly_minimum_unsourced"
    PRESENCE_DAYS_UNKNOWN = "presence_days_unknown"
    MONTH_NOT_WORKED = "month_not_worked"
    INDEMNIFIED_MONTH = "indemnified_month"


#: Reasons whose minimum the bundle cannot determine.
UNDETERMINED = frozenset({
    MinimumBaseReason.CATEGORY_UNKNOWN,
    MinimumBaseReason.PARTIAL_MONTH,
    MinimumBaseReason.ABSENCE_IN_MONTH,
    MinimumBaseReason.PAY_ADDED_TO_MONTH,
    MinimumBaseReason.MONTHLY_DAYS_UNSOURCED,
    MinimumBaseReason.HOURLY_MINIMUM_UNSOURCED,
    MinimumBaseReason.PRESENCE_DAYS_UNKNOWN,
})


@dataclass(frozen=True)
class MinimumBase:
    """The minimum the INPS base of a run is compared with.

    Attributes:
        actual: INPS base of the run before the minimum.
        bound: Highest minimum the month of the run can have.
        reason: How the minimum entered the base.
        minimum: Minimum of the month, ``None`` when not determined or not
            needed (the base reaches :attr:`bound`, or the worker is
            excluded).
        source: Location of the rule the minimum is read from.
    """

    actual: Decimal
    bound: Decimal
    reason: MinimumBaseReason
    minimum: Decimal | None = None
    source: SourceLocation | None = None

    @property
    def undetermined(self) -> bool:
        """Whether the base may be below a minimum the bundle cannot fix."""
        return self.reason in UNDETERMINED

    @property
    def base(self) -> Decimal:
        """INPS base of the run: the actual base raised to the minimum."""
        return self.raise_to_minimum(self.actual)

    def raise_to_minimum(self, amount: Decimal) -> Decimal:
        """Return ``amount`` raised to the minimum, when one is determined.

        Returns:
            The larger of ``amount`` and :attr:`minimum`; ``amount`` when the
            minimum is not determined.
        """
        return amount if self.minimum is None else max(amount, self.minimum)
