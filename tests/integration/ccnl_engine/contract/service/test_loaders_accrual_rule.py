"""The bundled accrual rules quote the signed clause they are read from.

A CCNL stores ``parameters.accrual_rule`` only with the verbatim clause of
the signed text: the quote must state the threshold in days and the
comparison the rule encodes ("superiore a 15 giorni" is ``more_than``;
"pari o superiore", "superiore o uguale", "non inferiore" or "almeno" is
``at_least``).
"""

from __future__ import annotations

import importlib.resources
import re

import pytest

from ccnl_engine.contract.domain.compensation import AccrualComparison
from ccnl_engine.contract.service.loaders import load_ccnl

_FILES = sorted(
    entry.name
    for entry in importlib.resources
    .files("ccnl_engine.knowledge")
    .joinpath("contract", "agreement")
    .iterdir()
    if entry.name.endswith(".json")
)
_WITH_RULE = [name for name in _FILES if load_ccnl(name).parameters.accrual_rule]
_AT_LEAST = re.compile(
    r"pari o superior|uguale o superior|superior[ei] o ugual|non inferior|almeno",
    re.IGNORECASE,
)
_MORE_THAN = re.compile(r"superior[ei]\s+a|superino", re.IGNORECASE)
_NUMBERS = {15: r"(15|quindici)"}


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
    days = _NUMBERS.get(rule.min_days, str(rule.min_days))
    assert re.search(rf"\b{days}\)?\s+giorni", quote, re.IGNORECASE), quote
    if rule.comparison is AccrualComparison.AT_LEAST:
        assert _AT_LEAST.search(quote), quote
    else:
        assert _MORE_THAN.search(quote), quote
        assert not _AT_LEAST.search(quote), quote
