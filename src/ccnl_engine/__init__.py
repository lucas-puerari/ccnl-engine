"""ccnl_engine — Italian CCNL payroll computation library.

Public API
----------
The single entry point is :class:`PayrollEngine`.  Construct it with
:meth:`~PayrollEngine.bundled` and call
:meth:`~PayrollEngine.calculate` for a single cedolino or
:meth:`~PayrollEngine.calculate_year` for a full-year run.

All types needed to call it and inspect its results are re-exported from
this module.

Usage::

    from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun

    engine = PayrollEngine.bundled()
    result = engine.calculate(PayrollRequest(
        run=PayrollRun.regular(2026, 1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(),
    ))
    print(result.period_net)
"""

from __future__ import annotations

from ccnl_engine.api.facade import PayrollEngine
from ccnl_engine.api.requests import EmploymentFacts, PayrollRequest, PayrollYearRequest
from ccnl_engine.api.results import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    PayrollResult,
)
from ccnl_engine.engine.capability_catalog import (
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityGap,
    CapabilityStatus,
)
from ccnl_engine.engine.contract.domain.category import WorkerCategory
from ccnl_engine.engine.contract.domain.ccnl import SupplementaryAllowance
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
from ccnl_engine.payroll.application.calculate_year import (
    YearCalculationResult as PayrollYearResult,
)
from ccnl_engine.payroll.application.opening_balances import OpeningBalances
from ccnl_engine.payroll.domain.calendar import WorkCalendar as PayrollCalendar
from ccnl_engine.payroll.domain.calendar_override import (
    CalendarOverride,
    CalendarOverrideReason,
)
from ccnl_engine.payroll.domain.employer import Employer, Headcount
from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.domain.obligations import RecoveryObligation
from ccnl_engine.payroll.domain.period import PeriodState as PayrollState
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRun, PayrollRunId
from ccnl_engine.version import __version__ as engine_version

__all__ = [
    "Apprentice",
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
    "DataIntegrityError",
    "Dependent",
    "DependentRelationship",
    "Employer",
    "EmploymentFacts",
    "FamilyComposition",
    "FixedTerm",
    "Headcount",
    "InvalidInputError",
    "OpeningBalances",
    "OutOfScopeError",
    "PayrollCalendar",
    "PayrollEngine",
    "PayrollRequest",
    "PayrollResult",
    "PayrollRun",
    "PayrollRunId",
    "PayrollState",
    "PayrollYearRequest",
    "PayrollYearResult",
    "Permanent",
    "RecoveryObligation",
    "RecoveryPlan",
    "SupplementaryAllowance",
    "UnknownCcnlError",
    "UnknownLevelError",
    "UnsupportedTaxYearError",
    "WorkerCategory",
    "engine_version",
    "get_ccnl",
    "list_ccnls",
    "search_ccnls",
]
