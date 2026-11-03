"""The trattamento integrativo speciale on a Turismo Federalberghi payslip.

Level 4, March 2026, a tourism employer, 2025 income 30,000, requested:
6 night hours on 1660.69 / 172 = 9.6552 an hour, premium 14.48: base 72.41,
15% = 10.86; 2 h of holiday overtime 25.10, 15% = 3.77.  The supplement is
not income: the net pay grows by 14.63, posted on the credits account with
codice tributo 1702.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import NightShiftEvent, OvertimeEvent, OvertimeKind
from ccnl_engine.inputs import PriorYearTaxFacts
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.reconciliation.validators import reconcile
from ccnl_engine.regime.models import EmployerActivity
from ccnl_engine.run.types import PeriodId

_EVENTS = (
    NightShiftEvent(date(2026, 3, 10), hours=Decimal(6)),
    OvertimeEvent(date(2026, 3, 8), Decimal(2), kind=OvertimeKind.HOLIDAY),
)
_REQUEST = PeriodCalculationRequest(
    employer=EmployerProfile(
        headcount=Headcount(20), activity=EmployerActivity.TOURISM
    ),
    period_id=PeriodId(2026, 3),
    payment_date=date(2026, 3, 27),
    ccnl_id="turismo-federalberghi",
    level_code="4",
    opening_state=PeriodState.zero(),
    roles=frozenset(),
    events=_EVENTS,
    prior_year=PriorYearTaxFacts(
        employment_income=Decimal(30_000), special_supplement_requested=True
    ),
)


def _run(request: PeriodCalculationRequest = _REQUEST) -> PeriodResult:
    result = calculate_period(
        request, repo=bundled_repository(), resolver=bundled_policies()
    )
    assert isinstance(result, PeriodResult)
    return result


def test_the_supplement_is_a_credit_out_of_income() -> None:
    """10.86 and 3.77 on the credits account, code 1702, net + 14.63."""
    paid = _run()
    none = _run(replace(_REQUEST, prior_year=PriorYearTaxFacts(Decimal(30_000))))
    credited = [
        (e.amount, e.remittance_code)
        for e in paid.ledger_entries
        if e.account is AccountKind.CREDITS
    ]

    assert credited == [(Decimal("10.86"), "1702"), (Decimal("3.77"), "1702")]
    assert paid.period_net - none.period_net == Decimal("14.63")
    assert [
        d.amount for d in paid.decisions if d.capability == "special_supplement"
    ] == [Decimal("10.86"), Decimal("3.77")]
    assert reconcile(paid, PeriodState.zero()).ok


def test_above_the_cap_nothing_is_paid() -> None:
    """2025 income 45,000: a decision, no credit."""
    facts = PriorYearTaxFacts(Decimal(45_000), special_supplement_requested=True)
    result = _run(replace(_REQUEST, prior_year=facts))

    assert {
        d.reason_code for d in result.decisions if d.capability == "special_supplement"
    } == {"income_above_cap"}
    assert not [e for e in result.ledger_entries if e.account is AccountKind.CREDITS]


def test_an_unknown_activity_or_income_is_a_missing_fact() -> None:
    """The request alone does not settle it."""
    no_activity = _run(
        replace(_REQUEST, employer=EmployerProfile(headcount=Headcount(20)))
    )
    no_income = _run(
        replace(
            _REQUEST, prior_year=PriorYearTaxFacts(special_supplement_requested=True)
        )
    )

    assert {
        i.fact for i in no_activity.issues if i.capability == "special_supplement"
    } == {"activity"}
    assert {
        i.fact for i in no_income.issues if i.capability == "special_supplement"
    } == {"employment_income"}
