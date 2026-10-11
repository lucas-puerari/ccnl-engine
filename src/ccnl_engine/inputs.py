"""Facts a caller passes to :class:`~ccnl_engine.PayrollEngine`.

Everything a request or a plan carries beyond the common path: contract
types, hours, seniority, the TFR fund, family, prior and current year tax
facts, the calendar, the opening state and the balances imported from another provider.
"""

from __future__ import annotations

from ccnl_engine.contribution.base.models import InpsBaseYtd
from ccnl_engine.contribution.ceiling.inputs import ContributionHistory
from ccnl_engine.employer.inputs import (
    AgriculturalZone,
    EmployerActivity,
)
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.fact.inputs import (
    ContributableHours,
    EmploymentPeriod,
    PublicEndOfService,
    WeeklyHours,
)
from ccnl_engine.employment.fixed_term.inputs import NaspiExclusion
from ccnl_engine.employment.inputs import Apprentice, FixedTerm, Permanent
from ccnl_engine.employment.spell.models import EmploymentSpell
from ccnl_engine.payroll.assurance.policies_engine_mode import EngineMode
from ccnl_engine.payroll.family.inputs import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.period.models_run import PayrollRunId
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.state.models_obligation import RecoveryObligation
from ccnl_engine.payroll.state.models_surtax_obligation import (
    SurtaxComponent,
    SurtaxObligation,
)
from ccnl_engine.payroll.state.serializers_persistence import (
    period_state_from_json,
    period_state_to_json,
)
from ccnl_engine.payroll.state.services_opening_balance import OpeningBalances
from ccnl_engine.payroll.taxation.inputs_current_year import (
    CurrentYearTaxFacts,
    IncomeEstimateQuality,
)
from ccnl_engine.payroll.taxation.inputs_prior_year import (
    ForeignTaxPaid,
    PriorYearTaxFacts,
    ShortfallDeferralRequest,
    SubstituteTaxRegime,
)
from ccnl_engine.payroll.withholding.inputs_shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.withholding.models_recovery_plan import RecoveryPlan
from ccnl_engine.payroll.year.inputs_calendar_override import (
    CalendarOverride,
    CalendarOverrideReason,
)
from ccnl_engine.payroll.year.models_calendar import WorkCalendar
from ccnl_engine.payroll.year.models_payment import PaymentId
from ccnl_engine.pension_fund.inputs import (
    NoPensionFund,
    PensionFundEnrolment,
)
from ccnl_engine.seniority.inputs import (
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.severance.provision.models import TfrFundBalance
from ccnl_engine.tax.regime.models import EmploymentSector

__all__ = [
    "AgriculturalZone",
    "Apprentice",
    "CalendarOverride",
    "CalendarOverrideReason",
    "ContributableHours",
    "ContributionHistory",
    "CurrentYearTaxFacts",
    "DeferredShortfall",
    "Dependent",
    "DependentRelationship",
    "EmployerActivity",
    "EmploymentPeriod",
    "EmploymentSector",
    "EmploymentSpell",
    "EngineMode",
    "FamilyComposition",
    "FixedTerm",
    "ForeignTaxPaid",
    "IncomeEstimateQuality",
    "InpsBaseYtd",
    "NaspiExclusion",
    "NoPensionFund",
    "OpeningBalances",
    "PaymentId",
    "PayrollRunId",
    "PensionFundEnrolment",
    "PeriodState",
    "Permanent",
    "PriorYearTaxFacts",
    "PublicEndOfService",
    "RecoveryObligation",
    "RecoveryPlan",
    "SeniorityFact",
    "SenioritySource",
    "ShortfallDeferralRequest",
    "SubstituteTaxRegime",
    "SurtaxComponent",
    "SurtaxObligation",
    "TfrFundBalance",
    "WeeklyHours",
    "WorkCalendar",
    "WorkerCategory",
    "period_state_from_json",
    "period_state_to_json",
]
