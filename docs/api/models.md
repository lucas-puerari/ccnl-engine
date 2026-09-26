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

::: ccnl_engine.engine.contract.domain.identity
    options:
      members:
        - CCNL
        - CCNLMeta
        - TaxSector
        - CoverageNote
        - NoteKind

::: ccnl_engine.engine.contract.domain.compensation
    options:
      members:
        - Level

## Fiscal

::: ccnl_engine.payroll.domain.jurisdiction
    options:
      members:
        - REGION_CODES
        - check_surtax_codes
