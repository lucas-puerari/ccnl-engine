"""ccnl_engine — Italian CCNL payroll computation library.

Public API
----------
The single entry point is :func:`compute`.  All types needed to call it and
interpret its result are re-exported from this module.

Usage::

    from ccnl_engine import compute, Scenario, load_ccnl, load_year_rules
    from ccnl_engine import Permanent
    from datetime import date

    ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
    rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)
    scenario = Scenario(
        level_code="C2",
        as_of=date(2026, 1, 1),
        employment=Permanent(),
    )
    payslip = compute(ccnl, rules, scenario)
"""

from __future__ import annotations

from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.engine.compute import Scenario, compute
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
    TaxSector,
)
from ccnl_engine.models.employment import Apprentice, Employment, FixedTerm, Permanent
from ccnl_engine.models.fiscal import FiscalSimplification
from ccnl_engine.models.validity import TimeSeries, ValidityPeriod
from ccnl_engine.tax.loaders import load_year_rules
from ccnl_engine.tax.models import YearRules

__all__ = [
    # CCNL models
    "CCNL",
    "Allowance",
    "Apprentice",
    # Apprenticeship
    "ApprenticeshipPercentage",
    "ApprenticeshipPeriod",
    "ApprenticeshipTrack",
    "ApprenticeshipUnderClassification",
    "CCNLExtraction",
    "CCNLMeta",
    "CCNLSource",
    "CCNLValidity",
    "Coverage",
    "CoverageStatus",
    "EmployerFund",
    # Employment
    "Employment",
    "FiscalSimplification",
    "FixedTerm",
    "Level",
    "LevelCategory",
    "Parameters",
    "Payslip",
    "Permanent",
    "Scenario",
    "SeniorityIncrements",
    "TaxSector",
    # Validity / time series
    "TimeSeries",
    "UnderClassificationPeriod",
    "ValidityPeriod",
    # Tax
    "YearRules",
    # Engine
    "compute",
    # Loaders
    "load_ccnl",
    "load_year_rules",
]
