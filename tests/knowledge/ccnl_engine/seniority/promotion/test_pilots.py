"""Seniority increments after a promotion: repriced at once or at the next one.

Turismo art. 158 c. 6, FIPE art. 182 c. 5 and Commercio and Terziario art.
205 keep the increments matured before a promotion at the amount of the
level they were matured at until the next increment matures; then every
increment takes the amount of the new level.  Federmeccanica art. 6,
Confapi art. 41 and Studi art. 134 reprice them from the promotion.

The worker's service is recognised from 1 January 2020.  Turismo and
Commercio pay triennial increments (36 months), so two have matured by
January 2026 and the third matures in January 2029; FIPE pays quadriennial
ones (48 months), one by January 2024.  Per increment: Turismo level 4
33.05, level 3 34.86 (art. 158 c. 4); FIPE the same; Commercio IV 20.66,
III 21.95 (art. 205).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import (
    EmploymentChange,
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SeniorityPromotion,
    SenioritySource,
)
from ccnl_engine.pay_item.facade import SeniorityEarning
from ccnl_engine.run.types import RunKind

_SINCE = date(2020, 1, 1)
_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(20))


def _employment(
    ccnl: str, level: str, promotion: SeniorityPromotion | None = None
) -> Employment:
    return Employment(
        ccnl_id=ccnl,
        level_code=level,
        contract_type=Permanent(),
        employment_period=EmploymentPeriod(_SINCE, None),
        seniority=SeniorityFact(
            0, _SINCE, SenioritySource.EMPLOYER_RECORDS, promotion=promotion
        ),
        pension_fund=NoPensionFund(),
        tfr_treasury_fund=False,
    )


def _seniority(employment: Employment, month: int) -> Decimal:
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=employment,
            employer=_EMPLOYER,
        )
    )
    return sum(
        (i.amount for i in result.pay_items if isinstance(i, SeniorityEarning)),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("ccnl", "before", "after", "kept"),
    [
        ("turismo-federalberghi", "4", "3", Decimal("66.10")),
        ("pubblici-esercizi-fipe-angem", "4", "3", Decimal("33.05")),
        ("commercio-confcommercio", "4", "3", Decimal("41.32")),
        ("terziario-confesercenti", "IV", "III", Decimal("41.32")),
    ],
)
def test_the_earlier_increments_keep_the_old_level_until_the_next(
    ccnl: str, before: str, after: str, kept: Decimal
) -> None:
    """Promoted on 1 April 2026, May pays the increments at the old level.

    Turismo 2 x 33.05 = 66.10; FIPE 1 x 33.05; Commercio and Terziario
    2 x 20.66 = 41.32.
    """
    promotion = SeniorityPromotion(date(2026, 4, 1), before)

    assert _seniority(_employment(ccnl, after, promotion), 5) == kept
    assert _seniority(_employment(ccnl, before), 5) == kept


def test_the_next_increment_reprices_them_all() -> None:
    """Promoted on 1 July 2025: the increment of January 2026 reprices both.

    One increment on the promotion (66 months), two in February 2026 (73
    months): 2 x 34.86 = 69.72 at level 3.
    """
    promotion = SeniorityPromotion(date(2025, 7, 1), "4")
    employment = _employment("turismo-federalberghi", "3", promotion)

    assert _seniority(employment, 2) == Decimal("69.72")


@pytest.mark.parametrize(
    ("ccnl", "before", "after"),
    [
        ("metalmeccanico-federmeccanica", "C2", "C3"),
        ("metalmeccanico-confapi", "4", "5"),
        ("studi-professionali-confprofessioni", "4", "3"),
    ],
)
def test_a_ccnl_that_reprices_at_once_ignores_the_promotion(
    ccnl: str, before: str, after: str
) -> None:
    """Federmeccanica art. 6, Confapi art. 41, Studi art. 134: the new amount."""
    promotion = SeniorityPromotion(date(2026, 4, 1), before)

    assert _seniority(_employment(ccnl, after, promotion), 5) == _seniority(
        _employment(ccnl, after), 5
    )


def test_a_plan_records_the_promotion_of_its_change_of_level() -> None:
    """Turismo, level 4 to 3 on 1 April 2026: 66.10 every month of the year."""
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_employment("turismo-federalberghi", "4"),
            employer=_EMPLOYER,
            employment_changes=(EmploymentChange(date(2026, 4, 1), level_code="3"),),
        )
    )
    regular = [
        r
        for r in year.period_results
        if r.run is not None and r.run.run_kind is RunKind.REGULAR
    ]
    amounts = {
        sum(
            (i.amount for i in r.pay_items if isinstance(i, SeniorityEarning)),
            Decimal(0),
        )
        for r in regular
    }

    assert len(regular) == 12
    assert amounts == {Decimal("66.10")}
