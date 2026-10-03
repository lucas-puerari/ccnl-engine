"""Tests for the tax cash state: payments of one tax year, no maximum."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import EarningsYtd
from ccnl_engine.shared.domain.errors import InvalidInputError

_PAYMENTS = "TaxCashState.payments"


def _paid(text: str, paid_on: date) -> PaymentId:
    return PaymentId(PayrollRunId.parse(text), paid_on)


def _tax_year_2027() -> tuple[PaymentId, ...]:
    """Return December 2026 paid on 13 January 2027, then the 2027 payslips.

    Returns:
        Fifteen payments of tax year 2027: one late regular of 2026, twelve
        regular months, the quattordicesima and the tredicesima.
    """
    payments = [_paid("2026-12-regular", date(2027, 1, 13))]
    for month in range(1, 13):
        payments.append(_paid(f"2027-{month:02d}-regular", date(2027, month, 27)))
        if month == 6:
            payments.append(_paid("2027-06-fourteenth", date(2027, 6, 27)))
    payments.append(_paid("2027-12-thirteenth", date(2027, 12, 18)))
    return tuple(payments)


class TestPayments:
    """Payments closed in the tax year."""

    def test_holds_more_than_fourteen_payments(self) -> None:
        """Fifteen payments of two competence years fit in one tax year."""
        payments = _tax_year_2027()
        state = TaxCashState(
            tax_year=2027,
            payments=payments,
            withholding_payments_closed=15,
            withholding_slots=15,
        )

        assert state.is_complete
        assert state.prior_competence_payments == payments[:1]

    def test_rejects_a_run_paid_twice(self) -> None:
        """A run is paid once, whatever the payment date."""
        with pytest.raises(InvalidInputError, match="already paid") as info:
            TaxCashState(
                tax_year=2026,
                payments=(
                    _paid("2026-01-regular", date(2026, 1, 27)),
                    _paid("2026-01-regular", date(2026, 1, 28)),
                ),
                withholding_payments_closed=2,
            )

        assert info.value.field == _PAYMENTS

    def test_rejects_a_payment_of_another_tax_year(self) -> None:
        """December 2026 paid on 13 January 2027 is not a 2026 payment."""
        with pytest.raises(InvalidInputError, match="belongs to tax year 2027"):
            TaxCashState(
                tax_year=2026,
                payments=(_paid("2026-12-regular", date(2027, 1, 13)),),
                withholding_payments_closed=1,
            )

    def test_rejects_payments_without_a_tax_year(self) -> None:
        """Payments belong to a tax year."""
        with pytest.raises(InvalidInputError, match="requires a tax_year"):
            TaxCashState(
                payments=(_paid("2026-01-regular", date(2026, 1, 27)),),
                withholding_payments_closed=1,
            )

    def test_rejects_more_slot_payments_than_the_counter(self) -> None:
        """The ids never outnumber the slots the counter closed."""
        with pytest.raises(InvalidInputError, match="slot-consuming payments"):
            TaxCashState(
                tax_year=2026,
                payments=(_paid("2026-01-regular", date(2026, 1, 27)),),
            )

    def test_an_adjustment_takes_no_slot(self) -> None:
        """An adjustment payment does not count against the counter."""
        state = TaxCashState(
            tax_year=2026,
            payments=(_paid("2026-01-adjustment", date(2026, 2, 27)),),
        )

        assert state.withholding_payments_closed == 0

    def test_check_next_payment(self) -> None:
        """The rules apply to the next payment before it is computed."""
        state = TaxCashState(
            tax_year=2026,
            payments=(_paid("2026-03-regular", date(2026, 3, 27)),),
            withholding_payments_closed=1,
        )

        state.check_next_payment(_paid("2026-04-regular", date(2026, 4, 27)))
        with pytest.raises(InvalidInputError, match="already paid"):
            state.check_next_payment(_paid("2026-03-regular", date(2026, 3, 28)))

    def test_unbound_state_accepts_a_payment_of_any_year(self) -> None:
        """Without a tax year only a repeated run is rejected."""
        TaxCashState().check_next_payment(_paid("2030-01-regular", date(2030, 1, 27)))


class TestCounters:
    """Withholding counter and completion, without any maximum."""

    @pytest.mark.parametrize(
        ("closed", "slots", "complete"),
        [(0, None, False), (12, 13, False), (13, 13, True), (16, 16, True)],
    )
    def test_is_complete_when_every_slot_is_closed(
        self, closed: int, slots: int | None, complete: bool
    ) -> None:
        """The year is complete once the last withholding slot is closed."""
        state = TaxCashState(
            withholding_payments_closed=closed, withholding_slots=slots
        )

        assert state.is_complete is complete

    @pytest.mark.parametrize(
        ("kwargs", "field"),
        [
            ({"withholding_slots": 0}, "TaxCashState.withholding_slots"),
            (
                {"withholding_payments_closed": -1},
                "TaxCashState.withholding_payments_closed",
            ),
            ({"tax_year": 2019}, "TaxCashState.tax_year"),
            ({"earnings": "0"}, "TaxCashState.earnings"),
            ({"payments": "2026-01-regular@2026-01-27"}, _PAYMENTS),
        ],
    )
    def test_rejects_invalid_fields(
        self, kwargs: dict[str, object], field: str
    ) -> None:
        """Each field is checked for its type and range."""
        with pytest.raises(InvalidInputError) as info:
            TaxCashState(**kwargs)  # type: ignore[arg-type]

        assert info.value.field == field

    def test_keeps_the_ytd_accounts(self) -> None:
        """The accounts are stored as given."""
        state = TaxCashState(earnings=EarningsYtd(taxable=Decimal("100.00")))

        assert state.earnings.taxable == Decimal("100.00")


class TestObligations:
    """Obligations carried into the tax year."""

    @staticmethod
    def _obligations(tax_year: int) -> EmploymentObligations:
        plan = RecoveryPlan(
            kind="trattamento_integrativo",
            original_amount=Decimal(80),
            installment_amount=Decimal(10),
            installments_total=8,
            installments_posted=0,
        )
        return EmploymentObligations(
            recoveries=(RecoveryObligation(tax_year=tax_year, plan=plan),)
        )

    def test_rejects_a_recovery_opened_after_its_tax_year(self) -> None:
        """A 2027 recovery cannot sit in a 2026 state."""
        with pytest.raises(InvalidInputError, match="opened in 2027") as info:
            TaxCashState(tax_year=2026, obligations=self._obligations(2027))

        assert info.value.field == "TaxCashState.obligations"

    def test_unbound_state_accepts_any_recovery(self) -> None:
        """Without a tax year there is nothing to compare the origin with."""
        state = TaxCashState(obligations=self._obligations(2027))

        assert state.obligations.latest_tax_year == 2027
