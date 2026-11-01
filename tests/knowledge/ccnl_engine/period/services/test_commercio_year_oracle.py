"""A Commercio year by hand: partial month, promotion, threshold, deferred pay.

Commercio Confcommercio level 5, hired on Tuesday 10 March 2026, promoted to
level 4 on Thursday 16 July, the December pay paid on 12 January 2027.
Every expected amount is computed here from the CCNL tables, not read
from the engine:

- paga base 1,136.07 (level 5) and 1,257.46 (level 4, 1,292.46 from the
  tranche of 1 November 2026), contingenza/EDR 521.94 and 524.22, terzo
  elemento 2.07 (Art. 212, Art. 215);
- a partial month pays the twenty-sixths of its Mondays to Saturdays
  (Art. 210): 10-31 March 2026 holds 19 of them;
- July is split 13/27 and 14/27 between the two levels, as a promotion
  inside a month is (``compensation.change``);
- a month counts for the extra months with at least 15 days of service
  (Artt. 220-221): March from the 10th (22 days) counts, from the 18th (14
  days) it does not;
- the quattordicesima of June pays its months at level 5, the tredicesima
  of December at level 4 with the November tranche, each component
  rounded apart;
- the TFR of a run is its pay over 13.5 less 0.50% of the whole-euro INPS
  base (art. 2120 c.c.; L. 297/1982 art. 3 c. 16);
- pay of December paid by 12 January belongs to the tax year 2026 (art. 51
  c. 1 TUIR).
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import PayrollEngine
from ccnl_engine.inputs import (
    EmploymentChange,
    EmploymentPeriod,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.run.models import RunKind
from tests.unit.ccnl_engine.builders import year_plan

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

type Runs = dict[tuple[int, RunKind], PeriodResult]

_CENT = Decimal("0.01")
_LEVEL_5 = (Decimal("1136.07"), Decimal("521.94"), Decimal("2.07"))
_LEVEL_4 = (Decimal("1257.46"), Decimal("524.22"), Decimal("2.07"))
_LEVEL_4_NOVEMBER = (Decimal("1292.46"), Decimal("524.22"), Decimal("2.07"))


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def _share(chain: tuple[Decimal, ...], units: int, of: int) -> tuple[Decimal, ...]:
    return tuple(_money(c * units / of) for c in chain)


def _tfr(gross: Decimal) -> Decimal:
    base = gross.quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return _money(gross / Decimal("13.5")) - _money(base * Decimal("0.005"))


def _year(hired: date) -> Runs:
    plan = year_plan(
        2026,
        "commercio-confcommercio",
        "5",
        seniority=SeniorityFact(0, hired, SenioritySource.PAYSLIP),
        employment_period=EmploymentPeriod(hired),
        roles=frozenset(),
    )
    plan = replace(
        plan,
        employment_changes=(EmploymentChange(date(2026, 7, 16), level_code="4"),),
        payment_dates={12: date(2027, 1, 12)},
    )
    year = PayrollEngine.bundled().calculate_competence_year(plan)
    return {(r.run.month, r.run.run_kind): r for r in year.period_results if r.run}


def _components(result: PeriodResult) -> tuple[Decimal, ...]:
    items = {i.item_id: i.amount for i in result.pay_items}

    def one(part: str) -> Decimal:
        (amount,) = (v for k, v in items.items() if part in k)
        return amount

    return (one("base_salary_"), one("CONTINGENZA_EDR_"), one("TERZO_ELEMENTO_"))


@pytest.fixture(scope="module")
def runs() -> Runs:
    """Return the runs of a hire on Tuesday 10 March 2026.

    Returns:
        The runs by month and kind.
    """
    return _year(date(2026, 3, 10))


def test_the_hire_month_pays_its_twenty_sixths(runs: Runs) -> None:
    """19 of 26: 830.21 + 381.42 + 1.51, TFR 83.79."""
    march = runs[3, RunKind.REGULAR]
    expected = _share(_LEVEL_5, 19, 26)

    assert expected == (Decimal("830.21"), Decimal("381.42"), Decimal("1.51"))
    assert _components(march) == expected
    tfr = sum(
        (e.amount for e in march.ledger_entries if e.account.value == "tfr_accrual"),
        Decimal(0),
    )
    assert tfr == _tfr(sum(expected, Decimal(0))) == Decimal("83.79")


def test_the_month_of_the_promotion_pays_each_level_for_its_days(runs: Runs) -> None:
    """13/27 of level 5 and 14/27 of level 4, each component apart."""
    expected = tuple(
        a + b
        for a, b in zip(_share(_LEVEL_5, 13, 27), _share(_LEVEL_4, 14, 27), strict=True)
    )
    assert _components(runs[7, RunKind.REGULAR]) == expected
    assert _components(runs[8, RunKind.REGULAR]) == _LEVEL_4
    assert _components(runs[11, RunKind.REGULAR]) == _LEVEL_4_NOVEMBER


def test_the_extra_months_count_march_and_pay_their_day_level(runs: Runs) -> None:
    """The 14th: 4/12 at level 5; the 13th: 10/12 at level 4 of November."""
    assert _components(runs[6, RunKind.FOURTEENTH]) == _share(_LEVEL_5, 4, 12)
    assert _components(runs[12, RunKind.THIRTEENTH]) == _share(
        _LEVEL_4_NOVEMBER, 10, 12
    )


def test_fourteen_days_of_march_are_no_month() -> None:
    """Hired on Wednesday 18 March: the 14th 3/12 and the 13th 9/12."""
    late = _year(date(2026, 3, 18))
    assert _components(late[6, RunKind.FOURTEENTH]) == _share(_LEVEL_5, 3, 12)
    assert _components(late[12, RunKind.THIRTEENTH]) == _share(_LEVEL_4_NOVEMBER, 9, 12)


def test_december_paid_on_12_january_belongs_to_2026(runs: Runs) -> None:
    """Art. 51 c. 1 TUIR: the tax year of the December pay is 2026."""
    december = runs[12, RunKind.REGULAR]
    assert december.payment_date == date(2027, 1, 12)
    assert december.closing_state.cash.tax_year == 2026


def test_the_tfr_of_the_year_is_the_sum_of_its_runs(runs: Runs) -> None:
    """The quota of 2026 the last run closes with: each run by hand."""
    expected = sum(
        (_tfr(sum(_components(r), Decimal(0))) for r in runs.values()), Decimal(0)
    )
    last = runs[12, RunKind.REGULAR].closing_state.accrual.tfr_quotas
    assert [(q.year, q.amount) for q in last] == [(2026, expected)]
