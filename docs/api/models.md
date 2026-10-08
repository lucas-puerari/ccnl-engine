# Models

!!! warning "Internal"
    This page documents internal modules, for contributors and tooling such as
    the demo. They are not part of the public API and may change without
    notice: import the public types from `ccnl_engine` and its four
    namespaces (see [API reference](index.md#public-namespaces)).

Domain models for employment contracts and CCNL structure.

See [Domain: Components](../domain/components.md) for the conceptual background
behind each model.

## Employment

::: ccnl_engine.payroll.domain.employment
    options:
      members:
        - Permanent
        - Apprentice

::: ccnl_engine.payroll.domain.fixed_term
    options:
      members:
        - FixedTerm
        - NaspiExclusion

## CCNL

::: ccnl_engine.contract.domain.identity
    options:
      members:
        - CCNL
        - CCNLMeta
        - TaxSector
        - CoverageNote
        - NoteKind

::: ccnl_engine.contract.domain.compensation
    options:
      members:
        - Level

## Fiscal

::: ccnl_engine.payroll.domain.jurisdiction
    options:
      members:
        - REGION_CODES
        - check_surtax_codes
