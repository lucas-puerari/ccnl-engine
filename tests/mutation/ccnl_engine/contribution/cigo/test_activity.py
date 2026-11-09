"""INPS CIGO is selected by employer activity, not by INPS sector."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.contribution.cigo.activity import with_activity_cigo
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.regime.models import EmployerActivity
from ccnl_engine.run.types import PeriodId
from ccnl_engine.sector.loaders import load_year_rules
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult


def _run(
    slug: str,
    level: str,
    activity: EmployerActivity | None,
    category: WorkerCategory = WorkerCategory.OPERAIO,
) -> PeriodResult:
    request = PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(10), activity=activity),
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        ccnl_id=slug,
        level_code=level,
        seniority=new_hire(),
        opening_state=PeriodState.zero(),
        category=category,
    )
    return calculate_period(
        request, repo=bundled_repository(), resolver=bundled_policies()
    )


@pytest.mark.parametrize(
    ("slug", "level", "activity", "before", "after", "base", "delta"),
    [
        (
            "lapidei-industria",
            "F",
            EmployerActivity.STONE_WORKING,
            Decimal("520.03"),
            Decimal("547.15"),
            Decimal("1695.00"),
            Decimal("0.016"),
        ),
        (
            "materiali-costruzione-lapidei-confapi",
            "8",
            EmployerActivity.STONE_WORKING,
            Decimal("500.39"),
            Decimal("526.49"),
            Decimal("1631.00"),
            Decimal("0.016"),
        ),
        (
            "legno-lapidei-artigianato-confartigianato",
            "AS",
            EmployerActivity.STONE_WORKING,
            Decimal("610.85"),
            Decimal("684.47"),
            Decimal("2231.00"),
            Decimal("0.033"),
        ),
        (
            "edilizia-artigianato-cna",
            "1",
            EmployerActivity.CONSTRUCTION,
            Decimal("443.55"),
            Decimal("519.69"),
            Decimal("1620.00"),
            Decimal("0.047"),
        ),
    ],
)
def test_operai_activity_contributions(
    slug: str,
    level: str,
    activity: EmployerActivity,
    before: Decimal,
    after: Decimal,
    base: Decimal,
    delta: Decimal,
) -> None:
    """Hand-computed CIGO: 1695 x 1.60% = 27.12; 1620 x 4.70% = 76.14.

    The other bases: 1631 x 1.60% = 26.10 and 2231 x 3.30% = 73.62.
    Sector-only employer totals are 520.03, 500.39, 610.85, 443.55;
    the activity totals are 547.15, 526.49, 684.47, 519.69.
    """
    generic = _run(slug, level, EmployerActivity.OTHER)
    selected = _run(slug, level, activity)
    assert generic.contribution_breakdown.employer == before
    assert selected.contribution_breakdown.employer == after
    assert (
        selected.contribution_breakdown.employee
        == generic.contribution_breakdown.employee
    )
    assert after - before == (base * delta).quantize(Decimal("0.01"))
    assert selected.contribution_breakdown.components[0].base == base


@pytest.mark.parametrize("category", [WorkerCategory.OPERAIO, WorkerCategory.IMPIEGATO])
def test_artisan_separate_workshop_owes_no_cigo(category: WorkerCategory) -> None:
    """On EUR 2231, covered operai add 2231 x 3.30% = EUR 73.62.

    The separate workshop stays at EUR 610.85 instead of EUR 684.47.
    Office workers also stay at their sector-only rate, without 1.70% CIGO.
    """
    slug = "legno-lapidei-artigianato-confartigianato"
    workshop = _run(
        slug, "AS", EmployerActivity.STONE_WORKING_SEPARATE_WORKSHOP, category
    )
    sector = _run(slug, "AS", EmployerActivity.OTHER, category)
    covered = _run(slug, "AS", EmployerActivity.STONE_WORKING, category)
    assert (
        workshop.contribution_breakdown.employer
        == sector.contribution_breakdown.employer
    )
    assert (
        workshop.contribution_breakdown.employee
        == sector.contribution_breakdown.employee
    )
    assert (
        covered.contribution_breakdown.employer
        > workshop.contribution_breakdown.employer
    )
    assert all(i.code != "cigo_activity_unknown" for i in workshop.issues)
    if category is WorkerCategory.OPERAIO:
        assert workshop.contribution_breakdown.employer == Decimal("610.85")
        assert covered.contribution_breakdown.employer == Decimal("684.47")


def test_office_rate_is_smaller_than_construction_operaio_rate() -> None:
    """On 2764 taxable euros the office CIGO is 1.70%, not 4.70%."""
    generic = _run(
        "edilizia-artigianato-cna",
        "7",
        EmployerActivity.OTHER,
        WorkerCategory.IMPIEGATO,
    )
    selected = _run(
        "edilizia-artigianato-cna",
        "7",
        EmployerActivity.CONSTRUCTION,
        WorkerCategory.IMPIEGATO,
    )
    assert generic.contribution_breakdown.employer == Decimal("695.43")
    assert selected.contribution_breakdown.employer == Decimal("742.41")
    assert selected.contribution_breakdown.components[2].rate == Decimal("0.0260")
    assert (
        selected.contribution_breakdown.employee
        == generic.contribution_breakdown.employee
    )


def test_apprentices_and_headcount_use_activity_cigo_only_in_non_ivs_share() -> None:
    """At 51 staff stone adds 1.30 points to industry apprentices; office stays 2%."""
    industry = load_year_rules(2026, TaxSector.INDUSTRIA, 51)
    stone = with_activity_cigo(
        industry, TaxSector.INDUSTRIA, EmployerActivity.STONE_WORKING, 51
    )
    assert industry.apprentice is not None
    assert stone.apprentice is not None
    assert industry.inps is not None
    assert stone.inps is not None
    assert (
        stone.apprentice.employer_rate_after - industry.apprentice.employer_rate_after
        == Decimal("0.013")
    )
    assert (
        stone.apprentice.employer_ivs_rate_after
        == industry.apprentice.employer_ivs_rate_after
    )
    assert (
        stone.inps.employer_rate_by_category[WorkerCategory.IMPIEGATO]
        == industry.inps.employer_rate_by_category[WorkerCategory.IMPIEGATO]
    )
    artisan = load_year_rules(2026, TaxSector.ARTIGIANATO, 51)
    built = with_activity_cigo(
        artisan, TaxSector.ARTIGIANATO, EmployerActivity.CONSTRUCTION, 51
    )
    assert artisan.inps is not None
    assert built.inps is not None
    assert built.inps.employer_rate_by_category[
        WorkerCategory.IMPIEGATO
    ] - artisan.inps.employer_rate_by_category[WorkerCategory.IMPIEGATO] == Decimal(
        "0.020"
    )


def test_unsupported_sector_or_activity_does_not_change_rates() -> None:
    """No CIGO adjustment for another activity or non-industrial INPS sector."""
    industry = load_year_rules(2026, TaxSector.INDUSTRIA, 10)
    domestic = load_year_rules(2026, TaxSector.LAVORO_DOMESTICO, 1)
    assert (
        with_activity_cigo(industry, TaxSector.INDUSTRIA, EmployerActivity.OTHER, 10)
        is industry
    )
    assert (
        with_activity_cigo(
            domestic, TaxSector.LAVORO_DOMESTICO, EmployerActivity.STONE_WORKING, 1
        )
        is domestic
    )
    assert (
        with_activity_cigo(
            industry, TaxSector.EDILIZIA, EmployerActivity.STONE_WORKING, 10
        )
        is industry
    )
    without_apprentices = industry.model_copy(update={"apprentice": None})
    adjusted = with_activity_cigo(
        without_apprentices, TaxSector.INDUSTRIA, EmployerActivity.STONE_WORKING, 10
    )
    assert adjusted.apprentice is None
    assert adjusted.inps is not None
    assert industry.inps is not None
    assert adjusted.inps.employer_rate - industry.inps.employer_rate == Decimal("0.016")


def test_missing_activity_only_when_cigo_clause_can_apply() -> None:
    """An unknown activity blocks the covered employer, not unrelated artisans."""
    covered = _run("edilizia-artigianato-cna", "1", None)
    unrelated = _run("metalmeccanico-artigianato", "5", None)
    assert any(
        i.code == "cigo_activity_unknown" and i.fact == "activity"
        for i in covered.issues
    )
    assert all(i.code != "cigo_activity_unknown" for i in unrelated.issues)
    assert all(
        i.code != "cigo_activity_unknown"
        for i in _run("edilizia-artigianato-cna", "1", EmployerActivity.OTHER).issues
    )
