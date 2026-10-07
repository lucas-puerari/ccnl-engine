"""calculate_tax_year and the tax-year boundaries of calculate_competence_year."""

from __future__ import annotations

from datetime import date
from functools import cache
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.application.calculate_competence_year import (
    calculate_competence_year,
)
from ccnl_engine.payroll.application.calculate_tax_year import calculate_tax_year
from ccnl_engine.payroll.domain.competence_year_plan import CompetenceYearPlan
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Employment
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.family import (
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.domain.inputs import PeriodFacts
from ccnl_engine.payroll.domain.tax_year_plan import TaxYearPlan
from ccnl_engine.shared.domain.errors import InvalidInputError
from tests.fixtures.current_year import employment_only
from tests.fixtures.dependents import declared_dependent
from tests.fixtures.next_year_repository import NextYearRepository

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.year_result import CompetenceYearResult
    from ccnl_engine.payroll.domain.period_state import PeriodState

_REPO = NextYearRepository()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_LATE = date(2027, 1, 13)


def _plan(
    *,
    period: EmploymentPeriod | None = None,
    opening: PeriodState | None = None,
    dates: dict[int | str, date] | None = None,
    family: FamilyComposition | None = None,
) -> CompetenceYearPlan:
    return CompetenceYearPlan(
        year=2026,
        employment=Employment(
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            employment_period=period,
        ),
        employer=_EMPLOYER,
        payment_dates={12: _LATE} if dates is None else dates,
        opening_state=opening,
        default_facts=PeriodFacts(family_composition=family),
        current_year=None if family is None else employment_only(2026),
    )


@cache
def _late_year() -> CompetenceYearResult:
    """Return 2026 with its December paid on 13 January 2027.

    Returns:
        The fourteen runs, the last one opening 2027.
    """
    return calculate_competence_year(_plan(), repo=_REPO)


class TestCompetenceYearAcrossTaxYears:
    """A competence year whose December is paid in the next tax year."""

    def test_the_late_december_opens_the_next_tax_year(self) -> None:
        """2026 closes on the tredicesima; the December opens 2027."""
        year = _late_year()

        assert [str(c) for c in year.conguagli] == ["2026-12-thirteenth@2026-12-28"]
        assert year.closing_state.tax_year == 2027
        assert year.next_opening_state is year.closing_state

    def test_resuming_on_the_next_tax_year_state_computes_nothing(self) -> None:
        """Every run of 2026 is already closed: nothing is computed again."""
        closing = _late_year().closing_state

        resumed = calculate_competence_year(_plan(opening=closing), repo=_REPO)

        assert resumed.period_results == ()
        assert resumed.closing_state == closing

    def test_a_later_state_missing_a_run_of_the_year_is_rejected(self) -> None:
        """A 2027 state that never paid November 2026 cannot resume 2026."""
        opened = _late_year().closing_state
        accrual = type(opened.accrual)(
            competence_runs=tuple(
                r for r in opened.accrual.competence_runs if str(r) != "2026-11-regular"
            )
        )
        state = type(opened)(accrual=accrual, cash=opened.cash)

        with pytest.raises(InvalidInputError, match="is not closed") as info:
            calculate_competence_year(_plan(opening=state), repo=_REPO)

        assert info.value.field == "CompetenceYearPlan.opening_state"

    def test_a_payment_date_of_a_run_not_computed_is_rejected(self) -> None:
        """An employment ended in May has no tredicesima of December."""
        plan = _plan(
            period=EmploymentPeriod(date(2026, 1, 1), date(2026, 5, 31)),
            dates={"2026-12-thirteenth": date(2026, 12, 15)},
        )

        with pytest.raises(InvalidInputError, match="not a run of 2026") as info:
            calculate_competence_year(plan, repo=_REPO)

        assert info.value.field == "CompetenceYearPlan.payment_dates"


class TestTaxYear:
    """The payments of one tax year, drawn from its competence years."""

    def test_rejects_a_tax_year_none_of_the_plans_pays_in(self) -> None:
        """The 2026 plan pays nothing in 2028."""
        with pytest.raises(InvalidInputError, match="is paid in tax year 2028"):
            calculate_tax_year(
                TaxYearPlan(tax_year=2028, competence_years=(_plan(),)), repo=_REPO
            )

    def test_a_tax_year_already_paid_computes_nothing(self) -> None:
        """2027 resumed after its only planned payment: no result, same state."""
        closing = _late_year().closing_state

        year = calculate_tax_year(
            TaxYearPlan(
                tax_year=2027, competence_years=(_plan(),), opening_state=closing
            ),
            repo=_REPO,
        )

        assert year.period_results == ()
        assert year.closing_state == closing
        assert [str(p) for p in year.payments] == ["2026-12-regular@2027-01-13"]
        assert year.conguaglio is None


class TestCurrentYearFacts:
    """The family deductions of a payment read the facts of its tax year."""

    _SPOUSE = FamilyComposition(
        dependents=(declared_dependent(relationship=DependentRelationship.SPOUSE),)
    )

    def _december_decision(self, plan: TaxYearPlan) -> CalculationStatus:
        (result,) = calculate_tax_year(plan, repo=_REPO).period_results
        (decision,) = [
            d for d in result.decisions if d.capability == "family_deductions"
        ]
        return decision.status

    def test_late_december_reads_the_facts_of_the_tax_year_plan(self) -> None:
        """December 2026 paid in 2027 uses the 2027 facts of the plan."""
        plan = TaxYearPlan(
            tax_year=2027,
            competence_years=(_plan(family=self._SPOUSE),),
            current_year=employment_only(2027),
        )
        assert self._december_decision(plan) is CalculationStatus.FINAL

    def test_competence_year_facts_of_another_tax_year_are_not_used(self) -> None:
        """Without 2027 facts the 2026 ones of the competence year do not count."""
        plan = TaxYearPlan(
            tax_year=2027, competence_years=(_plan(family=self._SPOUSE),)
        )
        assert self._december_decision(plan) is CalculationStatus.PROVISIONAL
