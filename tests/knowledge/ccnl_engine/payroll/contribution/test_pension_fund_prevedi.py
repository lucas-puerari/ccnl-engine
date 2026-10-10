"""The Prevedi contractual contribution of an impiegato of the building CCNLs.

Prevedi, Scheda 'I destinatari e i contributi' (31/07/2026), nota 1): "un
versamento mensile al Fondo Prevedi a carico del datore di lavoro, che varia
da 10 a 20 euro per ogni mese intero di lavoro [...] (applicato anche per 13°
e 14° mensilità)"; CCNL Edili-industria, impiegati: level 5 15,00, level 2
11,70.  CNCE vademecum (Comunicazione 559): owed "per intero se nel mese
abbiano lavorato per almeno 15 giorni di calendario", "riproporzionato in
relazione al ridotto orario di lavoro", "in relazione ai ratei maturati per
l'erogazione della 13° e della 14°"; the operai pay per hour of ordinary
work.  Accordo of 4 July 2025: owed only when the employment lasts more than
three months, unless the worker pays voluntary contributions.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine import CompetenceYearPlan, Employment
from ccnl_engine.events import AbsenceEvent, SicknessEpisode
from ccnl_engine.inputs import (
    Apprentice,
    ContributableHours,
    EmploymentPeriod,
    FixedTerm,
    NaspiExclusion,
    NoPensionFund,
    Permanent,
    WeeklyHours,
    WorkerCategory,
)
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire
from tests.knowledge.ccnl_engine.payroll.support import EMPLOYER, ENGINE, regular_period
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.events import WorkEvent

pytestmark = pytest.mark.legal_scenario

_EDILI = "edilizia-ance.json"
_FIXED = FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE)


def _employment(
    level: str = "5",
    category: WorkerCategory | None = WorkerCategory.IMPIEGATO,
    **fields: Any,  # noqa: ANN401
) -> Employment:
    base = Employment(
        ccnl_slug=_EDILI,
        level_code=level,
        category=category,
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
    )
    return replace(base, **fields)


def _january(employment: Employment) -> PeriodResult:
    return regular_period(employment=employment, current_year=employment_only())


def _contractual(result: PeriodResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == "pension_fund_employer"
        ),
        Decimal(0),
    )


def _codes(result: PeriodResult) -> set[str]:
    return {issue.code for issue in result.issues}


def test_impiegato_owes_the_monthly_amount() -> None:
    """Level 5 impiegato, not enrolled: 15.00 and 1.50 of solidarity."""
    result = _january(_employment())
    assert _contractual(result) == Decimal("15.00")


def test_part_time_is_proportioned() -> None:
    """20 of 40 weekly hours: 15.00 x 20 / 40 = 7.50."""
    employment = _employment(
        weekly_hours=WeeklyHours(20), full_time_weekly_hours=WeeklyHours(40)
    )
    assert _contractual(_january(employment)) == Decimal("7.50")


@pytest.mark.parametrize(
    ("started_on", "expected"),
    [(date(2026, 1, 10), Decimal("15.00")), (date(2026, 1, 20), Decimal(0))],
    ids=["22_days", "12_days"],
)
def test_fifteen_days_of_the_month(started_on: date, expected: Decimal) -> None:
    """Hired on the 10th, 22 days: owed; on the 20th, 12 days: not owed."""
    employment = _employment(employment_period=EmploymentPeriod(started_on))
    assert _contractual(_january(employment)) == expected


@pytest.mark.parametrize(
    ("ended_on", "expected"),
    [(date(2026, 3, 31), Decimal(0)), (date(2026, 4, 1), Decimal("15.00"))],
    ids=["three_months", "longer"],
)
def test_fixed_term_of_three_months_owes_none(
    ended_on: date, expected: Decimal
) -> None:
    """1 January to 31 March is three months, to 1 April more than three."""
    employment = _employment(
        contract_type=_FIXED,
        employment_period=EmploymentPeriod(date(2026, 1, 1), ended_on),
    )
    assert _contractual(_january(employment)) == expected


def test_operaio_pays_per_hour_worked() -> None:
    """Operaio qualificato, 160 hours: 0.0801 x 160 = 12.816 -> 13."""
    result = regular_period(
        employment=_employment("2", WorkerCategory.OPERAIO),
        current_year=employment_only(),
        ordinary_hours_worked=ContributableHours(Decimal(160)),
    )
    assert _contractual(result) == Decimal(13)


def test_apprentice_operaio_pays_the_apprentice_rate() -> None:
    """Apprentice operaio, 150 hours: 0.0700 x 150 = 10.50 -> 11."""
    result = regular_period(
        employment=_employment(
            "2", WorkerCategory.OPERAIO, contract_type=Apprentice(months_elapsed=6)
        ),
        current_year=employment_only(),
        ordinary_hours_worked=ContributableHours(Decimal(150)),
    )
    assert _contractual(result) == Decimal(11)


def test_operaio_hours_unknown_is_a_missing_fact() -> None:
    """Without the hours the amount is left out and the run names the fact."""
    result = _january(_employment("2", WorkerCategory.OPERAIO))
    assert _contractual(result) == 0
    assert "contractual_fund_hours_unknown" in _codes(result)
    assert not result.is_payable


def test_level_without_a_row_is_not_computed() -> None:
    """Artigianato 7Q, a quadro level the Prevedi table has no row for."""
    employment = replace(
        _employment("7Q", WorkerCategory.QUADRO),
        ccnl_slug="edilizia-artigianato-cna.json",
    )
    result = _january(employment)
    assert "contractual_fund_not_computed" in _codes(result)


def test_unknown_category_is_a_missing_fact() -> None:
    """Level 2 holds operai and impiegati: the category decides the amount."""
    result = _january(_employment("2", None))
    assert "contractual_fund_category_unknown" in _codes(result)


def test_tredicesima_owes_its_ratei() -> None:
    """A full year: the tredicesima owes 15.00 x 12 / 12 = 15.00."""
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_employment(),
            employer=EMPLOYER,
            current_year=employment_only(),
        )
    )
    (thirteenth,) = [
        r
        for r in year.period_results
        if r.run is not None and r.run.run_kind == "thirteenth"
    ]
    assert _contractual(thirteenth) == Decimal("15.00")


def test_apprentice_owes_the_apprentice_amount() -> None:
    """An apprentice impiegato owes 10.00 whatever the level."""
    employment = _employment(contract_type=Apprentice(months_elapsed=6))
    assert _contractual(_january(employment)) == Decimal("10.00")


@pytest.mark.parametrize(
    "event",
    [
        SicknessEpisode("S1", date(2026, 1, 1), date(2026, 1, 20)),
        AbsenceEvent(
            date(2026, 1, 1),
            Decimal(120),
            Decimal("10.00"),
            end_date=date(2026, 1, 20),
            suspends_accrual=True,
            no_pay_due=True,
        ),
    ],
    ids=["sickness", "unpaid_leave"],
)
def test_days_off_do_not_count(event: WorkEvent) -> None:
    """20 days of sickness or unpaid leave leave 11 worked days: none owed."""
    result = regular_period(
        employment=_employment(),
        events=(event,),
        current_year=employment_only(),
    )
    assert _contractual(result) == 0


def test_a_strike_still_counts() -> None:
    """20 days of strike are not sickness nor unpaid leave: 15.00 owed."""
    strike = AbsenceEvent(
        date(2026, 1, 1),
        Decimal(120),
        Decimal("10.00"),
        end_date=date(2026, 1, 20),
        suspends_accrual=False,
        no_pay_due=False,
    )
    result = regular_period(
        employment=_employment(), events=(strike,), current_year=employment_only()
    )
    assert _contractual(result) == Decimal("15.00")


@pytest.mark.parametrize(
    ("level", "category"),
    [("5", WorkerCategory.OPERAIO), ("5", WorkerCategory.DIRIGENTE)],
    ids=["operaio_without_hourly_rate", "dirigente"],
)
def test_category_or_level_without_amount_is_not_computed(
    level: str, category: WorkerCategory
) -> None:
    """An operaio at a level the hourly table lacks, a dirigente: an issue."""
    result = regular_period(
        employment=_employment(level, category),
        current_year=employment_only(),
        ordinary_hours_worked=ContributableHours(Decimal(160)),
    )
    assert "contractual_fund_not_computed" in _codes(result)
