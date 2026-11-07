"""The base of a leave reads the monthly payments of the month before."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from ccnl_engine.absence.insured.base.rules import _payments_before
from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.services import InsuredTerms


def _terms(series: TimeSeries | None) -> InsuredTerms:
    return cast("InsuredTerms", SimpleNamespace(monthly_payments=series))


def test_the_payments_are_those_of_the_last_day_of_the_month_before() -> None:
    """A change on 28 February counts for a leave from 1 March, one after not."""
    series = TimeSeries(
        periods=(
            ValidityPeriod(
                valid_from=date(2026, 1, 1),
                valid_until=date(2026, 2, 28),
                value=Decimal(13),
            ),
            ValidityPeriod(
                valid_from=date(2026, 2, 28),
                valid_until=date(2026, 3, 1),
                value=Decimal(14),
            ),
            ValidityPeriod(
                valid_from=date(2026, 3, 1), valid_until=None, value=Decimal(15)
            ),
        )
    )

    assert _payments_before(_terms(series), date(2026, 3, 1)) == Decimal(14)
    assert _payments_before(_terms(series), date(2026, 3, 31)) == Decimal(14)


def test_without_payments_before_the_series_none_is_known() -> None:
    """No series, or a leave before it starts, has no payments."""
    series = TimeSeries(
        periods=(
            ValidityPeriod(
                valid_from=date(2026, 3, 1), valid_until=None, value=Decimal(13)
            ),
        )
    )

    assert _payments_before(_terms(None), date(2026, 3, 1)) is None
    assert _payments_before(_terms(series), date(2026, 3, 1)) is None
