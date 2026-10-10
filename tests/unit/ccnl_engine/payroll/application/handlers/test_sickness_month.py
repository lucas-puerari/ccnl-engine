"""The sick days of a month against its pay and its unpaid absences.

Payable days are counted as the proration counts them: by 26, Mondays to
Saturdays; by 30, a commercial month where day 31 counts as day 30; by the
hour, Mondays to Fridays.  February 2026 has 24 Mondays to Saturdays, March
2026 has 31 days, May 2026 ends on Sunday 31.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.contract.absence.models import DailyDivisorMethod
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.application.handlers._sickness_month import (
    QUOTA_MISMATCH,
    WITH_UNPAID_ABSENCE,
    check_absences_off_sick_days,
    month_issues,
)
from ccnl_engine.payroll.application.handlers._sickness_terms import (
    DailyQuota,
    SicknessTerms,
)
from ccnl_engine.payroll.domain.events import AbsenceEvent
from ccnl_engine.payroll.domain.sickness import SicknessEpisode

_BY_26 = DailyQuota(DailyDivisorMethod.BY_26, Decimal(26))
_BY_30 = DailyQuota(DailyDivisorMethod.BY_30, Decimal(30))
_HOURLY = DailyQuota(DailyDivisorMethod.BY_HOURLY, Decimal(166), Decimal("7.6"))
_EPISODE = SicknessEpisode("a", date(2026, 3, 2), date(2026, 3, 6))


def _days(first: date, last: date) -> frozenset[date]:
    return frozenset(first + timedelta(days=k) for k in range((last - first).days + 1))


def _terms(employed: tuple[date, date], quota: DailyQuota) -> SicknessTerms:
    return SicknessTerms(employed=employed, quota=quota)


def _codes(
    employed: tuple[date, date],
    quota: DailyQuota,
    sick: tuple[date, date],
    deducted: Decimal,
) -> list[str]:
    issues = month_issues((_EPISODE,), _terms(employed, quota), _days(*sick), deducted)
    return [i.code for i in issues]


_FEBRUARY = date(2026, 2, 1), date(2026, 2, 28)
_MARCH = date(2026, 3, 1), date(2026, 3, 31)
_MAY = date(2026, 5, 1), date(2026, 5, 31)
_HIRED_16_MARCH = date(2026, 3, 16), date(2026, 3, 31)


@pytest.mark.parametrize(
    ("employed", "quota", "sick", "deducted", "codes"),
    [
        (_FEBRUARY, _BY_26, _FEBRUARY, Decimal(24), [QUOTA_MISMATCH]),
        (
            _MARCH,
            _BY_30,
            (date(2026, 3, 1), date(2026, 3, 30)),
            Decimal(30),
            [QUOTA_MISMATCH],
        ),
        (_MAY, _BY_26, (date(2026, 5, 1), date(2026, 5, 30)), Decimal(26), []),
        (_MARCH, _BY_30, _MARCH, Decimal(30), []),
        (
            (date(2026, 2, 16), date(2026, 2, 28)),
            _BY_26,
            (date(2026, 2, 16), date(2026, 2, 28)),
            Decimal(12),
            [],
        ),
        (
            (date(2026, 3, 16), date(2026, 3, 31)),
            _HOURLY,
            (date(2026, 3, 16), date(2026, 3, 31)),
            Decimal("91.2"),
            [],
        ),
        (_MARCH, _BY_26, (date(2026, 3, 2), date(2026, 3, 6)), Decimal(5), []),
        (
            _HIRED_16_MARCH,
            _BY_30,
            (date(2026, 3, 16), date(2026, 3, 30)),
            Decimal(15),
            [QUOTA_MISMATCH],
        ),
        (_HIRED_16_MARCH, _BY_30, _HIRED_16_MARCH, Decimal(15), []),
    ],
    ids=[
        "february_by_26_leaves_pay",
        "day_31_by_30_left_unpaid",
        "sunday_31_not_payable",
        "whole_month_by_30",
        "partial_month_by_26",
        "partial_month_by_hour",
        "some_days",
        "partial_month_by_30_day_31_worked",
        "partial_month_by_30_all_sick",
    ],
)
def test_quota_mismatch(
    employed: tuple[date, date],
    quota: DailyQuota,
    sick: tuple[date, date],
    deducted: Decimal,
    codes: list[str],
) -> None:
    """A full month that leaves pay, or a worked day left unpaid, is an issue.

    16-28 February by 26 are 12 Mondays to Saturdays; 16-31 March by the
    hour 12 Mondays to Fridays of 7.6 hours, 91.2 hours; by 30, 16-31
    March are days 16 to 30 of the commercial month, 15 units, and so are
    16-30 March, though 31 March is worked.
    """
    assert _codes(employed, quota, sick, deducted) == codes


def test_nothing_to_check_without_sick_days_or_quota() -> None:
    """No sick day, no posted month or no quota: no issue."""
    terms = _terms(_MARCH, _BY_26)
    assert month_issues((_EPISODE,), terms, frozenset(), Decimal(0)) == ()
    sick = _days(*_MARCH)
    assert month_issues((_EPISODE,), SicknessTerms(), sick, Decimal(26)) == ()
    no_quota = SicknessTerms(employed=_MARCH)
    assert month_issues((_EPISODE,), no_quota, sick, Decimal(26)) == ()


def test_an_unpaid_absence_beside_sick_days_is_an_issue() -> None:
    """Hours at the caller's rate and days at the CCNL quota do not add up."""
    absence = AbsenceEvent(date(2026, 3, 10), Decimal(8), Decimal("12.75"))
    issues = month_issues(
        (_EPISODE, absence),
        _terms(_MARCH, _BY_26),
        _days(date(2026, 3, 2), date(2026, 3, 6)),
        Decimal(5),
    )
    assert [i.code for i in issues] == [WITH_UNPAID_ABSENCE]


@pytest.mark.parametrize(
    ("first", "last"),
    [(date(2026, 3, 6), None), (date(2026, 3, 1), date(2026, 3, 2))],
    ids=["one_day", "range"],
)
def test_an_unpaid_absence_on_a_sick_day_is_rejected(
    first: date, last: date | None
) -> None:
    """A day cannot be both: 6 March and 1-2 March touch the 2-6 March episode."""
    absence = AbsenceEvent(first, Decimal(8), Decimal("12.75"), end_date=last)
    with pytest.raises(InvalidInputError, match="falls on days of sickness"):
        check_absences_off_sick_days((_EPISODE, absence))


def test_an_unpaid_absence_on_another_day_is_accepted() -> None:
    """9 March is not a day of the 2-6 March episode."""
    absence = AbsenceEvent(date(2026, 3, 9), Decimal(8), Decimal("12.75"))
    check_absences_off_sick_days((_EPISODE, absence))
