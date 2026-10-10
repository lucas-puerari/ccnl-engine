"""Synthetic period results for reconcile() invariant tests.

``ResultBuilder`` assembles a :class:`PeriodResult` field by field so a test
can break exactly one invariant; ``ledger_entry`` and ``salary_item`` build
the minimal ledger entries and pay items those scenarios need.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.amount.facade import BaseSalaryEarning, CompetencePeriod
from ccnl_engine.payroll.capability.results import CapabilityReport
from ccnl_engine.payroll.contribution.results import ContributionBreakdown
from ccnl_engine.payroll.event.results_benefit import BenefitBreakdown
from ccnl_engine.payroll.ledger.models import AccountKind, LedgerEntry
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.models_run import PayrollRunId, RunKind
from ccnl_engine.payroll.period.results import PeriodResult
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.state.models_accrual import EmploymentAccrualState
from ccnl_engine.payroll.state.models_tax_cash import TaxCashState
from ccnl_engine.payroll.state.models_ytd_account import EarningsYtd, TaxYtd
from ccnl_engine.payroll.taxation.results import TaxComputation
from ccnl_engine.payroll.year.models_payment import PaymentId

YEAR = 2026
COMPETENCE = CompetencePeriod(year=YEAR, month=1)
PAYMENT_DATE = date(YEAR, 1, 28)
PERIOD_ID = PeriodId(year=YEAR, month=1)
RUN_ID = PayrollRunId(year=YEAR, month=1, kind=RunKind.REGULAR)


def ledger_entry(
    pay_item_id: str,
    account: AccountKind,
    amount: Decimal,
) -> LedgerEntry:
    """Build a minimal LedgerEntry for invariant violation tests.

    Returns:
        A :class:`LedgerEntry` with the given item id, account and amount.
    """
    return LedgerEntry(
        entry_id=f"e_{pay_item_id}",
        competence_period=COMPETENCE,
        payment_date=PAYMENT_DATE,
        pay_item_id=pay_item_id,
        pay_item_kind="base_salary_earning",
        account=account,
        amount=amount,
    )


def salary_item(item_id: str, amount: Decimal) -> BaseSalaryEarning:
    """Build a minimal BaseSalaryEarning for coverage tests.

    Returns:
        A :class:`BaseSalaryEarning` with the given item_id and amount.
    """
    return BaseSalaryEarning(
        item_id=item_id,
        competence_period=COMPETENCE,
        payment_date=PAYMENT_DATE,
        quantity=Decimal(1),
        amount=amount,
    )


@dataclass
class ResultBuilder:
    """Mutable result builder for constructing synthetic violation scenarios."""

    period_gross: Decimal = Decimal("3000.00")
    period_net: Decimal = Decimal("2000.00")
    period_employer_cost: Decimal = Decimal("3400.00")
    closing_irpef: Decimal = Decimal("500.00")
    closing_inps: Decimal = Decimal("300.00")
    closing_gross: Decimal = Decimal("3000.00")
    pay_items: tuple[BaseSalaryEarning, ...] = ()
    ledger_entries: tuple[LedgerEntry, ...] = ()

    def build(self) -> PeriodResult:
        """Construct a :class:`PeriodResult` from the builder state.

        Returns:
            A frozen :class:`PeriodResult`.
        """
        return PeriodResult(
            period_id=PERIOD_ID,
            payment_date=PAYMENT_DATE,
            period_gross=self.period_gross,
            period_net=self.period_net,
            period_employer_cost=self.period_employer_cost,
            closing_state=PeriodState(
                accrual=EmploymentAccrualState(competence_runs=(RUN_ID,)),
                cash=TaxCashState(
                    tax_year=YEAR,
                    payments=(PaymentId(RUN_ID, PAYMENT_DATE),),
                    tax=TaxYtd(irpef=self.closing_irpef),
                    earnings=EarningsYtd(
                        inps_employee=self.closing_inps,
                        gross=self.closing_gross,
                    ),
                ),
            ),
            pay_items=self.pay_items,
            ledger_entries=self.ledger_entries,
            capability_report=CapabilityReport.empty(YEAR),
            contribution_breakdown=ContributionBreakdown(
                employee=Decimal(0), employer=Decimal(0), components=()
            ),
            tax_computation=TaxComputation(
                ordinary_tax=Decimal(0),
                trattamento_integrativo=Decimal(0),
                withholding_due=Decimal(0),
                components=(),
            ),
            benefit_breakdown=BenefitBreakdown(
                value=Decimal(0),
                cash=Decimal(0),
                irpef_base=Decimal(0),
                inps_base=Decimal(0),
                employer_cost=Decimal(0),
            ),
        )


OPENING = PeriodState.zero()
