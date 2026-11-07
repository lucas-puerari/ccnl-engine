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
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import (
    DisabilityPermitEvent,
    ExtraordinaryLeaveEvent,
    HourlyParentalLeaveEvent,
    InpsSicknessBase,
    LeaveHours,
    MaternityLeaveEvent,
    NursingRestEvent,
    ParentalLeaveEvent,
    ParentalLeaveTaken,
    PaternityLeaveEvent,
    WorkInjuryEvent,
)
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


class _NoRuleset(BundledKnowledgeRepository):
    """The bundle with a CCNL file that carries no ruleset identity."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        return load_ccnl(ccnl_id).model_copy(update={"ruleset": None})


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
    (decision,) = (d for d in result.decisions if d.capability == "maternity_leave")
    assert decision.source is None


def test_a_ccnl_without_a_ruleset_is_named_by_its_id_and_year() -> None:
    """No ruleset identity: the rule names the CCNL id, the version the year."""
    result = _run(_LEAVE, engine=PayrollEngine(repository=_NoRuleset()))
    (decision,) = (d for d in result.decisions if d.capability == "maternity_leave")

    assert (decision.rule, decision.rule_version) == (
        "ccnl/metalmeccanico-federmeccanica:work_rules.insured_absence",
        "2026",
    )


def test_an_injury_without_ccnl_rules_is_paid_by_inail_itself() -> None:
    """April: the month is deducted in full and INAIL is not advanced."""
    result = _run(_INJURY, 4)

    assert _decision_of(result, "workplace_injury") == ("provisional", Decimal(0))


@pytest.mark.parametrize(
    ("event", "capability"),
    [
        (_LEAVE, "maternity_leave"),
        (PaternityLeaveEvent((date(2026, 3, 2),)), "paternity_leave"),
        (DisabilityPermitEvent((date(2026, 3, 2),)), "disability_permits"),
        (
            NursingRestEvent(
                (LeaveHours(date(2026, 3, 2), Decimal(2)),), date(2025, 10, 1)
            ),
            "nursing_rests",
        ),
        (
            HourlyParentalLeaveEvent(
                (
                    LeaveHours(date(2026, 3, 2), Decimal(4)),
                    LeaveHours(date(2026, 3, 3), Decimal(4)),
                ),
                date(2025, 10, 1),
                ParentalLeaveTaken(0, 0, 0),
                Decimal(8),
            ),
            "parental_leave",
        ),
        (
            ExtraordinaryLeaveEvent(date(2026, 3, 2), date(2026, 3, 6)),
            "extraordinary_leave",
        ),
        (
            ParentalLeaveEvent(
                date(2026, 3, 2),
                date(2026, 3, 6),
                date(2025, 6, 1),
                ParentalLeaveTaken(0, 0, 0),
            ),
            "parental_leave",
        ),
        (_INJURY, "workplace_injury"),
    ],
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
            PaternityLeaveEvent((date(2026, 3, 2), date(2026, 3, 3))),
            {"hired": date(2026, 3, 20)},
        ),
        (DisabilityPermitEvent((date(2026, 3, 2),)), {"hired": date(2026, 3, 20)}),
        (
            ExtraordinaryLeaveEvent(date(2026, 3, 2), date(2026, 3, 6)),
            {"hired": date(2026, 3, 20)},
        ),
        (
            ParentalLeaveEvent(
                date(2026, 3, 2),
                date(2026, 3, 13),
                date(2025, 6, 1),
                ParentalLeaveTaken(0, 0, 0),
            ),
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
    with pytest.raises(InvalidInputError, match="monthly pay of a month") as error:
        _run(event, **kwargs)  # type: ignore[arg-type]

    assert (error.value.feature, error.value.field) == (
        _CAPABILITY[type(event)],
        type(event).__name__,
    )


_CAPABILITY = {
    MaternityLeaveEvent: "maternity_leave",
    PaternityLeaveEvent: "paternity_leave",
    ParentalLeaveEvent: "parental_leave",
    DisabilityPermitEvent: "disability_permits",
    ExtraordinaryLeaveEvent: "extraordinary_leave",
    WorkInjuryEvent: "workplace_injury",
}
_FEBRUARY = InpsSicknessBase(Decimal("2158.26"), Decimal(0))


def _maternity(category: WorkerCategory, base: InpsSicknessBase | None) -> PeriodResult:
    """Return March 2026 of a C3 worker on maternity leave from 2 March.

    Returns:
        The result of the run.
    """
    leave = MaternityLeaveEvent(
        date(2026, 3, 2), date(2026, 7, 31), maternity_base_pay=base
    )
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="metalmeccanico-federmeccanica",
                level_code="C3",
                category=category,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=(leave,)),
        )
    )


def _indemnity(result: PeriodResult) -> Decimal:
    return next(i.amount for i in result.pay_items if i.kind == "maternity_item")


def test_an_impiegata_is_paid_on_the_pay_of_the_month_before() -> None:
    """Art. 23 c. 4: (2158.26 + 2158.26 / 12) / 30 = 77.9372; 30 days at 80%.

    0.80 * 77.937167 * 30 = 1870.49.
    """
    result = _maternity(WorkerCategory.IMPIEGATO, _FEBRUARY)

    assert _indemnity(result) == Decimal("1870.49")
    assert "maternity_daily_base" not in {lim.id for lim in result.limitations}
    assert "maternity_base_pay_unknown" not in {i.code for i in result.issues}


def test_an_impiegata_without_the_pay_before_lacks_a_fact() -> None:
    """The base is a fact of the payroll history: its absence blocks."""
    result = _maternity(WorkerCategory.IMPIEGATO, None)

    assert ("missing_fact", "maternity_base_pay") in {
        (b.code, b.detail) for b in result.blockers
    }
    (issue,) = (i for i in result.issues if i.code == "maternity_base_pay_unknown")
    assert issue.message == (
        "INPS pays the indemnity on the pay of the month before the leave "
        "(MaternityLeaveEvent.maternity_base_pay), which the leave does not "
        "state; the indemnity is computed on the pay of the run meanwhile"
    )


def test_an_operaia_keeps_the_pay_of_the_run_under_a_limitation() -> None:
    """Art. 23 c. 5 is not computed: the engine says so."""
    result = _maternity(WorkerCategory.OPERAIO, _FEBRUARY)

    assert "maternity_daily_base" in {lim.id for lim in result.limitations}
