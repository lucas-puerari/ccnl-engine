"""Contract tests for ccnl_engine's public API surface.

These tests guard against accidental drift in __all__ and ensure that
every advertised name is importable.
"""

import ccnl_engine

EXPECTED_PUBLIC: frozenset[str] = frozenset({
    "AbsenceDays",
    "Agreement",
    "AnnualBreakdown",
    "AnnualPayrollScenario",
    "Apprentice",
    "Art15Deductions",
    "Bonus",
    "BonusInput",
    "CcnlEngineError",
    "CcnlId",
    "CcnlInfo",
    "Calculation",
    "CalculationTrace",
    "ConfidenceLevel",
    "CoverageStatus",
    "DestinationRalOverride",
    "Employee",
    "Employer",
    "Employment",
    "FamilyComposition",
    "FiscalSimplification",
    "FixedTerm",
    "FlatMonthlyFund",
    "FringeBenefit",
    "FringeBenefitInput",
    "InputSnapshot",
    "Jurisdiction",
    "Leave",
    "LeaveInput",
    "MonthlyPayrollReport",
    "OvertimeHours",
    "PayPeriod",
    "PayrollEmployer",
    "PayrollFigures",
    "PayrollPay",
    "PayrollPeriod",
    "PayrollQuality",
    "PayrollReport",
    "PayrollResult",
    "PayrollScenario",
    "PayrollSnapshot",
    "PayrollTax",
    "PayrollTrace",
    "PayrollWarning",
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
    "TraceCategory",
    "TraceStep",
    "UnknownCcnlError",
    "UnknownLevelError",
    "Welfare",
    "WelfareInput",
    "WeeklyOvertimeHours",
    "compute",
    "compute_month",
    "engine_version",
    "estimate_annual",
    "get_ccnl",
    "list_ccnls",
    "render_breakdown",
    "result_schema",
    "scenario_schema",
    "search_ccnls",
})


def test_all_exact() -> None:
    """__all__ must match the expected set exactly — no more, no less."""
    assert set(ccnl_engine.__all__) == EXPECTED_PUBLIC


def test_all_names_resolve() -> None:
    """Every name in __all__ must be importable from ccnl_engine."""
    for name in ccnl_engine.__all__:
        assert hasattr(ccnl_engine, name), f"Missing from ccnl_engine: {name}"
