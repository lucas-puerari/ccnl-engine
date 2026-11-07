"""The rate of each day of a parental leave (art. 34 D.Lgs. 151/2001)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.parental.inputs import (
    ParentalLeaveEvent,
    ParentalLeaveTaken,
)
from ccnl_engine.absence.insured.parental.models import EnhancedCohort, ParentalRates
from ccnl_engine.absence.insured.parental.rules import allocate, indemnity
from ccnl_engine.errors import InvalidInputError

_RATES = load_insured_absence_rates().parental
_LOW, _HIGH = Decimal("0.30"), Decimal("0.80")
_BORN = date(2025, 6, 1)
_END = date(2025, 9, 1)


def _leave(
    first: date,
    last: date,
    taken: ParentalLeaveTaken | None = None,
    *,
    born: date = _BORN,
    end: date | None = _END,
    single: bool = False,
) -> ParentalLeaveEvent:
    return ParentalLeaveEvent(
        first,
        last,
        born,
        taken or ParentalLeaveTaken(0, 0, 0),
        end,
        single_parent=single,
    )


def _rates(event: ParentalLeaveEvent) -> list[Decimal | None]:
    return list(allocate(event, _RATES).rates.values())


def test_february_is_one_month_its_last_day_three_days_of_counter() -> None:
    """Of 2 enhanced days left, both go on the last day of February."""
    taken = ParentalLeaveTaken(60, 60, 0)
    rates = _rates(_leave(date(2026, 2, 1), date(2026, 3, 2), taken))

    assert rates[:27] == [_HIGH] * 27
    assert rates[27] == _HIGH
    assert rates[28:] == [_LOW, _LOW]


def test_a_piece_shorter_than_a_month_counts_its_days() -> None:
    """Ten days of a piece are ten days of counter."""
    taken = ParentalLeaveTaken(85, 85, 0)
    days = allocate(_leave(date(2026, 3, 2), date(2026, 3, 11), taken), _RATES)

    assert list(days.rates.values()) == [_HIGH] * 5 + [_LOW] * 5
    assert days.split == set()


def test_the_enhanced_rate_ends_at_six_years() -> None:
    """The day the child turns six the leave is paid at 30%."""
    born, end = date(2020, 3, 10), date(2023, 1, 2)
    rates = _rates(_leave(date(2026, 3, 8), date(2026, 3, 11), born=born, end=end))

    assert rates == [_HIGH, _HIGH, _LOW, _LOW]


def test_a_sole_parent_has_nine_months_and_no_shared_ones() -> None:
    """Beyond the nine months nothing is paid."""
    taken = ParentalLeaveTaken(269, 90, 0)
    rates = _rates(_leave(date(2026, 3, 2), date(2026, 3, 3), taken, single=True))

    assert rates == [_LOW, None]


def test_the_shared_months_follow_the_parents_own() -> None:
    """After the own months, the couple's further months, then nothing."""
    taken = ParentalLeaveTaken(89, 90, 89)
    rates = _rates(_leave(date(2026, 3, 2), date(2026, 3, 4), taken))

    assert rates == [_LOW, _LOW, None]


@pytest.mark.parametrize(
    ("born", "end", "months"),
    [
        (date(2022, 6, 1), date(2022, 11, 1), 0),
        (date(2022, 6, 1), date(2023, 1, 1), 1),
        (date(2023, 12, 1), date(2024, 3, 1), 2),
        (date(2024, 12, 1), None, 2),
        (date(2025, 1, 1), None, 3),
    ],
)
def test_the_cohort_gives_the_months_at_80_percent(
    born: date, end: date | None, months: int
) -> None:
    """The later of the protected leave's end and the birth sets the cohort."""
    taken = ParentalLeaveTaken(29, 0, 0)
    rates = _rates(
        _leave(date(2026, 3, 2), date(2026, 3, 3), taken, born=born, end=end)
    )
    enhanced = [_HIGH, _HIGH] if months else [_LOW, _LOW]

    assert rates == enhanced
    assert _RATES.enhanced_months(date(2026, 3, 2), end or born, born) == months


def test_only_a_late_end_could_give_more_months() -> None:
    """An unstated end matters only when the birth gives fewer months."""
    early = allocate(
        _leave(date(2026, 3, 2), date(2026, 3, 3), born=date(2024, 6, 1), end=None),
        _RATES,
    )
    late = allocate(
        _leave(date(2026, 3, 2), date(2026, 3, 3), born=date(2025, 3, 1), end=None),
        _RATES,
    )

    stated = allocate(
        _leave(date(2026, 3, 2), date(2026, 3, 3), born=date(2024, 6, 1)), _RATES
    )

    assert (early.cohort_unknown, late.cohort_unknown) == (True, False)
    assert not stated.cohort_unknown


