"""Inputs and outputs of the amounts of one run."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.amounts._surtax import RunSurtax
from ccnl_engine.payroll.domain.recovery_plan import InstallmentRun
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
    from ccnl_engine.payroll.domain.surtax_obligations import SurtaxObligation
    from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
    from ccnl_engine.payroll.service.pension_fund import (
        PensionContribution,
        PensionFundTerms,
    )
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
    earlier conguaglio still to withhold; ``run_month`` and
    ``regular_run`` place the run in the installment windows.
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
    ulteriore_plan: RecoveryPlan | None = None
    installment_run: InstallmentRun = field(default_factory=InstallmentRun)
    withholding_agent: bool = True
    pension: PensionFundTerms | None = None
    conguaglio: bool = False
    surtax_obligations: tuple[SurtaxObligation, ...] = ()
    run_month: int = 1
    regular_run: bool = True


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
    when the worker is not enrolled.
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
    surtax: RunSurtax = field(default_factory=RunSurtax)
    decisions: tuple[CalculationDecision, ...] = ()
    projected_taxable: Decimal | None = None
    ulteriore: UlterioreSettlement | None = None
    pension: PensionContribution | None = None
