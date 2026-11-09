"""Resolve weekly overtime thresholds against the hours preceding an event."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import MissingRuleError

if TYPE_CHECKING:
    from ccnl_engine.event.facade import OvertimeEvent
    from ccnl_engine.working_time.models import OvertimeBand


def weekly_rate(
    event: OvertimeEvent,
    matching: list[tuple[OvertimeBand, Decimal]],
) -> tuple[Decimal, tuple[tuple[OvertimeBand, Decimal, Decimal], ...]]:
    """Return the weighted multiplier and (band, supplement, hours) slices.

    A threshold is the number of hours already worked, not the ordinal of
    the first hour in the higher tier. An unconditional band covers hours
    before the first threshold. A gap in coverage must not be guessed.

    Returns:
        The effective multiplier and the slices that determine it.

    Raises:
        MissingRuleError: If no band covers part of the event.
    """
    start = event.weekly_hours_before
    assert start is not None
    end = start + event.hours
    weekly = sorted(
        ((b, r) for b, r in matching if b.hour_threshold_per_day is None),
        key=lambda entry: (
            Decimal(-1)
            if entry[0].hour_threshold_per_week is None
            else Decimal(entry[0].hour_threshold_per_week)
        ),
    )
    slices: list[tuple[OvertimeBand, Decimal, Decimal]] = []
    position = start
    while position < end:
        eligible = [
            (b, r)
            for b, r in weekly
            if b.hour_threshold_per_week is None
            or Decimal(b.hour_threshold_per_week) <= position
        ]
        if not eligible:
            msg = "No weekly overtime band covers the start of the event"
            raise MissingRuleError(
                msg,
                as_of=event.event_date,
                feature="overtime",
                remediation="Supply covered overtime hours or a multiplier.",
            )
        band, supplement = eligible[-1]
        next_start = min(
            (
                Decimal(b.hour_threshold_per_week)
                for b, _ in weekly
                if b.hour_threshold_per_week is not None
                and Decimal(b.hour_threshold_per_week) > position
            ),
            default=end,
        )
        hours = min(end, next_start) - position
        slices.append((band, supplement, hours))
        position += hours
    multiplier = (
        Decimal(1)
        + sum((r * hours for _, r, hours in slices), Decimal(0)) / event.hours
    )
    return multiplier, tuple(slices)
