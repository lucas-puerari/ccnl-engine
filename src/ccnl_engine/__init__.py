"""ccnl_engine — Italian CCNL payroll computation library.

Public API
----------
Two entry points are available:

- :func:`estimate_annual` — annual gross-to-net estimate (no period events).
- :func:`estimate_period_effects` — annual estimate with informational
  period-event fields (overtime, absences, fringe, bonuses).  Net and cost
  totals remain annualised; use this when you need the per-period breakdown
  fields alongside the structural figures.

All types needed to call them and inspect their results are re-exported from
this module.

Tooling types (CCNL inspection, diff, loaders) are not part of the
stable API. Use the dedicated sub-namespaces instead:

- CCNL inspection: :mod:`ccnl_engine.engine.contract`
- Diff operations: :mod:`ccnl_engine.engine.diff`
- Tax/surtax loaders: :mod:`ccnl_engine.engine.tax`,
  :mod:`ccnl_engine.engine.surtax`

Usage::

    from datetime import date

    from ccnl_engine import (
        estimate_annual,
        AnnualPayrollScenario, Employee, Employment, Employer,
        Permanent,
    )

    result = estimate_annual(AnnualPayrollScenario(
        employee=Employee(level_code="C2"),
        employment=Employment(
            ccnl="metalmeccanico-federmeccanica.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    ))
    print(result.result.net_annual)
    print(result.engine_version)
    print(result.ruleset_version)
"""

from __future__ import annotations

from ccnl_engine.engine.contract.domain.ccnl import SupplementaryAllowance
from ccnl_engine.engine.contract.service.discovery import (
    CcnlId,
    CcnlInfo,
    get_ccnl,
    list_ccnls,
    search_ccnls,
)
from ccnl_engine.engine.errors import (
    PUBLIC_ERROR_CODES,
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
from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation as PayrollReport,
)
from ccnl_engine.engine.payroll.domain.calculation import (
    CalculationTrace as PayrollTrace,
)
from ccnl_engine.engine.payroll.domain.calculation import (
    InputSnapshot as PayrollSnapshot,
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
from ccnl_engine.engine.payroll.domain.payroll_result import (
    AnnualEstimate,
    Contributions,
    Coverage,
    Earnings,
    EmployerCost,
    PeriodPayroll,
    ScopeItem,
    Taxes,
)
from ccnl_engine.engine.payroll.domain.period import PayrollPeriod, YTDState
from ccnl_engine.engine.payroll.domain.quality import (
    ConfidenceLevel,
    CoverageStatus,
    PayrollWarning,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    AnnualPayrollScenario,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PayPeriod,
    PayrollScenario,
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
from ccnl_engine.engine.payroll.domain.supplements import (
    BonusInput as Bonus,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    FringeBenefitInput as FringeBenefit,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    LeaveInput as Leave,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    SickInput as SickLeave,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    WelfareInput as Welfare,
)
from ccnl_engine.engine.payroll.service.bundle_loader import load_payroll_bundle
from ccnl_engine.engine.payroll.service.orchestrator import (
    compute,
    compute_period,
    compute_year,
    estimate_annual,
    estimate_period_effects,
)
from ccnl_engine.engine.payroll.service.render import (
    AnnualBreakdown,
    render_breakdown,
)
from ccnl_engine.engine.payroll.service.schemas import result_schema, scenario_schema
from ccnl_engine.version import __version__ as engine_version

__all__ = [
    "PUBLIC_ERROR_CODES",
    "AbsenceDays",
    "Agreement",
    "AnnualBreakdown",
    "AnnualEstimate",
    "AnnualPayrollScenario",
    "Apprentice",
    "Art15Deductions",
    "Bonus",
    "BonusInput",
    "Calculation",
    "CalculationTrace",
    "CcnlEngineError",
    "CcnlId",
    "CcnlInfo",
    "ConfidenceLevel",
    "Contributions",
    "Coverage",
    "CoverageStatus",
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
    "FixedTerm",
    "FlatMonthlyFund",
    "FringeBenefit",
    "FringeBenefitInput",
    "InputSnapshot",
    "InvalidInputError",
    "Jurisdiction",
    "Leave",
    "LeaveInput",
    "OutOfScopeError",
    "OvertimeHours",
    "PayPeriod",
    "PayrollBundle",
    "PayrollPeriod",
    "PayrollReport",
    "PayrollScenario",
    "PayrollSnapshot",
    "PayrollTrace",
    "PayrollWarning",
    "PeriodPayroll",
    "Permanent",
    "RalOverride",
    "RateFund",
    "ScopeItem",
    "SeniorityByCount",
    "SeniorityByDate",
    "SeniorityByMonths",
    "SickInput",
    "SickLeave",
    "SupplementaryAllowance",
    "Taxes",
    "TraceCategory",
    "TraceStep",
    "UnknownCcnlError",
    "UnknownLevelError",
    "WeeklyOvertimeHours",
    "Welfare",
    "WelfareInput",
    "YTDState",
    "compute",
    "compute_period",
    "compute_year",
    "engine_version",
    "estimate_annual",
    "estimate_period_effects",
    "get_ccnl",
    "list_ccnls",
    "load_payroll_bundle",
    "render_breakdown",
    "result_schema",
    "scenario_schema",
    "search_ccnls",
]
