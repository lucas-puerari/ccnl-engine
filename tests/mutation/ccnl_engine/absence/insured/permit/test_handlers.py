"""The permits to assist a disabled person, paid back in full by INPS.

Metalmeccanico Federmeccanica C3 impiegato, 2158.26 EUR a month, daily
quota by 26.  Three days of permit, 2-4 March 2026: deduction 2158.26 * 3 /
26 = 249.03, paid back in full as the INPS indemnity (art. 43 D.Lgs.
151/2001), out of the INPS base (art. 44 c. 2).  Four hours of permit
are the hourly pay: 2158.26 * 4 / 173 = 49.90; hired in 2018 with a
superminimo of 100, (2158.26 + 4 * 29.64 + 100) * 4 / 173 = 54.96.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.compensation.individual.inputs import IndividualElement
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.events import DisabilityPermitEvent, LeaveHours, WorkEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.pay_item.facade import AbsenceDeduction, MaternityItem

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2025, 1, 1)
_PERMITS = DisabilityPermitEvent((date(2026, 3, 2), date(2026, 3, 3), date(2026, 3, 4)))


def _run(
    *events: WorkEvent,
    hired: date = _HIRED,
    individual: tuple[IndividualElement, ...] = (),
    ccnl: tuple[str, str] = ("metalmeccanico-federmeccanica", "C3"),
) -> PeriodResult:
    """Return March 2026 with ``events``.

    Returns:
        The result of the run.
    """
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id=ccnl[0],
                level_code=ccnl[1],
                category=WorkerCategory.IMPIEGATO,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(hired, None),
                seniority=SeniorityFact.since(hired, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
                individual_elements=individual,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=events),
        )
    )


def _amounts(result: PeriodResult) -> dict[str, tuple[str, Decimal, Decimal]]:
    return {
        i.kind: (i.item_id.rsplit("_", 1)[-1], i.amount, i.absence_days)
        for i in result.pay_items
        if isinstance(i, AbsenceDeduction | MaternityItem)
    }


def _ivs_base(result: PeriodResult) -> Decimal:
    components = result.contribution_breakdown.components
    (base,) = (c.base for c in components if c.name == "ivs_employee")
    return base


def _tfr(result: PeriodResult) -> Decimal:
    (amount,) = (d.amount for d in result.decisions if d.capability == "tfr")
    assert amount is not None
    return amount


def test_three_days_are_paid_back_in_full() -> None:
    """The deduction at the CCNL quota, the same amount from INPS."""
    result = _run(_PERMITS)

    assert _amounts(result) == {
        "absence_deduction": ("abs", Decimal("249.03"), Decimal(3)),
        "maternity_item": ("inps", Decimal("249.03"), Decimal(3)),
    }
    (decision,) = (d for d in result.decisions if d.capability == "disability_permits")
    assert (decision.amount, decision.status) == (Decimal("249.03"), "final")


def test_the_days_leave_the_inps_base_and_keep_the_rest() -> None:
    """Figurative contributions; 13th, leave and TFR unchanged."""
    worked, away = _run(), _run(_PERMITS)

    # INPS base in whole euros: 2158.26 and 2158.26 - 249.03 = 1909.23.
    assert (_ivs_base(worked), _ivs_base(away)) == (Decimal(2158), Decimal(1909))
    assert away.extra_months == worked.extra_months
    assert away.closing_state.accrual.leave == worked.closing_state.accrual.leave
    # The TFR base is kept; its quota is net of the 0.50% IVS contribution
    # (art. 3 L. 297/1982), whose base fell by 249: 0.005 * 249 = 1.24.
    assert _tfr(away) - _tfr(worked) == Decimal("1.24")
    assert "disability_permit_tfr" in {lim.id for lim in away.limitations}


def test_a_sunday_of_permit_deducts_nothing() -> None:
    """A day the CCNL does not pay has no pay to replace."""
    result = _run(DisabilityPermitEvent((date(2026, 3, 8),)))

    assert _amounts(result) == {}


def test_hours_of_permit_are_paid_back_at_the_hourly_pay() -> None:
    """Four hours beside one whole day: a line of each, the hours by 173."""
    hours = (LeaveHours(date(2026, 3, 3), Decimal(4)),)
    result = _run(DisabilityPermitEvent((date(2026, 3, 2),), hours))

    lines = {
        i.item_id.rsplit("_", 1)[-1]: (i.amount, i.absence_days)
        for i in result.pay_items
        if isinstance(i, AbsenceDeduction | MaternityItem)
    }
    assert lines == {
        "abs": (Decimal("83.01"), Decimal(1)),
        "inps": (Decimal("83.01"), Decimal(1)),
        "abshours": (Decimal("49.90"), Decimal(4)),
        "inpshours": (Decimal("49.90"), Decimal(4)),
    }
    (decision,) = (d for d in result.decisions if d.capability == "disability_permits")
    assert (decision.amount, decision.inputs["deduction"]) == (
        Decimal("132.91"),
        Decimal("132.91"),
    )


def test_an_hour_holds_the_seniority_and_the_individual_elements() -> None:
    """Four steps and a superminimo enter the hourly pay: 54.96.

    The hours of 1 April belong to the April run.
    """
    hours = (
        LeaveHours(date(2026, 3, 31), Decimal(4)),
        LeaveHours(date(2026, 4, 1), Decimal(2)),
    )
    result = _run(
        DisabilityPermitEvent((), hours),
        hired=date(2018, 1, 1),
        individual=(IndividualElement("superminimo", Decimal("100.00")),),
    )

    assert {
        i.item_id.rsplit("_", 1)[-1]: i.amount
        for i in result.pay_items
        if isinstance(i, AbsenceDeduction | MaternityItem)
    } == {"abshours": Decimal("54.96"), "inpshours": Decimal("54.96")}


def test_hours_without_a_verified_hourly_base_post_nothing() -> None:
    """Chimica PMI has no verified hourly base: the day is paid, not the hours."""
    hours = (LeaveHours(date(2026, 3, 3), Decimal(4)),)
    result = _run(
        DisabilityPermitEvent((date(2026, 3, 2),), hours),
        ccnl=("chimica-affini-pmi-unionchimica", "D"),
    )

    assert set(_amounts(result)) == {"absence_deduction", "maternity_item"}
    assert not {"abshours", "inpshours"} & {
        i.item_id.rsplit("_", 1)[-1] for i in result.pay_items
    }
    (issue,) = (i for i in result.issues if i.capability == "disability_permits")
    assert (issue.code, issue.status) == (
        "disability_permit_hours_underived",
        "incomplete",
    )
    assert "has no verified hourly base" in issue.message
    (decision,) = (d for d in result.decisions if d.capability == "disability_permits")
    assert (decision.status, decision.reason_code, decision.amount) == (
        "incomplete",
        "disability_permit_hours_underived",
        Decimal("87.19"),  # the day only: 2267.00 / 26
    )
