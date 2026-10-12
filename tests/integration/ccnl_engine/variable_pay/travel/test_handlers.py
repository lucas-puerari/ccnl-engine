"""Travel allowance: exempt up to the daily cap of art. 51 c. 5 TUIR.

The caps are the lire amounts of art. 51 c. 5 converted at 1,936.27 lire per
euro: 90,000 lire (46.48) a day in Italy, 150,000 (77.47) abroad, reduced by
one third (60,000 / 100,000 lire: 30.99 / 51.65) when meals or lodging are
reimbursed or provided, by two thirds (30,000 / 50,000 lire: 15.49 / 25.82)
when both are.  Within the comune the allowance is income in full.  The INPS
base follows the same rule (art. 12 c. 2 L. 153/1969).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.context.models import EffectiveDateContext
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.allocation.services import _process_events
from ccnl_engine.event.facade import BonusEvent, TravelAllowanceEvent
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.facade import CompetencePeriod
from ccnl_engine.pay_item.loaders import load_policy_resolver
from ccnl_engine.pay_item.policies import PolicyContext
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import calculate_period
from ccnl_engine.reconciliation.validators import reconcile
from ccnl_engine.run.types import PeriodId
from ccnl_engine.variable_pay.benefit.handlers import fringe_threshold_of
from ccnl_engine.variable_pay.loaders import load_variable_pay_rules
from ccnl_engine.variable_pay.travel.handlers import TravelAllowanceAssessment

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_DAY = date(2026, 3, 10)
_RULES = load_variable_pay_rules(2026).travel_allowance


def _trip(**changes: object) -> TravelAllowanceEvent:
    fields: dict[str, object] = {
        "event_date": _DAY,
        "days": 3,
        "daily_amount": Decimal("60.00"),
        "outside_municipality": True,
        "in_tfr_base": False,
        "meals_lodging": "none",
    }
    fields.update(changes)
    return TravelAllowanceEvent(**fields)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("changes", "exempt", "reason"),
    [
        ({}, "139.44", "above_cap"),  # 3 x 46.48
        ({"meals_lodging": "one"}, "92.97", "above_cap"),  # 3 x 30.99
        ({"meals_lodging": "both"}, "46.47", "above_cap"),  # 3 x 15.49
        ({"abroad": True}, "180.00", "within_cap"),  # 60.00 < 77.47
        ({"abroad": True, "meals_lodging": "one"}, "154.95", "above_cap"),
        ({"abroad": True, "meals_lodging": "both"}, "77.46", "above_cap"),
        ({"outside_municipality": False}, "0.00", "within_municipality"),
    ],
    ids=[
        "italy",
        "italy_one",
        "italy_both",
        "abroad",
        "abroad_one",
        "abroad_both",
        "comune",
    ],
)
def test_exempt_part(changes: dict[str, object], exempt: str, reason: str) -> None:
    """3 days at 60.00: the exempt part is the days times the cap."""
    assessment = TravelAllowanceAssessment(_trip(**changes), _RULES, 2026)

    assert assessment.gross == Decimal("180.00")
    assert assessment.exempt == Decimal(exempt)
    assert assessment.taxable == Decimal("180.00") - Decimal(exempt)
    assert assessment.reason_code == reason


def test_caps_come_from_the_lire_amounts() -> None:
    """The bundled caps are the converted lire amounts, cited to art. 51 c. 5."""
    assert (_RULES.italy.none, _RULES.italy.one, _RULES.italy.both) == (
        Decimal("46.48"),
        Decimal("30.99"),
        Decimal("15.49"),
    )
    assert (_RULES.abroad.none, _RULES.abroad.one, _RULES.abroad.both) == (
        Decimal("77.47"),
        Decimal("51.65"),
        Decimal("25.82"),
    )
    assert _RULES.provenance is not None
    location = _RULES.provenance.location
    assert location is not None
    assert location.section == "art. 51 c. 5"


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"trasfertista": True}, "trasfertista"),
        ({"days": 0}, "days"),
        ({"daily_amount": Decimal(0)}, "daily_amount"),
        ({"meals_lodging": "dinner"}, "meals_lodging"),
        ({"in_tfr_base": None}, "in_tfr_base"),
    ],
    ids=["trasfertista", "no_days", "no_amount", "meals_lodging", "tfr_unstated"],
)
def test_invalid_events_are_rejected(changes: dict[str, object], field: str) -> None:
    """A trasfertista is not supported; the other fields are validated."""
    with pytest.raises(InvalidInputError, match=field):
        _trip(**changes)


def _run(*events: object) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            opening_state=PeriodState.zero(),
            events=tuple(events),  # type: ignore[arg-type]
        )
    )


def _account(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account), Decimal(0)
    )


def test_the_whole_allowance_is_paid_and_only_the_excess_is_income() -> None:
    """180.00 paid in cash; 40.56 above the cap is income like a bonus of 40.56.

    The INPS contributions and the taxable income grow as with a 40.56
    contract renewal increment (pay of the period, ordinary IRPEF).
    """
    base = _run()
    trip = _run(_trip())
    same = _run(BonusEvent(_DAY, Decimal("40.56"), kind="contract_renewal"))

    paid = _account(trip, AccountKind.CASH_EARNINGS) - _account(
        base, AccountKind.CASH_EARNINGS
    )
    assert paid == Decimal("180.00")
    assert _account(trip, AccountKind.EMPLOYEE_CONTRIBUTIONS) == _account(
        same, AccountKind.EMPLOYEE_CONTRIBUTIONS
    )
    assert (
        trip.closing_state.cash.earnings.taxable
        == same.closing_state.cash.earnings.taxable
    )
    (caller, decision) = sorted(
        (d for d in trip.decisions if d.capability == "travel_allowance"),
        key=lambda d: d.origin,
    )
    assert caller.reason_code == "caller_supplied_amount"
    assert decision.amount == Decimal("40.56")
    assert decision.inputs["daily_cap"] == Decimal("46.48")
    assert decision.rule == "tax/variable-pay-rules/2026"
    assert reconcile(trip, PeriodState.zero()).ok


def test_the_tfr_base_follows_the_event() -> None:
    """The CCNL decides whether the allowance enters the TFR base."""
    out = _run(_trip())
    included = _run(_trip(in_tfr_base=True))

    assert _account(included, AccountKind.TFR_ACCRUAL) > _account(
        out, AccountKind.TFR_ACCRUAL
    )


def test_events_without_the_rules_of_the_year_fail() -> None:
    """The event processor must be given the caps of the tax year."""
    year = 2026
    payment = date(year, 3, 28)
    with pytest.raises(ValueError, match="travel allowance rules"):
        _process_events(
            (_trip(),),
            CompetencePeriod(year=year, month=3),
            payment,
            "t",
            EffectiveDateContext.from_period(year, 3, payment),
            load_policy_resolver(),
            PolicyContext(year=year, as_of=date(year, 3, 1)),
            fringe_threshold_of(
                load_variable_pay_rules(year).fringe_benefit, year, with_children=False
            ),
        )
