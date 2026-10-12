"""The bundled accrual rules quote the signed clause they are read from.

A CCNL stores ``parameters.accrual_rule`` only with the verbatim clause of
the signed text: the quote must state the threshold in days and the
comparison the rule encodes ("superiore a 15 giorni" is ``more_than``;
"pari o superiore", "superiore o uguale", "raggiungono o superano", "non
inferiore" or "almeno" is ``at_least``; "l'eventuale frazione", any fraction,
is ``at_least`` 1 day).  A clause that accrues days names them instead
(twenty-sixths, 365ths, 360ths).
"""

from __future__ import annotations

import importlib.resources
import re

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.models import AccrualComparison

_FILES = sorted(
    entry.name
    for entry in importlib.resources
    .files("ccnl_engine.knowledge")
    .joinpath("agreement")
    .iterdir()
    if entry.name.endswith(".json")
)
_WITH_RULE = [name for name in _FILES if load_ccnl(name).parameters.accrual_rule]
_AT_LEAST = re.compile(
    r"pari o superior|uguale o superior|superior[ei] o ugual|raggiung\w* o super"
    r"|non inferior|almeno",
    re.IGNORECASE,
)
_MORE_THAN = re.compile(r"superior[ei]\s+a|superino", re.IGNORECASE)
#: How a clause states its threshold: in days, in weeks, or any fraction.
_THRESHOLDS = {
    1: r"eventuale frazione",
    14: r"\b(14|quattordici)\)?\s+giorni|\b2 settimane",
    15: r"\b(15|quindici)\)?\s+giorni",
}
#: The words of a clause that accrues days instead of comparing a threshold.
_DAY_BASED = {
    AccrualComparison.WORKING_DAYS_26: r"ventiseiesim|26mi",
    AccrualComparison.DAYS_365: r"trecentosessantacinquesim|365esim",
    AccrualComparison.DAYS_360: r"trecentosessantesim|360esim",
    AccrualComparison.SERVICE_DAYS_365: r"365esim|trecentosessantacinquesim",
    AccrualComparison.CUMULATED_FRACTIONS: r"frazioni di mese saranno cumulate",
}


def test_some_ccnl_carries_the_clause() -> None:
    """The bundle holds at least one sourced accrual rule."""
    assert _WITH_RULE


@pytest.mark.parametrize("name", _WITH_RULE)
def test_quote_states_threshold_and_comparison(name: str) -> None:
    """The quote names the days and the comparison of the stored rule."""
    rule = load_ccnl(name).parameters.accrual_rule
    assert rule is not None
    location = rule.provenance.location
    assert location is not None
    assert location.section
    assert location.source_document.url.startswith("http")
    quote = " ".join((location.quote or "").split())
    if rule.min_days is None:
        assert re.search(_DAY_BASED[rule.comparison], quote, re.IGNORECASE), quote
        return
    days = _THRESHOLDS.get(rule.min_days, rf"\b{rule.min_days}\)?\s+giorni")
    assert re.search(days, quote, re.IGNORECASE), quote
    if rule.comparison is AccrualComparison.AT_LEAST:
        assert _AT_LEAST.search(quote) or rule.min_days == 1, quote
    else:
        assert _MORE_THAN.search(quote), quote
        assert not _AT_LEAST.search(quote), quote
