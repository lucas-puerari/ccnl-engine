# API reference

Full reference for every public type and function exported by `ccnl_engine`.

## Modules

The package is split in two namespaces: `ccnl_engine.engine` (computation,
schemas and loaders) and `ccnl_engine.knowledge` (the versioned JSON data
bundle the loaders read). See [Knowledge base](knowledge.md).

| Page | Contents |
|---|---|
| [Engine](engine.md) | `compute()`, `Calculation`, `InputSnapshot`, `Employee`, `ContractPosition`, `WorkArrangement`, `TaxProfile`, `Employer`, `PayrollResult` |
| [Loaders](loaders.md) | `load_ccnl()`, `load_year_rules()`, `load_surtax_rules()`, `YearRules`, `InpsRates` |
| [Models](models.md) | `CCNL`, `Level`, `Allowance`, employment types, fiscal enums |
| [Knowledge](knowledge.md) | data layout, `__version__` |

## Quick reference

```python
from ccnl_engine import (
    # Core function
    compute,
    # Loaders
    load_ccnl, load_year_rules, load_surtax_rules,
    # Employee input
    Employee, ContractPosition, WorkArrangement, TaxProfile,
    # Employer input
    Employer,
    # Employment types
    Permanent, FixedTerm, Apprentice,
    # Seniority (union type)
    SeniorityByCount, SeniorityByMonths,
    # Salary overrides
    SalaryOverrides, RalOverride, RalOverrideMode, DestinationRalOverride,
    # Output
    PayrollResult, FiscalSimplification,
    # Calculation
    Calculation, InputSnapshot,
    # Provenance
    RulesetIdentity, VerificationStatus, engine_version,
    # Contract domain
    CCNL, CCNLMeta, CCNLParameters, Level, TaxSector, TimeSeries,
    # Tax domain
    YearRules, SurtaxRules,
)
```

All types above are re-exported from the top-level `ccnl_engine` package.

## Guide cross-references

| Guide | Relevant API |
|---|---|
| [Employment types](../guide/employment-types.md) | `ContractPosition`, `Permanent`, `FixedTerm`, `Apprentice` |
| [Pay components](../guide/pay-components.md) | `WorkArrangement`, `SeniorityByCount`, `SeniorityByMonths`, `SalaryOverrides` |
| [Second level](../guide/second-level.md) | `Employer`, `SupplementaryAllowance` |
| [Fiscal](../guide/fiscal.md) | `TaxProfile`, `FiscalSimplification`, `load_surtax_rules` |
| [Domestic work](../guide/domestic-work.md) | `WorkArrangement.weekly_hours` |
