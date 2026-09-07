# Models

Domain models for employment contracts and CCNL structure.

See [Domain: Components](../domain/components.md) for the conceptual background
behind each model.

## Employment

::: ccnl_engine.engine.payroll.domain.employment
    options:
      members:
        - Permanent
        - FixedTerm
        - Apprentice

## CCNL

::: ccnl_engine.engine.contract.domain.ccnl
    options:
      members:
        - CCNL
        - CCNLMeta
        - Level
        - TaxSector
        - CoverageNote
        - NoteKind

## Fiscal

::: ccnl_engine.engine.payroll.domain.fiscal
    options:
      members:
        - FiscalSimplification