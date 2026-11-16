"""Work-time supplement events: overtime, night, holiday and shift work."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.validators import (
    parse_enum,
    require_bool,
    require_date,
    require_decimal,
    require_str,
)
from ccnl_engine.working_time.event_kinds import (
    HolidayWorkKind,
    OvertimeKind,
    ShiftKind,
)
from ccnl_engine.working_time.supplement.checks import check_supplement

if TYPE_CHECKING:
    from datetime import date

_ZERO = Decimal(0)
#: Hours of a month of 31 days: no event of a month can exceed them.
_HOURS_IN_A_MONTH = Decimal(31 * 24)

__all__ = [
    "HolidayWorkEvent",
    "HolidayWorkKind",
    "NightShiftEvent",
    "OvertimeEvent",
    "OvertimeKind",
    "ShiftKind",
    "ShiftWorkEvent",
]


@dataclass(frozen=True)
class OvertimeEvent:
    """Overtime hours: INPS + IRPEF + TFR on computed gross.

    Attributes:
        event_date: Calendar date the overtime was worked.
        hours: Overtime hours, above 0 and at most 744 (a month of 31 days).
        hourly_rate: Base hourly rate in EUR, above 0; ``None`` derives it
            from the CCNL hourly base (the run is rejected without one).
        multiplier: Overtime multiplier applied to the hourly rate (e.g.
            ``1.25`` for 25% supplement).  Must be > 0.  ``None`` (the
            default) derives it from the CCNL band of ``kind`` as
            ``1 + band``; the run is rejected when the CCNL has no single
            percentage band for it.  An explicit value prevails over the
            CCNL band.
        kind: When the hours were worked, selecting the CCNL band.
        non_occasional: Whether the overtime is worked 'a titolo non
            occasionale', which a CCNL may count in the TFR (operai agricoli
            OTD: 10%); ``False`` is occasional overtime.
        banked: Whether the worker elected compensatory rest for these hours.
            Only an agreement with an overtime bank rule can pay the premium
            alone; the hours remain a separate rest balance outside this event.
        weekly_hours_before: Total hours already worked in the week before
            this event; when supplied, weekly overtime tiers can be split
            across the event. Does not include the hours of this event.
        exempt_quota_hours_before: Overtime hours worked earlier in the
            calendar year under the CCNL regime of the 'quote esenti'
            (Federmeccanica art. 7); stating it places the event in that
            regime, ``None`` for overtime outside it.
        in_periodic_shift: Whether the worker is a turnista, which chooses
            the yearly exempt quota; ``None`` when not stated.
        supplementary_hours_before: Part-time supplementary hours worked
            earlier in the calendar year, for a CCNL whose rate rises past a
            share of the agreed annual hours.
        agreed_annual_hours: Annual hours of the part-time contract that
            share is taken of.
        multiweek_hours_before: Hours of the multi-week schedule worked
            earlier in its period (at most 12 months from its activation),
            for a CCNL whose premiums rise past a threshold of hours.
    """

    event_date: date
    hours: Decimal
    hourly_rate: Decimal | None = None
    multiplier: Decimal | None = None
    kind: OvertimeKind = OvertimeKind.WEEKDAY
    non_occasional: bool = False
    banked: bool = False
    weekly_hours_before: Decimal | None = None
    exempt_quota_hours_before: Decimal | None = None
    in_periodic_shift: bool | None = None
    supplementary_hours_before: Decimal | None = None
    agreed_annual_hours: Decimal | None = None
    multiweek_hours_before: Decimal | None = None

    def __post_init__(self) -> None:  # noqa: D105
        feature = "overtime"
        require_date(self.event_date, "OvertimeEvent.event_date", feature=feature)
        require_decimal(
            self.hours,
            "OvertimeEvent.hours",
            feature=feature,
            positive=True,
            maximum=_HOURS_IN_A_MONTH,
        )
        for name in ("hourly_rate", "multiplier"):
            require_decimal(
                getattr(self, name),
                f"OvertimeEvent.{name}",
                feature=feature,
                positive=True,
                optional=True,
            )
        for name in (
            "weekly_hours_before",
            "exempt_quota_hours_before",
            "supplementary_hours_before",
            "agreed_annual_hours",
            "multiweek_hours_before",
        ):
            require_decimal(
                getattr(self, name),
                f"OvertimeEvent.{name}",
                feature=feature,
                minimum=_ZERO,
                optional=True,
            )
        if self.in_periodic_shift is not None:
            require_bool(
                self.in_periodic_shift,
                "OvertimeEvent.in_periodic_shift",
                feature=feature,
            )
        require_bool(
            self.non_occasional, "OvertimeEvent.non_occasional", feature=feature
        )
        require_bool(self.banked, "OvertimeEvent.banked", feature=feature)
        kind = parse_enum(
            self.kind, OvertimeKind, "OvertimeEvent.kind", feature=feature
        )
        object.__setattr__(self, "kind", kind)


@dataclass(frozen=True)
class NightShiftEvent:
    """Night-work supplement: INPS + IRPEF on the supplement amount.

    Covers the maggiorazioni and indennita for ordinary night work (D.Lgs.
    66/2003 art. 1 c. 2 and the CCNL), eligible for the 15% substitute tax
    within the 1,500 EUR annual cap.  Night overtime is an
    :class:`OvertimeEvent`.

    Attributes:
        event_date: Calendar date the night hours were worked.
        supplement_amount: Supplement for the night hours in EUR, >= 0;
            reported as caller-supplied.  ``None`` (the default) derives it
            from the CCNL night band and hourly base, ``hours`` required;
            the run is rejected when the CCNL has none the engine applies.
        hours: Ordinary night hours, above 0 and at most 744.
        before_22: Whether the hours fall before 22:00, which a CCNL may pay
            at a lower night rate (Confapi art. 29 row b).
        shifts: Night turns worked, for a CCNL that pays the turn (scuola
            Tabella E1.8); ``None`` when not stated.
        service: The kind of night service, by the code of the CCNL band
            (Farmacie art. 19: ``doors_open``, ``doors_closed`` and their
            ``_beyond_8`` hours), for a CCNL that pays it by the service;
            ``None`` when not stated.
    """

    event_date: date
    supplement_amount: Decimal | None = None
    hours: Decimal | None = None
    before_22: bool = False
    shifts: int | None = None
    service: str | None = None

    def __post_init__(self) -> None:  # noqa: D105
        check_supplement(
            self.event_date,
            self.supplement_amount,
            self.hours,
            "NightShiftEvent",
            "night_shift",
            self.shifts,
        )
        require_bool(self.before_22, "NightShiftEvent.before_22", feature="night_shift")
        require_str(
            self.service,
            "NightShiftEvent.service",
            feature="night_shift",
            non_blank=True,
            optional=True,
        )


@dataclass(frozen=True)
class HolidayWorkEvent:
    """Holiday or weekly rest-day supplement: INPS + IRPEF on the supplement.

    Covers the maggiorazioni and indennita for work on public holidays and on
    weekly rest days as identified by the CCNL, eligible for the 15%
    substitute tax within the 1,500 EUR annual cap.  TFR is not accrued on
    holiday supplements under the standard Italian treatment (art. 2120 c.c.
    excludes accidental pay).  Where the CCNL also pays the hours themselves,
    the engine does not post them: the run reports it.

    Attributes:
        event_date: Calendar date the holiday or rest day was worked.
        supplement_amount: Supplement for the day in EUR, >= 0; reported as
            caller-supplied.  ``None`` (the default) derives it from the
            CCNL band of ``kind`` and hourly base, ``hours`` required.
        hours: Hours worked that day, above 0 and at most 744.
        kind: Which holiday or rest-day work the hours are.
        in_periodic_shift: Whether the worker is a turnista (rotating-shift
            worker); ``None`` when unknown. Required only by bands excluding
            such workers, even if these particular hours are outside a turn.
        shifts: Turns worked that day, for a CCNL that pays the turn (scuola
            Tabella E1.8); ``None`` when not stated.
    """

    event_date: date
    supplement_amount: Decimal | None = None
    hours: Decimal | None = None
    kind: HolidayWorkKind = HolidayWorkKind.HOLIDAY
    in_periodic_shift: bool | None = None
    shifts: int | None = None

    def __post_init__(self) -> None:  # noqa: D105
        feature = "holiday_work"
        check_supplement(
            self.event_date,
            self.supplement_amount,
            self.hours,
            "HolidayWorkEvent",
            feature,
            self.shifts,
        )
        kind = parse_enum(
            self.kind, HolidayWorkKind, "HolidayWorkEvent.kind", feature=feature
        )
        object.__setattr__(self, "kind", kind)
        if self.in_periodic_shift is not None:
            require_bool(
                self.in_periodic_shift,
                "HolidayWorkEvent.in_periodic_shift",
                feature=feature,
            )


@dataclass(frozen=True)
class ShiftWorkEvent:
    """Shift-work allowance: INPS + IRPEF on the supplement amount.

    Covers the indennita di turno and the other shift-work pay set by the
    CCNL, eligible for the 15% substitute tax within the 1,500 EUR annual
    cap.  TFR is not accrued, as for the other work-time supplements.

    Attributes:
        event_date: Calendar date the shift was worked.
        supplement_amount: Shift allowance in EUR, >= 0; reported as
            caller-supplied.  ``None`` (the default) derives it from the
            CCNL band of ``kind`` and hourly base, ``hours`` and ``kind``
            required.
        hours: Hours of the shift, above 0 and at most 744.
        kind: The shift of the rotation; ``None`` when not stated.
        shifts: Days of shift worked, for a CCNL that pays the day of shift
            (Sanità art. 67 c. 2: "per ogni giornata di effettivo lavoro").
        service: The kind of rotation, by the code of the CCNL band, for a
            CCNL that pays it by the rotation (Mobilità AF art. 30).
    """

    event_date: date
    supplement_amount: Decimal | None = None
    hours: Decimal | None = None
    kind: ShiftKind | None = None
    shifts: int | None = None
    service: str | None = None

    def __post_init__(self) -> None:  # noqa: D105
        feature = "shift_work"
        check_supplement(
            self.event_date,
            self.supplement_amount,
            self.hours,
            "ShiftWorkEvent",
            feature,
            self.shifts,
        )
        if self.kind is not None:
            kind = parse_enum(
                self.kind, ShiftKind, "ShiftWorkEvent.kind", feature=feature
            )
            object.__setattr__(self, "kind", kind)
        path = "ShiftWorkEvent.service"
        require_str(self.service, path, feature=feature, non_blank=True, optional=True)
