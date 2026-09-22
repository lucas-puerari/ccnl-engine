"""PayrollEngine — unified entry point for period and year payroll computation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.calculate_period import (
    calculate_period as _calculate_period,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import (
        PeriodCalculationRequest,
        PeriodCalculationResult,
    )

__all__ = ["PayrollEngine"]


class PayrollEngine:
    """Unified entry point for Italian CCNL payroll computation.

    Provides :meth:`calculate_period` for single-period cedolino computation
    with full YTD state threading.

    Example::

        from datetime import date
        from ccnl_engine import PayrollEngine, PeriodCalculationRequest, PeriodState
        from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId

        engine = PayrollEngine()
        result = engine.calculate_period(PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            opening_state=PeriodState.zero(),
        ))
        print(result.period_net)
    """

    def calculate_period(  # noqa: PLR6301
        self, request: PeriodCalculationRequest
    ) -> PeriodCalculationResult:
        """Compute a single payroll period.

        Args:
            request: Period request specifying the competence period, CCNL slug,
                level code, and YTD opening state. Pass
                :meth:`~PeriodState.zero` as ``opening_state`` for January.

        Returns:
            A :class:`PeriodCalculationResult` with gross, net, employer cost,
            closing YTD state, pay items, and all ledger entries for the period.
        """
        return _calculate_period(request)
