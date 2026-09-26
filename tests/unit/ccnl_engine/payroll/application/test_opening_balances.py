"""Tests for OpeningBalances: validated totals of a previous provider."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.application.opening_balances import OpeningBalances
from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind

_PLAN = RecoveryPlan(
    kind="trattamento_integrativo",
    original_amount=Decimal(160),
    installment_amount=Decimal(20),
    installments_total=8,
    installments_posted=3,
)


def test_to_state_maps_every_total() -> None:
    """Each progressive total lands in its YTD account."""
    recovery = RecoveryObligation(tax_year=2025, plan=_PLAN)
    state = OpeningBalances(
        tax_year=2026,
        regular_periods_closed=6,
        tax_withholding_periods_closed=7,
        closed_run_ids=(PayrollRunId.parse("2026-06-regular"),),
        gross=Decimal("15000.00"),
        taxable=Decimal("13600.00"),
        inps_base=Decimal("15000.00"),
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
    ).to_state()

    ytd = state.ytd
    assert ytd.tax_year == 2026
    assert ytd.regular_periods_closed == 6
    assert ytd.tax_withholding_periods_closed == 7
    assert ytd.closed_run_ids == (PayrollRunId(2026, 6, RunKind.REGULAR),)
    assert ytd.withholding_slots is None
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
    assert state.obligations == EmploymentObligations(recoveries=(recovery,))


@pytest.mark.parametrize(
    "value", [Decimal(-1), Decimal("NaN"), Decimal("Infinity")], ids=str
)
def test_rejects_an_amount_that_is_not_a_non_negative_number(value: Decimal) -> None:
    """Negative and non-finite amounts are rejected by the state rules."""
    with pytest.raises(InvalidInputError, match=r"EarningsYtd\.gross") as info:
        OpeningBalances(tax_year=2026, gross=value)

    assert info.value.feature == "opening_balances"


def test_rejects_an_amount_finer_than_a_cent() -> None:
    """Amounts are in EUR with at most two decimals."""
    with pytest.raises(InvalidInputError, match="more than two decimals"):
        OpeningBalances(tax_year=2026, taxable=Decimal("0.001"))


def test_rejects_inconsistent_totals_as_invalid_input() -> None:
    """More trattamento recovered than recognized is not a valid state."""
    with pytest.raises(InvalidInputError, match="recovered") as info:
        OpeningBalances(tax_year=2026, trattamento_recovered=Decimal(10))

    assert info.value.feature == "opening_balances"


def test_rejects_a_recovery_opened_after_the_tax_year() -> None:
    """A recovery cannot originate after the year of the balances."""
    with pytest.raises(InvalidInputError, match="opened in 2027"):
        OpeningBalances(
            tax_year=2026,
            recoveries=(RecoveryObligation(tax_year=2027, plan=_PLAN),),
        )


def test_to_state_maps_due_reason_and_shortfall() -> None:
    """The last annual due and reason of a credit and the shortfall carry over."""
    ytd = (
        OpeningBalances(
            tax_year=2026,
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
        )
        .to_state()
        .ytd
    )

    assert ytd.trattamento.due == Decimal("1200.00")
    assert ytd.trattamento.reason == "full_amount"
    assert ytd.somma_esente.due == Decimal("0.00")
    assert ytd.somma_esente.reason == "income_above_threshold"
    assert ytd.ulteriore_detrazione.net == Decimal("461.54")
    assert ytd.ulteriore_detrazione.due == Decimal("1000.00")
    assert ytd.shortfall.irpef == Decimal("19.08")
    assert ytd.shortfall.surtax == Decimal("2.10")


def test_rejects_a_reason_that_is_not_a_code() -> None:
    """A reason is a lower snake case code, as on the engine's own accounts."""
    with pytest.raises(InvalidInputError, match="lower snake case"):
        OpeningBalances(tax_year=2026, trattamento_reason="Full amount")


def test_unknown_due_is_accepted() -> None:
    """A due left ``None`` is not checked for cents."""
    state = OpeningBalances(tax_year=2026, ulteriore_due=None).to_state()
    assert state.ytd.ulteriore_detrazione.due is None
