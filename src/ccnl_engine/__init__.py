"""ccnl_engine — Italian CCNL payroll computation library.

Public API
----------
The single entry point is :func:`compute`. All types needed to call it
and interpret its result are re-exported from this module.

Data loading (CCNL files, tax/INPS/surtax rules) is handled internally by
:func:`compute`; :func:`load_ccnl`, :func:`load_year_rules`, and
:func:`load_surtax_rules` remain public for inspection and tooling.

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

from ccnl_engine.engine.contract import CCNL, load_ccnl
from ccnl_engine.engine.contract.domain.ccnl import (
    Allowance,
    LevelCategory,
    SupplementaryAllowance,
    TaxSector,
)
from ccnl_engine.engine.diff import (
    RuleChange,
    RulesDiff,
    count_affected_scenarios,
    diff_ccnl,
    format_diff,
)
from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity, VerificationStatus
from ccnl_engine.engine.payroll.domain.calculation import Calculation
from ccnl_engine.engine.payroll.domain.employee import (
    DestinationRalOverride,
    RalOverride,
    SeniorityByCount,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    Contract,
    FixedTerm,
    Permanent,
)
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
from ccnl_engine.engine.payroll.domain.supplements import AbsenceDays, LeaveInput
from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.engine.provenance import SourceAuthority
from ccnl_engine.engine.surtax import SurtaxRules, load_surtax_rules
from ccnl_engine.engine.tax import YearRules, load_year_rules
from ccnl_engine.version import __version__ as engine_version

__all__ = [
    "CCNL",
    "AbsenceDays",
    "Agreement",
    "Allowance",
    "Apprentice",
    "Calculation",
    "Contract",
    "DestinationRalOverride",
    "Employee",
    "Employer",
    "Employment",
    "FiscalSimplification",
    "FixedTerm",
    "Jurisdiction",
    "LeaveInput",
    "LevelCategory",
    "PayrollResult",
    "PayrollScenario",
    "Permanent",
    "RalOverride",
    "RuleChange",
    "RulesDiff",
    "RulesetIdentity",
    "ScopeItem",
    "SeniorityByCount",
    "SeniorityByMonths",
    "SourceAuthority",
    "SupplementaryAllowance",
    "SurtaxRules",
    "TaxSector",
    "VerificationStatus",
    "YearRules",
    "compute",
    "count_affected_scenarios",
    "diff_ccnl",
    "engine_version",
    "format_diff",
    "load_ccnl",
    "load_surtax_rules",
    "load_year_rules",
]
