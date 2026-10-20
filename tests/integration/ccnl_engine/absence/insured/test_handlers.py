"""An insured absence in a run: where it may be passed, and without CCNL rules.

Metalmeccanico Federmeccanica C3, 2158.26 EUR a month, daily quota by 26;
the bundle holds no CCNL treatment of a maternity leave or a work injury
for it, so the run pays the statutory amounts and is provisional.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import MaternityLeaveEvent, WorkInjuryEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.run.types import RunKind

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.events import WorkEvent
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2025, 1, 1)
_LEAVE = MaternityLeaveEvent(date(2026, 3, 1), date(2026, 7, 31))
_INJURY = WorkInjuryEvent(date(2026, 3, 10), date(2026, 6, 30))


class _NoAbsenceRules(BundledKnowledgeRepository):
    """The bundle with no absence rule, so no daily quota."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        ccnl = load_ccnl(ccnl_id)
        assert ccnl.work_rules is not None
        rules = ccnl.work_rules.model_copy(update={"absence_rules": None})
        return ccnl.model_copy(update={"work_rules": rules})


def _run(
    event: WorkEvent,
    month: int = 3,
    *,
    run: PayrollRun | None = None,
    hired: date = _HIRED,
    engine: PayrollEngine | None = None,
) -> PeriodResult:
    return (engine or PayrollEngine.bundled()).calculate_period(
        PeriodInput(
            run=run or PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=Employment(
                ccnl_id="metalmeccanico-federmeccanica",
                level_code="C3",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(hired, None),
                seniority=SeniorityFact.since(hired, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=(event,)),
        )
    )


def _decision_of(result: PeriodResult, capability: str) -> tuple[str, object]:
    decision = next(d for d in result.decisions if d.capability == capability)
    return decision.status.value, decision.amount


def test_a_leave_without_ccnl_rules_pays_inps_alone() -> None:
    """March: (2158.26 / 30 + 2158.26 * 2 / 360) * 0.80 * 31 = 1932.84."""
    result = _run(_LEAVE)

    assert _decision_of(result, "maternity_leave") == (
        "provisional",
        Decimal("1932.84"),
    )
    assert "insured_absence_ccnl_not_modelled" in {i.code for i in result.issues}


def test_an_injury_without_ccnl_rules_is_paid_by_inail_itself() -> None:
    """April: the month is deducted in full and INAIL is not advanced."""
    result = _run(_INJURY, 4)

    assert _decision_of(result, "workplace_injury") == ("provisional", Decimal(0))


@pytest.mark.parametrize(
    ("event", "capability"),
    [(_LEAVE, "maternity_leave"), (_INJURY, "workplace_injury")],
)
def test_without_a_daily_quota_nothing_is_posted(
    event: WorkEvent, capability: str
) -> None:
    """The days cannot be deducted: the run is incomplete."""
    result = _run(event, engine=PayrollEngine(repository=_NoAbsenceRules()))

    issue = next(
        i for i in result.issues if i.code == "insured_absence_without_daily_quota"
    )
    assert issue.capability == capability
    assert not any(d.capability == capability for d in result.decisions)


def test_an_event_of_another_month_is_rejected() -> None:
    """A leave of March cannot be passed to the April run."""
    leave = MaternityLeaveEvent(date(2026, 3, 1), date(2026, 3, 15))

    with pytest.raises(InvalidInputError, match="does not touch period"):
        _run(leave, 4)


@pytest.mark.parametrize(
    ("event", "kwargs"),
    [
        (
            MaternityLeaveEvent(date(2026, 3, 1), date(2026, 3, 15)),
            {"hired": date(2026, 3, 20)},
        ),
        (
            WorkInjuryEvent(date(2026, 12, 1), date(2026, 12, 15)),
            {
                "month": 12,
                "run": PayrollRun(run_kind=RunKind.THIRTEENTH, month=12, year=2026),
            },
        ),
    ],
)
def test_an_event_outside_the_monthly_pay_is_rejected(
    event: WorkEvent, kwargs: dict[str, object]
) -> None:
    """Days before the hiring, or a run without monthly pay, pay nothing."""
    with pytest.raises(InvalidInputError, match="monthly pay of a month"):
        _run(event, **kwargs)  # type: ignore[arg-type]
