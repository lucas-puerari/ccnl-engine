"""Tests for the employment spells of a tax year and the days they count.

The days of the art. 13 TUIR deduction are the calendar days of the
employments whose income the withholding counts, "i giorni compresi in
periodi contemporanei" once (istruzioni CU 2026, punto 721).
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.employment_spells import (
    EmploymentSpell,
    spell_days,
    spells_of,
    spells_with,
)

_PATH = "TaxCashState.employment_spells"


def _spell(first: date, last: date, *, fixed_term: bool = False) -> EmploymentSpell:
    return EmploymentSpell(first, last, fixed_term)


#: 1 January to 31 March 2026: 31 + 28 + 31 = 90 days.
_WINTER = _spell(date(2026, 1, 1), date(2026, 3, 31))
#: 1 June to 31 December 2026: 30 + 31 + 31 + 30 + 31 + 30 + 31 = 214 days.
_REHIRE = _spell(date(2026, 6, 1), date(2026, 12, 31))


class TestEmploymentSpell:
    """A spell is the part of one employment within one year."""

    @pytest.mark.parametrize(
        ("period", "expected"),
        [
            (None, _spell(date(2026, 1, 1), date(2026, 12, 31))),
            (
                EmploymentPeriod(date(2020, 5, 1)),
                _spell(date(2026, 1, 1), date(2026, 12, 31)),
            ),
            (
                EmploymentPeriod(date(2026, 6, 1), date(2027, 2, 1)),
                _spell(date(2026, 6, 1), date(2026, 12, 31)),
            ),
            (EmploymentPeriod(date(2026, 1, 1), date(2026, 3, 31)), _WINTER),
        ],
        ids=["start unknown", "begun earlier", "ends later", "within the year"],
    )
    def test_of_clips_the_period_to_the_year(
        self, period: EmploymentPeriod | None, expected: EmploymentSpell
    ) -> None:
        """Unknown start or end take the bounds of the year."""
        assert EmploymentSpell.of(period, 2026, fixed_term=False) == expected

    @pytest.mark.parametrize(
        "period",
        [
            EmploymentPeriod(date(2025, 1, 1), date(2025, 12, 31)),
            EmploymentPeriod(date(2027, 1, 1)),
        ],
        ids=["ended before", "starts after"],
    )
    def test_of_a_period_outside_the_year_is_none(
        self, period: EmploymentPeriod
    ) -> None:
        """An employment with no day in the year has no spell."""
        assert EmploymentSpell.of(period, 2026, fixed_term=True) is None

    def test_of_keeps_the_contract(self) -> None:
        """The spell records whether the employment is fixed-term."""
        spell = EmploymentSpell.of(None, 2026, fixed_term=True)

        assert spell is not None
        assert spell.fixed_term

    @pytest.mark.parametrize(
        ("first", "last"),
        [
            (date(2026, 3, 1), date(2026, 2, 28)),
            (date(2026, 12, 1), date(2027, 1, 31)),
        ],
        ids=["last before first", "two years"],
    )
    def test_rejects_days_out_of_one_year(self, first: date, last: date) -> None:
        """A spell runs within one year, first day first."""
        with pytest.raises(InvalidInputError, match="within one year"):
            _spell(first, last)

    @pytest.mark.parametrize(
        ("first", "last", "fixed_term"),
        [
            ("2026-01-01", date(2026, 3, 31), False),
            (date(2026, 1, 1), None, False),
            (date(2026, 1, 1), date(2026, 3, 31), 1),
        ],
        ids=["first", "last", "fixed_term"],
    )
    def test_rejects_fields_of_another_type(
        self, first: object, last: object, fixed_term: object
    ) -> None:
        """Days are dates and the contract a bool."""
        with pytest.raises(InvalidInputError):
            EmploymentSpell(first, last, fixed_term)  # type: ignore[arg-type]


class TestSpellsWith:
    """The run's spell joins the spells the state paid in the year."""

    def test_a_rehire_adds_its_spell(self) -> None:
        """A different first day is another employment, kept in order."""
        assert spells_with((_REHIRE,), _WINTER) == (_WINTER, _REHIRE)

    def test_the_same_employment_replaces_its_spell(self) -> None:
        """January open to 31 December, then March with the end stated."""
        open_ended = _spell(date(2026, 1, 1), date(2026, 12, 31))

        assert spells_with((open_ended,), _WINTER) == (_WINTER,)

    def test_no_spell_keeps_the_spells(self) -> None:
        """A run with no day in the year adds nothing."""
        assert spells_with((_WINTER,), None) == (_WINTER,)


