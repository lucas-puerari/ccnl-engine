"""Inputs and outputs of the amounts of one run."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.fiscal_surtax import SurtaxOutcome
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
    from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
    from ccnl_engine.payroll.service.ulteriore_recovery import UlterioreSettlement
    from ccnl_engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.tax.domain.ruleset import YearRules
    from ccnl_engine.tax.domain.surtax_rules import SurtaxRules
    from ccnl_engine.tax.domain.variable_pay import PdRRules


@dataclass(frozen=True)
class _AmountsInput:
    """Everything the amounts of one run are computed from.

    ``upcoming_gross`` is the recurring gross of the withholding slots still
    to come, zero on the last slot.  ``eligible_work_days`` are the days of
    employment in the tax year the deductions are proportioned to.
    ``recovery_plan`` is the installment recovery opened in this tax year,
    if one is running.  ``later_payslips`` is false when the employment ends
    in the tax year: the conguaglio then defers nothing.
    """

    monthly_gross: Decimal
    event_inps_base: Decimal
    event_tfr_base: Decimal
    event_irpef_base: Decimal
    event_substitute_base: Decimal
    opening: TaxYearState
    withholding_schedule: WithholdingSchedule
    upcoming_gross: Decimal
    rules: YearRules
    contract_type: Permanent | FixedTerm | Apprentice
    category: WorkerCategory | None
    pdr_rules: PdRRules
    surtax_rules: SurtaxRules | None = None
    regione: str | None = None
    comune_belfiore: str | None = None
    family_composition: FamilyComposition | None = None
    family_deduction_rules: FamilyDeductionRules | None = None
    ivs_ceiling_applies: bool = True
    weekly_hours: int | None = None
    contributable_hours: Decimal | None = None
    domestic_hourly_rate: Decimal | None = None
    eligible_work_days: int = DAYS_IN_YEAR
    recovery_plan: RecoveryPlan | None = None
    later_payslips: bool = True


@dataclass(frozen=True)
class _PeriodAmounts:
    """Computed monetary amounts passed to pay-item and ledger builders.

    Does not include period_gross, period_net or period_employer_cost: those
    are derived from the ledger after all entries are posted.  ``surtax``
    carries the annual surtax decisions and issues behind ``period_surtax``;
    ``decisions`` holds every tax decision of the run, the surtax ones last.
    ``projected_taxable`` is the annual taxable income the IRPEF of the run
    was computed on; ``None`` when not recorded.  ``ulteriore`` is what
    the run recognized or recovered of the ulteriore detrazione.
    """

    monthly_gross: Decimal
    inps_employee: Decimal
    inps_employer: Decimal
    tfr: Decimal
    period_irpef: Decimal
    period_tratt: Decimal
    period_surtax: Decimal
    period_taxable: Decimal
    period_substitute_tax: Decimal
    pdr_eligible: Decimal
    surtax: SurtaxOutcome = field(default_factory=SurtaxOutcome)
    decisions: tuple[CalculationDecision, ...] = ()
    projected_taxable: Decimal | None = None
    ulteriore: UlterioreSettlement | None = None
