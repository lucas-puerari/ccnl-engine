"""An allowance that enters the TFR base from a date.

Alimentari Federalimentare art. 73: the EDR counts for the TFR only from
1 March 2024; the months before pay it outside the TFR base.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.rules import _level_chain, allowance_in_month
from ccnl_engine.compensation.models import Allowance
from tests.unit.ccnl_engine.builders import _series

_FROM = date(2024, 3, 1)


def _edr(tfr_relevant_from: date | None = _FROM) -> Allowance:
    return Allowance(
        code="EDR",
        description="EDR",
        monthly=TimeSeries.model_validate(_series("10.33")),
        tfr_relevant_from=tfr_relevant_from,
    )


@pytest.mark.parametrize(
    ("as_of", "relevant"),
    [(date(2024, 2, 29), False), (_FROM, True), (date(2026, 6, 1), True)],
)
def test_the_month_decides_the_tfr_relevance(as_of: date, relevant: bool) -> None:
    """Before the date the month's allowance is out of the TFR base."""
    assert allowance_in_month(_edr(), as_of).tfr_relevant is relevant


def test_without_a_date_the_allowance_is_returned_as_is() -> None:
    """No date: the same object, whatever the month."""
    edr = _edr(None)

    assert allowance_in_month(edr, date(2000, 1, 1)) is edr


def test_a_date_needs_the_allowance_to_count_for_the_tfr() -> None:
    """A date on an allowance never in the TFR base is rejected."""
    never = Allowance(
        code="X",
        description="X",
        monthly=TimeSeries.model_validate(_series("1.00")),
        tfr_relevant=False,
        tfr_relevant_from=_FROM,
    )
    with pytest.raises(ValueError, match="tfr_relevant_from needs tfr_relevant"):
        allowance_in_month(never, _FROM)


@pytest.mark.parametrize(
    ("as_of", "excluded"),
    [(date(2024, 2, 1), Decimal("10.33")), (date(2024, 3, 1), Decimal("0.00"))],
)
def test_federalimentare_edr_enters_the_tfr_base_in_march_2024(
    as_of: date, excluded: Decimal
) -> None:
    """Art. 73: February 2024 keeps the EDR out of the TFR base, March not."""
    ccnl = load_ccnl("alimentari-federalimentare")
    level = ccnl.levels[0]
    chain = _level_chain(ccnl, level, 0, frozenset(), as_of, is_apprentice=False)

    assert chain.tfr_excluded_total == excluded
