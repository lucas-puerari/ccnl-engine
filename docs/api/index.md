# API reference

Full reference for every public type and function exported by `ccnl_engine`.

## Modules

The package is split in two namespaces: `ccnl_engine.engine` (computation,
schemas and loaders) and `ccnl_engine.knowledge` (the versioned JSON data
bundle the loaders read). See [Knowledge base](knowledge.md).

| Page | Contents |
|---|---|
| [Engine](engine.md) | `compute()`, `Calculation`, `InputSnapshot`, `PayrollScenario`, `Employee`, `Employment`, `Employer`, `PayrollResult` |
| [Loaders](loaders.md) | `load_ccnl()`, `load_year_rules()`, `load_surtax_rules()`, `YearRules`, `InpsRates` |
| [Models](models.md) | `CCNL`, `Level`, `Allowance`, employment types, fiscal enums |
| [Knowledge](knowledge.md) | data layout, `__version__` |

## Quick reference

```python
from ccnl_engine import (
    # Core function
    compute,
    # Scenario and inputs
    PayrollScenario,
    Employee,
    Employment,
    Employer,
    Jurisdiction,
    Agreement,
    # Employment types
    Permanent,
    FixedTerm,
    Apprentice,
    # Seniority
    SeniorityByCount,
    SeniorityByDate,
    SeniorityByMonths,
    # Salary overrides
    RalOverride,
    DestinationRalOverride,
    # Dependants and deductions
    FamilyComposition,
    Art15Deductions,
    # Supplements
    OvertimeHours,
    WeeklyOvertimeHours,
    AbsenceDays,
    LeaveInput,
    SickInput,
    FringeBenefitInput,
    WelfareInput,
    BonusInput,
    # Output
    PayrollResult,
    FiscalSimplification,
    ScopeItem,
    # Calculation envelope
    Calculation,
    CalculationTrace,
    InputSnapshot,
    TraceCategory,
    TraceStep,
    # Rendering
    AnnualBreakdown,
    render_breakdown,
    # Version
    engine_version,
)
```

All types above are re-exported from the top-level `ccnl_engine` package.

## Guide cross-references

| Guide | Relevant API |
|---|---|
| [Employment types](../domain/employment-types.md) | `Permanent`, `FixedTerm`, `Apprentice` |
| [Pay components](../engine/pay-components.md) | `SeniorityByCount`, `SeniorityByMonths`, `RalOverride` |
| [Second level](../engine/second-level.md) | `Employer`, `Agreement` |
| [Fiscal](../engine/fiscal.md) | `Jurisdiction`, `FiscalSimplification` |
| [Domestic work](../engine/domestic-work.md) | `Employee.weekly_hours` |
