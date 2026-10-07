"""Runs of a year set aside when the base salary of the level is not in force.

ANAS is the bundled case: its pay tables (CCNL 2025-2027, "Tabella
retributiva") start with the tranche of 1 March 2026.
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.payroll.application.calculate_tax_year import calculate_tax_year
from ccnl_engine.payroll.application.year._payments import prepare_year
from ccnl_engine.payroll.domain.competence_year_plan import CompetenceYearPlan
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Employment
from ccnl_engine.payroll.domain.tax_year_plan import TaxYearPlan
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.shared.domain.errors import UnknownLevelError

_REPO = BundledKnowledgeRepository()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def _plan(level_code: str = "C1") -> CompetenceYearPlan:
    return CompetenceYearPlan(
        year=2026,
        employment=Employment(ccnl_slug="anas.json", level_code=level_code),
        employer=_EMPLOYER,
    )


def test_the_runs_before_the_tables_are_set_aside() -> None:
    """January and February have no base salary; March onwards are kept."""
    prepared = prepare_year(_plan(), _REPO)

    assert [u.payment.competence.month for u in prepared.uncovered] == [1, 2]
    assert min(p.payment.competence for p in prepared.payments) == date(2026, 3, 1)


def test_an_unknown_level_is_rejected_before_any_run() -> None:
    """The level whose base salary is read must exist."""
    with pytest.raises(UnknownLevelError):
        prepare_year(_plan("Z9"), _REPO)


def test_a_tax_year_lists_the_runs_it_left_out() -> None:
    """The tax year degrades like the competence year: partial, not payable."""
    result = calculate_tax_year(
        TaxYearPlan(tax_year=2026, competence_years=(_plan(),)), repo=_REPO
    )

    left_out = [str(u.payment.run_id) for u in result.uncovered_runs]
    assert left_out == ["2026-01-regular", "2026-02-regular"]
    assert all(p.run_id.month >= 3 for p in result.payments)
    assert result.conguaglio is not None
    assert not result.is_payable
