"""Context of one run: the request normalised into rules, chain and schedule.

The loads and resolutions run in a fixed order, so that when several inputs
are invalid the same error is raised first on every call.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.validity import rule_scope
from ccnl_engine.payroll.application._period_utils import (
    _apply_extra_month_policy,
    _effective_resolver,
    _int_value,
)
from ccnl_engine.payroll.application.period._chain import _resolve_chain
from ccnl_engine.payroll.application.period._checks import resolve_payment
from ccnl_engine.payroll.application.period._seniority import seniority_months_at
from ccnl_engine.payroll.application.withholding._cap import ends_in_year
from ccnl_engine.payroll.application.withholding._plan import (
    resolve_withholding_schedule,
    upcoming_recurring_gross,
)
from ccnl_engine.payroll.application.year._accrual_rule import month_accrual_rule
from ccnl_engine.payroll.application.year._extra_month_accrual import (
    run_accrual,
    run_fraction,
)
from ccnl_engine.payroll.domain.employment_context import (
    EffectiveDateContext,
    TemporalContext,
)
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.payroll.domain.policy import PolicyContext
from ccnl_engine.payroll.domain.recovery_plan import InstallmentRun
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.service.category import resolve_worker_category
from ccnl_engine.shared.domain.errors import UnknownLevelError

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.contract.domain.compensation import Level
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
    from ccnl_engine.payroll.domain.capability_catalog import CapabilityCatalog
    from ccnl_engine.payroll.domain.payment import PaymentId
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.policy import PolicyResolver
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
    from ccnl_engine.payroll.service.types import (
        ApprenticeshipScaling,
        MonthlyPayChain,
    )
    from ccnl_engine.tax.domain.ruleset import YearRules
    from ccnl_engine.tax.domain.variable_pay import VariablePayRules


@dataclass(frozen=True)
class _Contract:
    """CCNL, level, dates and yearly rules of a run."""

    ccnl: CCNL
    level: Level
    tctx: TemporalContext
    date_ctx: EffectiveDateContext
    year_rules: YearRules
    catalog: CapabilityCatalog


@dataclass(frozen=True)
class RunContext:
    """Normalised inputs of one run, shared by every step of the pipeline.

    Attributes:
        request: The period calculation request.
        repo: Knowledge repository the rules are loaded from.
        resolver: Policy resolver of the pay-item kinds.
        contract: CCNL, level, dates and yearly rules.
        withholding_schedule: Withholding slots of the tax year.
        worker_category: Canonical category of the worker.
        chain: Pay chain of the run, adjusted for an extra month.
        apprenticeship: Percentage scaling of a percentage apprenticeship,
            ``None`` for any other contract or track.
        payment: The payment the calculation closes: its run and date.
        upcoming_gross: Recurring gross of the slots still to come.
        accrual: Rateo an extra-month run pays, ``None`` for a regular run.
        var_pay_rules: Variable pay rules of the tax year.
        policy_context: Context the pay-item policies are resolved in.
        cp: Competence period of the run.
    """

    request: PeriodCalculationRequest
    repo: KnowledgeRepository
    resolver: PolicyResolver
    contract: _Contract
    withholding_schedule: WithholdingSchedule
    worker_category: WorkerCategory | None
    chain: MonthlyPayChain
    apprenticeship: ApprenticeshipScaling | None
    payment: PaymentId
    upcoming_gross: Decimal
    accrual: ExtraMonthAccrual | None
    var_pay_rules: VariablePayRules
    policy_context: PolicyContext
    cp: CompetencePeriod

    @property
    def fiscal_year(self) -> int:
        """Tax year the run belongs to."""
        return self.contract.tctx.fiscal_year

    @property
    def takes_last_slot(self) -> bool:
        """Whether the run takes the last withholding slot of the tax year.

        The one place the conguaglio position is read from the payments of
        the tax cash state and the withholding schedule.
        """
        closed = self.opening.cash.withholding_payments_closed
        return self.withholding_schedule.remaining(closed) == 1

    @property
    def run_kind(self) -> RunKind:
        """Kind of the run."""
        return self.payment.run_id.kind

    @property
    def run_id(self) -> str:
        """Run identifier as the tag of item and entry ids."""
        return str(self.payment.run_id)

    @property
    def installment_run(self) -> InstallmentRun:
        """The run as the credit recoveries see it.

        The run is final when it is a termination run, or when the
        employment ends in the tax year and the run takes its last
        withholding slot: no later payslip can carry an installment.
        """
        kind = self.run_kind
        final = kind is RunKind.TERMINATION or (
            ends_in_year(self.request.employment_period, self.fiscal_year)
            and self.takes_last_slot
        )
        return InstallmentRun(final=final, adjustment=kind is RunKind.ADJUSTMENT)

    @property
    def conguaglio(self) -> bool:
        """Whether the run settles the tax year.

        It does when it takes the last withholding slot of the year or is
        the last run of the employment (:attr:`installment_run`).
        """
        return self.installment_run.final or (
            self.run_kind.consumes_withholding_slot and self.takes_last_slot
        )

    @property
    def opening(self) -> PeriodState:
        """State the run opens with."""
        return self.request.opening_state

    @property
    def monthly_gross(self) -> Decimal:
        """Gross of the pay chain: base, seniority and allowances."""
        chain = self.chain
        return money(chain.base + chain.seniority + chain.allowances_total)

    @property
    def withholding_agent(self) -> bool:
        """Whether the employer withholds tax: false for a household employer.

        The only place a run reads it from the CCNL; see
        :mod:`~ccnl_engine.payroll.service.withholding_agent`.
        """
        return self.contract.ccnl.meta.withholding_agent


def _load_contract(
    request: PeriodCalculationRequest, repo: KnowledgeRepository
) -> _Contract:
    """Load the CCNL, level and yearly rules of the run.

    Returns:
        The contract of the run.

    Raises:
        UnknownLevelError: When the CCNL has no level ``request.level_code``.
    """
    period_id = request.period_id
    ccnl = repo.load_ccnl(request.ccnl_slug)
    tctx = TemporalContext.from_period(
        period_id.year, period_id.month, request.payment_date
    )
    try:
        level = ccnl.level_by_code(request.level_code)
    except ValueError:
        raise UnknownLevelError(request.level_code, ccnl.meta.ccnl_id) from None
    # The base salary of the level is the first rule every run reads.
    with rule_scope(ruleset=ccnl.meta.ccnl_id, feature="base_salary"):
        level.base_salary.value_at(tctx.competence)
    date_ctx = EffectiveDateContext.from_period(
        period_id.year, period_id.month, tctx.payment
    )
    year_rules = repo.load_year_rules(
        tctx.fiscal_year, ccnl.meta.tax_sector, request.employer.headcount.value
    )
    catalog = repo.load_capability_catalog(tctx.fiscal_year)
    return _Contract(ccnl, level, tctx, date_ctx, year_rules, catalog)


def _base_chain(
    request: PeriodCalculationRequest,
    contract: _Contract,
    worker_category: WorkerCategory | None,
) -> tuple[MonthlyPayChain, ApprenticeshipScaling | None]:
    """Return the pay chain of a regular month for the worker.

    Returns:
        The chain before any extra-month adjustment, and the apprenticeship
        scaling applied to it.
    """
    return _resolve_chain(
        contract.ccnl,
        contract.level,
        request.contract_type,
        contract.tctx.competence,
        seniority_months=seniority_months_at(
            request.seniority, contract.tctx.competence
        ),
        roles=request.roles,
        worker_category=worker_category,
        weekly_hours=_int_value(request.weekly_hours),
        full_time_weekly_hours=_int_value(request.full_time_weekly_hours),
    )


def build_context(
    request: PeriodCalculationRequest,
    repo: KnowledgeRepository | None,
    resolver: PolicyResolver | None,
) -> RunContext:
    """Normalise ``request`` into the context of its run.

    Returns:
        The run context.
    """
    effective_repo = repo if repo is not None else BundledKnowledgeRepository()
    effective_resolver = _effective_resolver(resolver)
    contract = _load_contract(request, effective_repo)
    competence, fiscal_year = contract.tctx.competence, contract.tctx.fiscal_year
    worker_category = resolve_worker_category(
        contract.ccnl, contract.level, request.category, seniority=request.seniority
    )
    chain, apprenticeship = _base_chain(request, contract, worker_category)
    payment = resolve_payment(request)
    schedule = resolve_withholding_schedule(request, payment, contract.ccnl, competence)
    opening = request.opening_state
    upcoming_gross = upcoming_recurring_gross(
        chain,
        schedule,
        opening.cash.withholding_payments_closed,
        request.employment_period,
        month_accrual_rule(contract.ccnl),
    )
    accrual = run_accrual(request, contract.ccnl, competence)
    chain = _apply_extra_month_policy(chain, payment.run_id.kind, run_fraction(accrual))
    return RunContext(
        request=request,
        repo=effective_repo,
        resolver=effective_resolver,
        contract=contract,
        withholding_schedule=schedule,
        worker_category=worker_category,
        chain=chain,
        apprenticeship=apprenticeship,
        payment=payment,
        upcoming_gross=upcoming_gross,
        accrual=accrual,
        var_pay_rules=effective_repo.load_variable_pay_rules(fiscal_year),
        policy_context=PolicyContext(
            year=fiscal_year,
            as_of=competence,
            ccnl_slug=request.ccnl_slug,
            sector=contract.ccnl.meta.tax_sector,
            gross_ytd=opening.cash.earnings.gross,
        ),
        cp=CompetencePeriod(year=request.period_id.year, month=request.period_id.month),
    )
