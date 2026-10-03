# API reference

Full reference for every public type and function exported by `ccnl_engine`.

## Modules

The package is organised by capability: `ccnl_engine.payroll` (computation),
`ccnl_engine.contract` and `ccnl_engine.tax` (schemas and loaders), and
`ccnl_engine.knowledge` (the versioned JSON data bundle the loaders read, plus
the readers in `ccnl_engine.knowledge.service`). See
[Knowledge base](knowledge.md).

| Page | Contents |
|---|---|
| [Engine](engine.md) | `PayrollEngine`, `EngineMode`, `ContractSummary`, `RulesetAssurance`, `PeriodInput`, `CompetenceYearPlan`, `TaxYearPlan`, `OpeningBalances`, `InpsBaseYtd`, `PeriodFacts`, `Employment`, `EmployerProfile`, `PriorYearTaxFacts`, `PayrollRun`, `CalendarOverride`, `PeriodResult`, `CompetenceYearResult`, `TaxYearResult`, `ResultAssurance`, `ResultBlocker`, `BlockerCode`, `ModelLimitation`, `MonetaryImpact`, `LimitationStatus`, `CalculationStatus`, `CalculationIssue`, `CalculationDecision` |
| [Loaders](loaders.md) | `load_ccnl()`, `load_year_rules()`, `load_surtax_rules()`, `YearRules`, `InpsRates` |
| [Models](models.md) | `CCNL`, `Level`, `Allowance`, employment types, fiscal enums |
| [Knowledge](knowledge.md) | data layout, `__version__` |

## Quick reference

```python
from ccnl_engine import (
    # Entry point
    PayrollEngine,
    # Inputs
    PeriodInput,
    CompetenceYearPlan,
    TaxYearPlan,
    PeriodFacts,
    PayrollRun,
    PayrollRunId,
    PaymentId,
    CalendarOverride,
    CalendarOverrideReason,
    WorkCalendar,
    PeriodState,
    OpeningBalances,
    InpsBaseYtd,
    RecoveryObligation,
    RecoveryPlan,
    SurtaxObligation,
    SurtaxComponent,
    # Employment, employer and prior-year facts
    Employment,
    EmploymentPeriod,
    WeeklyHours,
    SeniorityFact,
    SenioritySource,
    ContributableHours,
    ContributionHistory,
    EmploymentSector,
    Permanent,
    FixedTerm,
    Apprentice,
    WorkerCategory,
    EmployerProfile,
    EmployerActivity,
    Headcount,
    PriorYearTaxFacts,
    SubstituteTaxRegime,
    # Family
    FamilyComposition,
    Dependent,
    DependentRelationship,
    # Results and assurance
    PeriodResult,
    CompetenceYearResult,
    TaxYearResult,
    ResultAssurance,
    ResultBlocker,
    BlockerCode,
    ModelLimitation,
    MonetaryImpact,
    LimitationStatus,
    CoverageStatus,
    EvidenceStatus,
    Payability,
    RulesetAssurance,
    RulesetIdentity,
    RulesetKind,
    RulesetReadiness,
    VerificationStatus,
    EngineMode,
    CalculationStatus,
    CalculationIssue,
    CalculationDecision,
    # Capability coverage
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityGap,
    CapabilityImplementation,
    CapabilityScope,
    # CCNL discovery
    CcnlId,
    ContractSummary,
    get_ccnl,
    search_ccnls,
    # Errors
    CcnlEngineError,
    DataIntegrityError,
    InvalidInputError,
    MissingRequiredFactError,
    MissingRuleError,
    OutOfScopeError,
    UnknownCcnlError,
    UnknownLevelError,
    UnsupportedTaxYearError,
    # Version
    engine_version,
    # Work events
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
    TerminationTFREvent,
    WelfareEvent,
    WorkEvent,
)
```

Every public name, work events included, is exported by the top-level
`ccnl_engine` package. For the work events see
[Work rules](../engine/work-rules.md).

## Guide cross-references

| Guide | Relevant API |
|---|---|
| [Employment types](../domain/employment-types.md) | `Permanent`, `FixedTerm`, `Apprentice` |
| [Pay components](../engine/pay-components.md) | `Employment.seniority`, `Employment.weekly_hours`, `WorkerCategory`, `BilateralFundEvent` |
| [Second level](../engine/second-level.md) | `CompetenceYearPlan`, `CalendarOverride` |
| [Fiscal](../engine/fiscal.md) | `CalculationDecision`, `CalculationIssue`, `REGION_CODES` |
| [Domestic work](../engine/domestic-work.md) | `Employment.weekly_hours`, `PeriodFacts.contributable_hours` |
