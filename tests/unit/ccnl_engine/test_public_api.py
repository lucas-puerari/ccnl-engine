"""Contract tests for ccnl_engine's public API surface.

These tests guard against accidental drift in __all__ and ensure that
every advertised name is importable.
"""

import ccnl_engine

EXPECTED_PUBLIC: frozenset[str] = frozenset({
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
})


def test_all_exact() -> None:
    """__all__ must match the expected set exactly — no more, no less."""
    assert set(ccnl_engine.__all__) == EXPECTED_PUBLIC


def test_all_names_resolve() -> None:
    """Every name in __all__ must be importable from ccnl_engine."""
    for name in ccnl_engine.__all__:
        assert hasattr(ccnl_engine, name), f"Missing from ccnl_engine: {name}"
