"""Tests for the payment id: a run and the day it is paid."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.period.models_run import PayrollRunId
from ccnl_engine.payroll.year.models_payment import PaymentId

_DECEMBER = PayrollRunId.parse("2026-12-regular")


class TestPaymentId:
    """Identity, text form and tax year of a payment."""

    def test_text_form_round_trips(self) -> None:
        """``str`` and ``parse`` are inverse."""
        payment = PaymentId(_DECEMBER, date(2027, 1, 13))

        assert str(payment) == "2026-12-regular@2027-01-13"
        assert PaymentId.parse(str(payment)) == payment

    @pytest.mark.parametrize(
        ("paid_on", "tax_year", "prior"),
        [
            (date(2026, 12, 27), 2026, False),
            (date(2027, 1, 12), 2026, False),
            (date(2027, 1, 13), 2027, True),
        ],
    )
    def test_tax_year_follows_the_payment(
        self, paid_on: date, tax_year: int, prior: bool
    ) -> None:
        """Cassa allargata up to 12 January, then the payment year (art. 51)."""
        payment = PaymentId(_DECEMBER, paid_on)

        assert payment.tax_year == tax_year
        assert payment.is_prior_competence is prior

    def test_rejects_a_payment_before_the_run_month(self) -> None:
        """A run cannot be paid before its competence month starts."""
        with pytest.raises(InvalidInputError) as info:
            PaymentId(_DECEMBER, date(2026, 11, 30))

        assert info.value.field == "PaymentId.payment_date"

    @pytest.mark.parametrize(
        ("run_id", "paid_on", "field"),
        [
            ("2026-12-regular", date(2027, 1, 13), "PaymentId.run_id"),
            (_DECEMBER, "2027-01-13", "PaymentId.payment_date"),
        ],
    )
    def test_rejects_a_field_of_the_wrong_type(
        self, run_id: object, paid_on: object, field: str
    ) -> None:
        """Each field is checked for its type."""
        with pytest.raises(InvalidInputError) as info:
            PaymentId(run_id, paid_on)  # type: ignore[arg-type]

        assert info.value.field == field

    @pytest.mark.parametrize(
        "text",
        [
            "2026-12-regular",
            20261213,
            "2026-12-regular@2027-02-30",
            "2026-13-regular@2027-01-13",
        ],
    )
    def test_parse_rejects_malformed_text(self, text: object) -> None:
        """A text that is not a payment id is invalid input."""
        with pytest.raises(InvalidInputError):
            PaymentId.parse(text)  # type: ignore[arg-type]
