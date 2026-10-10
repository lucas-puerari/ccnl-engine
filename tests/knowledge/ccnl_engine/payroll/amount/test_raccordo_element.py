"""Elemento di Raccordo Contrattuale of the CCNL grafici editoriali.

Ipotesi di accordo of 19 January 2021: the ERC "maturerà progressivamente
per mese/frazione di mese e verrà corrisposto [...] nel mese di dicembre
contestualmente alla gratifica natalizia", and "non avrà alcuna incidenza
su alcun istituto contrattuale o di legge".

A C1 hired on 1 July 2026 with an annual ERC of 412.50 (the bundle holds
the scatti of this CCNL from July 2026): the tredicesima of 2026 counts 6
months and pays 412.50 x 6 / 12 = 206.25, outside the TFR base.  Ended on
30 September 2026, the September run liquidates 3 months of tredicesima
and 412.50 x 3 / 12 = 103.125 -> 103.13 of ERC.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment, PayrollRun, PeriodInput
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from tests.knowledge.ccnl_engine.payroll.support import EMPLOYER, ENGINE
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)

if TYPE_CHECKING:
    from ccnl_engine import CompetenceYearResult, PeriodResult

pytestmark = pytest.mark.legal_scenario

_SINCE_JULY = SeniorityFact.since(date(2026, 7, 1), SenioritySource.EMPLOYER_RECORDS)


def _year(erc: Decimal | None, ended_on: date | None = None) -> CompetenceYearResult:
    employment = Employment(
        ccnl_slug="grafica-editoria-aieg.json",
        level_code="C1",
        seniority=_SINCE_JULY,
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        employment_period=EmploymentPeriod(
            started_on=date(2026, 7, 1), ended_on=ended_on
        ),
        erc_amount=erc,
    )
    return ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=employment,
            employer=EMPLOYER,
            current_year=employment_only(),
        )
    )


def _run(year: CompetenceYearResult, kind: str, month: int = 12) -> PeriodResult:
    (result,) = [
        r
        for r in year.period_results
        if r.run is not None and r.run.run_kind == kind and r.period_id.month == month
    ]
    return result


def _erc(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("erc_")),
        Decimal(0),
    )


def _tfr_base(result: PeriodResult) -> object:
    (decision,) = [d for d in result.decisions if d.capability == "tfr"]
    return decision.inputs["base"]


def test_paid_with_the_tredicesima_outside_the_tfr() -> None:
    """6 months: 206.25, in the gross, not in the TFR base."""
    holder = _run(_year(Decimal("412.50")), "thirteenth")
    without = _run(_year(Decimal(0)), "thirteenth")
    assert _erc(holder) == Decimal("206.25")
    assert _erc(without) == 0
    assert holder.period_gross - without.period_gross == Decimal("206.25")
    assert _tfr_base(holder) == _tfr_base(without)


def test_liquidated_at_the_termination() -> None:
    """Ended on 30 September: 3 months of tredicesima, 103.13 of ERC."""
    september = _run(_year(Decimal("412.50"), date(2026, 9, 30)), "regular", 9)
    assert _erc(september) == Decimal("103.13")


def test_none_after_december_2020() -> None:
    """Hired in July 2026: no ERC to state, none paid, no issue."""
    thirteenth = _run(_year(None), "thirteenth")
    assert _erc(thirteenth) == 0
    assert "erc_unknown" not in {i.code for i in thirteenth.issues}


def test_unknown_erc_is_a_missing_fact() -> None:
    """Employed since 2019: the tredicesima leaves the ERC out, names it."""
    employment = Employment(
        ccnl_slug="grafica-editoria-aieg.json",
        level_code="C1",
        seniority=_SINCE_JULY,
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        employment_period=EmploymentPeriod(started_on=date(2019, 1, 1)),
    )
    thirteenth = ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.thirteenth(2026, 12),
            payment_date=date(2026, 12, 18),
            employment=employment,
            employer=EMPLOYER,
            current_year=employment_only(),
        )
    )
    assert _erc(thirteenth) == 0
    (issue,) = [i for i in thirteenth.issues if i.code == "erc_unknown"]
    assert issue.fact == "erc_amount"
    assert not thirteenth.is_payable
