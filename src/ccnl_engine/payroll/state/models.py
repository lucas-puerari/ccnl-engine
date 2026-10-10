"""State entering a payroll run: competence state and tax cash state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, final

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.state.models_accrual import EmploymentAccrualState
from ccnl_engine.payroll.state.models_tax_cash import TaxCashState
from ccnl_engine.payroll.year.models_payment import PaymentId
from ccnl_engine.validation import require_bool, require_instances

__all__ = ["PeriodState"]

_FEATURE = "period_state"


@final
@dataclass(frozen=True)
class PeriodState:
    """State entering a payroll run: what is accrued and what is paid.

    Pass :meth:`zero` for the first run of an employment.  Between runs,
    pass the ``closing_state`` of the previous run.  To open the next tax
    year, pass the closing state of the last run of the year to
    :func:`~ccnl_engine.payroll.year.rules_close.close_tax_year`:
    it restarts :attr:`cash` with its obligations and keeps :attr:`accrual`.

    A run that opens without the history of the employment before it (a
    zero state after the start of the employment, or a state descending
    from such a run) is computed as a simulation with a ``missing_fact
    opening_state`` blocker, and its closing state has :attr:`history_known`
    ``False``, so every later run of the chain blocks too.  The same holds
    for the closing state of a conguaglio of a withholding agent computed
    without the worker's residence: it determines no surtax of the year
    and opens none of the obligations of the next.  Import the balances of
    the previous provider, or recompute the chain with the missing facts,
    to restart from a known history.

    A run closes once (its competence run in :attr:`accrual`) and is paid
    once (its payment in :attr:`cash`).  The same request on the same
    opening state yields the same closing state; a state that already closed
    the run rejects it, so a retry never counts a payment twice.

    Attributes:
        accrual: Competence runs closed over the employment; carried across
            tax years.
        cash: Payments, YTD accounts and carried obligations of the current
            tax year; the payments and accounts restart every tax year.
        history_known: Whether the state accounts for every run of the
            employment before it.  The engine sets it ``False`` on the
            closing state of a run that opened without that history, or of
            a conguaglio without the residence; a state the caller builds
            states it.

    Raises:
        InvalidInputError: When a field is not of its type, or a payment of
            :attr:`cash` settles a run :attr:`accrual` has not closed.
    """

    SCHEMA_VERSION: ClassVar[int] = 14

    accrual: EmploymentAccrualState = field(default_factory=EmploymentAccrualState)
    cash: TaxCashState = field(default_factory=TaxCashState)
    history_known: bool = True

    def __post_init__(self) -> None:  # noqa: D105
        require_instances(
            "PeriodState",
            (
                ("accrual", self.accrual, EmploymentAccrualState, False),
                ("cash", self.cash, TaxCashState, False),
            ),
            feature=_FEATURE,
        )
        require_bool(self.history_known, "PeriodState.history_known", feature=_FEATURE)
        closed = set(self.accrual.competence_runs)
        unclosed = [p for p in self.cash.payments if p.run_id not in closed]
        if unclosed:
            msg = (
                f"payment '{unclosed[0]}' settles run '{unclosed[0].run_id}', "
                "which the accrual state has not closed"
            )
            raise InvalidInputError(
                msg, field="PeriodState.cash.payments", feature=_FEATURE
            )

    @property
    def tax_year(self) -> int | None:
        """Tax year of :attr:`cash`; ``None`` when not yet bound to a year."""
        return self.cash.tax_year

    def check_next(self, payment: PaymentId) -> None:
        """Check that ``payment`` and the run it settles can close next.

        A run already closed or out of order in its competence year, or a
        payment that cannot close in the tax year, raises
        ``InvalidInputError``.
        """
        self.accrual.check_next_run(payment.run_id)
        self.cash.check_next_payment(payment)

    @classmethod
    def zero(cls) -> PeriodState:
        """Return the state of a new employment: no run closed, no obligation.

        Returns:
            A :class:`PeriodState` with all counters and accumulators at zero.
        """
        return cls()
