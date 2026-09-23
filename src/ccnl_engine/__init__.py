"""ccnl_engine — Italian CCNL payroll computation library.

Public API
----------
The single entry point is :class:`PayrollEngine`.  Construct it with
:meth:`~PayrollEngine.from_builtin_data` and call
:meth:`~PayrollEngine.calculate` for a single cedolino or
:meth:`~PayrollEngine.calculate_year` for a full-year run.

All types needed to call it and inspect its results are re-exported from
this module.

Tooling types (CCNL inspection, diff, loaders) are not part of the
stable API. Use the dedicated sub-namespaces instead:

- CCNL inspection: :mod:`ccnl_engine.engine.contract`
- Diff operations: :mod:`ccnl_engine.engine.diff`
- Tax/surtax loaders: :mod:`ccnl_engine.engine.tax`,
  :mod:`ccnl_engine.engine.surtax`

Usage::

    from ccnl_engine import PayrollEngine, PayrollRequest, PayrollRun

    engine = PayrollEngine.from_builtin_data()
    result = engine.calculate(PayrollRequest(
        run=PayrollRun(year=2026, month=1),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
    ))
    print(result.period_net)
"""

from __future__ import annotations

from ccnl_engine.api.requests import PayrollRequest, PayrollYearRequest
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
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.bilateral_funds import FlatMonthlyFund, RateFund
from ccnl_engine.engine.payroll.domain.bundle import PayrollBundle
from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation,
    CalculationTrace,
    InputSnapshot,
    TraceCategory,
    TraceStep,
)
from ccnl_engine.engine.payroll.domain.employee import (
    DestinationRalOverride,
    RalOverride,
    SeniorityByCount,
    SeniorityByDate,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.fiscal_ytd import FiscalYTD
from ccnl_engine.engine.payroll.domain.payroll_result import (
    AnnualEstimate,
    Contributions,
    Earnings,
    EmployerCost,
    Taxes,
)
from ccnl_engine.engine.payroll.domain.payroll_state import PayrollState
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PeriodPayrollInput,
    TaxPeriod,
)
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
from ccnl_engine.engine.payroll.service.bundle_loader import load_payroll_bundle
from ccnl_engine.engine.payroll.service.engine import PayrollEngine
from ccnl_engine.engine.payroll.service.render import (
    AnnualBreakdown,
    render_breakdown,
)
from ccnl_engine.engine.payroll.service.schemas import result_schema, scenario_schema
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
)
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.version import __version__ as engine_version

__all__ = [
    "AbsenceDays",
    "Agreement",
    "AnnualBreakdown",
    "AnnualEstimate",
    "AnnualEstimateInput",
    "Apprentice",
    "Art15Deductions",
    "BonusInput",
    "Calculation",
    "CalculationTrace",
    "CapabilityCatalog",
    "CapabilityEntry",
    "CapabilityGap",
    "CapabilityStatus",
    "CcnlEngineError",
    "CcnlId",
    "CcnlInfo",
    "Contributions",
    "DataIntegrityError",
    "Dependent",
    "DependentRelationship",
    "DestinationRalOverride",
    "Earnings",
    "Employee",
    "Employer",
    "EmployerCost",
    "Employment",
    "FamilyComposition",
    "FiscalSimplification",
    "FiscalYTD",
    "FixedTerm",
    "FlatMonthlyFund",
    "FringeBenefitInput",
    "InputSnapshot",
    "InvalidInputError",
    "Jurisdiction",
    "LeaveInput",
    "OutOfScopeError",
    "OvertimeHours",
    "PayrollBundle",
    "PayrollEngine",
    "PayrollRequest",
    "PayrollResult",
    "PayrollRun",
    "PayrollState",
    "PayrollYearRequest",
    "PeriodCalculationRequest",
    "PeriodCalculationResult",
    "PeriodId",
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
    "Taxes",
    "TraceCategory",
    "TraceStep",
    "UnknownCcnlError",
    "UnknownLevelError",
    "WeeklyOvertimeHours",
    "WelfareInput",
    "engine_version",
    "get_ccnl",
    "list_ccnls",
    "load_payroll_bundle",
    "render_breakdown",
    "result_schema",
    "scenario_schema",
    "search_ccnls",
]
