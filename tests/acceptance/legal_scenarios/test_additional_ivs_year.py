"""The additional 1% IVS over a year: monthly charge and conguaglio.

D.L. 384/1992 art. 3-ter, as INPS applies it:

- circ. 6/2026 par. 5: the band of 2026 is 56,224.00, "rapportato a dodici
  mesi" 4,685.00, and "deve essere osservato il criterio della
  mensilizzazione";
- circ. 7/2010 par. 3 and msg. 5327/2015 par. 2.1: each month the 1% is due
  on the pay of the month above 4,685.00, "senza tenere conto del
  superamento del tetto minimo su base annua";
- msg. 5327/2015 par. 2.3 and circ. 156/2025 par. 5: the conguaglio settles
  the 1% of the year at year end or "con la denuncia relativa al mese nel
  corso del quale è cessato il rapporto di lavoro", credit or debit.

Metalmeccanico C3 at an industrial employer of 50, every other fact explicit
(:mod:`tests.fixtures.explicit_facts`).  The C3 minimum from June 2026 is
2,211.43 (``tests.fixtures.normative_oracles.payslips.metalmeccanico_c3_2026``).
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.events import BonusEvent
from ccnl_engine.inputs import EmploymentPeriod
from tests.acceptance.legal_scenarios._support import ENGINE
from tests.fixtures.explicit_facts import CONCIA_D2, FACTS, competence_year

if TYPE_CHECKING:
    from ccnl_engine import CompetenceYearResult, PeriodFacts, PeriodResult

pytestmark = pytest.mark.legal_scenario

_ZERO = Decimal(0)
_CENT = Decimal("0.01")
_MONTHLY = "addizionale_1pct"
_SETTLEMENT = "addizionale_1pct_conguaglio"
_MONTHLY_THRESHOLD = Decimal("4685.00")
_ANNUAL_THRESHOLD = Decimal("56224.00")


def _bonus(month: int, amount: Decimal) -> PeriodFacts:
    return replace(FACTS, events=(BonusEvent(date(2026, month, 15), amount),))


def _year(
    started_on: date,
    periods: dict[int, PeriodFacts],
    ended_on: date | None = None,
) -> CompetenceYearResult:
    return ENGINE.calculate_competence_year(
        competence_year(
            employment=replace(
                CONCIA_D2,
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                employment_period=EmploymentPeriod(started_on, ended_on),
            ),
            periods=periods,
        )
    )


def _component(result: PeriodResult, name: str) -> Decimal:
    return sum(
        (c.amount for c in result.contribution_breakdown.components if c.name == name),
        _ZERO,
    )


def _additional(result: PeriodResult) -> Decimal:
    return _component(result, _MONTHLY) + _component(result, _SETTLEMENT)


def _inps_base(result: PeriodResult) -> Decimal:
    (decision,) = (d for d in result.decisions if d.capability == "inps_employee")
    base = decision.inputs["base"]
    assert isinstance(base, Decimal)
    return base


def test_december_gives_back_the_1pct_of_a_bonus_month() -> None:
    """Hired 1 June, 10,000 bonus in June: the year stays below the band.

    June: 2,211.43 + 10,000 = 12,211.43; 12,211.43 - 4,685 = 7,526.43,
    x 1% = 75.2643 -> 75.26.  July to November pay 2,211.43, below
    4,685: nothing.  The year is at most 7 x 2,211.43 + 10,000 + a full
    tredicesima of 2,211.43 = 27,691.44, below 56,224: nothing is due, and
    December gives back the 75.26.
    """
    year = _year(date(2026, 6, 1), {6: _bonus(6, Decimal(10_000))})
    runs = year.period_results
    june = next(r for r in runs if r.period_id.month == 6)
    december = [r for r in runs if r.period_id.month == 12]

    assert _component(june, _MONTHLY) == Decimal("75.26")
    assert all(_additional(r) == _ZERO for r in runs if 6 < r.period_id.month < 12)
    assert sum((_component(r, _SETTLEMENT) for r in december), _ZERO) == Decimal(
        "-75.26"
    )
    assert sum((_additional(r) for r in runs), _ZERO) == _ZERO


def test_december_charges_a_year_above_the_band_paid_below_the_month() -> None:
    """Full year, a 2,450 bonus every month: each month stays below 4,685.

    No month pays more than 2,211.43 + 2,450 = 4,661.43 (the C3 minimum
    rises to 2,211.43 in June and is lower before), so no month charges the
    1%.  The year, read from the INPS bases of the runs, ends above 56,224
    with the tredicesima; the December runs charge 1% of the excess, the
    whole 1% of the year (msg. 5327/2015 par. 2.3).
    """
    periods = {m: _bonus(m, Decimal(2450)) for m in range(1, 13)}
    year = _year(date(2026, 1, 1), periods)
    runs = year.period_results
    year_base = sum((_inps_base(r) for r in runs), _ZERO)
    due = ((year_base - _ANNUAL_THRESHOLD) * Decimal("0.01")).quantize(
        _CENT, rounding=ROUND_HALF_UP
    )

    assert all(
        _inps_base(r) < _MONTHLY_THRESHOLD for r in runs if r.period_id.month < 12
    )
    assert all(_additional(r) == _ZERO for r in runs if r.period_id.month < 12)
    assert year_base > _ANNUAL_THRESHOLD
    assert sum((_additional(r) for r in runs), _ZERO) == due
    assert due > _ZERO


def test_the_month_of_termination_settles_the_year() -> None:
    """Hired 1 June, 10,000 bonus in June, employment ends 30 September.

    June charges 75.26 (as above); the year, at most 4 x 2,211.43 +
    10,000 + ratei, is far below 56,224, so the runs of September, the
    month the employment ends, give the 75.26 back and nothing is left to
    settle in the year.
    """
    year = _year(
        date(2026, 6, 1),
        {6: _bonus(6, Decimal(10_000))},
        ended_on=date(2026, 9, 30),
    )
    runs = year.period_results
    september = [r for r in runs if r.period_id.month == 9]

    assert sum((_component(r, _SETTLEMENT) for r in september), _ZERO) == Decimal(
        "-75.26"
    )
    assert sum((_additional(r) for r in runs), _ZERO) == _ZERO
