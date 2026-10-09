"""The contractual contribution a CCNL owes a fund for every worker.

Fondapi, Scheda 'I destinatari e i contributi' (29 July 2026), CCNL
Materiali da costruzione, lapidei: "a carico del datore di lavoro, è
istituito un contributo mensile di euro 5,00 (riparametrati su base 100) da
versare a Fondapi per ogni lavoratore [...] Sul contributo di cui sopra è
dovuta esclusivamente la contribuzione INPS di solidarietà"; level 5,
parametro 136: 6.80 EUR a month.  The ordinary contributions of an enrolled
worker are 2.40% employer and at least 1.40% employee of the pay the TFR is
computed on.

Level 5 in January 2026: 2014.85 minimum + 10.33 EDR = 2025.18.  Not
enrolled: 6.80 employer, solidarity 0.68.  Enrolled at 1.40%: employer
2025.18 x 2.40% = 48.60432 -> 48.60, plus 6.80 = 55.40; employee 28.35252
-> 28.35; solidarity 5.54.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment, PayrollRun
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    PensionFundEnrolment,
    Permanent,
    WeeklyHours,
)
from tests.acceptance.legal_scenarios._support import EMPLOYER, ENGINE, regular_period
from tests.fixtures.current_year import employment_only
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_LAPIDEI = "materiali-costruzione-lapidei-confapi.json"
_PARTIAL = "materiali-costruzione-lapidei-confapi/contractual_fund_partial"


def _january(
    pension: PensionFundEnrolment | NoPensionFund | None,
    weekly: WeeklyHours | None = None,
) -> PeriodResult:
    employment = Employment(
        ccnl_slug=_LAPIDEI,
        level_code="5",
        seniority=new_hire(),
        pension_fund=pension,
        weekly_hours=weekly,
        full_time_weekly_hours=None if weekly is None else WeeklyHours(40),
        contract_type=Permanent(),
    )
    return regular_period(employment=employment, current_year=employment_only())


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def _decision_inputs(result: PeriodResult) -> dict[str, object]:
    (decision,) = [
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    ]
    return {"reason": decision.reason_code, **decision.inputs}


def test_owed_without_enrolment() -> None:
    """A worker not enrolled is owed 6.80, with 0.68 of solidarity."""
    result = _january(NoPensionFund())
    inputs = _decision_inputs(result)
    assert inputs["reason"] == "contractual_only"
    assert _entry(result, "pension_fund_employer") == Decimal("6.80")
    assert inputs["solidarity"] == Decimal("0.68")
    assert _PARTIAL not in {
        limitation.id for limitation in result.assurance.limitations
    }


def test_added_to_the_ordinary_contributions() -> None:
    """Enrolled at 1.40%: 48.60 + 6.80 = 55.40 employer, 28.35 employee."""
    result = _january(
        PensionFundEnrolment("FONDAPI", Decimal("0.014"), tfr_to_fund=True)
    )
    inputs = _decision_inputs(result)
    assert inputs["contractual"] == Decimal("6.80")
    assert _entry(result, "pension_fund_employer") == Decimal("55.40")
    assert _entry(result, "pension_fund_employee") == Decimal("28.35")
    assert inputs["solidarity"] == Decimal("5.54")


def test_owed_while_the_enrolment_is_unknown() -> None:
    """The contractual part does not depend on the voluntary enrolment."""
    result = _january(None)
    assert _entry(result, "pension_fund_employer") == Decimal("6.80")
    assert _decision_inputs(result)["reason"] == "required_fact_missing"


def test_part_time_is_an_open_limitation() -> None:
    """The source gives no rule for part time: full amount, not payable."""
    result = _january(NoPensionFund(), WeeklyHours(20))
    assert _entry(result, "pension_fund_employer") == Decimal("6.80")
    assert _PARTIAL in {limitation.id for limitation in result.assurance.limitations}
    assert not result.is_payable


def test_partial_month_is_an_open_limitation() -> None:
    """A hire on 15 January: no rule for a partial month, not payable."""
    employment = Employment(
        ccnl_slug=_LAPIDEI,
        level_code="5",
        employment_period=EmploymentPeriod(started_on=date(2026, 1, 15)),
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
    )
    result = regular_period(employment=employment, current_year=employment_only())
    assert _entry(result, "pension_fund_employer") == Decimal("6.80")
    assert _PARTIAL in {limitation.id for limitation in result.assurance.limitations}


def test_extra_month_run_owes_none() -> None:
    """A monthly contribution: the tredicesima of December owes none."""
    employment = Employment(
        ccnl_slug=_LAPIDEI,
        level_code="5",
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
    )
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=employment,
            employer=EMPLOYER,
            current_year=employment_only(),
        )
    )
    (thirteenth,) = [
        r
        for r in year.period_results
        if r.run is not None and r.run.run_kind == "thirteenth"
    ]
    (december,) = [
        r for r in year.period_results if r.run == PayrollRun.regular(2026, 12)
    ]
    assert _entry(thirteenth, "pension_fund_employer") == 0
    assert _entry(december, "pension_fund_employer") == Decimal("6.80")
