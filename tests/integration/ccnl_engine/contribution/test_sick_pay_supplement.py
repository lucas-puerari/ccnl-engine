"""Additional sickness contribution of the employers of an INPS regime.

Commercio level 4 impiegato (terziario), March 2026, with its sickness rule
moved to the regime of the pubblici esercizi: the employer pays 0.77% of
the INPS taxable pay on top of the sector rate (INPS circ. 71/1985, news of
June 2024 on messaggio 2382/2024).  Industria has no such supplement.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.contribution.sick_pay_supplement.services import EMPLOYER_COMPONENT
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import calculate_period
from ccnl_engine.run.types import PeriodId
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.period.results import PeriodResult


class _PubbliciEsercizi(BundledKnowledgeRepository):
    """The CCNL with its sickness rule moved to the pubblici esercizi regime."""

    def load_ccnl(self, filename: str) -> CCNL:
        ccnl = load_ccnl(filename)
        assert ccnl.work_rules is not None
        assert ccnl.work_rules.sickness_rules is not None
        sickness = ccnl.work_rules.sickness_rules.model_copy(
            update={"inps_regime": "pubblici_esercizi"}
        )
        rules = ccnl.work_rules.model_copy(update={"sickness_rules": sickness})
        return ccnl.model_copy(update={"work_rules": rules})


def _march(
    slug: str, level: str, category: WorkerCategory, repo: BundledKnowledgeRepository
) -> PeriodResult:
    request = PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        ccnl_slug=slug,
        level_code=level,
        seniority=new_hire(),
        opening_state=PeriodState.zero(),
        category=category,
    )
    return calculate_period(request, repo=repo)


def test_the_employer_pays_the_supplement_on_the_taxable_pay() -> None:
    """0.77% of the base, added to the employer total and to nothing else."""
    args = ("commercio-confcommercio.json", "4", WorkerCategory.IMPIEGATO)
    bundled = _march(*args, BundledKnowledgeRepository())
    result = _march(*args, _PubbliciEsercizi())
    (component,) = (
        c
        for c in result.contribution_breakdown.components
        if c.name == EMPLOYER_COMPONENT
    )
    assert component.rate == Decimal("0.0077")
    assert component.amount == money(component.base * Decimal("0.0077"))
    assert component.amount > 0
    breakdown, before = result.contribution_breakdown, bundled.contribution_breakdown
    assert breakdown.employer == before.employer + component.amount
    assert breakdown.employee == before.employee
    assert EMPLOYER_COMPONENT not in {c.name for c in before.components}
    sources = result.capability_report.rule_sources
    assert (
        sources["inps_employer"]
        == bundled.capability_report.rule_sources["inps_employer"]
    )


def test_a_sector_without_the_supplement_is_a_data_error() -> None:
    """Industria holds no supplement for the regime: the data are rejected."""
    args = ("metalmeccanico-federmeccanica.json", "C3", WorkerCategory.OPERAIO)
    with pytest.raises(DataIntegrityError, match="pubblici_esercizi"):
        _march(*args, _PubbliciEsercizi())
