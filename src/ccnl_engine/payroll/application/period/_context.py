"""Context of one run: the request normalised into rules, chain and schedule.

The context is an immutable record; :mod:`._context_build` resolves it from
the request and :mod:`._context_facts` derives the facts it exposes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._context_facts import (
    chain_gross,
    installment_run,
    settles_tax_year,
)
from ccnl_engine.payroll.domain.opening_history import opening_state_issue

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.application.period._contract import RunContract
    from ccnl_engine.payroll.application.period._proration import RunProration
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
    from ccnl_engine.payroll.domain.decisions import CalculationIssue
    from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
    from ccnl_engine.payroll.domain.payment import PaymentId
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
    from ccnl_engine.payroll.domain.recovery_plan import InstallmentRun
    from ccnl_engine.payroll.domain.run import RunKind
    from ccnl_engine.payroll.domain.withholding_schedule import (
        WithholdingPosition,
        WithholdingSchedule,
    )
    from ccnl_engine.payroll.service.types import (
        ApprenticeshipScaling,
        MonthlyPayChain,
    )
    from ccnl_engine.tax.domain.variable_pay import VariablePayRules


@dataclass(frozen=True)
class RunContext:
    """Normalised inputs of one run, shared by every step of the pipeline.

    Attributes:
        request: The period calculation request.
        repo: Knowledge repository the rules are loaded from.
        resolver: Policy resolver of the pay-item kinds.
        contract: CCNL, level, dates and yearly rules.
        withholding_schedule: Withholding slots of the tax year.
        withholding: Position of the payment in the schedule: the slots it
            leaves unpaid and whether it settles the conguaglio.
        worker_category: Canonical category of the worker.
        chain: Pay chain of the run, adjusted for an extra month or
            prorated for a partly employed month.
        apprenticeship: Percentage scaling of a percentage apprenticeship,
            ``None`` for any other contract or track.
        payment: The payment the calculation closes: its run and date.
        upcoming_gross: Recurring gross of the slots still to come.
        accrual: Rateo an extra-month run pays, ``None`` for a regular run.
        var_pay_rules: Variable pay rules of the tax year.
        policy_context: Context the pay-item policies are resolved in.
        cp: Competence period of the run.
        regular_chain: Pay chain of a fully employed regular month, which
            the extra-month settlements and the domestic hourly rate read.
        proration: Payable part of the month of a regular run.
    """

    request: PeriodCalculationRequest
    repo: KnowledgeRepository
    resolver: PolicyResolver
    contract: RunContract
    withholding_schedule: WithholdingSchedule
    withholding: WithholdingPosition
    worker_category: WorkerCategory | None
    chain: MonthlyPayChain
    apprenticeship: ApprenticeshipScaling | None
    payment: PaymentId
    upcoming_gross: Decimal
    accrual: ExtraMonthAccrual | None
    var_pay_rules: VariablePayRules
    policy_context: PolicyContext
    cp: CompetencePeriod
    regular_chain: MonthlyPayChain
    proration: RunProration

    @property
    def fiscal_year(self) -> int:
        """Tax year the run belongs to."""
        return self.contract.tctx.fiscal_year

    @property
    def takes_last_slot(self) -> bool:
        """Whether the payment leaves no slot of its tax year unpaid.

        Read by identity from :attr:`withholding`: the runs the tax cash
        state has paid against the payments of the schedule.
        """
        return self.withholding.settles

    @property
    def ytd_inps_base(self) -> Decimal:
        """INPS base of the competence year before the run, all employers."""
        return self.opening.accrual.inps_base(self.cp.year).total

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
        return installment_run(
            self.run_kind,
            self.request.employment_period,
            self.fiscal_year,
            takes_last_slot=self.takes_last_slot,
        )

    @property
    def conguaglio(self) -> bool:
        """Whether the run settles the tax year.

        It does when it takes the last withholding slot of the year or is
        the last run of the employment (:attr:`installment_run`).
        """
        return settles_tax_year(
            self.installment_run, self.run_kind, takes_last_slot=self.takes_last_slot
        )

    @property
    def opening(self) -> PeriodState:
        """State the run opens with."""
        return self.request.opening_state

    @property
    def opening_issue(self) -> CalculationIssue | None:
        """Issue of an opening state that misses the employment history."""
        period = self.request.employment_period
        return opening_state_issue(
            self.opening,
            self.payment.run_id,
            None if period is None else period.started_on,
        )

    @property
    def monthly_gross(self) -> Decimal:
        """Gross of the pay chain: base, seniority and allowances."""
        return chain_gross(self.chain)

    @property
    def regular_gross(self) -> Decimal:
        """Gross of the pay chain of a fully employed regular month."""
        return chain_gross(self.regular_chain)

    @property
    def withholding_agent(self) -> bool:
        """Whether the employer withholds tax: false for a household employer.

        The only place a run reads it from the CCNL; see
        :mod:`~ccnl_engine.payroll.service.withholding_agent`.
        """
        return self.contract.ccnl.meta.withholding_agent
