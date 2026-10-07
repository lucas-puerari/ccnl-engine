"""The minimum INPS base of a run: the daily minimale and its exclusions.

Rule of INPS circ. 6/2026: par. 1, a daily minimum of 58.13 EUR (9.5% of
the 611.85 EUR minimum FPLD pension, D.L. 463/1983 art. 7 c. 1); par. 4,
the part-time hourly minimum of D.Lgs. 81/2015 art. 11 c. 1, "58,13 euro x
6/40 = 8,72 euro" for a 40-hour week and "58,13 euro x 5/36 = 8,07 euro"
for 36 hours on five days.  A fully paid month counts 26 days (6 x 52 /
12).  Art. 7 c. 5 excludes apprentices and operai agricoli.  Every
expected value below is worked by hand in its docstring.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.payroll.domain.minimum_base import MinimumBaseReason, MonthPosition
from ccnl_engine.payroll.service.minimum_base import resolve_minimum_base
from ccnl_engine.provenance.domain.chain import ProvenanceStatus, RuleProvenance
from ccnl_engine.provenance.domain.source import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.tax.domain.minimum_base import HourlyMinimum, MinimumBaseRule

_D = Decimal
_LOCATION = SourceLocation(
    source_document=SourceDocument(
        document_id="inps-circolare-6-2026",
        title="INPS Circolare n. 6 del 30 gennaio 2026",
        kind=SourceKind.INPS_CIRCOLARE,
    ),
    section="par. 1; par. 4",
)
_PRIVATE = MinimumBaseRule(
    daily=_D("58.13"),
    week_days=6,
    monthly_days=26,
    hourly=(HourlyMinimum(full_time_weekly_hours=_D(40), amount=_D("8.72")),),
    provenance=RuleProvenance(status=ProvenanceStatus.DERIVED, location=_LOCATION),
)
_AGRICULTURE = _PRIVATE.model_copy(
    update={"exempt_categories": frozenset({WorkerCategory.OPERAIO})}
)
_PUBLIC = MinimumBaseRule(
    daily=_D("58.13"),
    week_days=5,
    monthly_days=None,
    hourly=(HourlyMinimum(full_time_weekly_hours=_D(36), amount=_D("8.07")),),
)
#: 26 x 58.13.
_FULL_MONTH = _D("1511.38")


#: A full month of a full-time worker paid 1,437.20.
_FULL_TIME = MonthPosition(month_pay=_D("1437.20"))


def _part_time(full_time: int) -> MonthPosition:
    return MonthPosition(
        month_pay=_D("718.60"),
        weekly_hours=_D(20),
        full_time_weekly_hours=_D(full_time),
    )


def test_full_month_below_the_minimum_is_raised() -> None:
    """1,437.20 < 26 x 58.13 = 1,511.38: contributed on 1,511.38."""
    minimum = resolve_minimum_base(_PRIVATE, _D("1437.20"), _FULL_TIME)

    assert minimum.reason is MinimumBaseReason.RAISED_TO_MINIMUM
    assert (minimum.minimum, minimum.base, minimum.bound) == (_FULL_MONTH,) * 3
    assert not minimum.undetermined
    assert minimum.source == _LOCATION


def test_full_month_above_the_minimum_is_kept() -> None:
    """1,600.00 >= 1,511.38: the base is the pay, no minimum is needed."""
    minimum = resolve_minimum_base(_PRIVATE, _D("1600.00"), _FULL_TIME)

    assert minimum.reason is MinimumBaseReason.ABOVE_MINIMUM
    assert (minimum.minimum, minimum.base) == (None, _D("1600.00"))


def test_part_time_is_raised_to_the_hourly_minimum() -> None:
    """20 of 40 hours: 8.72 x 20 hours x 26 / 6 days = 755.733, so 755.73."""
    minimum = resolve_minimum_base(_PRIVATE, _D("718.60"), _part_time(40))

    assert minimum.reason is MinimumBaseReason.RAISED_TO_MINIMUM
    assert minimum.base == _D("755.73")


def test_part_time_between_bound_and_published_minimum_is_raised() -> None:
    """755.70 is below 755.73: the published 8.72 sets the bound too."""
    minimum = resolve_minimum_base(_PRIVATE, _D("755.70"), _part_time(40))

    assert minimum.base == _D("755.73")


def test_part_time_of_an_unpublished_week_is_undetermined() -> None:
    """20 of 38 hours: up to 58.13 x 6/38 x 20 x 26/6 = 795.4568, so 795.46.

    INPS publishes no hourly minimum of a 38-hour week and the days of its
    normal week are not known: 700.00 cannot be compared.
    """
    minimum = resolve_minimum_base(_PRIVATE, _D("700.00"), _part_time(38))

    assert minimum.reason is MinimumBaseReason.HOURLY_MINIMUM_UNSOURCED
    assert minimum.bound == _D("795.46")
    assert minimum.undetermined
    assert (minimum.minimum, minimum.base) == (None, _D("700.00"))


@pytest.mark.parametrize(
    ("rule", "position", "reason"),
    [
        (_PRIVATE, replace(_FULL_TIME, apprentice=True), MinimumBaseReason.APPRENTICE),
        (
            _AGRICULTURE,
            replace(_FULL_TIME, category=WorkerCategory.OPERAIO),
            MinimumBaseReason.EXEMPT_CATEGORY,
        ),
    ],
)
def test_art_7_c_5_exclusions_keep_the_pay(
    rule: MinimumBaseRule, position: MonthPosition, reason: MinimumBaseReason
) -> None:
    """Apprentices and operai agricoli are contributed on the pay, 900.00."""
    minimum = resolve_minimum_base(rule, _D("900.00"), position)

    assert minimum.reason is reason
    assert minimum.base == _D("900.00")
    assert not minimum.undetermined


def test_impiegato_agricolo_keeps_the_minimum() -> None:
    """Art. 7 c. 5 excludes the operai only: 1,000.00 is raised to 1,511.38."""
    position = replace(_FULL_TIME, category=WorkerCategory.IMPIEGATO)
    minimum = resolve_minimum_base(_AGRICULTURE, _D("1000.00"), position)

    assert minimum.base == _FULL_MONTH


@pytest.mark.parametrize(
    ("position", "reason"),
    [
        (_FULL_TIME, MinimumBaseReason.CATEGORY_UNKNOWN),
        (
            replace(_FULL_TIME, category=WorkerCategory.IMPIEGATO, absence=True),
            MinimumBaseReason.ABSENCE_IN_MONTH,
        ),
    ],
)
def test_open_month_below_the_bound_is_undetermined(
    position: MonthPosition, reason: MinimumBaseReason
) -> None:
    """An unknown category or an absence: 1,000.00 < 1,511.38 stays open."""
    minimum = resolve_minimum_base(_AGRICULTURE, _D("1000.00"), position)

    assert minimum.reason is reason
    assert minimum.undetermined
    assert minimum.base == _D("1000.00")


def test_pay_added_to_a_month_below_the_minimum_is_undetermined() -> None:
    """An extra month of a worker paid 1,437.20 a month stays open.

    Whether it counts toward the 1,511.38 of its month is not sourced.
    """
    position = replace(_FULL_TIME, adds_to_month=True)
    minimum = resolve_minimum_base(_PRIVATE, _D("300.00"), position)

    assert minimum.reason is MinimumBaseReason.PAY_ADDED_TO_MONTH
    assert minimum.base == _D("300.00")


def test_pay_added_to_a_month_above_the_minimum_is_kept() -> None:
    """A monthly pay of 1,600.00 reaches 1,511.38 alone: 300.00 is kept."""
    position = MonthPosition(month_pay=_D("1600.00"), adds_to_month=True)
    minimum = resolve_minimum_base(_PRIVATE, _D("300.00"), position)

    assert minimum.reason is MinimumBaseReason.ABOVE_MINIMUM
    assert minimum.base == _D("300.00")


@pytest.mark.parametrize(
    ("actual", "reason"),
    [
        ("470.00", MinimumBaseReason.ABOVE_MINIMUM),
        ("460.00", MinimumBaseReason.PARTIAL_MONTH),
    ],
)
def test_partial_month_is_bounded_by_its_working_days(
    actual: str, reason: MinimumBaseReason
) -> None:
    """Employed from Monday 22 to Tuesday 30 June 2026: at most 465.04.

    8 days of a six-day week (22-27, 29, 30): 8 x 58.13 = 465.04.
    """
    position = replace(_FULL_TIME, span=(date(2026, 6, 22), date(2026, 6, 30)))
    minimum = resolve_minimum_base(_PRIVATE, _D(actual), position)

    assert minimum.bound == _D("465.04")
    assert minimum.reason is reason


@pytest.mark.parametrize(
    ("actual", "reason"),
    [
        ("1600.00", MinimumBaseReason.ABOVE_MINIMUM),
        ("1520.00", MinimumBaseReason.MONTHLY_DAYS_UNSOURCED),
    ],
)
def test_sector_without_a_day_count_is_bounded_by_a_six_day_week(
    actual: str, reason: MinimumBaseReason
) -> None:
    """Even on a five-day week the count may be of six-day weeks.

    A calendar month holds at most 27 days of a six-day week (31 days from
    a Monday): 27 x 58.13 = 1,569.51.
    """
    minimum = resolve_minimum_base(_PUBLIC, _D(actual), _FULL_TIME)

    assert minimum.bound == _D("1569.51")
    assert minimum.reason is reason
    assert minimum.source is None
