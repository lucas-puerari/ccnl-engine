"""Byblos on the CCNL carta e cartotecnica.

Byblos, Scheda 'I destinatari e i contributi' (in force from 25/09/2026),
settore cartario-cartotecnico: worker at least 1%, employer 1.5% "sulla
normale retribuzione annua comprensiva di 13ma mensilità"; the ipotesi of
10/02/2026 raises the employer share by 0.2% from January 2027.

C1 in January 2026, seniority since 1 January 2022: 1855.11 minimum + two
scatti of 13.43 = 1881.97.  Employer 1.5% = 28.22955 -> 28.23; employee 1%
= 18.8197 -> 18.82; solidarity 10% of 28.23 = 2.823 -> 2.82.

Tredicesima of 2026 of a worker hired on 1 January 2026: the December pay
of C1, 1960.11 from April 2026, for twelve months.  Employer 1.5% =
29.40165 -> 29.40.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.inputs import (
    PensionFundEnrolment,
    Permanent,
    SeniorityFact,
    SenioritySource,
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

_CARTA = "carta-cartone-assocarta.json"
_ENROLLED = PensionFundEnrolment("BYBLOS", Decimal("0.01"), tfr_to_fund=True)


def _employment(seniority: SeniorityFact) -> Employment:
    return Employment(
        ccnl_slug=_CARTA,
        level_code="C1",
        seniority=seniority,
        pension_fund=_ENROLLED,
        contract_type=Permanent(),
    )


def _january(events: tuple[WorkEvent, ...] = ()) -> PeriodResult:
    since = SeniorityFact.since(date(2022, 1, 1), SenioritySource.EMPLOYER_RECORDS)
    return regular_period(
        employment=_employment(since),
        current_year=employment_only(),
        events=events,
    )


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def test_on_the_minimum_and_the_scatti() -> None:
    """1881.97 x 1.5% = 28.23 employer, x 1% = 18.82 employee."""
    result = _january()
    (decision,) = [
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    ]
    assert decision.inputs["base"] == Decimal("1881.97")
    assert _entry(result, "pension_fund_employer") == Decimal("28.23")
    assert _entry(result, "pension_fund_employee") == Decimal("18.82")
    assert decision.inputs["solidarity"] == Decimal("2.82")


def test_overtime_stays_out_of_the_base() -> None:
    """Overtime is not normale retribuzione, nor in the TFR base of the run."""
    overtime = OvertimeEvent(
        event_date=date(2026, 1, 13), hours=Decimal(2), hourly_rate=Decimal(12)
    )
    result = _january((overtime,))
    (decision,) = [
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    ]
    assert decision.inputs["base"] == Decimal("1881.97")


def test_thirteenth_bears_the_contribution() -> None:
    """The normale retribuzione annua holds the 13ma: 29.40 employer."""
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_employment(new_hire()),
            employer=EMPLOYER,
            current_year=employment_only(),
        )
    )
    (thirteenth,) = [
        r
        for r in year.period_results
        if r.run is not None and r.run.run_kind == "thirteenth"
    ]
    assert _entry(thirteenth, "pension_fund_employer") == Decimal("29.40")
