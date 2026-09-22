"""PayrollEngine — unified entry point for period and year payroll computation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.period_service import compute_period_payroll
from ccnl_engine.engine.payroll.service.year_service import (
    compute_payroll_year,
    summarize_payroll_year,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.engine.payroll.domain.bundle import PayrollBundle
    from ccnl_engine.engine.payroll.domain.engine_types import (
        PeriodRequest,
        PeriodResult,
        YearRequest,
        YearResult,
    )
    from ccnl_engine.engine.payroll.domain.period_payroll import AnnualPayrollSummary

__all__ = ["PayrollEngine"]


class PayrollEngine:
    """Unified entry point for Italian CCNL payroll computation.

    Provides two computation modes:

    - :meth:`calculate_period` — single payroll period with YTD state.
    - :meth:`project_year` — full twelve-period year chain.

    Both methods delegate to the underlying period service and propagate
    deprecation warnings; they will be backed by the period-first engine
    in a future release.

    Args:
        bundle: Optional pre-loaded knowledge bundle. When ``None``,
            rulesets are loaded on demand for each computation.
        repo: Optional knowledge repository override. When ``None``,
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is used.

    Example::

        from ccnl_engine import PayrollEngine, PeriodRequest, PayrollState
        from ccnl_engine import AnnualEstimateInput, Employee, Employment, Employer
        from ccnl_engine import Permanent, PeriodPayrollInput
        from datetime import date

        engine = PayrollEngine()
        result = engine.calculate_period(PeriodRequest(
            structural=AnnualEstimateInput(
                employee=Employee(level_code="C3"),
                employment=Employment(
                    ccnl="metalmeccanico-federmeccanica.json",
                    contract=Permanent(),
                    employer=Employer(num_employees=50),
                    as_of=date(2026, 1, 1),
                ),
            ),
            period=PeriodPayrollInput(),
            opening_state=PayrollState.zero(),
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

    def calculate_period(self, request: PeriodRequest) -> PeriodResult:
        """Compute a single payroll period.

        Args:
            request: Period request including structural scenario, period events,
                and YTD opening state. Pass :meth:`~PayrollState.zero` as
                ``opening_state`` for January.

        Returns:
            A :class:`PeriodResult` with gross, net, employer cost, closing
            YTD state, and all ledger entries for this period.
        """
        return compute_period_payroll(request, self._bundle, repo=self._repo)

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
