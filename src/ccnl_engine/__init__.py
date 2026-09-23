"""ccnl_engine — Italian CCNL payroll computation library.

Public API
----------
The single entry point is :class:`PayrollEngine`.  Construct it with
:meth:`~PayrollEngine.from_builtin_data` and call
:meth:`~PayrollEngine.calculate` for a single cedolino or
:meth:`~PayrollEngine.calculate_year` for a full-year run.

All types needed to call it and inspect its results are re-exported from
this module.  Internal types (legacy scenario domain, rendering utilities,
JSON schema helpers, bundle loaders) are available from their respective
sub-namespaces and are not part of the stable public API.

Usage::

    from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun

    engine = PayrollEngine.from_builtin_data()
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

from ccnl_engine.api.requests import EmploymentFacts, PayrollRequest, PayrollYearRequest
from ccnl_engine.api.results import PayrollResult
from ccnl_engine.engine.capability_catalog import (
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityGap,
    CapabilityStatus,
)
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
)
from ccnl_engine.engine.payroll.domain.annual_input import AnnualEstimateInput
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.bilateral_funds import FlatMonthlyFund, RateFund
from ccnl_engine.engine.payroll.domain.employee import (
    Agreement,
    DestinationRalOverride,
    Employee,
    Jurisdiction,
    RalOverride,
    SeniorityByCount,
    SeniorityByDate,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.employer import Employer
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    Employment,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.period_input import PeriodPayrollInput
from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    SickInput,
    WeeklyOvertimeHours,
    WelfareInput,
)
from ccnl_engine.engine.payroll.domain.tax_basis import TaxPeriod
from ccnl_engine.engine.payroll.service.engine import PayrollEngine
from ccnl_engine.payroll.domain.period import PeriodState as PayrollState
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.version import __version__ as engine_version

__all__ = [
    "AbsenceDays",
    "Agreement",
    "AnnualEstimateInput",
    "Apprentice",
    "Art15Deductions",
    "BonusInput",
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
    "DestinationRalOverride",
    "Employee",
    "Employer",
    "Employment",
    "EmploymentFacts",
    "FamilyComposition",
    "FiscalSimplification",
    "FixedTerm",
    "FlatMonthlyFund",
    "FringeBenefitInput",
    "InvalidInputError",
    "Jurisdiction",
    "LeaveInput",
    "OutOfScopeError",
    "OvertimeHours",
    "PayrollEngine",
    "PayrollRequest",
    "PayrollResult",
    "PayrollRun",
    "PayrollState",
    "PayrollYearRequest",
    "PeriodPayrollInput",
    "Permanent",
    "RalOverride",
    "RateFund",
    "SeniorityByCount",
    "SeniorityByDate",
    "SeniorityByMonths",
    "SickInput",
    "SupplementaryAllowance",
    "TaxPeriod",
    "UnknownCcnlError",
    "UnknownLevelError",
    "WeeklyOvertimeHours",
    "WelfareInput",
    "engine_version",
    "get_ccnl",
    "list_ccnls",
    "search_ccnls",
]
