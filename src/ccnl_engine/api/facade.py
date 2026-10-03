"""PayrollEngine: unified entry point for period and year payroll computation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from ccnl_engine.contract.application.catalog import (
    inspect_ruleset as _inspect_ruleset,
)
from ccnl_engine.contract.application.catalog import (
    list_contracts as _list_contracts,
)
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
from ccnl_engine.payroll.application.mode_input import (
    closing_state as _closing_state,
)
from ccnl_engine.payroll.application.mode_input import (
    parse_mode,
    period_request,
    year_request,
)

if TYPE_CHECKING:
    from ccnl_engine.contract.service.discovery import ContractSummary
    from ccnl_engine.payroll.application.calculate_year import YearResult
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.domain.engine_mode import EngineMode
    from ccnl_engine.payroll.domain.inputs import PeriodInput
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.policy import PolicyResolver
    from ccnl_engine.payroll.domain.year_input import YearInput
    from ccnl_engine.provenance.domain.ruleset_assurance import RulesetAssurance

__all__ = ["PayrollEngine"]

#: Mode names accepted in place of an :class:`EngineMode` member.
type Mode = Literal["simulation", "operational"]


class PayrollEngine:
    """Unified entry point for Italian CCNL payroll computation.

    Pass explicit ``repository`` and ``policies`` arguments to inject custom
    knowledge and policy data, useful for testing or air-gapped deployments.
    Call :meth:`bundled` to create an engine backed by the package-bundled
    data.

    The ``mode`` sets the payability policy of every result (see
    :class:`~ccnl_engine.payroll.domain.engine_mode.EngineMode`):
    ``"simulation"`` (the default) reports ruleset readiness, while
    ``"operational"`` also blocks payment from any ruleset that is not
    ``production``.  Both modes compute the same amounts.

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
        print(result.is_payable, result.period_net)
        for ruleset in result.rulesets:
            print(ruleset.id, ruleset.readiness)
    """

    def __init__(
        self,
        *,
        repository: KnowledgeRepository | None = None,
        policies: PolicyResolver | None = None,
        mode: EngineMode | Mode = "simulation",
    ) -> None:
        """Initialise the engine with explicit or bundled knowledge sources.

        Args:
            repository: Knowledge repository to use for CCNL, tax rules, and
                surtax tables.  Defaults to the package-bundled data.
            policies: Pre-loaded policy resolver for pay-item treatment rules.
                Defaults to the bundled Italian ruleset.  Pass an instance to
                avoid repeated JSON parsing across many calculations.
            mode: ``"simulation"`` or ``"operational"``; any other value
                raises
                :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.
        """
        self._repo: KnowledgeRepository = (
            repository if repository is not None else bundled_repository()
        )
        self._resolver: PolicyResolver = (
            policies if policies is not None else bundled_policies()
        )
        self._mode: EngineMode = parse_mode(mode)

    @classmethod
    def bundled(cls, *, mode: EngineMode | Mode = "simulation") -> PayrollEngine:
        """Create an engine backed by the package-bundled knowledge data.

        Args:
            mode: ``"simulation"`` (the default) returns amounts with their
                assurance; ``"operational"`` also requires every ruleset
                that tracks readiness to be ``production``.

        Returns:
            A :class:`PayrollEngine` instance using the shipped CCNL and
            policy JSON files.  The resolver is loaded once and cached on
            the instance.
        """
        return cls(mode=mode)

    @property
    def mode(self) -> EngineMode:
        """Payability policy of the results of this engine."""
        return self._mode

    @staticmethod
    def list_contracts() -> tuple[ContractSummary, ...]:
        """Return every bundled contract with its readiness tier.

        Returns:
            One summary per bundled CCNL, sorted by ``ccnl_id``.
        """
        return _list_contracts()

    def inspect_ruleset(self, ccnl_id: str) -> RulesetAssurance:
        """Return the identity, hash, readiness and confidence of a CCNL.

        A run of the same CCNL reports the same assurance in
        ``result.rulesets``, so a caller can check readiness before
        calculating.

        Args:
            ccnl_id: Slug (e.g. ``"metalmeccanico-federmeccanica"``) or CNEL
                code of a bundled CCNL.

        Returns:
            The assurance of the CCNL ruleset.

        A ``ccnl_id`` that matches no bundled CCNL raises
        :class:`~ccnl_engine.shared.domain.errors.UnknownCcnlError`.
        """
        return _inspect_ruleset(self._repo, ccnl_id)

    def calculate_period(self, request: PeriodInput) -> PeriodResult:
        """Compute a single payroll run.

        Args:
            request: The run, its payment date, the employment, the employer,
                the facts of the run, the prior-year facts and the opening
                state.

        Returns:
            The :class:`~ccnl_engine.payroll.domain.period.PeriodResult`:
            assurance and payability, issues, decisions, amounts, closing
            state, pay items, ledger entries and capability report.
        """
        return _calculate_period(
            period_request(request),
            repo=self._repo,
            resolver=self._resolver,
            bundle_version=__version__,
            mode=self._mode,
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
            year_request(request),
            repo=self._repo,
            resolver=self._resolver,
            bundle_version=__version__,
            mode=self._mode,
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
        return _close_tax_year(_closing_state(closing_state))
