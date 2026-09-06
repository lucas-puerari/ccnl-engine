"""ccnl_engine — Italian CCNL payroll computation library.

Public API
----------
The single entry point is :func:`compute`.  All types needed to call it and
interpret its result are re-exported from this module.

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

from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.engine.compute import compute
from ccnl_engine.engine.payslip import Payslip
from ccnl_engine.models.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipPeriod,
    ApprenticeshipTrack,
    ApprenticeshipUnderClassification,
    UnderClassificationPeriod,
)
from ccnl_engine.models.ccnl import (
    CCNL,
    Allowance,
    CCNLExtraction,
    CCNLMeta,
    CCNLSource,
    CCNLValidity,
    Coverage,
    CoverageStatus,
    EmployerFund,
    Level,
    LevelCategory,
    Parameters,
    SeniorityIncrements,
    SupplementaryAllowance,
    TaxSector,
)
from ccnl_engine.models.employee import (
    ContractPosition,
    DestinationRalOverride,
    Employee,
    IndividualAgreement,
    RalOverride,
    RalOverrideMode,
    Seniority,
    SeniorityByCount,
    SeniorityByMonths,
    TaxProfile,
    WorkArrangement,
)
from ccnl_engine.models.employer import Employer
from ccnl_engine.models.employment import Apprentice, Employment, FixedTerm, Permanent
from ccnl_engine.models.fiscal import FiscalSimplification
from ccnl_engine.models.validity import TimeSeries, ValidityPeriod
from ccnl_engine.tax.loaders import load_year_rules
from ccnl_engine.tax.models import YearRules

__all__ = [
    "CCNL",
    "Allowance",
    "Apprentice",
    "ApprenticeshipPercentage",
    "ApprenticeshipPeriod",
    "ApprenticeshipTrack",
    "ApprenticeshipUnderClassification",
    "CCNLExtraction",
    "CCNLMeta",
    "CCNLSource",
    "CCNLValidity",
    "ContractPosition",
    "Coverage",
    "CoverageStatus",
    "DestinationRalOverride",
    "Employee",
    "Employer",
    "EmployerFund",
    "Employment",
    "FiscalSimplification",
    "FixedTerm",
    "IndividualAgreement",
    "Level",
    "LevelCategory",
    "Parameters",
    "Payslip",
    "Permanent",
    "RalOverride",
    "RalOverrideMode",
    "Seniority",
    "SeniorityByCount",
    "SeniorityByMonths",
    "SeniorityIncrements",
    "SupplementaryAllowance",
    "TaxProfile",
    "TaxSector",
    "TimeSeries",
    "UnderClassificationPeriod",
    "ValidityPeriod",
    "WorkArrangement",
    "YearRules",
    "compute",
    "load_ccnl",
    "load_year_rules",
]
