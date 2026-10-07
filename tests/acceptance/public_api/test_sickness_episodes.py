"""A sickness episode over two months: the same pay however it is computed.

Episode of a metalmeccanico C3 operaio from Friday 20 February to Friday 13
March 2026.  The March run pays days 10 to 22 of the episode; it gives the
same sickness amounts when the whole competence year is computed, when the
runs are chained by hand, and when March resumes from opening balances
imported from another provider (INPS 484.22, employer 428.89, deduction
913.11: see the integration tests of the handler for the hand computation).

Sick days that cover a whole month suspend its whole pay (art. 2110 c.c.):
the run deducts that pay, rounded once, however many episodes or INPS
bands the month holds.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import OpeningBalances, PeriodState, WorkerCategory
from tests.fixtures.sickness_episode import metalmeccanico_c3, sickness_episode
from tests.fixtures.withholding import paid_before

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_EMPLOYMENT = metalmeccanico_c3(WorkerCategory.OPERAIO)
_EPISODE = sickness_episode("2026-02-20", date(2026, 2, 20), date(2026, 3, 13))
_FACTS = PeriodFacts(events=(_EPISODE,))
_MARCH = {
    "sickness_inps_item": Decimal("484.22"),
    "sickness_item": Decimal("428.89"),
    "absence_deduction": Decimal("913.11"),
}


def _base_salary(result: PeriodResult) -> Decimal:
    (item,) = (i for i in result.pay_items if i.kind == "base_salary_earning")
    return item.amount


def _sickness(result: PeriodResult) -> dict[str, Decimal]:
    return {i.kind: i.amount for i in result.pay_items if "_evt" in i.item_id}


def _run(month: int, opening: PeriodState | None = None) -> PeriodResult:
    period = PeriodInput(
        run=PayrollRun.regular(2026, month),
        payment_date=date(2026, month, 27),
        employment=_EMPLOYMENT,
        employer=_EMPLOYER,
        facts=_FACTS,
    )
    return _ENGINE.calculate_period(
        period if opening is None else replace(period, opening_state=opening)
    )


def test_competence_year_matches_chained_runs() -> None:
    """The year and the chained runs pay March the same."""
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
            periods={2: _FACTS, 3: _FACTS},
            payment_day=27,
        )
    )
    january = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 27),
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
        )
    )
    february = _run(2, january.closing_state)
    march = _run(3, february.closing_state)
    in_year = next(
        r for r in year.period_results if r.run == PayrollRun.regular(2026, 3)
    )
    assert _sickness(in_year) == _sickness(march) == _MARCH


def test_resume_from_opening_balances_matches() -> None:
    """Imported balances that carry the episode up to 28 February."""
    opening = _ENGINE.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            payments=paid_before(PayrollRun.regular(2026, 3)),
            sickness_episodes=(_EPISODE.through(date(2026, 2, 28)),),
        )
    )
    assert _sickness(_run(3, opening)) == _MARCH


def test_month_past_the_inps_cap_deducts_the_month_pay() -> None:
    """Sick 5 January to 31 May, then 3 August to 30 September 2026.

    INPS stops indemnifying within September: the month holds a band at
    66.66% and one at 0%, each deducted with the daily quota by 26.
    """
    first = PeriodFacts(
        events=(sickness_episode("A", date(2026, 1, 5), date(2026, 5, 31)),)
    )
    second = PeriodFacts(
        events=(sickness_episode("C", date(2026, 8, 3), date(2026, 9, 30)),)
    )
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
            periods={1: first, 2: first, 3: first, 4: first, 5: first}
            | {8: second, 9: second},
            payment_day=27,
        )
    )
    september = next(
        r for r in year.period_results if r.run == PayrollRun.regular(2026, 9)
    )
    (decision,) = (d for d in september.decisions if d.capability == "sickness")
    assert ":inps=0.6666:" in str(decision.inputs["segments"])
    assert ":inps=0:" in str(decision.inputs["segments"])
    assert september.unpaid_absence_deduction == _base_salary(september)


def test_two_episodes_of_a_whole_month_deduct_the_month_pay() -> None:
    """Sick 1 to 15 July 2026, then again 16 to 31 July.

    Each episode counts its days by 26 from its own first day: 13 and 14
    of the 27 working days of July, one more than a monthly pay.
    """
    facts = PeriodFacts(
        events=(
            sickness_episode("J1", date(2026, 7, 1), date(2026, 7, 15)),
            sickness_episode("J2", date(2026, 7, 16), date(2026, 7, 31)),
        )
    )
    july = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 7),
            payment_date=date(2026, 7, 27),
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
            facts=facts,
        )
    )
    assert july.unpaid_absence_deduction == _base_salary(july)
