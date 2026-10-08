"""Tests for the state entering a run: accrual state and tax cash state."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.shared.domain.errors import InvalidInputError

_JANUARY = PayrollRunId.parse("2026-01-regular")
_PAID = PaymentId(_JANUARY, date(2026, 1, 27))


def _paid_january() -> PeriodState:
    return PeriodState(
        accrual=EmploymentAccrualState(competence_runs=(_JANUARY,)),
        cash=TaxCashState(tax_year=2026, payments=(_PAID,)),
    )


class TestPeriodState:
    """Composition and cross-checks of the two states."""

    def test_zero_closes_nothing(self) -> None:
        """A new employment has no run, no payment and no tax year."""
        state = PeriodState.zero()

        assert state.accrual.competence_runs == ()
        assert state.cash.payments == ()
        assert state.cash.withholding_payments_closed == 0
        assert state.tax_year is None

    def test_schema_version(self) -> None:
        """SCHEMA_VERSION is 13 since the spells record their unpaid days."""
        assert PeriodState.SCHEMA_VERSION == 13

    def test_tax_year_is_that_of_the_cash_state(self) -> None:
        """The tax year is read from the cash state."""
        assert _paid_january().tax_year == 2026

    def test_history_is_known_unless_the_engine_marks_it(self) -> None:
        """A state the caller builds states its history; a flag is a bool."""
        assert PeriodState.zero().history_known
        with pytest.raises(InvalidInputError) as info:
            PeriodState(history_known=1)  # type: ignore[arg-type]

        assert info.value.field == "PeriodState.history_known"

    def test_rejects_a_payment_of_a_run_not_closed(self) -> None:
        """A payment settles a run the accrual state has closed."""
        with pytest.raises(InvalidInputError, match="has not closed") as info:
            PeriodState(cash=_paid_january().cash)

        assert info.value.field == "PeriodState.cash.payments"

    def test_accrual_may_hold_runs_of_earlier_tax_years(self) -> None:
        """The accrual state survives the change of tax year."""
        state = PeriodState(
            accrual=EmploymentAccrualState(competence_runs=(_JANUARY,)),
            cash=TaxCashState(tax_year=2027),
        )

        assert state.accrual.regular_months(2026) == 1

    @pytest.mark.parametrize(
        ("kwargs", "field"),
        [
            ({"accrual": ()}, "PeriodState.accrual"),
            ({"cash": None}, "PeriodState.cash"),
        ],
    )
    def test_rejects_a_field_of_the_wrong_type(
        self, kwargs: dict[str, object], field: str
    ) -> None:
        """Each field is checked for its type."""
        with pytest.raises(InvalidInputError) as info:
            PeriodState(**kwargs)  # type: ignore[arg-type]

        assert info.value.field == field

    def test_check_next_rejects_a_retry_of_the_same_payment(self) -> None:
        """A state that closed the payment rejects it: no double count."""
        state = _paid_january()

        with pytest.raises(InvalidInputError, match="already closed"):
            state.check_next(_PAID)

    def test_check_next_rejects_a_payment_of_another_tax_year(self) -> None:
        """The run may close, but its payment belongs to 2027."""
        state = _paid_january()
        late = PaymentId(PayrollRunId.parse("2026-12-regular"), date(2027, 1, 13))

        with pytest.raises(InvalidInputError, match="belongs to tax year 2027"):
            state.check_next(late)
