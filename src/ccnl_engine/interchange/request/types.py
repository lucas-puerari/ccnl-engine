"""The types a request of :class:`~ccnl_engine.PayrollEngine` is built from."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.hours.inputs import LeaveHours
from ccnl_engine.absence.insured.parental.inputs import ParentalLeaveTaken
from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.balance.serializers import STATE_TYPES
from ccnl_engine.calendar.inputs import CalendarOverride, CalendarOverrideReason
from ccnl_engine.calendar.models import WorkCalendar
from ccnl_engine.compensation.individual.inputs import IndividualElement
from ccnl_engine.compensation.second_level.inputs import (
    SecondLevelAgreement,
    SecondLevelElement,
)
from ccnl_engine.contribution.ceiling.inputs import ContributionHistory
from ccnl_engine.contribution.zone.models import AgriculturalZone
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.apprentice.inputs import ApprenticeshipProgramme, DualHours
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.change.inputs import EmploymentChange
from ccnl_engine.employment.fact.inputs import (
    ContributableHours,
    PublicEndOfService,
    WeeklyHours,
    WorkPattern,
)
from ccnl_engine.employment.fixed_term.inputs import FixedTerm, NaspiExclusion
from ccnl_engine.employment.inputs import Apprentice, Employment, Permanent
from ccnl_engine.employment.period.inputs import (
    CollectiveDismissal,
    EmploymentPeriod,
    NaspiCase,
    TerminationCause,
)
from ccnl_engine.employment.rest_day.inputs import Weekday
from ccnl_engine.employment.rota.inputs import Rota
from ccnl_engine.event.types import WORK_EVENT_TYPES
from ccnl_engine.extra_month.schedule.models import (
    ExtraMonthKind,
    ExtraMonthSchedule,
)
from ccnl_engine.family.inputs import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.irpef.declaration.inputs import PriorYearTaxFacts
from ccnl_engine.irpef.other_income.inputs import (
    CurrentYearTaxFacts,
    IncomeEstimateQuality,
)
from ccnl_engine.irpef.prior.inputs import PriorEmployerIncome
from ccnl_engine.pension_fund.inputs import NoPensionFund, PensionFundEnrolment
from ccnl_engine.period.facts.holiday import PaidHolidayDays
from ccnl_engine.period.inputs import PeriodFacts, PeriodInput
from ccnl_engine.personal_withholding.inputs import (
    PersonalWithholding,
    PersonalWithholdingKind,
)
from ccnl_engine.regime.models import (
    EmployerActivity,
    EmploymentSector,
    SubstituteTaxRegime,
)
from ccnl_engine.run.models import PayrollRun
from ccnl_engine.run.types import PeriodId
from ccnl_engine.seniority.inputs import (
    EarnedIncrements,
    SeniorityFact,
    SeniorityPromotion,
    SenioritySource,
)
from ccnl_engine.severance.provision.models import TfrFundBalance
from ccnl_engine.sickness.diagnosis import SeriousIllnessKind
from ccnl_engine.tax_credit.art15.inputs import Art15Expense, Art15Kind
from ccnl_engine.tax_credit.foreign.inputs import ForeignTaxPaid
from ccnl_engine.withholding.assistance.inputs import (
    Form730Kind,
    Form730Line,
    Form730Settlement,
)
from ccnl_engine.withholding.deferral.inputs import ShortfallDeferralRequest
from ccnl_engine.working_time.inputs import (
    HolidayWorkKind,
    OvertimeKind,
    ShiftKind,
)
from ccnl_engine.working_time.standby.inputs import StandbyKind
from ccnl_engine.year.competence.inputs import CompetenceYearPlan
from ccnl_engine.year.tax_year.inputs import TaxYearPlan

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["REQUEST_TYPES"]

#: Every type a request may contain, keyed by the tag it is written with:
#: the request types, what they hold and the types of an opening state.
REQUEST_TYPES: Mapping[str, type] = MappingProxyType({
    **STATE_TYPES,
    **{
        cls.__name__: cls
        for cls in (
            *WORK_EVENT_TYPES,
            AgriculturalZone,
            Apprentice,
            ApprenticeshipProgramme,
            CalendarOverride,
            CalendarOverrideReason,
            CompetenceYearPlan,
            CollectiveDismissal,
            ContributableHours,
            ContributionHistory,
            CurrentYearTaxFacts,
            Dependent,
            DualHours,
            DependentRelationship,
            EmployerActivity,
            EmployerProfile,
            Employment,
            EarnedIncrements,
            SeniorityPromotion,
            SecondLevelAgreement,
            SecondLevelElement,
            EmploymentChange,
            EmploymentPeriod,
            EmploymentSector,
            ExtraMonthKind,
            ExtraMonthSchedule,
            FamilyComposition,
            FixedTerm,
            ForeignTaxPaid,
            Headcount,
            PriorEmployerIncome,
            Form730Settlement,
            Form730Line,
            Form730Kind,
            Art15Expense,
            Art15Kind,
            HolidayWorkKind,
            IncomeEstimateQuality,
            IndividualElement,
            ParentalLeaveTaken,
            NaspiCase,
            NaspiExclusion,
            NoPensionFund,
            OvertimeKind,
            PaidHolidayDays,
            PayrollRun,
            PensionFundEnrolment,
            PersonalWithholding,
            PersonalWithholdingKind,
            LeaveHours,
            PeriodFacts,
            PeriodId,
            PeriodInput,
            Permanent,
            PriorYearTaxFacts,
            PublicEndOfService,
            SeniorityFact,
            SenioritySource,
            SeriousIllnessKind,
            ShiftKind,
            ShortfallDeferralRequest,
            StandbyKind,
            SubstituteTaxRegime,
            TaxSector,
            TaxYearPlan,
            TerminationCause,
            TfrFundBalance,
            WeeklyHours,
            Weekday,
            Rota,
            WorkCalendar,
            WorkerCategory,
            WorkPattern,
        )
    },
})