def test_the_sixth_birthday_is_past_the_enhanced_rate() -> None:
    """Born 2 March 2020: from 2 March 2026 no cohort can give the 80%."""
    sixth = allocate(
        _leave(date(2026, 3, 2), date(2026, 3, 3), born=date(2020, 3, 2), end=None),
        _RATES,
    )

    assert not sixth.cohort_unknown


def test_a_cohort_applies_from_its_first_day() -> None:
    """Before 2023 no day is paid at 80%, whatever the birth."""
    assert _RATES.enhanced_months(date(2022, 12, 31), date.max, date(2022, 6, 1)) == 0


def test_the_indemnity_sums_the_rates_of_the_days() -> None:
    """Two days at 80% and one at 30% of 100: 190.00."""
    taken = ParentalLeaveTaken(88, 88, 0)
    days = allocate(_leave(date(2026, 3, 2), date(2026, 3, 4), taken), _RATES)

    assert indemnity(days, date(2026, 3, 2), date(2026, 3, 4), Decimal(100)) == (
        Decimal("190.00")
    )


@pytest.mark.parametrize(
    ("cohorts", "match"),
    [
        (
            [
                EnhancedCohort(from_date=date(2024, 1, 1), months=1),
                EnhancedCohort(from_date=date(2023, 1, 1), months=2),
            ],
            "grow in date and months",
        ),
        ([EnhancedCohort(from_date=date(2023, 1, 1), months=4)], "fit in"),
    ],
)
def test_the_cohorts_grow_and_fit_in_a_parents_months(
    cohorts: list[EnhancedCohort], match: str
) -> None:
    """A cohort of more months starts later, within the own months."""
    data = _RATES.model_dump()
    data["enhanced"] = [c.model_dump() for c in cohorts]

    with pytest.raises(ValueError, match=match):
        ParentalRates.model_validate(data)


def test_a_single_day_is_one_day_of_counter() -> None:
    """A leave of one day is paid that day."""
    assert _rates(_leave(date(2026, 3, 2), date(2026, 3, 2))) == [_HIGH]


def test_two_calendar_months_are_sixty_days_of_counter() -> None:
    """March and April use up the own months; 1 May is a shared month."""
    taken = ParentalLeaveTaken(30, 30, 0)
    rates = _rates(_leave(date(2026, 3, 1), date(2026, 5, 1), taken))

    assert rates == [_HIGH] * 61 + [_LOW]


def test_december_is_one_month_into_the_next_year() -> None:
    """A month from 15 December ends on 14 January."""
    taken = ParentalLeaveTaken(80, 80, 0)
    days = allocate(_leave(date(2026, 12, 15), date(2027, 1, 14), taken), _RATES)

    assert list(days.rates.values()) == [_HIGH] * 10 + [_LOW] * 21
    assert len(days.split) == 31


def test_the_enhanced_months_of_the_couple_run_out_first() -> None:
    """The other parent took 85 days at 80%: 5 are left, then 30%."""
    taken = ParentalLeaveTaken(0, 85, 0)

    assert _rates(_leave(date(2026, 3, 2), date(2026, 3, 8), taken)) == (
        [_HIGH] * 5 + [_LOW] * 2
    )


def test_the_shared_months_run_out_day_by_day() -> None:
    """Two shared days are left: the third is not paid."""
    taken = ParentalLeaveTaken(90, 90, 88)

    assert _rates(_leave(date(2026, 3, 2), date(2026, 3, 4), taken)) == [
        _LOW,
        _LOW,
        None,
    ]


def test_a_child_born_on_29_february_is_six_on_28_february() -> None:
    """The enhanced rate ends on 28 February of the sixth year."""
    born, end = date(2020, 2, 29), date(2023, 1, 2)
    rates = _rates(_leave(date(2026, 2, 27), date(2026, 2, 28), born=born, end=end))

    assert rates == [_HIGH, _LOW]


def test_the_leave_cannot_reach_the_fourteenth_birthday() -> None:
    """The day the child turns fourteen is no longer a day of leave."""
    leave = _leave(date(2026, 3, 1), date(2026, 3, 15), born=date(2012, 3, 15))

    with pytest.raises(InvalidInputError) as error:
        allocate(leave, _RATES)

    assert (str(error.value), error.value.field, error.value.feature) == (
        "ParentalLeaveEvent.ended_on must precede the child's 14th birthday",
        "ParentalLeaveEvent.ended_on",
        "parental_leave",
    )


def test_a_cohort_starts_on_its_first_day_and_birth() -> None:
    """Leave on 1 January 2023, or a birth on 1 January 2025, is in."""
    born = date(2025, 1, 1)

    assert _RATES.enhanced_months(date(2023, 1, 1), date(2023, 1, 1), born) == 1
    assert _RATES.enhanced_months(date(2026, 3, 1), date(2024, 1, 1), born) == 3
