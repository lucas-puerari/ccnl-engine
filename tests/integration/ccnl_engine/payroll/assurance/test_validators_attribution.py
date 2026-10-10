"""Invariant of attribution: every posted amount rests on a decision."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.validators import reconcile
from ccnl_engine.payroll.assurance.validators_attribution import (
    ACCOUNT_CAPABILITIES,
    KIND_ACCOUNTS,
    check_amount_has_decision,
)
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.event.facade import OvertimeEvent, WelfareEvent
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.state.models_ytd_account import WithholdingShortfall

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.results import PeriodResult

_INVARIANT = "amount_has_decision"
_DAY = date(2026, 3, 10)


def _result() -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            opening_state=PeriodState.zero(),
            events=(
                OvertimeEvent(_DAY, Decimal(4), Decimal("15.00")),
                WelfareEvent(_DAY, Decimal(100)),
            ),
        )
    )


def _without(result: PeriodResult, capability: str) -> PeriodResult:
    return replace(
        result,
        decisions=tuple(d for d in result.decisions if d.capability != capability),
    )


def test_engine_run_holds() -> None:
    """Salary, contributions, TFR, IRPEF and the events all have decisions."""
    assert check_amount_has_decision(_result()) == []


def test_carried_surtax_rests_on_the_cap_decision() -> None:
    """Surtax carried from an earlier run is withheld without a residence.

    The run declares no region or municipality, so no surtax decision is
    taken; the 40.00 carried in is withheld and decided by the cap.
    """
    opening = PeriodState.zero()
    carried = WithholdingShortfall(surtax=Decimal("40.00"))
    opening = replace(opening, cash=replace(opening.cash, shortfall=carried))
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            opening_state=opening,
        )
    )
    surtax = [
        e.amount for e in result.ledger_entries if e.account is AccountKind.SURTAX
    ]
    assert surtax == [Decimal("40.00")]
    reasons = {d.reason_code for d in result.decisions}
    assert "shortfall_withheld" in reasons
    assert check_amount_has_decision(result) == []


def test_entry_without_its_decision_is_reported() -> None:
    """Dropping the overtime decision leaves its earning unattributed."""
    (violation,) = check_amount_has_decision(_without(_result(), "overtime"))
    assert violation.invariant_id == _INVARIANT
    assert "overtime_earning" in violation.message
    assert "has no decision of overtime" in violation.message
    # 4 h x 15.00 EUR x (1 + 0.25), the OT_DIURNO band of the CCNL.
    assert violation.actual == Decimal("75.00")


def test_account_entries_map_by_account() -> None:
    """Without the TFR decision the TFR accrual entry is reported."""
    violations = check_amount_has_decision(_without(_result(), "tfr"))
    assert [v.message.split(" ")[1] for v in violations] == ["tfr_2026-03-regular"]


def test_unmapped_kind_is_reported() -> None:
    """An earnings kind no capability posts cannot be attributed."""
    result = _result()
    entries = tuple(
        e.model_copy(update={"pay_item_kind": "maternity_item"})
        if e.pay_item_kind == "welfare_item"
        else e
        for e in result.ledger_entries
    )
    (violation,) = check_amount_has_decision(replace(result, ledger_entries=entries))
    assert "no decision of no mapped capability" in violation.message


def test_zero_amounts_need_no_decision() -> None:
    """A zero entry posts nothing, so it needs no decision."""
    result = _without(_result(), "tfr")
    entries = tuple(
        e.model_copy(update={"amount": Decimal(0)})
        if e.account is AccountKind.TFR_ACCRUAL
        else e
        for e in result.ledger_entries
    )
    assert check_amount_has_decision(replace(result, ledger_entries=entries)) == []


def test_every_account_is_mapped() -> None:
    """Each account maps by kind or by account, never by both or neither."""
    assert set(AccountKind) == KIND_ACCOUNTS | set(ACCOUNT_CAPABILITIES)
    assert not KIND_ACCOUNTS & set(ACCOUNT_CAPABILITIES)


def test_reconcile_reports_the_invariant() -> None:
    """The invariant runs with the others."""
    result = _without(_result(), "irpef")
    codes = {v.invariant_id for v in reconcile(result, PeriodState.zero()).violations}
    assert _INVARIANT in codes
