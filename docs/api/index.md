# API reference

Full reference for every public type and function of `ccnl_engine` and its
public namespaces.

## Modules

The package is organised by capability: `ccnl_engine.payroll` (computation),
`ccnl_engine.contract` and `ccnl_engine.tax` (schemas and loaders), and
`ccnl_engine.knowledge` (the versioned JSON data bundle the loaders read, plus
the readers in `ccnl_engine.knowledge.service`). See
[Knowledge base](knowledge.md).

| Page | Contents |
|---|---|
| [Engine](engine.md) | `PayrollEngine`, `EngineMode`, `ContractSummary`, `RulesetAssurance`, `PeriodInput`, `CompetenceYearPlan`, `TaxYearPlan`, `OpeningBalances`, `InpsBaseYtd`, `PeriodFacts`, `Employment`, `EmployerProfile`, `PriorYearTaxFacts`, `CurrentYearTaxFacts`, `PayrollRun`, `CalendarOverride`, `PeriodResult`, `CompetenceYearResult`, `TaxYearResult`, `ResultAssurance`, `ResultBlocker`, `BlockerCode`, `ModelLimitation`, `MonetaryImpact`, `LimitationStatus`, `CalculationStatus`, `CalculationIssue`, `CalculationDecision` |
| [Loaders](loaders.md) (internal) | `load_ccnl()`, `load_year_rules()`, `load_surtax_rules()`, `YearRules`, `InpsRates` |
| [Models](models.md) (internal) | `CCNL`, `Level`, `Allowance`, employment types, fiscal enums |
| [Knowledge](knowledge.md) | data layout, `__version__` |

The Engine page documents the public types from the modules that define
them; import them from the namespaces below. Loaders and Models document
internal modules, for contributors and tooling such as the demo: they are
not part of the public API and may change without notice.

## Public namespaces

The public API is the package root and four namespaces. Each public name has
exactly one import path: there are no aliases.

| Module | Holds |
|---|---|
| `ccnl_engine` | The common path: `PayrollEngine`, the request and plan types (`PeriodInput`, `PeriodFacts`, `PayrollRun`, `Employment`, `EmployerProfile`, `Headcount`, `CompetenceYearPlan`, `TaxYearPlan`), the results the facade returns (`PeriodResult`, `CompetenceYearResult`, `TaxYearResult`), every public error and `engine_version` |
| `ccnl_engine.inputs` | Facts beyond the common path: contract types, hours, seniority, family, prior and current year tax facts, calendar, engine mode, opening state and imported balances |
| `ccnl_engine.events` | Work events of a period and the `PeriodId` an arrears event refers to |
| `ccnl_engine.results` | Assurance, blockers, decisions, issues, model limitations, capability gaps, runs a year left out, ledger account kinds and remittance lines |
| `ccnl_engine.catalog` | Bundled contracts and their discovery, ruleset identity and readiness, the capability catalog |

Any module below these five is internal and may change without notice,
including the loaders, the CCNL models and `REGION_CODES` named in the
guides.

## Quick reference

```python
from ccnl_engine import (
    # Entry point
    PayrollEngine,
    # Requests and plans
    PeriodInput,
    PeriodFacts,
    PayrollRun,
    Employment,
    EmployerProfile,
    Headcount,
    CompetenceYearPlan,
    TaxYearPlan,
    # Results
    PeriodResult,
    CompetenceYearResult,
    TaxYearResult,
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
)
from ccnl_engine.catalog import (
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityImplementation,
    CcnlId,
    ContractSummary,
    RulesetAssurance,
    RulesetIdentity,
    RulesetKind,
    RulesetReadiness,
    ValidityWindow,
    VerificationStatus,
    get_ccnl,
    search_ccnls,
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
    OvertimeKind,
    PeriodId,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessEpisode,
    TerminationTFREvent,
    WelfareEvent,
    WorkEvent,
)
from ccnl_engine.inputs import (
    # Contract type, hours and seniority
    Apprentice,
    FixedTerm,
    Permanent,
    WorkerCategory,
    EmploymentPeriod,
    WeeklyHours,
    ContributableHours,
    SeniorityFact,
    SenioritySource,
    ContributionHistory,
    EmploymentSector,
    PensionFundEnrolment,
    NoPensionFund,
    EmployerActivity,
    # Family and tax facts
    FamilyComposition,
    Dependent,
    DependentRelationship,
    PriorYearTaxFacts,
    CurrentYearTaxFacts,
    IncomeEstimateQuality,
    ForeignTaxPaid,
    ShortfallDeferralRequest,
    SubstituteTaxRegime,
    # Calendar and engine mode
    WorkCalendar,
    CalendarOverride,
    CalendarOverrideReason,
    EngineMode,
    # Opening state and imported balances
    PeriodState,
    OpeningBalances,
    InpsBaseYtd,
    PaymentId,
    PayrollRunId,
    RecoveryObligation,
    RecoveryPlan,
    SurtaxComponent,
    SurtaxObligation,
    DeferredShortfall,
)
from ccnl_engine.results import (
    ResultAssurance,
    ResultBlocker,
    BlockerCode,
    Payability,
    CoverageStatus,
    EvidenceStatus,
    CalculationStatus,
    CalculationIssue,
    CalculationDecision,
    DecisionOrigin,
    ModelLimitation,
    MonetaryImpact,
    LimitationStatus,
    CapabilityGap,
    CapabilityScope,
    UnresolvedRequirement,
    UncoveredRun,
    AccountKind,
    RemittanceColumn,
    RemittanceLine,
)
```

For the work events see [Work rules](../engine/work-rules.md).

## Guide cross-references

| Guide | Relevant API |
|---|---|
| [Employment types](../domain/employment-types.md) | `Permanent`, `FixedTerm`, `Apprentice` |
| [Pay components](../engine/pay-components.md) | `Employment.seniority`, `Employment.weekly_hours`, `WorkerCategory`, `BilateralFundEvent` |
| [Second level](../engine/second-level.md) | `CompetenceYearPlan`, `CalendarOverride` |
| [Fiscal](../engine/fiscal.md) | `CalculationDecision`, `CalculationIssue`, `REGION_CODES` |
| [Domestic work](../engine/domestic-work.md) | `Employment.weekly_hours`, `PeriodFacts.contributable_hours` |
