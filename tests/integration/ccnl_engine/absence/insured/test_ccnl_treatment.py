"""Insured absences under the Chimica CCNL, which tops the insurer share up.

Impiegato D1, injured on Monday 2 March 2026 and unable to work to 13 March.
INAIL pays on the weekly earnings of the full-time hours: stated at 38
instead of the default 40, its share is 38/40 of it, 431.59 x 0.95 = 410.01,
and the CCNL top-up grows by the difference.

A maternity leave of March on February's 2,500.00: INPS pays (2,500 +
2,500 / 12) / 30 x 80% x 31 = 2,238.89 (art. 22-23 D.Lgs. 151/2001), and
the CCNL tops it up to the whole pay of the month, 2,360.26 - 2,238.89.
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
from ccnl_engine.events import (
    ExtraordinaryLeaveEvent,
    InpsSicknessBase,
    MaternityLeaveEvent,
    ParentalLeaveEvent,
    ParentalLeaveTaken,
    WorkInjuryEvent,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
    WorkerCategory,
)
from ccnl_engine.pay_item.facade import (
    AbsenceDeduction,
    AbsenceIntegrationItem,
    MaternityItem,
    WorkInjuryItem,
)

if TYPE_CHECKING:
    from ccnl_engine.events import WorkEvent
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2025, 1, 1)
_INJURY = WorkInjuryEvent(date(2026, 3, 2), date(2026, 3, 13))


def _run(
    full_time: WeeklyHours | None = None, event: WorkEvent = _INJURY
) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="chimica-farmaceutica-federchimica",
                level_code="D1",
                category=WorkerCategory.IMPIEGATO,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
                full_time_weekly_hours=full_time,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=(event,)),
        )
    )


@pytest.mark.parametrize(
    ("full_time", "inail", "top_up"),
    [
        (None, Decimal("431.59"), Decimal("170.55")),
        (WeeklyHours(Decimal(38)), Decimal("410.01"), Decimal("194.39")),
    ],
)
def test_inail_pays_on_the_full_time_hours(
    full_time: WeeklyHours | None, inail: Decimal, top_up: Decimal
) -> None:
    """The deduction and the carenza hold; INAIL and the top-up move."""
    result = _run(full_time)
    (decision,) = (d for d in result.decisions if d.capability == "workplace_injury")

    assert (decision.inputs["indemnity"], decision.inputs["integration"]) == (
        inail,
        top_up,
    )
    assert (decision.inputs["deduction"], decision.inputs["carenza"]) == (
        Decimal("971.08"),
        Decimal("323.69"),
    )


def test_the_lines_of_the_injury() -> None:
    """A deduction, then the carenza, INAIL and the top-up paid in cash."""
    result = _run()
    (decision,) = (d for d in result.decisions if d.capability == "workplace_injury")
    entries = {
        e.entry_id.split("_2026")[0] + "_" + e.entry_id.rsplit("_", 1)[1]: (
            e.policy_decision_id,
            e.amount,
        )
        for e in result.ledger_entries
        if "_evt0_" in e.entry_id
    }
    items = {i.item_id.rsplit("_", 1)[1]: i for i in result.pay_items}

    assert entries == {
        "deduction_abs": ("it/indemnity/absence_integration", Decimal("971.08")),
        "cash_crnz": ("it/indemnity/absence_integration", Decimal("323.69")),
        "cash_inail": ("it/indemnity/work_injury", Decimal("431.59")),
        "cash_intg": ("it/indemnity/absence_integration", Decimal("170.55")),
    }
    assert isinstance(items["abs"], AbsenceDeduction)
    assert isinstance(items["inail"], WorkInjuryItem)
    assert {items[k].quantity for k in ("crnz", "inail", "intg")} == {Decimal(1)}
    ruleset = load_ccnl("chimica-farmaceutica-federchimica").ruleset
    assert ruleset is not None
    assert (decision.rule, decision.rule_version) == (
        f"{ruleset.id}:work_rules.insured_absence",
        ruleset.version,
    )
    assert decision.source is not None
    assert (decision.status.value, decision.reason_code, decision.amount) == (
        "final",
        "ccnl_treatment_applied",
        Decimal("431.59") + Decimal("170.55") + Decimal("323.69"),
    )
    assert decision.inputs == {
        "first_day": "2026-03-02",
        "last_day": "2026-03-13",
        "deduction": Decimal("971.08"),
        "indemnity": Decimal("431.59"),
        "indemnity_advanced": "yes",
        "integration": Decimal("170.55"),
        "carenza": Decimal("323.69"),
    }
    assert "insured_absence_ccnl_not_modelled" not in {i.code for i in result.issues}


def test_a_maternity_leave_is_topped_up_to_the_whole_pay() -> None:
    """INPS 80% on February's pay, the CCNL the rest of March's pay."""
    leave = MaternityLeaveEvent(
        date(2026, 3, 1),
        date(2026, 3, 31),
        InpsSicknessBase(Decimal(2500), Decimal(0)),
    )
    result = _run(event=leave)
    (decision,) = (d for d in result.decisions if d.capability == "maternity_leave")
    items = {i.item_id.rsplit("_", 1)[1]: i for i in result.pay_items}

    assert (decision.reason_code, decision.amount) == (
        "ccnl_treatment_applied",
        Decimal("2360.26"),
    )
    assert (decision.inputs["indemnity"], decision.inputs["integration"]) == (
        Decimal("2238.89"),
        Decimal("121.37"),
    )
    assert isinstance(items["abs"], AbsenceDeduction)
    assert isinstance(items["inps"], MaternityItem)
    assert isinstance(items["intg"], AbsenceIntegrationItem)
    work = load_ccnl("chimica-farmaceutica-federchimica").work_rules
    assert work is not None
    assert work.insured_absence is not None
    assert work.insured_absence.maternity is not None
    assert decision.source == work.insured_absence.maternity.provenance.location
    assert "insured_absence_ccnl_not_modelled" not in {i.code for i in result.issues}


def _tfr(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("tfr_2026")),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("event", "quota"),
    [
        # Art. 2120 c. 3 c.c.: the causes of art. 2110 keep the pay the
        # worker would have had; the indemnities bear no 0.50% IVS.
        (
            MaternityLeaveEvent(
                date(2026, 3, 1),
                date(2026, 3, 31),
                InpsSicknessBase(Decimal(2500), Decimal(0)),
            ),
            Decimal("174.22"),
        ),
        (_INJURY, Decimal("165.41")),
        # Parental and extraordinary leave are no cause of art. 2110: the
        # days of leave leave the TFR base (art. 42 c. 5-quinquies says so
        # of the extraordinary leave).
        (
            ParentalLeaveEvent(
                date(2026, 3, 2),
                date(2026, 3, 13),
                date(2025, 6, 1),
                ParentalLeaveTaken(0, 0, 0),
            ),
            Decimal("88.50"),
        ),
        (
            ExtraordinaryLeaveEvent(date(2026, 3, 2), date(2026, 3, 13), Decimal(2500)),
            Decimal("88.50"),
        ),
    ],
)
def test_the_tfr_base_of_each_absence(event: WorkEvent, quota: Decimal) -> None:
    """A full March accrues 2,360.26 / 13.5 less its 0.50% IVS: 163.03."""
    assert _tfr(_run(event=event)) == quota
