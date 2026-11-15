"""The exemption of the IVS share of a working mother of three or more.

INPS circ. 27/2024: 100% of the worker's IVS up to 250 EUR a month, "8,06
euro (€ 250/31) per ogni giorno di fruizione" when the employment starts
or ends in the month, not cut for part time.  A commercio 4 worker pays
9.19% IVS on 1,784: 163.95, all exempted; her taxable income rises by it.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment, InvalidInputError
from ccnl_engine.contribution.exemption.inputs import MothersExemption
from ccnl_engine.contribution.exemption.mothers import (
    MOTHERS_COMPONENT,
    with_mother_exemption,
)
from ccnl_engine.contribution.results import (
    ContributionBreakdown,
    ContributionComponent,
)
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    FixedTerm,
    Permanent,
    WeeklyHours,
)
from tests.knowledge.ccnl_engine.irpef.other_income.builders import (
    employment_only,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

_YOUNGEST = date(2015, 4, 2)


def _run(
    exemption: MothersExemption | None,
    *,
    hired: date = date(2025, 1, 1),
    month: int = 1,
    contract: Permanent | FixedTerm | None = None,
) -> PeriodResult:
    employment = Employment(
        ccnl_id="commercio-confcommercio",
        level_code="4",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(hired),
        contract_type=contract or Permanent(),
        mothers_exemption=exemption,
    )
    return regular_period(
        employment=employment, month=month, current_year=employment_only()
    )


def _exempted(result: PeriodResult) -> Decimal:
    return -sum(
        (
            c.amount
            for c in result.contribution_breakdown.components
            if c.name == MOTHERS_COMPONENT
        ),
        Decimal(0),
    )


def test_the_whole_ivs_share_is_exempted() -> None:
    """163.95 of IVS below the 250.00 cap: the employee pays the rest only."""
    plain = _run(None)
    result = _run(MothersExemption(_YOUNGEST))
    ivs = next(
        c for c in plain.contribution_breakdown.components if c.name == "ivs_employee"
    )
    assert _exempted(result) == ivs.amount
    employee = result.contribution_breakdown.employee
    assert employee == plain.contribution_breakdown.employee - ivs.amount
    assert result.period_net > plain.period_net
    (decision,) = (
        d for d in result.decisions if d.reason_code == "mothers_ivs_exemption_applied"
    )
    assert dict(decision.inputs) == {"cap": "250", "code": "ELA3"}
    assert decision.amount == ivs.amount


def test_a_hire_in_the_month_takes_its_days() -> None:
    """Hired on 22 January 2026: 10 days at 8.06, cap 80.60."""
    result = _run(MothersExemption(_YOUNGEST), hired=date(2026, 1, 22))
    assert _exempted(result) <= Decimal("80.60")
    (decision,) = (
        d for d in result.decisions if d.reason_code == "mothers_ivs_exemption_applied"
    )
    assert decision.inputs["cap"] == "80.60"


@pytest.mark.parametrize(
    "youngest",
    [date(2007, 12, 31), date(2007, 12, 1)],
    ids=["eighteen-in-december-2025", "eighteen-on-the-first"],
)
def test_it_ends_with_the_month_the_youngest_turns_eighteen(youngest: date) -> None:
    """The youngest turned eighteen in December 2025: January takes none."""
    result = _run(MothersExemption(youngest))
    assert _exempted(result) == 0
    assert not [d for d in result.decisions if d.capability == "contribution_exemption"]


def test_the_month_of_the_eighteenth_birthday_is_exempted() -> None:
    """Eighteen on 31 January 2026: January is still exempted."""
    assert _exempted(_run(MothersExemption(date(2008, 1, 31)))) > 0


def test_a_fixed_term_contract_is_rejected() -> None:
    """Permanent contracts only."""
    with pytest.raises(InvalidInputError, match="permanent"):
        _run(MothersExemption(_YOUNGEST), contract=FixedTerm())


def test_the_cap_binds_and_nothing_without_ivs() -> None:
    """300.00 of IVS: 250.00 exempted; no IVS component: unchanged."""
    ivs = ContributionComponent(
        "ivs_employee", Decimal(3000), Decimal("0.1"), Decimal(300)
    )
    breakdown = ContributionBreakdown(Decimal(300), Decimal(0), (ivs,))
    cut = with_mother_exemption(Decimal(250), breakdown)
    assert cut.employee == 50
    empty = ContributionBreakdown(Decimal(0), Decimal(0), ())
    assert with_mother_exemption(Decimal(250), empty) is empty
    assert with_mother_exemption(None, breakdown) is breakdown


def test_the_birth_day_must_be_a_date() -> None:
    """A string is rejected."""
    with pytest.raises(InvalidInputError, match="youngest_child_born_on"):
        MothersExemption("2015-04-02")  # type: ignore[arg-type]


def test_domestic_work_is_rejected() -> None:
    """The circular leaves domestic work out."""
    employment = Employment(
        ccnl_id="lavoro-domestico-non-convivente",
        level_code="CS",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(date(2025, 1, 1)),
        weekly_hours=WeeklyHours(Decimal(25)),
        full_time_weekly_hours=WeeklyHours(Decimal(25)),
        contract_type=Permanent(),
        mothers_exemption=MothersExemption(_YOUNGEST),
    )
    with pytest.raises(InvalidInputError, match="domestic"):
        regular_period(
            employment=employment,
            current_year=employment_only(),
            contributable_hours=ContributableHours(Decimal(108)),
        )
