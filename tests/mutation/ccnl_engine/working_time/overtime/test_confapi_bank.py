"""Immediate bank premium: two hours at EUR 10 pay EUR 24 ordinary, EUR 2 banked.

Art. 29 p. 102: banked overtime pays half the 20% weekday premium,
not the ordinary hour; residual rest credit and its later payout are separate.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.event.facade import OvertimeEvent, OvertimeKind
from tests.mutation.ccnl_engine.working_time.overtime.test_policies import (
    _overtime_paid,
    _run,
)


def test_paid_and_banked_months() -> None:
    """March EUR 24 paid; April EUR 2 banked (2 x 10 x 20% x 50%)."""
    paid = _run(
        OvertimeEvent(date(2026, 3, 10), Decimal(2), Decimal(10)),
        "metalmeccanico-confapi",
        "5",
    )
    banked = _run(
        OvertimeEvent(date(2026, 4, 10), Decimal(2), Decimal(10), banked=True),
        "metalmeccanico-confapi",
        "5",
        month=4,
    )
    assert _overtime_paid(paid) == Decimal("24.00")
    assert _overtime_paid(banked) == Decimal("2.00")
    assert any(d.reason_code == "overtime_bank_premium" for d in banked.decisions)


def test_derived_hourly_rate_decision_uses_banked_amount() -> None:
    """Two hours at EUR 2195.87 / 173 pay EUR 2.54 (half 20% premium)."""
    banked = _run(
        OvertimeEvent(date(2026, 3, 10), Decimal(2), banked=True),
        "metalmeccanico-confapi",
        "5",
    )
    assert _overtime_paid(banked) == Decimal("2.54")
    assert any(
        d.reason_code == "ccnl_hourly_rate_derived" and d.amount == Decimal("2.54")
        for d in banked.decisions
    )


def test_night_bank_uses_its_own_premium() -> None:
    """Two night hours at EUR 10 pay EUR 5 (2 x 10 x 50% x 50%)."""
    banked = _run(
        OvertimeEvent(
            date(2026, 3, 10),
            Decimal(2),
            Decimal(10),
            kind=OvertimeKind.NIGHT,
            banked=True,
        ),
        "metalmeccanico-confapi",
        "5",
    )
    assert _overtime_paid(banked) == Decimal("5.00")


def test_bank_not_assumed_for_other_agreements() -> None:
    """A two-hour bank election without an agreement bank rule cannot pay EUR 2."""
    with pytest.raises(MissingRuleError, match="bank rule"):
        _run(OvertimeEvent(date(2026, 3, 10), Decimal(2), Decimal(10), banked=True))


def test_bank_election_is_boolean() -> None:
    """A string election cannot silently turn EUR 24 into EUR 2."""
    with pytest.raises(InvalidInputError, match="banked"):
        OvertimeEvent(date(2026, 3, 10), Decimal(2), Decimal(10), banked="yes")  # type: ignore[arg-type]


def test_bank_without_a_rule_names_the_gap() -> None:
    """The rejection cites the event date, the capability and the remedy."""
    day = date(2026, 3, 10)
    with pytest.raises(MissingRuleError) as raised:
        _run(OvertimeEvent(day, Decimal(2), Decimal(10), banked=True))
    error = raised.value
    assert error.as_of == day
    assert error.feature == "overtime"
    assert error.detail == "No percentage overtime bank rule applies to these hours"
    assert error.remediation == "Use an agreement with a verified overtime bank rule."


def test_bank_decision_cites_the_bank_share() -> None:
    """Art. 29: the decision records 2 hours, the 0.50 share and EUR 2.00."""
    banked = _run(
        OvertimeEvent(date(2026, 3, 10), Decimal(2), Decimal(10), banked=True),
        "metalmeccanico-confapi",
        "5",
    )
    decision = next(
        d for d in banked.decisions if d.reason_code == "overtime_bank_premium"
    )
    assert decision.capability == "overtime"
    assert decision.status is CalculationStatus.FINAL
    assert decision.rule.endswith(":work_rules.time_supplements.overtime_bank_share")
    assert decision.rule_version
    assert decision.inputs == {"hours": Decimal(2), "premium_share": Decimal("0.50")}
    assert decision.source is not None
    assert decision.source.page
    assert decision.amount == Decimal("2.00")
