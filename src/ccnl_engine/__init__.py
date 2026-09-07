"""ccnl_engine — Italian CCNL payroll computation library.

Public API
----------
The single entry point is :func:`compute`.  All types needed to call
it and interpret its result are re-exported from this module.

Data loading (CCNL files, tax/INPS/surtax rules) is implemented in
:mod:`ccnl_engine.engine` loaders and reads the versioned datasets bundled in
:mod:`ccnl_engine.knowledge`.

Usage::

    from ccnl_engine import (
        compute, Employee, Employer, load_ccnl, load_year_rules,
        ContractPosition, WorkArrangement,
        Permanent,
    )
    from datetime import date

    ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
    rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)
    employee = Employee(
        position=ContractPosition(
            level_code="C2",
            as_of=date(2026, 1, 1),
            employment=Permanent(),
        ),
        arrangement=WorkArrangement(),
    )
    payslip = compute(ccnl, rules, employee)
"""

from __future__ import annotations

from ccnl_engine.engine.contract import CCNL, load_ccnl
from ccnl_engine.engine.contract.domain.ccnl import (
    Allowance,
    CCNLMeta,
    CCNLParameters,
    EmployerFund,
    Level,
    LevelCategory,
    SeniorityIncrements,
    SupplementaryAllowance,
    TaxSector,
)
from ccnl_engine.engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.engine.payroll.domain.employee import (
    ContractPosition,
    DestinationRalOverride,
    Employee,
    RalOverride,
    RalOverrideMode,
    SalaryOverrides,
    Seniority,
    SeniorityByCount,
    SeniorityByMonths,
    TaxProfile,
    WorkArrangement,
)
from ccnl_engine.engine.payroll.domain.employer import Employer
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    Employment,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.payslip import Payslip
from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.engine.surtax import SurtaxRules, load_surtax_rules
from ccnl_engine.engine.tax import YearRules, load_year_rules

__all__ = [
    "CCNL",
    "Allowance",
    "Apprentice",
    "CCNLMeta",
    "CCNLParameters",
    "ContractPosition",
    "DestinationRalOverride",
    "Employee",
    "Employer",
    "EmployerFund",
    "Employment",
    "FiscalSimplification",
    "FixedTerm",
    "Level",
    "LevelCategory",
    "Payslip",
    "Permanent",
    "RalOverride",
    "RalOverrideMode",
    "SalaryOverrides",
    "Seniority",
    "SeniorityByCount",
    "SeniorityByMonths",
    "SeniorityIncrements",
    "SupplementaryAllowance",
    "SurtaxRules",
    "TaxProfile",
    "TaxSector",
    "TimeSeries",
    "ValidityPeriod",
    "WorkArrangement",
    "YearRules",
    "compute",
    "load_ccnl",
    "load_surtax_rules",
    "load_year_rules",
]
