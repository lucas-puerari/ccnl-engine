"""The contribution exemption of a run, through the public facade.

A commercio 4 worker hired on 1 January 2026, terziario above fifteen
employees: employer contributions 537.22 on a base of 1,784, of which
0.83333% (14.87) is the continuing training and the FIS no exemption cuts
(INPS circ. 82/2026 p. 5).  The young measure exempts the other 522.35 up
to 500.00 (DL 60/2024 art. 22), 70% of it without a net headcount growth.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment, InvalidInputError
from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.contribution.exemption.inputs import (
    ContributionExemption,
    ExemptionMeasure,
)
from ccnl_engine.contribution.exemption.services import (
    EXCLUSION_UNKNOWN,
    EXEMPTION_COMPONENT,
    OTHER_RUN,
    ExemptionRun,
    with_exemption,
)
from ccnl_engine.contribution.results import (
    ContributionBreakdown,
    ContributionComponent,
)
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.inputs import (
    Apprentice,
    ContributableHours,
    EmploymentPeriod,
    FixedTerm,
    Permanent,
    WeeklyHours,
)
from ccnl_engine.sector.loaders import load_year_rules
from tests.knowledge.ccnl_engine.irpef.other_income.builders import (
    employment_only,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

_HIRED = date(2026, 1, 1)


def _run(
    exemption: ContributionExemption | None,
    *,
    hired: date = _HIRED,
    month: int = 1,
    **kwargs: object,
) -> PeriodResult:
    fields: dict[str, object] = {
        "ccnl_id": "commercio-confcommercio",
        "level_code": "4",
        "seniority": new_hire(),
        "employment_period": EmploymentPeriod(hired),
        "contract_type": Permanent(),
        "contribution_exemption": exemption,
        **kwargs,
    }
    employment = Employment(**fields)  # type: ignore[arg-type]
    return regular_period(
        employment=employment, month=month, current_year=employment_only()
    )


def _exempted(result: PeriodResult) -> Decimal:
    return -sum(
        (
            c.amount
            for c in result.contribution_breakdown.components
            if c.name == EXEMPTION_COMPONENT
        ),
        Decimal(0),
    )


def _decision_inputs(result: PeriodResult) -> dict[str, Decimal | str] | None:
    found = [d for d in result.decisions if d.capability == "contribution_exemption"]
    return None if not found else dict(found[0].inputs)


def test_the_young_measure_takes_its_cap() -> None:
    """522.35 exempted up to 500.00: 37.22 left, code EG35."""
    plain = _run(None)
    result = _run(ContributionExemption(ExemptionMeasure.YOUNG, _HIRED))
    assert plain.contribution_breakdown.employer == Decimal("537.22")
    assert _exempted(result) == Decimal("500.00")
    assert result.contribution_breakdown.employer == Decimal("37.22")
    assert result.period_employer_cost == plain.period_employer_cost - 500
    assert result.period_net == plain.period_net
    assert _decision_inputs(result) == {
        "measure": "young",
        "share": "1",
        "cap": "500.00",
        "code": "EG35",
    }
    assert _decision_inputs(plain) is None


def test_seventy_percent_without_growth() -> None:
    """522.35 x 0.7 = 365.65, below the cap."""
    exemption = ContributionExemption(
        ExemptionMeasure.YOUNG, _HIRED, share=Decimal("0.7")
    )
    assert _exempted(_run(exemption)) == Decimal("365.65")


def test_a_hire_in_the_month_takes_its_days() -> None:
    """Mothers hired on 16 January: 21.50 x 16 = 344.00 caps the half month."""
    start = date(2026, 1, 16)
    result = _run(ContributionExemption(ExemptionMeasure.MOTHERS, start), hired=start)
    assert _decision_inputs(result) is not None
    exempted = _exempted(result)
    assert exempted <= Decimal("344.00")
    assert result.contribution_breakdown.employer > 0


def test_a_part_time_worker_takes_a_cut_cap() -> None:
    """20 of 40 hours: the 650.00 of the women halved, 325.00."""
    result = _run(
        ContributionExemption(ExemptionMeasure.WOMEN, _HIRED),
        weekly_hours=WeeklyHours(Decimal(20)),
        full_time_weekly_hours=WeeklyHours(Decimal(40)),
    )
    inputs = _decision_inputs(result)
    assert inputs is not None
    assert inputs["cap"] == "325.00"
    assert _exempted(result) <= Decimal("325.00")


def test_the_months_end() -> None:
    """A fixed-term mother: 12 months from January 2025 end in December."""
    exemption = ContributionExemption(ExemptionMeasure.MOTHERS, date(2025, 1, 1))
    result = _run(exemption, hired=date(2025, 1, 1), contract_type=FixedTerm())
    assert _decision_inputs(result) is None
    assert _exempted(result) == 0


@pytest.mark.parametrize(
    ("exemption", "kwargs", "message"),
    [
        (
            ContributionExemption(ExemptionMeasure.YOUNG, _HIRED),
            {"contract_type": Apprentice(months_elapsed=0, track="livelli_2_5")},
            "apprentice",
        ),
        (
            ContributionExemption(ExemptionMeasure.ZES, _HIRED),
            {"category": WorkerCategory.DIRIGENTE},
            "dirigenti",
        ),
        (
            ContributionExemption(ExemptionMeasure.YOUNG, date(2026, 5, 4)),
            {},
            "until 2026-04-30",
        ),
    ],
)
def test_an_excluded_worker_or_hire_is_rejected(
    exemption: ContributionExemption, kwargs: dict[str, object], message: str
) -> None:
    """Apprentices, the dirigenti of young and ZES, late hires."""
    hired = min(exemption.start, _HIRED)
    with pytest.raises(InvalidInputError, match=message):
        _run(
            exemption,
            hired=hired,
            month=5 if exemption.start.month == 5 else 1,
            **kwargs,
        )


def test_an_open_category_is_reported() -> None:
    """A terziario dirigente: the rate table does not break their rate down."""
    result = _run(
        ContributionExemption(ExemptionMeasure.WOMEN, _HIRED),
        category=WorkerCategory.DIRIGENTE,
    )
    assert _exempted(result) == 0
    assert EXCLUSION_UNKNOWN in {i.code for i in result.issues}


_BREAKDOWN = ContributionBreakdown(Decimal(100), Decimal(300), ())
_RUN = ExemptionRun(
    measure=ContributionExemption(ExemptionMeasure.YOUNG, _HIRED).measure,
    share=Decimal(1),
    cap=Decimal(500),
    code="EG35",
)


def test_a_separate_run_takes_none() -> None:
    """A tredicesima run leaves the cap to the regular run of the month."""
    cut, issues = with_exemption(replace(_RUN, monthly=False), None, None, _BREAKDOWN)
    assert cut is _BREAKDOWN
    assert [i.code for i in issues] == [OTHER_RUN]


def test_nothing_to_cut() -> None:
    """No exemption, or no employer contribution: unchanged, no issue."""
    assert with_exemption(None, None, None, _BREAKDOWN) == (_BREAKDOWN, ())
    empty = ContributionBreakdown(Decimal(0), Decimal(0), ())
    assert with_exemption(_RUN, None, None, empty) == (empty, ())


def test_domestic_work_is_rejected() -> None:
    """The exemptions are for the private employers of INPS sectors."""
    employment = Employment(
        ccnl_id="lavoro-domestico-non-convivente",
        level_code="CS",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(_HIRED),
        weekly_hours=WeeklyHours(Decimal(25)),
        full_time_weekly_hours=WeeklyHours(Decimal(25)),
        contract_type=Permanent(),
        contribution_exemption=ContributionExemption(ExemptionMeasure.WOMEN, _HIRED),
    )
    with pytest.raises(InvalidInputError, match="private employers"):
        regular_period(
            employment=employment,
            current_year=employment_only(),
            contributable_hours=ContributableHours(Decimal(108)),
        )


def test_all_excluded_leaves_nothing_to_exempt() -> None:
    """A base whose whole contribution is excluded exempts nothing."""
    inps = load_year_rules(2026, TaxSector.TERZIARIO, 20).inps
    assert inps is not None
    breakdown = ContributionBreakdown(
        Decimal(0),
        Decimal("8.33"),
        (
            ContributionComponent(
                "non_ivs_employer", Decimal(1000), Decimal(1), Decimal("8.33")
            ),
        ),
    )
    assert with_exemption(_RUN, inps, None, breakdown) == (breakdown, ())
