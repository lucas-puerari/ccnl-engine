"""PayrollEngine: unified entry point for period and year payroll computation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.knowledge import __version__
from ccnl_engine.payroll.application.bundled_sources import (
    bundled_policies,
    bundled_repository,
)
from ccnl_engine.payroll.application.calculate_period import (
    calculate_period as _calculate_period,
)
from ccnl_engine.payroll.application.calculate_year import (
    calculate_year as _calculate_year,
)
from ccnl_engine.payroll.application.close_tax_year import (
    close_tax_year as _close_tax_year,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.calculate_year import YearResult
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.domain.inputs import PeriodInput
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.policy import PolicyResolver
    from ccnl_engine.payroll.domain.year_input import YearInput

__all__ = ["PayrollEngine"]


class PayrollEngine:
    """Unified entry point for Italian CCNL payroll computation.

    Pass explicit ``repository`` and ``policies`` arguments to inject custom
    knowledge and policy data, useful for testing or air-gapped deployments.
    Call :meth:`bundled` to create an engine backed by the package-bundled
    data.

    Example::

        from datetime import date
        from ccnl_engine import (
            Employment, EmployerProfile, Headcount, PayrollEngine,
            PayrollRun, PeriodInput,
        )

        engine = PayrollEngine.bundled()
        result = engine.calculate_period(PeriodInput(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 28),
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
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
                avoid repeated JSON parsing across many calculations.
        """
        self._repo: KnowledgeRepository = (
            repository if repository is not None else bundled_repository()
        )
        self._resolver: PolicyResolver = (
            policies if policies is not None else bundled_policies()
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

    def calculate_period(self, request: PeriodInput) -> PeriodResult:
        """Compute a single payroll run.

        Args:
            request: The run, its payment date, the employment, the employer,
                the facts of the run, the prior-year facts and the opening
                state.

        Returns:
            The :class:`~ccnl_engine.payroll.domain.period.PeriodResult`:
            status, issues, decisions, amounts, closing state, pay items,
            ledger entries and capability report.
        """
        return _calculate_period(
            request.calculation_request(),
            repo=self._repo,
            resolver=self._resolver,
            bundle_version=__version__,
        )

    def calculate_year(self, request: YearInput) -> YearResult:
        """Compute payroll for all runs in a year.

        Args:
            request: The year, the employment, the employer, the prior-year
                facts, the facts per run, an optional calendar override, the
                payment day and the opening state.

        Returns:
            The :class:`~ccnl_engine.payroll.application.calculate_year\
.YearResult` with one result per run and the annual totals.

        A calendar override that drops or lowers an extra month the CCNL
        grants, or does not match its reason, raises
        :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.
        """
        return _calculate_year(
            request,
            repo=self._repo,
            resolver=self._resolver,
            bundle_version=__version__,
        )

    @staticmethod
    def close_tax_year(closing_state: PeriodState) -> PeriodState:
        """Open the next tax year from the closing state of the last run.

        See :func:`~ccnl_engine.payroll.application.close_tax_year\
.close_tax_year`.

        Args:
            closing_state: ``closing_state`` of the last run of the year.

        Returns:
            The opening state of the next tax year: a fresh tax year state
            and the obligations still running.
        """
        return _close_tax_year(closing_state)
