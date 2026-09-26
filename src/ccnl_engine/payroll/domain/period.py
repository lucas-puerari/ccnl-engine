"""Result of one period-first payroll calculation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_state import PeriodState

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.benefit import BenefitBreakdown
    from ccnl_engine.payroll.domain.capability_catalog import CapabilityReport
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.payroll.domain.run import PayrollRun
    from ccnl_engine.payroll.domain.tax import TaxComputation


@dataclass(frozen=True)
class PeriodResult:
    """Result of one period-first payroll calculation.

    Attributes:
        period_id: The competence period, identical to the request.
        payment_date: Payment date, identical to the request.
        period_gross: Contractual gross entitlement for this period
            (sum of CASH_EARNINGS ledger entries). This is the theoretical
            wage the worker is entitled to before absence deductions.
        period_net: Net pay for this period only.
        period_employer_cost: Total employer cost net of unpaid absences:
            ``period_gross - unpaid_absence_deduction + employer_contributions
            + bilateral_fund_employer + tfr_accrual + non_cash_benefits``.
        unpaid_absence_deduction: Sum of EMPLOYEE_DEDUCTIONS ledger entries.
            Represents wages not paid due to unpaid absences or sickness.
            Zero when no absences are present.
        closing_state: State after closing this period: the tax year state
            and the obligations.  Pass as ``opening_state`` to the next
            run of the same tax year, or to
            :func:`~ccnl_engine.payroll.application.close_tax_year\
.close_tax_year` after the last run of the year.
        pay_items: All pay items produced for this period.
        ledger_entries: All ledger entries posted for this period.
        contribution_breakdown: Per-component INPS breakdown for audit
            and compliance tracing.
        benefit_breakdown: Per-axis fringe/welfare benefit breakdown for
            audit and cost-centre reporting.
        issues: Conditions that lower the reliability of this result, in
            the order they were raised.  Empty when every capability
            decided from known rules and facts.
        decisions: What the capabilities that record a decision decided in
            this run, e.g. the eligibility of a pay item for a preferential
            tax regime, in the order they were taken.
    """

    period_id: PeriodId
    payment_date: date
    period_gross: Decimal
    period_net: Decimal
    period_employer_cost: Decimal
    closing_state: PeriodState
    pay_items: tuple[PayItem, ...]
    ledger_entries: tuple[LedgerEntry, ...]
    capability_report: CapabilityReport
    contribution_breakdown: ContributionBreakdown
    tax_computation: TaxComputation
    benefit_breakdown: BenefitBreakdown
    run: PayrollRun | None = None
    unpaid_absence_deduction: Decimal = Decimal(0)
    bundle_version: str | None = None
    issues: tuple[CalculationIssue, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()

    @property
    def status(self) -> CalculationStatus:
        """Worst status implied by :attr:`issues`; final when there are none."""
        return CalculationStatus.worst(issue.status for issue in self.issues)
