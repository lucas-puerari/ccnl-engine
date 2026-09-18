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
    "WelfareInput",
    "WeeklyOvertimeHours",
    "compute_month",
    "engine_version",
    "estimate_annual",
    "render_breakdown",
})


def test_all_exact() -> None:
    """__all__ must match the expected set exactly — no more, no less."""
    assert set(ccnl_engine.__all__) == EXPECTED_PUBLIC


def test_all_names_resolve() -> None:
    """Every name in __all__ must be importable from ccnl_engine."""
    for name in ccnl_engine.__all__:
        assert hasattr(ccnl_engine, name), f"Missing from ccnl_engine: {name}"
