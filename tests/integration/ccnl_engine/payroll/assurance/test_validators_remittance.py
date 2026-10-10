"""Invariant of the codici tributo: coded where known, consistent with the account."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.validators_remittance import (
    check_remittance_code_consistent,
)
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from tests.integration.ccnl_engine.payroll.taxation.builders_imported_surtax import (
    opening_with_2025_surtax,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.results import PeriodResult

_INVARIANT = "remittance_code_consistent"


def _result() -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=9),
            payment_date=date(2026, 9, 28),
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            opening_state=opening_with_2025_surtax("IT-25", "A001"),
            regione="IT-25",
            comune_belfiore="A001",
        )
    )


def _recode(
    result: PeriodResult, account: AccountKind, code: str | None
) -> PeriodResult:
    return replace(
        result,
        ledger_entries=tuple(
            e.model_copy(update={"remittance_code": code})
            if e.account == account
            else e
            for e in result.ledger_entries
        ),
    )


def test_engine_run_holds() -> None:
    """IRPEF under 1001; regional 3802, municipal saldo 3848, acconto 3847."""
    result = _result()

    codes = {(e.account, e.remittance_code) for e in result.ledger_entries}
    assert (AccountKind.ORDINARY_TAX, "1001") in codes
    assert {c for a, c in codes if a is AccountKind.SURTAX} == {"3802", "3847", "3848"}
    assert check_remittance_code_consistent(result) == []


def test_irpef_without_code_is_reported() -> None:
    """IRPEF withheld always has a known code: an uncoded entry fails."""
    result = _recode(_result(), AccountKind.ORDINARY_TAX, None)

    (violation,) = check_remittance_code_consistent(result)
    assert violation.invariant_id == _INVARIANT
    assert "has no codice tributo" in violation.message


def test_code_of_another_account_is_reported() -> None:
    """A credit code on the surtax account fails."""
    result = _recode(_result(), AccountKind.SURTAX, "1701")

    violations = check_remittance_code_consistent(result)
    assert {v.invariant_id for v in violations} == {_INVARIANT}
    assert all("carries codice tributo 1701" in v.message for v in violations)
    assert len(violations) == 3
