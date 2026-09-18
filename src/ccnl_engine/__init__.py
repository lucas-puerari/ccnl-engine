"""ccnl_engine — Italian CCNL payroll computation library.

Public API
----------
Two entry points are available:

- :func:`estimate_annual` — annual gross-to-net estimate (no period events).
- :func:`compute_month` — monthly payroll including period-specific events.

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
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation,
    CalculationTrace,
    InputSnapshot,
    MonthlyPayrollReport,
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
    Contract,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.family import FamilyComposition
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult, ScopeItem
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
from ccnl_engine.engine.payroll.service.orchestrator import (
    compute,  # noqa: F401 — kept for compatibility; not in __all__
    compute_month,
    estimate_annual,
)
from ccnl_engine.engine.payroll.service.render import (
    AnnualBreakdown,
    render_breakdown,
)
from ccnl_engine.version import __version__ as engine_version

__all__ = [
    "AbsenceDays",
    "Agreement",
    "AnnualBreakdown",
    "AnnualPayrollScenario",
    "Apprentice",
    "Art15Deductions",
    "BonusInput",
    "Calculation",
    "CalculationTrace",
    "Contract",
    "DestinationRalOverride",
    "Employee",
    "Employer",
    "Employment",
    "FamilyComposition",
    "FiscalSimplification",
    "FixedTerm",
    "FringeBenefitInput",
    "InputSnapshot",
    "Jurisdiction",
    "LeaveInput",
    "MonthlyPayrollReport",
    "OvertimeHours",
    "PayPeriod",
    "PayrollResult",
    "PayrollScenario",
    "Permanent",
    "RalOverride",
    "ScopeItem",
    "SeniorityByCount",
    "SeniorityByDate",
    "SeniorityByMonths",
    "SickInput",
    "SupplementaryAllowance",
    "TraceCategory",
    "TraceStep",
    "WeeklyOvertimeHours",
    "WelfareInput",
    "compute_month",
    "engine_version",
    "estimate_annual",
    "render_breakdown",
]
