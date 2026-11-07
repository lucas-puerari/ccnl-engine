"""Garnishments and salary assignments on the payslips of a Metalmeccanico C3.

The engine withholds them last, from the net pay, carries what it withheld
in the closing state across runs and tax years, and reports at the end of
the employment what is still due.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_DOWN, Decimal
from typing import TYPE_CHECKING

from ccnl_engine.balance.cash.models import TaxCashState
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.balance.obligation.models import EmploymentObligations
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.events import TerminationTFREvent
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.services import _sum_ledger
from ccnl_engine.period.services import bundled_policies, bundled_repository
from ccnl_engine.personal_withholding.inputs import (
    PersonalWithholding,
    PersonalWithholdingKind,
)
from ccnl_engine.personal_withholding.limit.rules import ASSIGNMENT_LIMIT, FIFTH_LIMIT
from ccnl_engine.personal_withholding.models import WithheldToDate
from ccnl_engine.personal_withholding.services import SAME_KIND
from ccnl_engine.year.competence.services import calculate_competence_year
from ccnl_engine.year.tax_year.closing.rules import close_tax_year
from tests.unit.ccnl_engine.builders import year_plan

if TYPE_CHECKING:
    from ccnl_engine.decision.models import CalculationDecision
    from ccnl_engine.period.results import PeriodResult
    from ccnl_engine.year.results import CompetenceYearResult

_YEAR = 2026
_ASSIGNMENT = PersonalWithholding(
    "cessione",
    PersonalWithholdingKind.SALARY_ASSIGNMENT,
    date(_YEAR, 1, 10),
    date(_YEAR, 2, 1),
    Decimal(3000),
    Decimal(250),
)
_GARNISHMENT = PersonalWithholding(
    "pignoramento",
    PersonalWithholdingKind.ORDINARY,
    date(_YEAR, 3, 1),
    date(_YEAR, 3, 1),
    Decimal(1000),
)


def _year(
    *withholdings: PersonalWithholding,
    opening: PeriodState | None = None,
    employment_period: EmploymentPeriod | None = None,
    events: dict[int, tuple[TerminationTFREvent, ...]] | None = None,
) -> CompetenceYearResult:
    return calculate_competence_year(
        year_plan(
            _YEAR,
            "metalmeccanico-federmeccanica",
            "C3",
            personal_withholdings=withholdings,
            opening_state=opening,
            employment_period=employment_period,
            events=events,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _assigned_and_garnished() -> CompetenceYearResult:
    return _year(_ASSIGNMENT, _GARNISHMENT)


def _decisions(result: PeriodResult) -> dict[str, CalculationDecision]:
    return {
        str(d.inputs["withholding_id"]): d
        for d in result.decisions
        if d.capability == "personal_withholdings"
    }


def _withheld(result: PeriodResult) -> dict[str, Decimal]:
    return {
        w.withholding_id: w.withheld
        for w in result.closing_state.cash.obligations.personal_withholdings
    }


def test_the_garnishment_takes_a_fifth_of_the_net_beside_the_assignment() -> None:
    """March: cessione 250, then a fifth of the net before both."""
    march = _assigned_and_garnished().period_results[2]
    decisions = _decisions(march)
    base = decisions["pignoramento"].inputs["net_base"]
    assert isinstance(base, Decimal)

    assert decisions["cessione"].amount == Decimal(250)
    assert decisions["pignoramento"].amount == (base / 5).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )
    assert march.period_net == base - 250 - decisions["pignoramento"].amount
    assert _sum_ledger(march.ledger_entries, AccountKind.PERSONAL_WITHHOLDINGS) == (
        250 + decisions["pignoramento"].amount
    )
    assert SAME_KIND not in {lim.id for lim in march.limitations}


def test_the_residual_is_carried_until_the_garnishment_is_paid() -> None:
    """The garnishment stops at 1,000; the cessione skips the tredicesima."""
    runs = _assigned_and_garnished().period_results
    december, thirteenth = runs[-2], runs[-1]

    assert _withheld(december) == {
        "cessione": Decimal(2750),
        "pignoramento": Decimal("1000.00"),
    }
    assert _decisions(thirteenth) == {}
    assert _withheld(thirteenth) == _withheld(december)
    assert close_tax_year(
        thirteenth.closing_state
    ).cash.obligations.personal_withholdings == (
        thirteenth.closing_state.cash.obligations.personal_withholdings
    )


def test_a_new_year_withholds_what_the_old_one_left() -> None:
    """2,900 of 3,000 withheld before: January takes the last 100."""
    opening = PeriodState(
        cash=TaxCashState(
            tax_year=_YEAR,
            obligations=EmploymentObligations(
                personal_withholdings=(WithheldToDate("cessione", Decimal(2900)),)
            ),
        )
    )
    assignment = PersonalWithholding(
        "cessione",
        PersonalWithholdingKind.SALARY_ASSIGNMENT,
        date(_YEAR - 1, 1, 10),
        date(_YEAR - 1, 2, 1),
        Decimal(3000),
        Decimal(250),
    )
    january, february = _year(assignment, opening=opening).period_results[:2]

    assert _decisions(january)["cessione"].amount == Decimal(100)
    assert _decisions(february) == {}
    assert _withheld(february) == {"cessione": Decimal(3000)}


def test_two_garnishments_of_one_kind_share_the_fifth() -> None:
    """The later order waits for the earlier one, under a limitation."""
    later = PersonalWithholding(
        "pignoramento_2",
        PersonalWithholdingKind.ORDINARY,
        date(_YEAR, 3, 2),
        date(_YEAR, 3, 2),
        Decimal(500),
    )
    march = _year(_GARNISHMENT, later).period_results[2]

    assert _decisions(march)["pignoramento_2"].reason_code == "nothing_withheld"
    assert SAME_KIND in {lim.id for lim in march.limitations}


def test_the_end_of_the_employment_reports_the_residual() -> None:
    """The cessione ends with the employment; the TFR is left to the caller."""
    result = _year(
        _ASSIGNMENT,
        employment_period=EmploymentPeriod(date(2020, 1, 1), date(_YEAR, 6, 30)),
    )
    last = result.period_results[-1]
    (issue,) = (i for i in last.issues if i.code == "personal_withholding_residual")

    assert "1750 of the salary_assignment cessione" in issue.message
    assert last.closing_state.cash.obligations.personal_withholdings == ()


def test_each_decision_records_its_base_limit_and_residual() -> None:
    """March: the cessione first (notified 10 January), then the garnishment."""
    march = _assigned_and_garnished().period_results[2]
    decisions = _decisions(march)
    assignment, garnishment = decisions["cessione"], decisions["pignoramento"]
    base = assignment.inputs["net_base"]
    assert isinstance(base, Decimal)
    fifth = (base / 5).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    (line,) = (
        e
        for e in march.ledger_entries
        if e.account is AccountKind.PERSONAL_WITHHOLDINGS
        and e.pay_item_id.startswith("personal_withholding_cessione")
    )
    (item,) = (i for i in march.pay_items if i.item_id == line.pay_item_id)

    assert assignment.inputs == {
        "withholding_id": "cessione",
        "kind": "salary_assignment",
        "notified_on": "2026-01-10",
        "net_base": base,
        "legal_limit": fifth,
        "installment": Decimal(250),
        "residual_before": Decimal(2750),
        "residual_after": Decimal(2500),
    }
    assert (assignment.rule, assignment.rule_version, assignment.source) == (
        ASSIGNMENT_LIMIT.rule,
        "2026",
        ASSIGNMENT_LIMIT.source,
    )
    assert (garnishment.inputs["installment"], garnishment.rule) == (
        "none",
        FIFTH_LIMIT.rule,
    )
    assert garnishment.amount is not None
    assert garnishment.inputs["residual_after"] == Decimal(1000) - garnishment.amount
    assert (item.quantity, line.amount) == (Decimal(1), Decimal(250))
    assert line.policy_decision_id is not None


def test_a_deduction_starts_on_its_day() -> None:
    """Starting on 28 February, the payment day: February withholds it."""
    starting = PersonalWithholding(
        "dal_28",
        PersonalWithholdingKind.ORDINARY,
        date(_YEAR, 2, 1),
        date(_YEAR, 2, 28),
        Decimal(100),
    )
    january, february = _year(starting).period_results[:2]

    assert _decisions(january) == {}
    assert _decisions(february)["dal_28"].amount == Decimal(100)


def test_a_run_that_does_not_state_a_deduction_keeps_its_history() -> None:
    """Nothing is withheld without the order, and what was withheld stays."""
    opening = PeriodState(
        cash=TaxCashState(
            tax_year=_YEAR,
            obligations=EmploymentObligations(
                personal_withholdings=(WithheldToDate("cessione", Decimal(100)),)
            ),
        )
    )
    january = _year(opening=opening).period_results[0]

    assert _decisions(january) == {}
    assert _withheld(january) == {"cessione": Decimal(100)}


def test_the_tfr_settled_is_out_of_the_base() -> None:
    """June, the last month: the TFR paid in the run leaves the base as is."""
    period = EmploymentPeriod(date(2020, 1, 1), date(_YEAR, 6, 30))
    tfr = TerminationTFREvent(
        date(_YEAR, 6, 30), Decimal(9000), separate_tax_rate=Decimal("0.23")
    )
    garnishment = PersonalWithholding(
        "pignoramento",
        PersonalWithholdingKind.ORDINARY,
        date(_YEAR, 6, 1),
        date(_YEAR, 6, 1),
        Decimal(5000),
    )
    without = _year(garnishment, employment_period=period).period_results[5]
    settled = _year(
        garnishment, employment_period=period, events={6: (tfr,)}
    ).period_results[5]
    base = _decisions(without)["pignoramento"].inputs["net_base"]

    assert _decisions(settled)["pignoramento"].inputs["net_base"] == base
