"""Metamorphic properties of the events of a run, on every production CCNL.

Each test compares runs whose relation is known without computing either:

- the same event split in two, or two equal events merged, post the same
  ledger;
- independent events in any order post the same ledger;
- more of an event never lowers the gross, the taxable or the employer
  cost of the run (the rules are monotone there: no threshold of the bases
  is reached by the amounts used).

The worker is an impiegato of the middle level hired on 1 January 2026,
with a 2025 income above the 33,000 EUR of the renewal regime, so no credit
threshold moves with the amounts.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from itertools import pairwise, permutations
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import BonusEvent, FringeEvent, OvertimeEvent
from ccnl_engine.inputs import EmploymentPeriod, Permanent, PriorYearTaxFacts
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.events import WorkEvent

pytestmark = pytest.mark.legal_scenario

_D = Decimal
_ENGINE = PayrollEngine.bundled()
#: Middle level of each production CCNL.
_PRODUCTION = {
    "commercio-confcommercio": "4",
    "metalmeccanico-federmeccanica": "C3",
    "edilizia-ance-impiegati": "4",
    "pubblici-esercizi-fipe-angem-ristorazione-collettiva": "4",
}
_CCNLS = sorted(_PRODUCTION)
_DAY = date(2026, 3, 10)
#: Stated, so that the CCNLs without a verified hourly base run it too.
_RATE = _D("12.00")


def _march(ccnl: str, events: tuple[WorkEvent, ...] = ()) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id=ccnl,
                level_code=_PRODUCTION[ccnl],
                seniority=new_hire(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005", events=events),
            prior_year=PriorYearTaxFacts(employment_income=_D(40000)),
        )
    )


def _ledger(result: PeriodResult) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for entry in result.ledger_entries:
        key = entry.account.value
        totals[key] = totals.get(key, _D(0)) + entry.amount
    return totals


def _overtime(hours: str) -> OvertimeEvent:
    return OvertimeEvent(_DAY, _D(hours), _RATE)


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_a_bonus_split_in_two_posts_what_it_posts_whole(ccnl: str) -> None:
    """300 EUR of bonus, or 100 and 200 on the same day: the same ledger."""
    whole = _march(ccnl, (BonusEvent(_DAY, _D(300)),))
    split = _march(ccnl, (BonusEvent(_DAY, _D(100)), BonusEvent(_DAY, _D(200))))

    assert _ledger(split) == _ledger(whole)
    assert (split.period_gross, split.period_net) == (
        whole.period_gross,
        whole.period_net,
    )


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_overtime_split_in_two_posts_what_it_posts_whole(ccnl: str) -> None:
    """Six hours, or two and four on the same day at the same rate."""
    whole = _march(ccnl, (_overtime("6"),))
    split = _march(ccnl, (_overtime("2"), _overtime("4")))

    assert _ledger(split) == _ledger(whole)


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_independent_events_post_the_same_ledger_in_any_order(ccnl: str) -> None:
    """Overtime, a bonus and a fringe benefit, in each of their six orders."""
    events: tuple[WorkEvent, ...] = (
        _overtime("4"),
        BonusEvent(_DAY, _D(150)),
        FringeEvent(_DAY, _D(80)),
    )
    ledgers = [_ledger(_march(ccnl, order)) for order in permutations(events)]

    assert all(ledger == ledgers[0] for ledger in ledgers)


def _axes(result: PeriodResult) -> tuple[Decimal, Decimal, Decimal]:
    return (
        result.period_gross,
        result.closing_state.cash.earnings.taxable,
        result.period_employer_cost,
    )


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_a_larger_bonus_never_lowers_the_gross_taxable_or_cost(ccnl: str) -> None:
    """0, 100, 200 and 400 EUR: each axis grows or stays."""
    runs = [
        _axes(_march(ccnl, (BonusEvent(_DAY, _D(a)),) if a else ()))
        for a in (0, 100, 200, 400)
    ]

    for low, high in pairwise(runs):
        assert all(h >= lo for lo, h in zip(low, high, strict=True)), (low, high)
        assert high[0] > low[0]


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_more_overtime_never_lowers_the_gross_taxable_or_cost(ccnl: str) -> None:
    """0, 2, 4 and 8 hours: each axis grows or stays."""
    runs = [
        _axes(_march(ccnl, (_overtime(str(h)),) if h else ())) for h in (0, 2, 4, 8)
    ]

    for low, high in pairwise(runs):
        assert all(h >= lo for lo, h in zip(low, high, strict=True)), (low, high)
        assert high[0] > low[0]


def test_the_events_reach_the_run() -> None:
    """The properties above would hold vacuously if no event were paid."""
    plain = _march(_CCNLS[0])
    paid = _march(_CCNLS[0], (_overtime("4"), BonusEvent(_DAY, _D(150))))

    assert paid.period_gross > plain.period_gross
