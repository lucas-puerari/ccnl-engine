"""A fixed term covered by its months within the calendar year (Alimentari FASA).

Art. 74 quater (FLAI text 2024, PDF p. 157): FASA covers the permanent workers
and the fixed terms "con durata del rapporto pari o superiore a nove mesi
nell'arco dell'anno solare".
"""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.fixed_term.inputs import FixedTerm
from ccnl_engine.fund.health.rules import excluded

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

_FASA = next(
    f
    for f in load_ccnl("alimentari-federalimentare").parameters.health_funds
    if f.code == "fasa"
)


def _ctx(started: date, ended: date, competence: date) -> RunContext:
    period = SimpleNamespace(started_on=started, ended_on=ended, probation_until=None)
    request = SimpleNamespace(
        contract_type=FixedTerm(), weekly_hours=None, employment_period=period
    )
    contract = SimpleNamespace(tctx=SimpleNamespace(competence=competence))
    return SimpleNamespace(request=request, contract=contract)  # type: ignore[return-value]


@pytest.mark.parametrize(
    ("started", "ended", "competence", "left_out"),
    [
        (date(2026, 1, 1), date(2026, 10, 1), date(2026, 3, 1), False),
        (date(2026, 1, 1), date(2026, 9, 30), date(2026, 3, 1), True),
        (date(2025, 6, 1), date(2026, 5, 31), date(2026, 3, 1), True),
        (date(2025, 6, 1), date(2026, 5, 31), date(2025, 7, 1), True),
        (date(2025, 3, 1), date(2026, 5, 31), date(2025, 7, 1), False),
    ],
    ids=[
        "nine_months_in_the_year",
        "a_day_short",
        "twelve_months_split_over_two_years",
        "seven_months_in_the_first_year",
        "ten_months_in_the_first_year",
    ],
)
def test_the_months_of_the_year_decide(
    started: date, ended: date, competence: date, left_out: bool
) -> None:
    """Only the part of the fixed term within the year of the run counts.

    As for every ``minimum_fixed_term_months``, the end must come at least
    the months after the start (``ends_within``).
    """
    assert excluded(_FASA, _ctx(started, ended, competence)) is left_out
