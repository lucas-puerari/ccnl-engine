"""Which runs assess the renewal regime on their minimo.

The regime of L. 199/2025 art. 1 c. 7 covers increments paid in 2026 under
renewals signed from 1 January 2024 to 31 December 2026.  A run assesses it
on the minimo when it pays one whose level has a table dated within that
window, its employer withholds tax and its tax year is 2026.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.models import BlockerCode
from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.employment.inputs_fact import (
    ContributableHours,
    WeeklyHours,
)
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.taxation.inputs_prior_year import PriorYearTaxFacts
from ccnl_engine.tax.regime.models import EmploymentSector
from tests.integration.ccnl_engine.payroll.year.builders_next_year_repository import (
    NextYearRepository,
)
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.results import PeriodResult

_RENEWAL = "rinnovo_substitute_tax"


def _june(
    ccnl: str = "metalmeccanico-federmeccanica.json",
    level: str = "C3",
    *,
    year: int = 2026,
    contributable_hours: ContributableHours | None = None,
    weekly_hours: WeeklyHours | None = None,
    prior_year: PriorYearTaxFacts | None = None,
) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=year, month=6),
            payment_date=date(year, 6, 27),
            ccnl_slug=ccnl,
            level_code=level,
            seniority=new_hire(year),
            sector=EmploymentSector.PRIVATE,
            opening_state=PeriodState.zero(),
            contributable_hours=contributable_hours,
            weekly_hours=weekly_hours,
            prior_year=prior_year or PriorYearTaxFacts(),
        ),
        repo=NextYearRepository(),
    )


def _renewal_decisions(result: PeriodResult) -> list[str]:
    return [d.reason_code for d in result.decisions if d.capability == _RENEWAL]


def test_unknown_prior_income_blocks_the_run_with_its_own_fact() -> None:
    """Metalmeccanico C3, June 2026, no 2025 income: a dedicated missing fact.

    The C3 minimo rises to 2,211.43 on 1 June 2026, and its tables of 1 June
    2024 and 1 June 2025 also fall within the signing window.
    """
    result = _june()
    (decision,) = (d for d in result.decisions if d.capability == _RENEWAL)
    assert decision.reason_code == "prior_income_unknown"
    assert decision.status is CalculationStatus.PROVISIONAL
    assert decision.inputs["table_from"] == "2024-06-01"
    assert decision.inputs["minimum"] == Decimal("2211.43")
    assert (BlockerCode.MISSING_FACT, "employment_income") in {
        (b.code, b.detail) for b in result.blockers
    }
    assert not result.is_payable


def test_known_income_above_the_ceiling_rules_the_regime_out() -> None:
    """2025 income 40,000 > 33,000: a final decision and no renewal blocker."""
    result = _june(prior_year=PriorYearTaxFacts(employment_income=Decimal(40_000)))
    assert _renewal_decisions(result) == ["prior_income_above_ceiling"]
    assert _RENEWAL not in {b.feature for b in result.blockers}


def test_minimo_without_a_table_in_the_window_is_not_assessed() -> None:
    """Farmacie private: the last table of the minimo predates 2024."""
    assert _renewal_decisions(_june("farmacie-private-h121.json", "1")) == []


def test_household_employer_is_not_assessed() -> None:
    """A household employer withholds no tax, so applies no substitute tax."""
    result = _june(
        "lavoro-domestico-non-convivente.json",
        "B",
        contributable_hours=ContributableHours(Decimal(100)),
        weekly_hours=WeeklyHours(25),
    )
    assert _renewal_decisions(result) == []


def test_tax_year_outside_the_regime_is_not_assessed() -> None:
    """The regime covers payments of 2026 only: a June 2027 run is not assessed."""
    assert _renewal_decisions(_june(year=2027)) == []
