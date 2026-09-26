"""ccnl_engine: Italian CCNL payroll computation library.

Public API
----------
The single entry point is :class:`PayrollEngine`.  Construct it with
:meth:`~PayrollEngine.bundled` and call
:meth:`~PayrollEngine.calculate_period` for one cedolino,
:meth:`~PayrollEngine.calculate_year` for every run of a tax year and
:meth:`~PayrollEngine.close_tax_year` to open the next tax year.

All types needed to call it and inspect its results are re-exported from
this module, work events included.

Usage::

    from datetime import date
    from ccnl_engine import (
        Employment, EmployerProfile, Headcount, PayrollEngine, PayrollRun,
        PeriodInput,
    )

    engine = PayrollEngine.bundled()
    result = engine.calculate_period(PeriodInput(
        run=PayrollRun.regular(2026, 1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    ))
    print(result.status, result.period_net)
"""

from __future__ import annotations

from ccnl_engine.api.facade import PayrollEngine
from ccnl_engine.engine.capability_catalog import (
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityGap,
    CapabilityStatus,
)
from ccnl_engine.engine.contract.domain.category import WorkerCategory
from ccnl_engine.engine.contract.service.discovery import (
    CcnlId,
    CcnlInfo,
    get_ccnl,
    list_ccnls,
    search_ccnls,
)
from ccnl_engine.engine.errors import (
    CcnlEngineError,
    DataIntegrityError,
    InvalidInputError,
    OutOfScopeError,
    UnknownCcnlError,
    UnknownLevelError,
    UnsupportedTaxYearError,
)
from ccnl_engine.engine.tax.domain.preferential_regime import EmploymentSector
from ccnl_engine.payroll.application.calculate_year import YearResult
from ccnl_engine.payroll.application.opening_balances import OpeningBalances
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.calendar_override import (
    CalendarOverride,
    CalendarOverrideReason,
)
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.eligibility import ContributionCeilingStatus
from ccnl_engine.payroll.domain.employer import (
    EmployerActivity,
    EmployerProfile,
    Headcount,
)
from ccnl_engine.payroll.domain.employment import (
    Apprentice,
    ContributableHours,
    Employment,
    EmploymentPeriod,
    FixedTerm,
    Permanent,
    SeniorityMonths,
    WeeklyHours,
)
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
    TerminationTFREvent,
    WelfareEvent,
    WorkEvent,
)
from ccnl_engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.domain.inputs import PeriodFacts, PeriodInput, YearInput
from ccnl_engine.payroll.domain.obligations import RecoveryObligation
from ccnl_engine.payroll.domain.period import PeriodResult, PeriodState
from ccnl_engine.payroll.domain.prior_year import (
    PriorYearTaxFacts,
    SubstituteTaxRegime,
)
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRun, PayrollRunId
from ccnl_engine.version import __version__ as engine_version

__all__ = [
    "AbsenceEvent",
    "Apprentice",
    "ArrearsEvent",
    "BilateralFundEvent",
    "BonusEvent",
    "CalculationDecision",
    "CalculationIssue",
    "CalculationStatus",
    "CalendarOverride",
    "CalendarOverrideReason",
    "CapabilityCatalog",
    "CapabilityEntry",
    "CapabilityGap",
    "CapabilityStatus",
    "CcnlEngineError",
    "CcnlId",
    "CcnlInfo",
    "ContributableHours",
    "ContributionCeilingStatus",
    "DataIntegrityError",
    "Dependent",
    "DependentRelationship",
    "EmployerActivity",
    "EmployerProfile",
    "Employment",
    "EmploymentPeriod",
    "EmploymentSector",
    "FamilyComposition",
    "FixedTerm",
    "FringeEvent",
    "Headcount",
    "HolidayWorkEvent",
    "InvalidInputError",
    "NightShiftEvent",
    "OpeningBalances",
    "OutOfScopeError",
    "OvertimeEvent",
    "PayrollEngine",
    "PayrollRun",
    "PayrollRunId",
    "PeriodFacts",
    "PeriodInput",
    "PeriodResult",
    "PeriodState",
    "Permanent",
    "PriorYearTaxFacts",
    "RecoveryObligation",
    "RecoveryPlan",
    "SeniorityMonths",
    "ShiftWorkEvent",
    "SickLeaveEvent",
    "SicknessCaseEvent",
    "SubstituteTaxRegime",
    "TerminationTFREvent",
    "UnknownCcnlError",
    "UnknownLevelError",
    "UnsupportedTaxYearError",
    "WeeklyHours",
    "WelfareEvent",
    "WorkCalendar",
    "WorkEvent",
    "WorkerCategory",
    "YearInput",
    "YearResult",
    "engine_version",
    "get_ccnl",
    "list_ccnls",
    "search_ccnls",
]
