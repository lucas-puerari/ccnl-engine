# API reference

Full reference for every public type and function exported by `ccnl_engine`.

## Modules

The package is split in two namespaces: `ccnl_engine.engine` (computation,
schemas and loaders) and `ccnl_engine.knowledge` (the versioned JSON data
bundle the loaders read). See [Knowledge base](knowledge.md).

| Page | Contents |
|---|---|
| [Engine](engine.md) | `PayrollEngine`, `PayrollRequest`, `PayrollYearRequest`, `PayrollRun`, `EmploymentFacts`, `CalendarOverride`, `Employer`, `WorkerCategory`, `CalculationStatus`, `CalculationIssue`, `CalculationDecision` |
| [Loaders](loaders.md) | `load_ccnl()`, `load_year_rules()`, `load_surtax_rules()`, `YearRules`, `InpsRates` |
| [Models](models.md) | `CCNL`, `Level`, `Allowance`, employment types, fiscal enums |
| [Knowledge](knowledge.md) | data layout, `__version__` |

## Quick reference

```python
from ccnl_engine import (
    # Entry point
    PayrollEngine,
    # Requests
    PayrollRequest,
    PayrollYearRequest,
    PayrollRun,
    EmploymentFacts,
    CalendarOverride,
    CalendarOverrideReason,
    PayrollCalendar,
    PayrollState,
    # Employment and employer
    Permanent,
    FixedTerm,
    Apprentice,
    WorkerCategory,
    Employer,
    Headcount,
    SupplementaryAllowance,
    # Family
    FamilyComposition,
    Dependent,
    DependentRelationship,
    # Results
    PayrollResult,
    PayrollYearResult,
    CalculationStatus,
    CalculationIssue,
    CalculationDecision,
    # Capability coverage
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityGap,
    CapabilityStatus,
    # CCNL discovery
    CcnlId,
    CcnlInfo,
    list_ccnls,
    get_ccnl,
    search_ccnls,
    # Errors
    CcnlEngineError,
    DataIntegrityError,
    InvalidInputError,
    OutOfScopeError,
    UnknownCcnlError,
    UnknownLevelError,
    UnsupportedTaxYearError,
    # Version
    engine_version,
)
from ccnl_engine.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
    TerminationTFREvent,
    WelfareEvent,
    WorkEvent,
)
```

All names in the first import are re-exported from the top-level
`ccnl_engine` package. Work event types live in `ccnl_engine.events`; see
[Work rules](../engine/work-rules.md).

## Guide cross-references

| Guide | Relevant API |
|---|---|
| [Employment types](../domain/employment-types.md) | `Permanent`, `FixedTerm`, `Apprentice` |
| [Pay components](../engine/pay-components.md) | `EmploymentFacts.seniority_months`, `EmploymentFacts.weekly_hours`, `WorkerCategory`, `BilateralFundEvent` |
| [Second level](../engine/second-level.md) | `SupplementaryAllowance` |
| [Fiscal](../engine/fiscal.md) | `CalculationDecision`, `CalculationIssue`, `REGION_CODES` |
| [Domestic work](../engine/domestic-work.md) | `EmploymentFacts.weekly_hours` |
