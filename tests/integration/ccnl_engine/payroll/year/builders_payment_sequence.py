"""Builder of payment sequences: runs paid one after the other.

Each run opens with the closing state of the run paid before it, as an
integration chains its cedolini.  The engine defaults to
``NextYearRepository``, so a
sequence may cross into tax year 2027; on 2027 runs only the state, not the
amounts, is meaningful.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import PeriodState
from tests.integration.ccnl_engine.payroll.year.builders_next_year_repository import (
    NextYearRepository,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from ccnl_engine import PeriodResult

__all__ = ["Payment", "PaymentSequence"]


@dataclass(frozen=True)
class Payment:
    """One run and the day it is paid."""

    run: PayrollRun
    payment_date: date


@dataclass
class PaymentSequence:
    """Pays runs in order, each opening with the previous closing state.

    Attributes:
        employment: Employment of every run.
        employer: Employer of every run; 50 employees by default.
        engine: Engine computing the runs; 2026 rules stand in for 2027.
        state: State the next run opens with.
        results: Results of the runs paid so far, in payment order.
    """

    employment: Employment
    employer: EmployerProfile = field(
        default_factory=lambda: EmployerProfile(headcount=Headcount(50))
    )
    engine: PayrollEngine = field(
        default_factory=lambda: PayrollEngine(repository=NextYearRepository())
    )
    state: PeriodState = field(default_factory=PeriodState.zero)
    results: list[PeriodResult] = field(default_factory=list)

    def pay(self, payment: Payment) -> PeriodResult:
        """Compute ``payment`` and open the next run with its closing state.

        Returns:
            The result of the run.
        """
        result = self.engine.calculate_period(
            PeriodInput(
                run=payment.run,
                payment_date=payment.payment_date,
                employment=self.employment,
                employer=self.employer,
                opening_state=self.state,
            )
        )
        self.state = result.closing_state
        self.results.append(result)
        return result

    def pay_all(self, payments: Iterable[Payment]) -> list[PeriodResult]:
        """Pay every payment in order.

        Returns:
            The results of the runs paid so far, the new ones last.
        """
        for payment in payments:
            self.pay(payment)
        return self.results
