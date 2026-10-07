"""Inputs and outputs of the amounts of one run."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.amounts._surtax import RunSurtax
from ccnl_engine.payroll.domain.recovery_plan import InstallmentRun
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.service.additional_ivs import AdditionalIvsPosition
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.payroll.application.amounts._assistance import (
        AssistanceContribution,
        AssistanceTerms,
    )
    from ccnl_engine.payroll.application.amounts._contributions import TfrAccrual
    from ccnl_engine.payroll.domain.current_year import CurrentYearTaxFacts
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.foreign_tax import ForeignTaxPaid
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.surtax_obligations import SurtaxObligation
    from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
    from ccnl_engine.payroll.domain.withholding_schedule import WithholdingPosition
    from ccnl_engine.payroll.service.pension_fund import (
        PensionContribution,
        PensionFundTerms,
    )
    from ccnl_engine.payroll.service.ulteriore_settlement import UlterioreSettlement
    from ccnl_engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.tax.domain.ruleset import YearRules
    from ccnl_engine.tax.domain.surtax_rules import SurtaxRules
    from ccnl_engine.tax.domain.variable_pay import PdRRules


@dataclass(frozen=True)
class _AmountsInput:
    """Everything the amounts of one run are computed from.

    ``upcoming_gross`` is the recurring gross of the withholding slots still
    to come, zero on the last slot.  ``eligible_work_days`` are the days of
    employment in the tax year the deductions are proportioned to: the union
    of the employments the tax cash state paid in it, the run's included.
    ``fixed_term_in_year`` tells whether one of them is fixed-term, which
    sets the art. 13 c. 1 lett. a) TUIR minimum at 1,380 EUR.
    ``period_days`` are the days of the pay period of a regular run, zero
    for any other run.  ``event_separate_base`` is the part of
    ``event_irpef_base`` withheld apart from the pay of the period (art. 23
    c. 2 lett. b) DPR 600/1973), and so is the whole of an
    :attr:`additional_month` run.
    ``recovery_plan`` is the installment recovery opened in this tax year,
    if one is running, ``ulteriore_plan`` the ulteriore detrazione plan
    opened by a conguaglio of this tax year.  ``installment_run`` tells
    whether the run is the last of the employment, which defers nothing and
    settles every running plan, or an adjustment run.
    ``withholding_agent`` is false for an employer that withholds no tax
    (see :mod:`~ccnl_engine.payroll.service.withholding_agent`).
    ``pension`` holds the rates of the pension fund the worker is enrolled
    in, ``None`` when not enrolled.  ``conguaglio`` is true on the run that
    settles the tax year: its last withholding slot, or the last run of the
    employment.  ``surtax_obligations`` is the surtax determined by an
    earlier conguaglio still to withhold; ``run_month`` and ``run_kind``
    place the run in the installment windows.
    ``foreign_taxes`` are credited on the conguaglio only.
    ``deferred_irpef`` is the IRPEF a conguaglio of this tax year deferred
    on written request: it counts as withheld when the balance is settled
    again.  ``additional_ivs`` is the position of the run toward the
    additional 1% IVS of its competence year.  ``tfr_treasury_fund`` says
    whether the TFR not paid to a pension fund goes to the Fondo Tesoreria,
    ``None`` when not known.  ``assistance`` holds the rates of the
    contractual assistance contribution, ``None`` when the CCNL charges
    none.  ``in_kind`` is the value of the benefits the
    pay chain provides in kind, which enters the TFR base only.
    ``inps_minimum`` is the minimum INPS base of
    the run (:mod:`~ccnl_engine.payroll.service.minimum_base`), ``None``
    when none is determined.
    """

    monthly_gross: Decimal
    in_kind: Decimal
    event_inps_base: Decimal
    event_tfr_base: Decimal
    event_irpef_base: Decimal
    event_substitute_base: Decimal
    opening: TaxCashState
    ytd_inps_base: Decimal
    withholding: WithholdingPosition
    upcoming_gross: Decimal
    rules: YearRules
    contract_type: Permanent | FixedTerm | Apprentice
    category: WorkerCategory | None
    pdr_rules: PdRRules
    ivs_ceiling_applies: bool
    inps_minimum: Decimal | None = None
    surtax_rules: SurtaxRules | None = None
    regione: str | None = None
    comune_belfiore: str | None = None
    family_composition: FamilyComposition | None = None
    family_deduction_rules: FamilyDeductionRules | None = None
    current_year: CurrentYearTaxFacts | None = None
    weekly_hours: int | None = None
    contributable_hours: Decimal | None = None
    domestic_hourly_rate: Decimal | None = None
    eligible_work_days: int = DAYS_IN_YEAR
    fixed_term_in_year: bool = False
    period_days: int = 0
    event_separate_base: Decimal = Decimal(0)
    recovery_plan: RecoveryPlan | None = None
    ulteriore_plan: RecoveryPlan | None = None
    installment_run: InstallmentRun = field(default_factory=InstallmentRun)
    withholding_agent: bool = True
    pension: PensionFundTerms | None = None
    conguaglio: bool = False
    surtax_obligations: tuple[SurtaxObligation, ...] = ()
    run_month: int = 1
    run_kind: RunKind = RunKind.REGULAR
    foreign_taxes: tuple[ForeignTaxPaid, ...] = ()
    deferred_irpef: Decimal = Decimal(0)
    additional_ivs: AdditionalIvsPosition = field(default_factory=AdditionalIvsPosition)
    tfr_treasury_fund: bool | None = None
    assistance: AssistanceTerms | None = None

    @property
    def regular_run(self) -> bool:
        """Whether the run pays a regular month."""
        return self.run_kind is RunKind.REGULAR

    @property
    def additional_month(self) -> bool:
        """Whether the run pays a tredicesima or a quattordicesima."""
        return self.run_kind in {RunKind.THIRTEENTH, RunKind.FOURTEENTH}


@dataclass(frozen=True)
class _PeriodAmounts:
    """Computed monetary amounts passed to pay-item and ledger builders.

    Does not include period_gross, period_net or period_employer_cost: those
    are derived from the ledger after all entries are posted.  ``surtax``
    carries what the run withholds and determines of the surtax, whose
    total before the pay cap is ``surtax.due`` and after it
    ``period_surtax``;
    ``decisions`` holds every tax decision of the run, the surtax ones last.
    ``projected_taxable`` is the annual taxable income the IRPEF of the run
    was computed on; ``None`` when not recorded.  ``ulteriore`` is what
    the run recognized or recovered of the ulteriore detrazione.
    ``pension`` holds the pension fund contributions of the run, ``None``
    when the worker is not enrolled.  ``issues`` are those of the
    capabilities computed here: the family deductions and the TFR.
    ``tfr`` holds the art. 2120 c.c. quota and the additional IVS
    deducted from it.  ``assistance`` is the contractual assistance
    contribution of the run, ``None`` when the CCNL charges none.
    """

    monthly_gross: Decimal
    inps_employee: Decimal
    inps_employer: Decimal
    tfr: TfrAccrual
    period_irpef: Decimal
    period_tratt: Decimal
    period_surtax: Decimal
    period_taxable: Decimal
    period_substitute_tax: Decimal
    pdr_eligible: Decimal
    surtax: RunSurtax = field(default_factory=RunSurtax)
    decisions: tuple[CalculationDecision, ...] = ()
    projected_taxable: Decimal | None = None
    ulteriore: UlterioreSettlement | None = None
    pension: PensionContribution | None = None
    issues: tuple[CalculationIssue, ...] = ()
    assistance: AssistanceContribution | None = None
