"""The dates on which a series, a set of series or a model has a value."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from ccnl_engine.contract.identity.models_validity_window import (
    ValidityWindow,
    model_window,
    rules_window,
    series_window,
)
from ccnl_engine.contract.identity.rules_validity import (
    SalaryGapKind,
    TimeSeries,
    ValidityPeriod,
)

_JAN = date(2026, 1, 1)
_MAR = date(2026, 3, 1)
_JUL = date(2026, 7, 1)


def _value(start: date, end: date | None) -> ValidityPeriod:
    return ValidityPeriod(valid_from=start, valid_until=end, value=Decimal(1))


def _gap(start: date, end: date | None, kind: SalaryGapKind) -> ValidityPeriod:
    return ValidityPeriod(valid_from=start, valid_until=end, gap_kind=kind)


def _series(*periods: ValidityPeriod) -> TimeSeries:
    return TimeSeries(periods=periods)


class TestValidityWindow:
    """A span of dates, both ends included."""

    def test_covers_both_ends(self) -> None:
        """The first and the last day are inside, the days around are not."""
        window = ValidityWindow(_JAN, date(2026, 2, 28))

        assert window.covers(_JAN)
        assert window.covers(date(2026, 2, 28))
        assert not window.covers(date(2025, 12, 31))
        assert not window.covers(_MAR)

    def test_an_open_window_covers_every_later_day(self) -> None:
        """No last day: open-ended."""
        assert ValidityWindow(_JAN).covers(date(2099, 12, 31))

    def test_intersection_takes_the_later_start_and_earlier_end(self) -> None:
        """Two overlapping spans share their middle."""
        left = ValidityWindow(_JAN, date(2026, 6, 30))
        right = ValidityWindow(_MAR)

        assert left.intersect(right) == ValidityWindow(_MAR, date(2026, 6, 30))
        assert right.intersect(ValidityWindow(_JAN)) == ValidityWindow(_MAR)

    def test_disjoint_spans_have_no_intersection(self) -> None:
        """A span that ends before the other starts shares nothing."""
        assert (
            ValidityWindow(_JAN, date(2026, 2, 28)).intersect(ValidityWindow(_MAR))
            is None
        )


class TestSeriesWindow:
    """The last span of a series with a value or not in force."""

    def test_a_series_is_covered_from_its_first_period(self) -> None:
        """Before the first period a run has no value."""
        series = _series(_value(_MAR, _JUL), _value(_JUL, None))

        assert series_window(series) == ValidityWindow(_MAR)

    def test_a_missing_gap_at_the_start_moves_the_first_day(self) -> None:
        """A declared missing gap is not covered."""
        series = _series(_gap(_JAN, _JUL, SalaryGapKind.MISSING), _value(_JUL, None))

        assert series_window(series) == ValidityWindow(_JUL)

    def test_a_not_applicable_gap_is_covered(self) -> None:
        """A rule not in force is not read, so it is not a hole."""
        series = _series(
            _gap(_JAN, _MAR, SalaryGapKind.NOT_APPLICABLE), _value(_MAR, None)
        )

        assert series_window(series) == ValidityWindow(_JAN)

    def test_the_last_span_after_a_hole_wins(self) -> None:
        """An unknown gap between two values ends the first span."""
        series = _series(
            _value(_JAN, _MAR),
            _gap(_MAR, _JUL, SalaryGapKind.UNKNOWN),
            _value(_JUL, None),
        )

        assert series_window(series) == ValidityWindow(_JUL)

    def test_a_trailing_gap_closes_the_window(self) -> None:
        """Values until a missing gap open to further notice."""
        series = _series(_value(_JAN, _JUL), _gap(_JUL, None, SalaryGapKind.MISSING))

        assert series_window(series) == ValidityWindow(_JAN, date(2026, 6, 30))

    def test_a_series_of_gaps_has_no_window(self) -> None:
        """No date carries a value."""
        series = _series(_gap(_JAN, None, SalaryGapKind.MISSING))

        assert series_window(series) is None


class TestRulesWindow:
    """The dates every series of a set covers."""

    def test_the_latest_start_bounds_the_set(self) -> None:
        """The window starts when the last series starts."""
        rules = (_series(_value(_JAN, None)), _series(_value(_MAR, None)))

        assert rules_window(rules) == ValidityWindow(_MAR)

    def test_no_rule_covers_every_date(self) -> None:
        """An empty set constrains nothing."""
        assert rules_window(()) == ValidityWindow(date.min)

    def test_a_series_without_window_empties_the_set(self) -> None:
        """One series never covered: no date covers every rule."""
        rules = (
            _series(_gap(_JAN, None, SalaryGapKind.MISSING)),
            _series(_value(_JAN, None)),
        )

        assert rules_window(rules) is None

    def test_disjoint_series_have_no_window(self) -> None:
        """Once the set is empty the other series are not read."""
        rules = (
            _series(_value(_JAN, _MAR), _gap(_MAR, None, SalaryGapKind.MISSING)),
            _series(_value(_JUL, None)),
            _series(_value(_JAN, None)),
        )

        assert rules_window(rules) is None


class _Leaf(BaseModel):
    model_config = ConfigDict(frozen=True)

    series: TimeSeries
    label: str


class _Tree(BaseModel):
    model_config = ConfigDict(frozen=True)

    by_level: dict[str, TimeSeries]
    leaves: tuple[_Leaf, ...]
    extra: list[TimeSeries]
    note: str | None = None


def test_every_series_of_a_model_is_read() -> None:
    """Series in fields, mappings, tuples and lists all bound the window."""
    tree = _Tree(
        by_level={"A": _series(_value(_JAN, None))},
        leaves=(_Leaf(series=_series(_value(_MAR, None)), label="x"),),
        extra=[_series(_value(_JUL, None))],
    )

    assert model_window(tree) == ValidityWindow(_JUL)
