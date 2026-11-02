"""The NASpI contribution of the run that closes an employment.

Metalmeccanico Federmeccanica C3, hired 1 January 2016 and leaving on 10
March 2026: 36 months of service in the last three years, 3 * 649.73 =
1949.19 (L. 92/2012 art. 2 c. 31, 2026 maximum 1584.70).  Hired 1 June
2025: June 2025 to February 2026, nine months, 649.73 / 12 * 9 = 487.29.
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
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.inputs import (
    CollectiveDismissal,
    EmploymentPeriod,
    FixedTerm,
    NaspiCase,
    NoPensionFund,
    Permanent,
)
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.reconciliation.validators import reconcile
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2016, 1, 1)
_D, _R = TerminationCause.DISMISSAL, TerminationCause.RESIGNATION
_CAPABILITY = "naspi_dismissal"


def _run(
    *,
    cause: TerminationCause | None = _D,
    just: bool | None = False,
    ended: date | None = date(2026, 3, 10),
    hired: date = _HIRED,
    fixed_term: bool = False,
    kind: RunKind = RunKind.REGULAR,
    opening: PeriodState | None = None,
    year: int = 2026,
    month: int = 3,
    case: NaspiCase | CollectiveDismissal | None = None,
) -> PeriodResult:
    period = EmploymentPeriod(hired, ended, cause, just, case) if ended else None
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun(run_kind=kind, month=month, year=year),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_id="metalmeccanico-federmeccanica",
                level_code="C3",
                category=WorkerCategory.IMPIEGATO,
                contract_type=FixedTerm() if fixed_term else Permanent(),
                employment_period=period or EmploymentPeriod(hired),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(),
            opening_state=opening or PeriodState.zero(),
        )
    )


def _contribution(result: PeriodResult) -> list[Decimal]:
    return [
        e.amount
        for e in result.ledger_entries
        if e.account is AccountKind.EMPLOYER_CONTRIBUTIONS
        and e.entry_id.startswith("naspi_dismissal_")
    ]


def _decision_reasons(result: PeriodResult) -> list[str]:
    return [d.reason_code for d in result.decisions if d.capability == _CAPABILITY]


def _limited(result: PeriodResult) -> bool:
    return "naspi_dismissal_case_unknown" in {i.code for i in result.issues}


@pytest.mark.parametrize(
    ("hired", "amount"),
    [(_HIRED, "1949.19"), (date(2025, 6, 1), "487.29")],
)
def test_a_dismissal_posts_the_contribution_on_the_employer(
    hired: date, amount: str
) -> None:
    """An employer contribution entry, in the employer cost, not the net."""
    result = _run(hired=hired)
    (decision,) = (d for d in result.decisions if d.capability == _CAPABILITY)
    (item,) = (i for i in result.pay_items if i.item_id.startswith("naspi_"))
    (entry,) = (e for e in result.ledger_entries if e.pay_item_id == item.item_id)

    assert _contribution(result) == [Decimal(amount)]
    assert (decision.reason_code, decision.amount) == ("due", Decimal(amount))
    assert decision.rule_version == "2026"
    assert decision.inputs == {
        "cause": "dismissal",
        "contract_type": "permanent",
        "ended_on": "2026-03-10",
        "service_months": "36" if hired == _HIRED else "9",
        "rate": Decimal("0.41"),
        "monthly_maximum": Decimal("1584.70"),
    }
    assert (item.kind, item.quantity, item.source) == (
        "employer_contribution_item",
        Decimal(1),
        "L. 92/2012 art. 2 c. 31",
    )
    assert entry.policy_decision_id is not None
    assert result.capability_report.rule_sources[_CAPABILITY] == "verified"
    assert reconcile(result, PeriodState.zero()).ok
    (issue,) = (i for i in result.issues if i.code == "naspi_dismissal_case_unknown")
    assert (issue.fact, issue.status, decision.status) == (
        "naspi_case",
        "provisional",
        "provisional",
    )


def test_the_contribution_is_employer_cost_only() -> None:
    """The net pay is the one of a resignation, the employer cost higher."""
    dismissed, resigned = _run(), _run(cause=_R, just=False)

    assert dismissed.period_net == resigned.period_net
    assert dismissed.period_employer_cost - resigned.period_employer_cost == Decimal(
        "1949.19"
    )


@pytest.mark.parametrize(
    ("cause", "just", "fixed_term"),
    [
        (_R, False, False),
        (TerminationCause.MUTUAL_AGREEMENT, None, False),
        (TerminationCause.DEATH, None, False),
        (_D, False, True),
    ],
)
def test_ends_that_owe_none_decide_nil(
    cause: TerminationCause, just: bool | None, fixed_term: bool
) -> None:
    """A resignation without just cause, a mutual agreement, a death, a term."""
    result = _run(cause=cause, just=just, fixed_term=fixed_term)
    limited = _limited(result)

    (decision,) = (d for d in result.decisions if d.capability == _CAPABILITY)

    assert _contribution(result) == []
    assert (decision.reason_code, decision.amount) == ("not_due", Decimal(0))
    assert decision.inputs.get("just_cause") == ("false" if cause is _R else None)
    assert limited is (cause is not TerminationCause.DEATH and not fixed_term)
    assert decision.status == ("provisional" if limited else "final")


def test_a_resignation_for_just_cause_owes_it() -> None:
    """INPS circ. 44/2013 par. 1."""
    result = _run(cause=_R, just=True)
    (decision,) = (d for d in result.decisions if d.capability == _CAPABILITY)

    assert _contribution(result) == [Decimal("1949.19")]
    assert decision.inputs["just_cause"] == "true"


@pytest.mark.parametrize(
    ("cause", "just", "code", "fact"),
    [
        (None, None, "naspi_dismissal_cause_unknown", "ended_by"),
        (_R, None, "naspi_dismissal_just_cause_unknown", "just_cause"),
    ],
)
def test_an_unstated_cause_is_a_missing_fact(
    cause: TerminationCause | None, just: bool | None, code: str, fact: str
) -> None:
    """Nothing posted, an issue naming the field to state."""
    result = _run(cause=cause, just=just)
    (issue,) = (i for i in result.issues if i.capability == _CAPABILITY)

    assert (issue.code, issue.fact) == (code, fact)
    assert issue.status is CalculationStatus.INCOMPLETE
    assert _contribution(result) == []


def test_a_run_that_does_not_close_the_employment_owes_nothing() -> None:
    """The month before the last: no decision, no issue."""
    result = _run(ended=date(2026, 4, 30), cause=_D)

    assert _decision_reasons(result) == []
    assert not [i for i in result.issues if i.capability == _CAPABILITY]


def test_the_runs_of_earlier_months_leave_it_to_the_last() -> None:
    """February closed before: March, the last month, still posts it."""
    february = _run(ended=date(2026, 3, 10), month=2)
    march = _run(opening=february.closing_state)

    assert _contribution(february) == []
    assert _contribution(march) == [Decimal("1949.19")]


def test_the_termination_run_after_the_last_regular_run_does_not_repeat_it() -> None:
    """The regular run of March closed the employment and posted it."""
    regular = _run()
    termination = _run(kind=RunKind.TERMINATION, opening=regular.closing_state)

    assert _contribution(regular) == [Decimal("1949.19")]
    assert _contribution(termination) == []
    assert _decision_reasons(termination) == []


def test_a_termination_run_without_the_last_day_is_incomplete() -> None:
    """The service is counted to the last day, which is not stated."""
    result = _run(ended=None, kind=RunKind.TERMINATION)
    codes = {i.code for i in result.issues if i.capability == _CAPABILITY}

    assert codes == {"naspi_dismissal_end_unknown"}


def test_a_year_without_the_naspi_maximum_is_a_missing_rule() -> None:
    """2027 has no maximum yet: a dismissal is not computed, a resignation is."""
    dismissed = _run(ended=date(2027, 3, 10), year=2027)
    resigned = _run(ended=date(2027, 3, 10), year=2027, cause=_R, just=False)
    (issue,) = (i for i in dismissed.issues if i.capability == _CAPABILITY)

    assert issue.code == "naspi_dismissal_rule_missing"
    assert _contribution(dismissed) == []
    assert _decision_reasons(resigned) == ["not_due"]


@pytest.mark.parametrize(
    ("cause", "case", "amount"),
    [
        (_D, NaspiCase.ORDINARY, "1949.19"),
        (_R, NaspiCase.PROTECTED_MATERNITY, "1949.19"),
        (TerminationCause.MUTUAL_AGREEMENT, NaspiCase.CONCILIATION, "1949.19"),
        (TerminationCause.MUTUAL_AGREEMENT, NaspiCase.TRANSFER, "1949.19"),
        (_D, NaspiCase.CONTRACTOR_CHANGE, None),
        (_D, NaspiCase.SITE_CLOSURE, None),
    ],
)
def test_a_stated_case_decides_without_limitation(
    cause: TerminationCause, case: NaspiCase, amount: str | None
) -> None:
    """Circ. 44/2013 par. 1 owes it, c. 34 leaves it out; no limitation."""
    result = _run(cause=cause, just=None, case=case)
    (decision,) = (d for d in result.decisions if d.capability == _CAPABILITY)

    assert _contribution(result) == ([Decimal(amount)] if amount else [])
    assert decision.reason_code == ("due" if amount else "not_due")
    assert decision.inputs["naspi_case"] == case.value
    assert "just_cause" not in decision.inputs
    assert not _limited(result)


@pytest.mark.parametrize(
    ("agreement", "cigs", "rate", "amount"),
    [
        (True, False, "0.41", "1949.19"),
        (False, False, "0.41", "5847.57"),
        (True, True, "0.82", "3898.35"),
        (False, True, "0.82", "11695.05"),
    ],
)
def test_a_collective_dismissal(
    agreement: bool,
    cigs: bool,
    rate: str,
    amount: str,
) -> None:
    """82% if the employer owes the CIGS contribution, x3 without agreement.

    L. 205/2017 art. 1 c. 137 and L. 92/2012 art. 2 c. 35; the rules used
    are the ones reported.
    """
    result = _run(case=CollectiveDismissal(agreement, cigs))
    (decision,) = (d for d in result.decisions if d.capability == _CAPABILITY)

    assert _contribution(result) == [Decimal(amount)]
    assert decision.inputs["rate"] == Decimal(rate)
    assert decision.inputs.get("multiplier") == (None if agreement else Decimal(3))
    assert decision.inputs["naspi_case"] == "collective_dismissal"
    assert (decision.inputs["union_agreement"], decision.inputs["cigs_employer"]) == (
        str(agreement).lower(),
        str(cigs).lower(),
    )
    assert not _limited(result)
    assert reconcile(result, PeriodState.zero()).ok
    assert result.capability_report.rule_sources[_CAPABILITY] == (
        "verified" if agreement and not cigs else "derived"
    )
