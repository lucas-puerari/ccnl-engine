"""Facts a caller passes to :class:`~ccnl_engine.PayrollEngine`.

Everything a request or a plan carries beyond the common path: contract
types, hours, seniority, the TFR fund, family, prior and current year tax
facts, the calendar, the opening state and the balances imported from another provider.
"""

from __future__ import annotations

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.payroll.application.opening_balances import OpeningBalances
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.calendar_override import (
    CalendarOverride,
    CalendarOverrideReason,
)
from ccnl_engine.payroll.domain.current_year import (
    CurrentYearTaxFacts,
    IncomeEstimateQuality,
)
from ccnl_engine.payroll.domain.eligibility import ContributionHistory
from ccnl_engine.payroll.domain.employer import EmployerActivity
from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.payroll.domain.employment_facts import (
    ContributableHours,
    EmploymentPeriod,
    PublicEndOfService,
    WeeklyHours,
)
from ccnl_engine.payroll.domain.employment_spells import EmploymentSpell
from ccnl_engine.payroll.domain.engine_mode import EngineMode
from ccnl_engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.domain.fixed_term import NaspiExclusion
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.obligations import RecoveryObligation
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.pension_fund import NoPensionFund, PensionFundEnrolment
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.prior_year import (
    ForeignTaxPaid,
    PriorYearTaxFacts,
    ShortfallDeferralRequest,
    SubstituteTaxRegime,
)
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.seniority_fact import SeniorityFact, SenioritySource
from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.domain.state_codec import (
    period_state_from_json,
    period_state_to_json,
)
from ccnl_engine.payroll.domain.surtax_obligations import (
    SurtaxComponent,
    SurtaxObligation,
)
from ccnl_engine.payroll.domain.tfr_fund import TfrFundBalance
from ccnl_engine.tax.domain.preferential_regime import EmploymentSector

__all__ = [
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
