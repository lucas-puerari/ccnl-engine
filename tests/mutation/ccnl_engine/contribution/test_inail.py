"""The INAIL premium the employer accrues on the contribution base of the run.

Agenti immobiliari FIAIP IV, March 2026: the premium is the INPS base of the
run times the rate of the employer's position per mille (art. 29 DPR
1124/1965), an employer contribution that leaves the net pay unchanged.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WeeklyHours
from ccnl_engine.ledger.models import AccountKind
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()
_RATE = Decimal("9.50")


def _run(rate: Decimal | None) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="agenti-immobiliari-fiaip",
                level_code="IV",
                seniority=new_hire(2023),
                roles=frozenset(),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2023, 3, 1)),
                weekly_hours=WeeklyHours(Decimal(40)),
                full_time_weekly_hours=WeeklyHours(Decimal(40)),
            ),
            employer=EmployerProfile(headcount=Headcount(20), inail_rate=rate),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )


def test_a_stated_rate_accrues_the_premium_on_the_inps_base() -> None:
    """Base times the rate per mille, an employer contribution, not a deduction."""
    plain, rated = _run(None), _run(_RATE)

    (decision,) = (d for d in rated.decisions if d.capability == "inail")
    base = Decimal(str(decision.inputs["base"]))
    premium = (base * _RATE / 1000).quantize(Decimal("0.01"))
    assert base > 0
    assert decision.inputs["rate_per_mille"] == "9.50"
    assert decision.amount == premium
    assert decision.status is CalculationStatus.FINAL
    assert decision.reason_code == "inail_premium_accrued"
    assert decision.rule == "dpr-1124-1965-art29"
    assert rated.period_employer_cost == plain.period_employer_cost + premium
    assert rated.period_net == plain.period_net
    (entry,) = (e for e in rated.ledger_entries if e.entry_id.startswith("inail_"))
    assert (entry.account, entry.amount) == (
        AccountKind.EMPLOYER_CONTRIBUTIONS,
        premium,
    )


def test_no_rate_no_premium() -> None:
    """Without the employer's rate the run accrues nothing."""
    result = _run(None)

    assert not [d for d in result.decisions if d.capability == "inail"]
    assert not [e for e in result.ledger_entries if e.entry_id.startswith("inail_")]


def test_a_negative_rate_is_rejected() -> None:
    """The rate is a non-negative per mille."""
    with pytest.raises(InvalidInputError) as error:
        EmployerProfile(headcount=Headcount(1), inail_rate=Decimal(-1))
    assert error.value.field == "EmployerProfile.inail_rate"
