"""Tests for opening_state: the period state built from imported balances."""

from __future__ import annotations

import dataclasses
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.opening_balances import OpeningBalances
from ccnl_engine.payroll.application.opening_state import opening_state
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind
from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.domain.surtax_obligations import (
    SurtaxComponent,
    SurtaxObligation,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

_JUNE = (PaymentId.parse("2026-06-regular@2026-06-27"),)
_PLAN = RecoveryPlan(
    kind="trattamento_integrativo",
    original_amount=Decimal(160),
    installment_amount=Decimal(20),
    installments_total=8,
    installments_posted=3,
)


def test_opening_state_maps_every_total() -> None:
    """Each progressive total lands in its YTD account."""
    recovery = RecoveryObligation(tax_year=2025, plan=_PLAN)
    state = opening_state(
        OpeningBalances(
            tax_year=2026,
            payments=(PaymentId.parse("2026-06-regular@2026-06-27"),),
            gross=Decimal("15000.00"),
            taxable=Decimal("13600.00"),
            inps_employee=Decimal("1377.00"),
            irpef_withheld=Decimal("2100.00"),
            surtax_withheld=Decimal("150.00"),
            fringe_value=Decimal("400.00"),
            fringe_taxed=Decimal("0.00"),
            pdr=Decimal("1000.00"),
            trattamento_recognized=Decimal("600.00"),
            trattamento_recovered=Decimal("0.00"),
            somma_esente_recognized=Decimal("300.00"),
            somma_esente_recovered=Decimal("40.00"),
            work_time_regime_used=Decimal("500.00"),
            recoveries=(recovery,),
        )
    )

    ytd = state.cash
    assert ytd.tax_year == 2026
    assert ytd.withholding_payments_closed == 1
    june = PayrollRunId(2026, 6, RunKind.REGULAR)
    assert ytd.payments == (PaymentId(june, date(2026, 6, 27)),)
    assert state.accrual.competence_runs == (june,)
    assert ytd.conguaglio is None
    assert ytd.earnings.taxable == Decimal("13600.00")
    assert ytd.earnings.inps_employee == Decimal("1377.00")
    assert ytd.tax.irpef == Decimal("2100.00")
    assert ytd.tax.surtax == Decimal("150.00")
    assert ytd.fringe.value == Decimal("400.00")
    assert ytd.fringe.pdr == Decimal("1000.00")
    assert ytd.trattamento.recognized == Decimal("600.00")
    assert ytd.somma_esente.recognized == Decimal("300.00")
    assert ytd.somma_esente.recovered == Decimal("40.00")
    assert ytd.work_time_regime.used == Decimal("500.00")
    assert state.cash.obligations == EmploymentObligations(recoveries=(recovery,))


def test_opening_state_maps_due_reason_and_shortfall() -> None:
    """The last annual due and reason of a credit and the shortfall carry over."""
    ytd = opening_state(
        OpeningBalances(
            tax_year=2026,
            payments=_JUNE,
            trattamento_recognized=Decimal("600.00"),
            trattamento_due=Decimal("1200.00"),
            trattamento_reason="full_amount",
            somma_esente_due=Decimal("0.00"),
            somma_esente_reason="income_above_threshold",
            ulteriore_recognized=Decimal("461.54"),
            ulteriore_due=Decimal("1000.00"),
            ulteriore_reason="share_recognized",
            irpef_shortfall=Decimal("19.08"),
            surtax_shortfall=Decimal("2.10"),
            credit_recovery_shortfall=Decimal("7.50"),
        )
    ).cash

    assert ytd.trattamento.due == Decimal("1200.00")
    assert ytd.trattamento.reason == "full_amount"
    assert ytd.somma_esente.due == Decimal("0.00")
    assert ytd.somma_esente.reason == "income_above_threshold"
    assert ytd.ulteriore_detrazione.net == Decimal("461.54")
    assert ytd.ulteriore_detrazione.due == Decimal("1000.00")
    assert ytd.shortfall.irpef == Decimal("19.08")
    assert ytd.shortfall.surtax == Decimal("2.10")
    assert ytd.shortfall.credit_recovery == Decimal("7.50")


def test_unknown_due_is_accepted() -> None:
    """A due left ``None`` is not checked for cents."""
    state = opening_state(OpeningBalances(tax_year=2026, ulteriore_due=None))
    assert state.cash.ulteriore_detrazione.due is None


def test_imports_the_surtax_of_the_previous_conguaglio() -> None:
    """The 2025 saldo and the 2026 acconto open 2026, with the acconto withheld."""
    saldo = SurtaxObligation.open(
        SurtaxComponent.REGIONAL_BALANCE, 2025, "IT-88", Decimal("110.00")
    )
    state = opening_state(
        OpeningBalances(
            tax_year=2026,
            payments=_JUNE,
            surtax_withheld=Decimal(30),
            municipal_advance_withheld=Decimal(12),
            regional_settled=Decimal(5),
            municipal_settled=Decimal(3),
            surtax_obligations=(saldo,),
        )
    )

    assert state.cash.obligations.surtax == (saldo,)
    assert state.cash.tax.municipal_advance == Decimal(12)
    assert state.cash.tax.regional_settled == Decimal(5)
    assert state.cash.tax.municipal_settled == Decimal(3)


def _deferred(tax_year: int) -> DeferredShortfall:
    return DeferredShortfall(
        tax_year=tax_year,
        signed_on=date(tax_year, 12, 10),
        deferred_from=date(tax_year, 12, 1),
        irpef=Decimal("300.00"),
    )


def test_imports_the_deferral_of_the_previous_conguaglio() -> None:
    """The IRPEF the 2025 conguaglio deferred opens 2026."""
    deferred = _deferred(2025)
    state = opening_state(OpeningBalances(tax_year=2026, deferred_shortfall=deferred))
    assert state.cash.obligations.deferred_shortfall == (deferred,)


def test_accepts_more_than_fourteen_payments() -> None:
    """A tax year with a late December has fifteen payments: no maximum."""
    payments = [PaymentId.parse("2026-12-regular@2027-01-13")]
    for month in range(1, 13):
        payments.append(
            PaymentId.parse(f"2027-{month:02d}-regular@2027-{month:02d}-27")
        )
        if month == 7:
            payments.append(PaymentId.parse("2027-07-fourteenth@2027-07-27"))
    payments.append(PaymentId.parse("2027-12-thirteenth@2027-12-27"))

    state = opening_state(OpeningBalances(tax_year=2027, payments=tuple(payments)))

    assert state.cash.withholding_payments_closed == 15


def test_obligations_alone_need_no_payment() -> None:
    """A new tax year opens with obligations and no payment."""
    recovery = RecoveryObligation(tax_year=2025, plan=_PLAN)
    state = opening_state(OpeningBalances(tax_year=2026, recoveries=(recovery,)))

    assert state.cash.payments == ()


def test_imports_competence_runs_of_an_earlier_tax_year() -> None:
    """2026 paid in 2026 is closed: December 2026 paid in 2027 may follow it."""
    earlier = tuple(PayrollRunId(2026, m, RunKind.REGULAR) for m in range(1, 12))
    state = opening_state(OpeningBalances(tax_year=2027, competence_runs=earlier))

    assert state.accrual.regular_months(2026) == 11
    with pytest.raises(InvalidInputError, match="already closed"):
        state.accrual.check_next_run(earlier[0])
    state.accrual.check_next_run(PayrollRunId(2026, 12, RunKind.REGULAR))


def test_imports_the_inps_base_of_other_employers() -> None:
    """The base of an earlier employment of the year counts toward the massimale."""
    base = InpsBaseYtd(2026, other_employers=Decimal("80000.00"))
    state = opening_state(OpeningBalances(tax_year=2026, inps_bases=(base,)))

    assert state.accrual.inps_base(2026).total == Decimal("80000.00")
    assert state.accrual.inps_base(2026).own == Decimal(0)
    assert state.accrual.inps_base(2025).total == Decimal(0)


def _leaves(value: object, path: str) -> dict[str, object]:
    """Return the scalar leaves of a dataclass tree, by dotted path.

    Returns:
        Each leaf value keyed by its path.
    """
    if not dataclasses.is_dataclass(value):
        return {path: value}
    found: dict[str, object] = {}
    for f in dataclasses.fields(value):
        found |= _leaves(getattr(value, f.name), f"{path}.{f.name}")
    return found


def test_every_total_of_the_cash_state_can_be_imported() -> None:
    """Each YTD leaf of TaxCashState is reached by an OpeningBalances field.

    Every amount is set to a value no default has; a leaf left at its
    default would be a total no integration could import.
    """
    amounts: dict[str, object] = {
        f.name: Decimal("10.00")
        for f in dataclasses.fields(OpeningBalances)
        if f.type in {"Decimal", "Decimal | None"}
    }
    amounts |= {"municipal_advance_withheld": Decimal("5.00")}
    reasons: dict[str, object] = {
        f.name: "full_amount"
        for f in dataclasses.fields(OpeningBalances)
        if f.type == "str | None"
    }
    state = opening_state(
        OpeningBalances(
            tax_year=2026,
            payments=_JUNE,
            **amounts,  # type: ignore[arg-type]
            **reasons,  # type: ignore[arg-type]
        )
    )

    skipped = {"cash.tax_year", "cash.payments", "cash.conguaglio", "cash.obligations"}
    defaults = {
        path: value
        for path, value in _leaves(state.cash, "cash").items()
        if path not in skipped and value in {Decimal(0), None}
    }
    assert defaults == {}
