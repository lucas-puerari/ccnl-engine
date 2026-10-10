"""An employer rate chosen without the worker category is provisional."""

from __future__ import annotations

from datetime import date

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Apprentice, Permanent
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.service._contributions_rates import (
    CATEGORY_RATE_ASSUMED_CODE,
    category_rate_issue,
)
from ccnl_engine.tax.annual.loaders import load_year_rules

_ARTIGIANATO = load_year_rules(2026, TaxSector.ARTIGIANATO, 10)


def _run(category: WorkerCategory | None = None) -> list[str]:
    request = PeriodCalculationRequest(
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        ccnl_slug="metalmeccanico-artigianato.json",
        level_code="5",
        employer=EmployerProfile(headcount=Headcount(10)),
        opening_state=PeriodState.zero(),
        category=category,
    )
    result = calculate_period(request)
    return [i.code for i in result.issues if i.status is CalculationStatus.PROVISIONAL]


def test_level_without_category_gets_a_provisional_issue() -> None:
    """Artigianato sets rates by category: the operai rate is an assumption."""
    issue = category_rate_issue(_ARTIGIANATO, Permanent(), None)
    assert issue is not None
    assert issue.code == CATEGORY_RATE_ASSUMED_CODE
    assert issue.status is CalculationStatus.PROVISIONAL
    assert "0.2693" in issue.message
    assert "impiegato, quadro" in issue.message


def test_declared_category_needs_no_issue() -> None:
    """With the category the rate is the one of the category."""
    assert (
        category_rate_issue(_ARTIGIANATO, Permanent(), WorkerCategory.IMPIEGATO) is None
    )


def test_apprentice_rates_need_no_category() -> None:
    """Apprentices take the statutory apprentice rates."""
    assert category_rate_issue(_ARTIGIANATO, Apprentice(months_elapsed=0), None) is None


def test_sector_without_category_rates_needs_no_issue() -> None:
    """A single rate for every category depends on no category."""
    terziario = load_year_rules(2026, TaxSector.TERZIARIO, 10)
    assert category_rate_issue(terziario, Permanent(), None) is None


def test_domestic_sector_needs_no_issue() -> None:
    """Flat domestic contributions have no category rate."""
    domestic = load_year_rules(2026, TaxSector.LAVORO_DOMESTICO, 1)
    assert category_rate_issue(domestic, Permanent(), None) is None


def test_run_without_category_is_provisional() -> None:
    """The run carries the issue until the category is declared."""
    assert CATEGORY_RATE_ASSUMED_CODE in _run()
    assert CATEGORY_RATE_ASSUMED_CODE not in _run(WorkerCategory.OPERAIO)
