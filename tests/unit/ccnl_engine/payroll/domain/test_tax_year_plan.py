"""Validation of a tax-year plan: its competence years and opening state."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.competence_year_plan import CompetenceYearPlan
from ccnl_engine.payroll.domain.current_year import CurrentYearTaxFacts
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Employment, Permanent
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.tax_year_plan import TaxYearPlan

_EMPLOYMENT = Employment(
    ccnl_slug="commercio-confcommercio.json", level_code="4", contract_type=Permanent()
)
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def _year(year: int, opening: PeriodState | None = None) -> CompetenceYearPlan:
    return CompetenceYearPlan(
        year=year,
        employment=_EMPLOYMENT,
        employer=_EMPLOYER,
        payment_dates={12: date(year + 1, 1, 13)},
        opening_state=opening,
    )


def test_holds_the_competence_years_paid_in_the_tax_year() -> None:
    """A late December of 2026 and the year 2027, as a tuple."""
    plan = TaxYearPlan(tax_year=2027, competence_years=[_year(2026), _year(2027)])  # type: ignore[arg-type]

    assert [p.year for p in plan.competence_years] == [2026, 2027]
    assert plan.opening_state is None


@pytest.mark.parametrize(
    ("years", "field", "match"),
    [
        ((), "TaxYearPlan.competence_years", "at least one"),
        (
            (_year(2026), _year(2026)),
            "TaxYearPlan.competence_years[1]",
            "appear once",
        ),
        ((_year(2028),), "TaxYearPlan.competence_years[0]", "not after"),
        (
            (_year(2027, PeriodState.zero()),),
            "TaxYearPlan.competence_years[0].opening_state",
            "carries no opening state",
        ),
        (("2027",), "TaxYearPlan.competence_years[0]", "CompetenceYearPlan"),
    ],
    ids=["empty", "twice", "later year", "own opening state", "not a plan"],
)
def test_rejects_competence_years_that_cannot_be_paid_in_the_year(
    years: tuple[object, ...], field: str, match: str
) -> None:
    """Each competence year appears once, not after the tax year, unopened."""
    with pytest.raises(InvalidInputError, match=match) as info:
        TaxYearPlan(tax_year=2027, competence_years=years)  # type: ignore[arg-type]

    assert info.value.field == field
    assert info.value.feature == "tax_year_plan"


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"tax_year": "2027"}, "TaxYearPlan.tax_year"),
        ({"opening_state": "zero"}, "TaxYearPlan.opening_state"),
        ({"current_year": 2027}, "TaxYearPlan.current_year"),
    ],
)
def test_rejects_fields_of_the_wrong_type(
    kwargs: dict[str, object], field: str
) -> None:
    """The tax year is an int, the opening state a PeriodState."""
    fields: dict[str, object] = {"tax_year": 2027, "competence_years": (_year(2027),)}
    with pytest.raises(InvalidInputError) as info:
        TaxYearPlan(**(fields | kwargs))  # type: ignore[arg-type]

    assert info.value.field == field


def test_current_year_facts_must_be_of_the_tax_year() -> None:
    """Facts of 2026 do not describe tax year 2027."""
    facts = CurrentYearTaxFacts.employment_only(2026, date(2026, 1, 1))
    with pytest.raises(InvalidInputError, match="tax year 2026") as info:
        TaxYearPlan(tax_year=2027, competence_years=(_year(2027),), current_year=facts)

    assert info.value.field == "TaxYearPlan.current_year"


def test_current_year_facts_of_the_tax_year_are_kept() -> None:
    """Facts of the tax year are accepted as given."""
    facts = CurrentYearTaxFacts.employment_only(2027, date(2027, 1, 1))
    plan = TaxYearPlan(
        tax_year=2027, competence_years=(_year(2027),), current_year=facts
    )

    assert plan.current_year is facts
