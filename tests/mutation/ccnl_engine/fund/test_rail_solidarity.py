"""Ordinary FS fund contribution is conditional on employer coverage.

D.I. 99296/2017 art. 2(2), art. 6(1)(a); INPS circulars 208/2015,
107/2018 and 70/2020 distinguish employer eligibility, ordinary charges
and benefit eligibility.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.contribution.results import ContributionComponent
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.fund.solidarity.coverage import solidarity_coverage_issue
from ccnl_engine.inputs import FixedTerm, Permanent
from ccnl_engine.period.results import PeriodResult
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

_ENGINE = PayrollEngine.bundled()


def _run(
    covered: bool | None, contract: Permanent | FixedTerm | None = None
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="trasporto-ferroviario-agens",
                level_code="D1",
                seniority=new_hire(),
                contract_type=contract or Permanent(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(100), solidarity_fund_covered=covered
            ),
        )
    )


def _fund(result: PeriodResult) -> dict[str, ContributionComponent]:
    return {
        component.name: component
        for component in result.contribution_breakdown.components
        if component.name.startswith("solidarity_fund_")
    }


def test_covered_permanent_month() -> None:
    """On EUR 1994 INPS pay: before EUR 0; after EUR 2.66 employer, EUR 1.33 worker."""
    result = _run(True)
    parts = _fund(result)
    base = parts["solidarity_fund_employer"].base
    assert base == Decimal("1994.00")
    assert parts["solidarity_fund_employee"].base == base
    assert parts["solidarity_fund_employer"].amount == Decimal("2.66")
    assert parts["solidarity_fund_employee"].amount == Decimal("1.33")
    assert parts["solidarity_fund_employer"].amount == (
        base * Decimal(2) / Decimal(1500)
    ).quantize(Decimal("0.01"))
    assert parts["solidarity_fund_employee"].amount == (base / Decimal(1500)).quantize(
        Decimal("0.01")
    )
    assert not any(i.fact == "solidarity_fund_covered" for i in result.issues)


@pytest.mark.parametrize("covered", [False, None])
def test_uncovered_or_unknown_employer_owes_no_fs_fund(covered: bool | None) -> None:
    """False owes zero; unknown owes zero with an employer INPS blocker."""
    result = _run(covered)
    assert not _fund(result)
    issues = [i for i in result.issues if i.fact == "solidarity_fund_covered"]
    assert bool(issues) == (covered is None)
    if issues:
        assert issues[0].code == "missing_fact"
        assert issues[0].capability == "inps_employer"


def test_fixed_term_has_no_ordinary_fs_contribution() -> None:
    """Benefits for fixed terms do not imply an ordinary contribution."""
    assert not _fund(_run(True, FixedTerm()))
    assert not any(
        i.fact == "solidarity_fund_covered" for i in _run(None, FixedTerm()).issues
    )


def test_unknown_coverage_does_not_block_executives() -> None:
    """A worker outside the fund needs no employer coverage declaration."""
    ctx = cast(
        "RunContext",
        SimpleNamespace(
            contract=SimpleNamespace(ccnl=load_ccnl("trasporto-ferroviario-agens")),
            request=SimpleNamespace(
                employer=EmployerProfile(headcount=Headcount(100)),
                contract_type=Permanent(),
            ),
            worker_category=WorkerCategory.DIRIGENTE,
        ),
    )
    assert solidarity_coverage_issue(ctx) is None
