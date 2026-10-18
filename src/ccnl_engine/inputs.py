"""Facts a caller passes to :class:`~ccnl_engine.PayrollEngine`.

Everything a request or a plan carries beyond the common path: contract
types, hours, seniority, the TFR fund, family, prior and current year tax
facts, the calendar, the opening state and the balances imported from another provider.
"""

from __future__ import annotations

from ccnl_engine.assurance.policies import EngineMode
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.balance.obligation.models import RecoveryObligation
from ccnl_engine.balance.opening.provider.services import OpeningBalances
from ccnl_engine.balance.persistence.serializers import (
    period_state_from_json,
    period_state_to_json,
)
from ccnl_engine.calendar.inputs import (
    CalendarOverride,
    CalendarOverrideReason,
)
from ccnl_engine.calendar.models import WorkCalendar
from ccnl_engine.calendar.payment.models import PaymentId
from ccnl_engine.contribution.base.models import InpsBaseYtd
from ccnl_engine.contribution.ceiling.inputs import ContributionHistory
from ccnl_engine.employer.inputs import (
    AgriculturalZone,
    EmployerActivity,
    TaxSector,
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
from ccnl_engine.family.inputs import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.irpef.declaration.inputs import (
    ForeignTaxPaid,
    PriorYearTaxFacts,
    ShortfallDeferralRequest,
    SubstituteTaxRegime,
)
from ccnl_engine.irpef.other_income.inputs import (
    CurrentYearTaxFacts,
    IncomeEstimateQuality,
)
from ccnl_engine.pension_fund.inputs import (
    NoPensionFund,
    PensionFundEnrolment,
)
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.run.models import PayrollRunId
from ccnl_engine.seniority.inputs import (
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.severance.provision.models import TfrFundBalance
from ccnl_engine.surtax.obligation.models import (
    SurtaxComponent,
    SurtaxObligation,
)
from ccnl_engine.tax_credit.recovery.models import RecoveryPlan
from ccnl_engine.withholding.deferral.inputs import DeferredShortfall

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
    "TaxSector",
    "TfrFundBalance",
    "WeeklyHours",
    "WorkCalendar",
    "WorkerCategory",
    "period_state_from_json",
    "period_state_to_json",
]
