"""PayrollEngine: unified entry point for period and year payroll computation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.knowledge import __version__
from ccnl_engine.payroll.application.calculate_period import (
    calculate_period as _calculate_period,
)
from ccnl_engine.payroll.application.calculate_year import (
    calculate_year as _calculate_year,
)
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.policy import PolicyResolver

if TYPE_CHECKING:
    from ccnl_engine.api.requests import PayrollRequest, PayrollYearRequest
    from ccnl_engine.api.results import PayrollResult
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.application.calculate_year import YearCalculationResult

__all__ = ["PayrollEngine"]


class PayrollEngine:
    """Unified entry point for Italian CCNL payroll computation.

    Pass explicit ``repository`` and ``policies`` arguments to inject custom
    knowledge and policy data — useful for testing or air-gapped deployments.
    Call :meth:`bundled` (or its alias :meth:`from_builtin_data`) to create
    an engine backed by the package-bundled data.

    Example::

        from datetime import date
        from ccnl_engine import (
            EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun,
        )

        engine = PayrollEngine.bundled()
        result = engine.calculate(PayrollRequest(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
        ))
        print(result.period_net)
    """

    def __init__(
        self,
        *,
        repository: KnowledgeRepository | None = None,
        policies: PolicyResolver | None = None,
    ) -> None:
        """Initialise the engine with explicit or bundled knowledge sources.

        Args:
            repository: Knowledge repository to use for CCNL, tax rules, and
                surtax tables.  Defaults to the package-bundled data.
            policies: Pre-loaded policy resolver for pay-item treatment rules.
                Defaults to the bundled Italian ruleset.  Pass an instance to
                avoid repeated JSON parsing across many :meth:`calculate` calls.
        """
        self._repo: KnowledgeRepository = (
            repository if repository is not None else BundledKnowledgeRepository()
        )
        self._resolver: PolicyResolver = (
            policies if policies is not None else PolicyResolver.load()
        )

    @classmethod
    def bundled(cls) -> PayrollEngine:
        """Create an engine backed by the package-bundled knowledge data.

        Returns:
            A :class:`PayrollEngine` instance using the shipped CCNL and
            policy JSON files.  The resolver is loaded once and cached on
            the instance.
        """
        return cls()

    @classmethod
    def from_builtin_data(cls) -> PayrollEngine:
        """Alias for :meth:`bundled` kept for backward compatibility.

        Returns:
            A :class:`PayrollEngine` instance using the bundled data.
        """
        return cls()

    def calculate(self, request: PayrollRequest) -> PayrollResult:
        """Compute a single payroll run.

        Args:
            request: A :class:`~ccnl_engine.api.requests.PayrollRequest`
                carrying the run, CCNL slug, level, YTD state and events.

        Returns:
            A :class:`~ccnl_engine.api.results.PayrollResult` with gross,
            net, employer cost, closing state, pay items and ledger entries.
        """
        ef = request.employment_facts
        period_req = PeriodCalculationRequest(
            period_id=PeriodId(year=request.run.year, month=request.run.month),
            payment_date=request.payment_date,
            ccnl_slug=request.ccnl_slug,
            level_code=request.level_code,
            opening_state=request.opening_state,
            contract_type=ef.contract_type,
            employer=request.employer,
            ceiling_status=ef.ceiling_status,
            weekly_hours=ef.contracted_hours,
            contributable_hours=ef.contributable,
            full_time_weekly_hours=ef.full_time_hours,
            employment_period=ef.period,
            seniority_months=ef.seniority,
            roles=ef.roles,
            category=ef.category,
            events=request.events,
            regione=request.regione,
            comune_belfiore=request.comune_belfiore,
            family_composition=request.family_composition,
            has_dependent_children=request.has_dependent_children,
            run=request.run,
        )
        return _calculate_period(
            period_req,
            repo=self._repo,
            resolver=self._resolver,
            bundle_version=__version__,
        )

    def calculate_year(self, request: PayrollYearRequest) -> YearCalculationResult:
        """Compute payroll for all runs in a year.

        Args:
            request: A :class:`~ccnl_engine.api.requests.PayrollYearRequest`
                carrying year, CCNL slug, level, an optional calendar override
                and optional events.

        Returns:
            A :class:`~ccnl_engine.payroll.application.calculate_year.\
YearCalculationResult` with one result per run and aggregated annual totals.

        A calendar override that drops or lowers an extra month the CCNL
        grants, or does not match its reason, raises
        :class:`~ccnl_engine.engine.errors.InvalidInputError`.
        """
        ef = request.employment_facts
        return _calculate_year(
            request.year,
            request.ccnl_slug,
            request.level_code,
            calendar=request.calendar,
            contract_type=ef.contract_type,
            employer=request.employer,
            ceiling_status=ef.ceiling_status,
            weekly_hours=ef.contracted_hours,
            contributable_hours=ef.contributable,
            full_time_weekly_hours=ef.full_time_hours,
            employment_period=ef.period,
            seniority_months=ef.seniority,
            roles=ef.roles,
            category=ef.category,
            period_events=request.period_events or None,
            per_run_events=request.per_run_events or None,
            regione=request.regione,
            comune_belfiore=request.comune_belfiore,
            family_composition=request.family_composition,
            has_dependent_children=request.has_dependent_children,
            payment_day=request.payment_day,
            repo=self._repo,
            resolver=self._resolver,
            bundle_version=__version__,
        )
