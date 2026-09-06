# Models

Domain models for employment contracts and CCNL structure.

See [Domain: Components](../domain/components.md) for the conceptual background
behind each model.

## Employment

::: ccnl_engine.payroll.domain.employment
    options:
      members:
        - Permanent
        - FixedTerm
        - Apprentice

## CCNL

::: ccnl_engine.contract.domain.ccnl
    options:
      members:
        - CCNL
        - CCNLMeta
        - Level
        - TaxSector
        - CoverageNote
        - NoteKind

## Fiscal

::: ccnl_engine.payroll.domain.fiscal
    options:
      members:
        - FiscalSimplification
