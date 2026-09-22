"""PayrollEngine — unified entry point for period and year payroll computation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.year_service import (
    compute_payroll_year,
    summarize_payroll_year,
)
from ccnl_engine.payroll.application.calculate_period import (
    calculate_period as _calculate_period,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.engine.payroll.domain.bundle import PayrollBundle
    from ccnl_engine.engine.payroll.domain.engine_types import (
        YearRequest,
        YearResult,
    )
    from ccnl_engine.engine.payroll.domain.period_payroll import AnnualPayrollSummary
    from ccnl_engine.payroll.domain.period import (
        PeriodCalculationRequest,
        PeriodCalculationResult,
    )

__all__ = ["PayrollEngine"]


class PayrollEngine:
    """Unified entry point for Italian CCNL payroll computation.

    Provides two computation modes:

    - :meth:`calculate_period` — single payroll period with YTD state.
    - :meth:`project_year` — full twelve-period year chain.

    Args:
        bundle: Optional pre-loaded knowledge bundle (used by
            :meth:`project_year`). When ``None``, rulesets are loaded on
            demand for each computation.
        repo: Optional knowledge repository override. When ``None``,
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is used.

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

    def __init__(
        self,
        bundle: PayrollBundle | None = None,
        repo: KnowledgeRepository | None = None,
    ) -> None:
        """Initialise the engine with optional shared bundle and repository.

        Args:
            bundle: Optional pre-loaded knowledge bundle. When ``None``,
                rulesets are loaded on demand for each computation.
            repo: Optional knowledge repository override. When ``None``,
                :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is used.
        """
        self._bundle = bundle
        self._repo = repo

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

    def project_year(self, request: YearRequest) -> YearResult:
        """Compute all twelve periods of a payroll year.

        Args:
            request: Year request with structural scenario, calendar year,
                and optional per-month period events. The closing YTD state of
                each period is threaded into the next.

        Returns:
            A :class:`YearResult` containing one :class:`PeriodResult` per
            month in calendar order and the final YTD closing state.
        """
        return compute_payroll_year(request, self._bundle, repo=self._repo)

    @staticmethod
    def summarize(result: YearResult) -> AnnualPayrollSummary:
        """Aggregate a :class:`YearResult` into annual totals.

        Args:
            result: The year result produced by :meth:`project_year`.

        Returns:
            An :class:`AnnualPayrollSummary` with total gross, net, and
            employer cost across all twelve periods and all ledger entries
            in calendar order.
        """
        return summarize_payroll_year(result)
