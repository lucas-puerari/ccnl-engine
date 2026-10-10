"""Tests for the tax cash state: payments of one tax year, no maximum."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import EarningsYtd

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
    payments.append(_paid("2027-12-thirteenth", date(2027, 12, 27)))
    return tuple(payments)


class TestPayments:
    """Payments closed in the tax year."""

    def test_holds_more_than_fourteen_payments(self) -> None:
        """Fifteen payments of two competence years fit in one tax year."""
        payments = _tax_year_2027()
        state = TaxCashState(tax_year=2027, payments=payments, conguaglio=payments[-1])

        assert state.is_complete
        assert state.withholding_payments_closed == 15
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
            )

        assert info.value.field == _PAYMENTS

    def test_rejects_a_payment_of_another_tax_year(self) -> None:
        """December 2026 paid on 13 January 2027 is not a 2026 payment."""
        with pytest.raises(InvalidInputError, match="belongs to tax year 2027"):
            TaxCashState(
                tax_year=2026,
                payments=(_paid("2026-12-regular", date(2027, 1, 13)),),
            )

    def test_rejects_payments_without_a_tax_year(self) -> None:
        """Payments belong to a tax year."""
        with pytest.raises(InvalidInputError, match="requires a tax_year"):
            TaxCashState(
                payments=(_paid("2026-01-regular", date(2026, 1, 27)),),
            )

    def test_rejects_a_payment_dated_before_the_last_one(self) -> None:
        """Payments close in payment order: each reads the totals before it."""
        with pytest.raises(InvalidInputError, match="dated before") as info:
            TaxCashState(
                tax_year=2026,
                payments=(
                    _paid("2026-12-thirteenth", date(2026, 12, 15)),
                    _paid("2026-11-regular", date(2026, 11, 27)),
                ),
            )

        assert info.value.field == _PAYMENTS

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
        )

        state.check_next_payment(_paid("2026-04-regular", date(2026, 4, 27)))
        with pytest.raises(InvalidInputError, match="already paid"):
            state.check_next_payment(_paid("2026-03-regular", date(2026, 3, 28)))

    def test_unbound_state_accepts_a_payment_of_any_year(self) -> None:
        """Without a tax year only a repeated run is rejected."""
        TaxCashState().check_next_payment(_paid("2030-01-regular", date(2030, 1, 27)))


class TestConguaglio:
    """The year is complete when its last slot payment settled the conguaglio."""

    _NOVEMBER = _paid("2026-11-regular", date(2026, 11, 27))
    _THIRTEENTH = _paid("2026-12-thirteenth", date(2026, 12, 15))

    def test_incomplete_without_a_conguaglio(self) -> None:
        """Payments alone do not complete the year."""
        state = TaxCashState(tax_year=2026, payments=(self._THIRTEENTH,))

        assert not state.is_complete

    def test_complete_on_the_conguaglio(self) -> None:
        """The tredicesima paid last settled the year."""
        state = TaxCashState(
            tax_year=2026,
            payments=(self._NOVEMBER, self._THIRTEENTH),
            conguaglio=self._THIRTEENTH,
        )

        assert state.is_complete

    @pytest.mark.parametrize(
        "payments", [(), (_THIRTEENTH, _paid("2026-12-regular", date(2026, 12, 20)))]
    )
    def test_rejects_a_conguaglio_that_is_not_the_last_slot_payment(
        self, payments: tuple[PaymentId, ...]
    ) -> None:
        """The conguaglio is the last payment that takes a slot."""
        with pytest.raises(InvalidInputError, match="last payment") as info:
            TaxCashState(tax_year=2026, payments=payments, conguaglio=self._THIRTEENTH)

        assert info.value.field == "TaxCashState.conguaglio"

    def test_an_adjustment_after_the_conguaglio_keeps_it(self) -> None:
        """An adjustment takes no slot: the conguaglio stays the last one."""
        adjustment = _paid("2026-12-adjustment", date(2026, 12, 30))
        state = TaxCashState(
            tax_year=2026,
            payments=(self._THIRTEENTH, adjustment),
            conguaglio=self._THIRTEENTH,
        )

        assert state.paid_runs == {self._THIRTEENTH.run_id, adjustment.run_id}

    @pytest.mark.parametrize(
        ("kwargs", "field"),
        [
            ({"conguaglio": "2026-12-regular"}, "TaxCashState.conguaglio"),
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
