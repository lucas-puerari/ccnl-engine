"""ccnl_engine — Italian CCNL payroll computation library.

Public API
----------
The single entry point is :func:`compute`. All types needed to call it
and inspect its result are re-exported from this module.

Tooling types (CCNL inspection, diff, loaders) are not part of the
stable API. Use the dedicated sub-namespaces instead:

- CCNL inspection: :mod:`ccnl_engine.engine.contract`
- Diff operations: :mod:`ccnl_engine.engine.diff`
- Tax/surtax loaders: :mod:`ccnl_engine.engine.tax`,
  :mod:`ccnl_engine.engine.surtax`

Usage::

    from datetime import date

    from ccnl_engine import (
        compute,
        PayrollScenario, Employee, Employment, Employer,
        Permanent,
    )

    result = compute(PayrollScenario(
        employee=Employee(level_code="C2"),
        employment=Employment(
            ccnl="metalmeccanico-federmeccanica.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            date=date(2026, 1, 1),
        ),
    ))
    print(result.result.net_annual)
    print(result.engine_version)
    print(result.ruleset_version)
"""

from __future__ import annotations

from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
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
    Contract,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.family import FamilyComposition
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult, ScopeItem
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PayrollScenario,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    SickInput,
    WelfareInput,
)
from ccnl_engine.engine.payroll.render import AnnualBreakdown, render_breakdown
from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.version import __version__ as engine_version

__all__ = [
    "AbsenceDays",
    "Agreement",
    "AnnualBreakdown",
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
    "OvertimeHours",
    "PayrollResult",
    "PayrollScenario",
    "Permanent",
    "RalOverride",
    "ScopeItem",
    "SeniorityByCount",
    "SeniorityByDate",
    "SeniorityByMonths",
    "SickInput",
    "TraceCategory",
    "TraceStep",
    "WelfareInput",
    "compute",
    "engine_version",
    "render_breakdown",
]
