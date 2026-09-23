"""PayrollEngine — unified entry point for period and year payroll computation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application.calculate_period import (
    calculate_period as _calculate_period,
)
from ccnl_engine.payroll.application.calculate_year import (
    calculate_year as _calculate_year,
)
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest

if TYPE_CHECKING:
    from ccnl_engine.api.requests import PayrollRequest, PayrollYearRequest
    from ccnl_engine.api.results import PayrollResult
    from ccnl_engine.payroll.application.calculate_year import YearCalculationResult
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult

__all__ = ["PayrollEngine"]


class PayrollEngine:
    """Unified entry point for Italian CCNL payroll computation.

    Preferred usage via :meth:`from_builtin_data` and :meth:`calculate`:

    Example::

        from datetime import date
        from ccnl_engine import PayrollEngine
        from ccnl_engine.api import PayrollRequest
        from ccnl_engine.payroll.domain.run import PayrollRun
        from ccnl_engine.payroll.domain.period import PeriodState

        engine = PayrollEngine.from_builtin_data()
        result = engine.calculate(PayrollRequest(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            opening_state=PeriodState.zero(),
        ))
        print(result.period_net)
    """

    @classmethod
    def from_builtin_data(cls) -> PayrollEngine:
        """Create an engine backed by the bundled knowledge data.

        Returns:
            A :class:`PayrollEngine` instance ready to compute payroll
            using the knowledge bundle shipped with ccnl-engine.
        """
        return cls()

    def calculate(  # noqa: PLR6301
        self, request: PayrollRequest
    ) -> PayrollResult:
        """Compute a single payroll run.

        Unlike :meth:`calculate_period`, this method requires a
        :class:`~ccnl_engine.payroll.domain.run.PayrollRun` as the primary
        identifier, enforcing run identity and kind through the type system.

        Args:
            request: A :class:`~ccnl_engine.api.requests.PayrollRequest`
                that carries the run, CCNL slug, level, YTD state and events.

        Returns:
            A :class:`~ccnl_engine.api.results.PayrollResult` (currently
            :class:`~ccnl_engine.payroll.domain.period.PeriodCalculationResult`)
            with gross, net, employer cost, closing state, pay items and
            ledger entries.
        """
        period_req = PeriodCalculationRequest(
            period_id=PeriodId(year=request.run.year, month=request.run.month),
            payment_date=request.payment_date,
            ccnl_slug=request.ccnl_slug,
            level_code=request.level_code,
            opening_state=request.opening_state,
            contract_type=request.contract_type,
            num_employees=request.num_employees,
            events=request.events,
            regione=request.regione,
            comune_belfiore=request.comune_belfiore,
            family_composition=request.family_composition,
            has_dependent_children=request.has_dependent_children,
        )
        return _calculate_period(period_req)

    def calculate_year(  # noqa: PLR6301
        self, request: PayrollYearRequest
    ) -> YearCalculationResult:
        """Compute payroll for all runs in a year.

        Args:
            request: A :class:`~ccnl_engine.api.requests.PayrollYearRequest`
                carrying year, CCNL slug, level, calendar and optional events.

        Returns:
            A :class:`~ccnl_engine.payroll.application.calculate_year.\
YearCalculationResult` with one result per run and aggregated annual totals.
        """
        return _calculate_year(
            request.year,
            request.ccnl_slug,
            request.level_code,
            calendar=request.calendar,
            contract_type=request.contract_type,
            num_employees=request.num_employees,
            period_events=request.period_events or None,
            regione=request.regione,
            comune_belfiore=request.comune_belfiore,
            family_composition=request.family_composition,
            has_dependent_children=request.has_dependent_children,
        )

    def calculate_period(  # noqa: PLR6301
        self, request: PeriodCalculationRequest
    ) -> PeriodCalculationResult:
        """Compute a single payroll period.

        Prefer :meth:`calculate` with a
        :class:`~ccnl_engine.api.requests.PayrollRequest` for new code;
        this method is retained for backward compatibility.

        Args:
            request: Period request specifying the competence period, CCNL slug,
                level code, and YTD opening state.

        Returns:
            A :class:`~ccnl_engine.payroll.domain.period.PeriodCalculationResult`.
        """
        return _calculate_period(request)