class TestSpellDays:
    """The union of the spells, at most 365 days."""

    @pytest.mark.parametrize(
        ("spells", "days"),
        [
            ((), 0),
            ((_WINTER,), 90),
            ((_WINTER, _REHIRE), 90 + 214),
            # 1 March to 30 April overlaps 1 to 31 March: 31 + 30 days in
            # March and April, plus 31 + 28 in January and February.
            ((_WINTER, _spell(date(2026, 3, 1), date(2026, 4, 30))), 31 + 28 + 31 + 30),
            # 1 to 15 February lies within _WINTER.
            ((_WINTER, _spell(date(2026, 2, 1), date(2026, 2, 15))), 90),
            ((_spell(date(2028, 1, 1), date(2028, 12, 31)),), 365),
        ],
        ids=["none", "one", "disjoint", "overlapping", "contained", "leap year"],
    )
    def test_counts_contemporaneous_days_once(
        self, spells: tuple[EmploymentSpell, ...], days: int
    ) -> None:
        """Days in two spells count once; a leap year counts 365."""
        assert spell_days(spells) == days


class TestSpellsOf:
    """The spells a tax cash state holds."""

    def test_accepts_spells_of_the_year_in_order(self) -> None:
        """A list is accepted and stored as a tuple."""
        assert spells_of([_WINTER, _REHIRE], _PATH, 2026) == (_WINTER, _REHIRE)

    @pytest.mark.parametrize(
        ("spells", "tax_year", "match"),
        [
            ((_REHIRE, _WINTER), 2026, "in order"),
            ((_WINTER, _WINTER), 2026, "distinct first days"),
            ((_WINTER,), 2027, "tax year 2027"),
            ((_WINTER,), None, "tax year None"),
        ],
        ids=["out of order", "repeated", "another year", "unbound state"],
    )
    def test_rejects_spells_not_of_the_year_in_order(
        self, spells: tuple[EmploymentSpell, ...], tax_year: int | None, match: str
    ) -> None:
        """Spells are of the tax year, by distinct first day."""
        with pytest.raises(InvalidInputError, match=match) as info:
            spells_of(spells, _PATH, tax_year)

        assert info.value.field == _PATH

    def test_rejects_an_item_that_is_not_a_spell(self) -> None:
        """Each item is an EmploymentSpell."""
        with pytest.raises(InvalidInputError):
            spells_of(("2026-01-01",), _PATH, 2026)


class TestUnpaidDays:
    """Days without any pay leave the count (AdE circ. 15/E/2007 par. 1.5.1)."""

    def test_unpaid_days_leave_the_count(self) -> None:
        """January 2026, 31 days, less 12 and 13 January: 29."""
        spell = _spell(date(2026, 1, 1), date(2026, 1, 31)).with_unpaid([
            date(2026, 1, 13),
            date(2026, 1, 12),
            date(2026, 2, 2),
        ])
        assert spell.unpaid_days == (date(2026, 1, 12), date(2026, 1, 13))
        assert spell_days((spell,)) == 29

    def test_a_day_another_spell_pays_still_counts(self) -> None:
        """12 January unpaid in one spell, paid by a concurrent one: 31."""
        unpaid = _spell(date(2026, 1, 1), date(2026, 1, 31)).with_unpaid([
            date(2026, 1, 12)
        ])
        other = _spell(date(2026, 1, 10), date(2026, 1, 20))
        assert spell_days((unpaid, other)) == 31

    @pytest.mark.parametrize(
        "days",
        [
            (date(2026, 1, 13), date(2026, 1, 12)),
            (date(2026, 1, 12), date(2026, 1, 12)),
            (date(2026, 2, 1),),
        ],
        ids=["unordered", "repeated", "outside"],
    )
    def test_invalid_unpaid_days_raise(self, days: tuple[date, ...]) -> None:
        """Unpaid days are distinct days of the spell, in order."""
        with pytest.raises(InvalidInputError) as caught:
            EmploymentSpell(date(2026, 1, 1), date(2026, 1, 31), False, days)
        assert caught.value.field == "EmploymentSpell.unpaid_days"
