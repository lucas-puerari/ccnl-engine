"""Calendar override: a validated replacement of the CCNL standard calendar.

The standard calendar is always derived from the CCNL.  A caller replaces it
only through a :class:`CalendarOverride`, which carries a
:class:`CalendarOverrideReason` and is validated against the standard
calendar: no reason allows an override to drop or lower an extra month the
CCNL grants.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.calendar import ExtraMonthKind, WorkCalendar

__all__ = ["CalendarOverride", "CalendarOverrideReason"]

_FEATURE = "calendar_override"


class CalendarOverrideReason(StrEnum):
    """Domain reason for replacing the standard calendar of a CCNL.

    The list is deliberately short.  Paying the ratei monthly inside the
    regular pay (mensilizzazione) is real practice, but the engine does not
    pay ratei in regular runs, so an override that drops extra-month runs
    would underpay the worker; no reason allows it.

    Members:
        PAYMENT_MONTH: The CCNL article or the employer's practice pays an
            extra month in a different month than the engine default
            (quattordicesima in June), e.g. a quattordicesima paid with the
            July salary.  The extra months and their fractions must equal the
            ones the CCNL grants.
        MORE_FAVOURABLE_TREATMENT: An individual or company agreement grants
            more than the CCNL (trattamento di miglior favore, art. 2077 c.c.):
            an extra month the CCNL does not grant, or a larger fraction of
            one it grants.  Every CCNL extra month must be kept at least at
            its CCNL fraction, and at least one must be larger or added.
    """

    PAYMENT_MONTH = "payment_month"
    MORE_FAVOURABLE_TREATMENT = "more_favourable_treatment"


def _require_instance(name: str, value: object, expected: type) -> None:
    if not isinstance(value, expected):
        msg = f"CalendarOverride.{name} must be a {expected.__name__}; got {value!r}"
        raise InvalidInputError(msg, feature=_FEATURE)


def _require_note(value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        msg = "CalendarOverride.note must be a non-blank justification"
        raise InvalidInputError(msg, feature=_FEATURE)


def _fractions(calendar: WorkCalendar) -> dict[ExtraMonthKind, Decimal]:
    return {s.kind: s.max_fraction for s in calendar.extra_months}


def _require_window_ending_at_payment(calendar: WorkCalendar) -> None:
    # The engine accrues an extra month over the regular runs closed up to its
    # payment run plus the prior-year months of the window.  Only a 12-month
    # window ending in the payment month pays the full fraction to a
    # full-year worker; any other window silently lowers the amount.
    for sched in calendar.extra_months:
        start = sched.payment_month % 12 + 1
        if sched.accrual_window_start_month != start:
            msg = (
                f"the {sched.kind.value} extra month paid in month "
                f"{sched.payment_month} must accrue over the 12 months ending "
                f"in its payment month (accrual_window_start_month={start}); "
                f"got {sched.accrual_window_start_month}, which pays less than "
                f"its fraction"
            )
            raise InvalidInputError(msg, feature=_FEATURE)


@dataclass(frozen=True)
class CalendarOverride:
    """A calendar that replaces the CCNL standard one, with its reason.

    Attributes:
        calendar: The calendar to run instead of the standard one.
        reason: Why the standard calendar does not apply.
        note: Free-text justification kept for audit, e.g. the CCNL article
            or the agreement that sets the payment month.  Must not be blank.

    Raises:
        InvalidInputError: When ``calendar`` is not a :class:`WorkCalendar`,
            ``reason`` is not a :class:`CalendarOverrideReason` or ``note``
            is blank.
    """

    calendar: WorkCalendar
    reason: CalendarOverrideReason
    note: str

    def __post_init__(self) -> None:  # noqa: D105
        _require_instance("calendar", self.calendar, WorkCalendar)
        _require_instance("reason", self.reason, CalendarOverrideReason)
        _require_note(self.note)

    def resolve(self, standard: WorkCalendar) -> WorkCalendar:
        """Validate the override against the standard calendar and return it.

        Rules, compared per :class:`ExtraMonthKind` on ``max_fraction``
        (names are free):

        - the override is for the same year as ``standard``;
        - every extra month accrues over the 12 months ending in its payment
          month (``accrual_window_start_month == payment_month % 12 + 1``),
          so it pays its full fraction; a tredicesima is therefore paid in
          December;
        - every extra month of ``standard`` is kept with at least its
          fraction, whatever the reason;
        - :attr:`CalendarOverrideReason.PAYMENT_MONTH`: the fractions equal
          the standard ones, no extra month is added;
        - :attr:`CalendarOverrideReason.MORE_FAVOURABLE_TREATMENT`: at least
          one extra month is added or has a larger fraction.

        Args:
            standard: Calendar derived from the CCNL for the same year.

        Returns:
            :attr:`calendar`, the effective calendar of the year.

        Raises:
            InvalidInputError: When any rule is broken.
        """
        if self.calendar.year != standard.year:
            msg = (
                f"calendar override year {self.calendar.year} does not match "
                f"the payroll year {standard.year}"
            )
            raise InvalidInputError(msg, feature=_FEATURE)
        _require_window_ending_at_payment(self.calendar)
        granted = _fractions(standard)
        given = _fractions(self.calendar)
        for kind, fraction in granted.items():
            if given.get(kind, Decimal(0)) < fraction:
                msg = (
                    f"calendar override drops or lowers the {kind.value} extra "
                    f"month the CCNL grants (fraction {fraction}); no override "
                    f"reason allows reducing a CCNL entitlement"
                )
                raise InvalidInputError(msg, feature=_FEATURE)
        more = given != granted
        reason = self.reason
        if reason is CalendarOverrideReason.PAYMENT_MONTH and more:
            msg = (
                "a payment_month override must keep the CCNL extra months and "
                "fractions unchanged; use more_favourable_treatment to grant more"
            )
            raise InvalidInputError(msg, feature=_FEATURE)
        if reason is CalendarOverrideReason.MORE_FAVOURABLE_TREATMENT and not more:
            msg = (
                "a more_favourable_treatment override must add an extra month or "
                "raise a fraction; use payment_month to only move payments"
            )
            raise InvalidInputError(msg, feature=_FEATURE)
        return self.calendar
