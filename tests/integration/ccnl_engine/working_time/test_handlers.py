"""Work-time regime cap account: validation, availability and the plafond invariant."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.cash.account.models import RegimeCapAccount
from ccnl_engine.balance.cash.models import TaxCashState
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import (
    EmployerActivity,
    EmployerProfile,
    Headcount,
)
from ccnl_engine.event.facade import BonusEvent, NightShiftEvent, OvertimeEvent
from ccnl_engine.irpef.declaration.inputs import PriorYearTaxFacts
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import calculate_period
from ccnl_engine.reconciliation.decision.validators import (
    check_substitute_tax_plafond,
)
from ccnl_engine.reconciliation.types import RunFacts
from ccnl_engine.reconciliation.validators import reconcile
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_YEAR = 2026
_CAP = Decimal(1_500)


def _night_run(amount: Decimal, opening: PeriodState) -> PeriodResult:
    event = NightShiftEvent(
        event_date=date(_YEAR, 3, 10),
        supplement_amount=amount,
    )
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(50), activity=EmployerActivity.OTHER
            ),
            sector=EmploymentSector.PRIVATE,
            prior_year=PriorYearTaxFacts(employment_income=Decimal(20_000)),
            period_id=PeriodId(year=_YEAR, month=3),
            payment_date=date(_YEAR, 3, 27),
            ccnl_id="commercio-confcommercio",
            level_code="4",
            opening_state=opening,
            events=(event,),
        )
    )


def _with_used(result: PeriodResult, used: Decimal) -> PeriodResult:
    state = result.closing_state
    closing = replace(
        state, cash=replace(state.cash, work_time_regime=RegimeCapAccount(used))
    )
    return replace(result, closing_state=closing)


class TestRegimeCapAccount:
    """The account holds a non-negative used amount."""

    def test_zero_by_default(self) -> None:
        """A new tax year starts with nothing used."""
        assert PeriodState.zero().cash.work_time_regime.used == Decimal(0)

    def test_negative_used_is_rejected(self) -> None:
        """A negative used amount cannot be represented."""
        with pytest.raises(ValueError, match="must be >= 0"):
            RegimeCapAccount(used=Decimal("-0.01"))

    @pytest.mark.parametrize(
        ("used", "available"),
        [
            (Decimal(0), _CAP),
            (Decimal(1_000), Decimal(500)),
            (_CAP, Decimal(0)),
            (Decimal(2_000), Decimal(0)),
        ],
    )
    def test_available_is_never_negative(
        self, used: Decimal, available: Decimal
    ) -> None:
        """What is left of the cap is ``cap - used``, floored at zero."""
        assert RegimeCapAccount(used).available(_CAP) == available


class TestPlafondInvariant:
    """substitute_tax_plafond: the account advances by the eligible amounts."""

    def test_real_run_passes(self) -> None:
        """An engine run above the cap consumes exactly the cap."""
        opening = PeriodState.zero()
        result = _night_run(Decimal(2_000), opening)

        assert result.closing_state.cash.work_time_regime.used == _CAP
        assert check_substitute_tax_plafond(result, opening, RunFacts()) == []

    def test_wrong_advance_is_reported(self) -> None:
        """A closing account that ignores the eligible amount is a violation."""
        opening = PeriodState.zero()
        bad = _with_used(_night_run(Decimal(500), opening), Decimal(0))

        (violation,) = check_substitute_tax_plafond(bad, opening, RunFacts())
        assert violation.invariant_id == "substitute_tax_plafond"
        assert violation.expected == Decimal(500)
        assert violation.actual == Decimal(0)
        assert "substitute_tax_plafond" in {
            v.invariant_id for v in reconcile(bad, opening).violations
        }

    def test_used_above_cap_is_reported(self) -> None:
        """An account above the annual cap is a violation even if it adds up."""
        result = _night_run(Decimal(1_500), PeriodState.zero())
        opening = PeriodState(
            cash=TaxCashState(work_time_regime=RegimeCapAccount(Decimal(100)))
        )
        bad = _with_used(result, Decimal(1_600))

        violations = check_substitute_tax_plafond(bad, opening, RunFacts())
        above = [v for v in violations if "exceeds the annual cap" in v.message]
        assert [(v.expected, v.actual) for v in above] == [(_CAP, Decimal(1_600))]


_METAL = "metalmeccanico-federmeccanica"
_PDR_CEILING = Decimal("80000.00")


def _bonus_run(*events: object, income: Decimal = Decimal(25_000)) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            prior_year=PriorYearTaxFacts(employment_income=income),
            period_id=PeriodId(year=_YEAR, month=3),
            payment_date=date(_YEAR, 3, 27),
            ccnl_id=_METAL,
            level_code="C3",
            opening_state=PeriodState.zero(),
            events=events,  # type: ignore[arg-type]
        )
    )


def _posted(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account), Decimal(0)
    )


def _bonus(kind: str, amount: str = "1000.00") -> BonusEvent:
    return BonusEvent(date(_YEAR, 3, 10), Decimal(amount), kind=kind)  # type: ignore[arg-type]


def test_a_premium_is_withheld_apart_from_the_pay_of_the_period() -> None:
    """Art. 23 c. 2 lett. b): a bonus is taxed apart, a renewal increment is not.

    Above the income ceilings of the substitute regimes, a bonus, a renewal
    increment and a night supplement of 1,000 EUR are taxable income of the
    run alike (INPS in, TFR out); only the bonus, a premium, is withheld at
    the rates of the mensilità aggiuntive.
    """
    high = Decimal(90_000)
    night = NightShiftEvent(
        event_date=date(_YEAR, 3, 10), supplement_amount=Decimal(1000)
    )
    runs = {
        "bonus": _bonus_run(_bonus("bonus"), income=high),
        "renewal": _bonus_run(_bonus("contract_renewal"), income=high),
        "night": _bonus_run(night, income=high),
    }
    taxable = {k: r.closing_state.cash.earnings.taxable for k, r in runs.items()}
    tax = {k: _posted(r, AccountKind.ORDINARY_TAX) for k, r in runs.items()}

    assert taxable["bonus"] == taxable["renewal"] == taxable["night"]
    assert tax["renewal"] == tax["night"] != tax["bonus"]


@pytest.mark.parametrize(
    ("income", "substitute"),
    [(_PDR_CEILING, Decimal("10.00")), (_PDR_CEILING + Decimal("0.01"), Decimal(0))],
    ids=["at_the_ceiling", "above_it"],
)
def test_the_pdr_rate_needs_an_income_not_above_80000(
    income: Decimal, substitute: Decimal
) -> None:
    """Art. 1 c. 186 L. 208/2015: "reddito ... non superiore" to 80,000 EUR."""
    result = _bonus_run(_bonus("productivity_bonus"), income=income)

    assert _posted(result, AccountKind.SUBSTITUTE_TAX) == substitute


def test_a_pdr_above_the_ceiling_keeps_its_contributions_and_tfr() -> None:
    """Above the ceiling only the tax changes: INPS and TFR bases stay."""
    eligible = _bonus_run(_bonus("productivity_bonus"))
    above = _bonus_run(_bonus("productivity_bonus"), income=Decimal(90_000))
    ordinary = _bonus_run(_bonus("bonus"), income=Decimal(90_000))

    for account in (AccountKind.EMPLOYEE_CONTRIBUTIONS, AccountKind.TFR_ACCRUAL):
        assert _posted(above, account) == _posted(eligible, account)
    assert above.closing_state.cash.earnings.taxable == (
        ordinary.closing_state.cash.earnings.taxable
    )
    assert _posted(above, AccountKind.ORDINARY_TAX) == _posted(
        ordinary, AccountKind.ORDINARY_TAX
    )


def test_the_regime_substitute_tax_traces_to_the_policy_of_the_supplement() -> None:
    """The 15% tax on a night supplement names the policy that governed it."""
    result = _night_run(Decimal("100.00"), PeriodState.zero())
    entries = {
        e.account: (e.amount, e.policy_decision_id)
        for e in result.ledger_entries
        if e.pay_item_id.endswith("_evt0")
    }

    assert entries == {
        AccountKind.CASH_EARNINGS: (Decimal("100.00"), "it/earning/supplement"),
        AccountKind.SUBSTITUTE_TAX: (Decimal("15.00"), "it/earning/supplement"),
    }


def test_the_overtime_band_decision_states_the_amount_paid() -> None:
    """Without a multiplier the CCNL band pays the hours; the decision says how much."""
    result = _bonus_run(OvertimeEvent(date(_YEAR, 3, 10), Decimal(3), Decimal("15.00")))
    (item,) = (i for i in result.pay_items if i.kind == "overtime_earning")
    (decision,) = (
        d for d in result.decisions if d.reason_code == "ccnl_overtime_band_applied"
    )

    assert decision.amount == item.amount > Decimal(0)
