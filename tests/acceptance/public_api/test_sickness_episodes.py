"""A sickness episode over two months: the same pay however it is computed.

Episode of a metalmeccanico C3 operaio from Friday 20 February to Friday 13
March 2026.  The March run pays days 10 to 22 of the episode; it gives the
same sickness amounts when the whole competence year is computed, when the
runs are chained by hand, and when March resumes from opening balances
imported from another provider (INPS 484.22, employer 428.89, deduction
913.11: see the integration tests of the handler for the hand computation).
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
