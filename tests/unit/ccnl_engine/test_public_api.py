"""Contract tests for ccnl_engine's public API surface.

These tests guard against accidental drift in __all__ and ensure that
every advertised name is importable.
"""

import ccnl_engine

EXPECTED_PUBLIC: frozenset[str] = frozenset({
    "AbsenceDays",
    "Agreement",
    "AnnualBreakdown",
    "AnnualEstimate",
    "AnnualEstimateInput",
    "AnnualPayrollSummary",
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
    "FiscalYTD",
    "FlatMonthlyFund",
    "FringeBenefitInput",
    "InputSnapshot",
    "Jurisdiction",
    "LeaveInput",
    "OvertimeHours",
    "PeriodPayrollInput",
    "PayrollPeriod",
    "PayrollState",
    "PayrollYearRequest",
    "PayrollYearResult",
    "PeriodId",
    "PeriodPayroll",
    "PeriodPayrollRequest",
    "PeriodPayrollResult",
    "Taxes",
    "Permanent",
    "RalOverride",
    "RateFund",
    "SeniorityByCount",
    "SeniorityByDate",
    "SeniorityByMonths",
    "SickInput",
    "SupplementaryAllowance",
    "TaxPeriod",
    "TraceCategory",
    "TraceStep",
    "DataIntegrityError",
    "InvalidInputError",
    "OutOfScopeError",
    "UnknownCcnlError",
    "UnknownLevelError",
    "WelfareInput",
    "WeeklyOvertimeHours",
    "compute_payroll_year",
    "compute_period_payroll",
    "engine_version",
    "estimate_annual",
    "estimate_period_effects",
    "get_ccnl",
    "YTDState",
    "list_ccnls",
    "load_payroll_bundle",
    "PayrollBundle",
    "render_breakdown",
    "result_schema",
    "scenario_schema",
    "search_ccnls",
    "summarize_payroll_year",
})


def test_all_exact() -> None:
    """__all__ must match the expected set exactly — no more, no less."""
    assert set(ccnl_engine.__all__) == EXPECTED_PUBLIC


def test_all_names_resolve() -> None:
    """Every name in __all__ must be importable from ccnl_engine."""
    for name in ccnl_engine.__all__:
        assert hasattr(ccnl_engine, name), f"Missing from ccnl_engine: {name}"
