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

::: ccnl_engine.employment.inputs
    options:
      members:
        - Permanent
        - Apprentice

::: ccnl_engine.employment.fixed_term.inputs
    options:
      members:
        - FixedTerm
        - NaspiExclusion

## CCNL

::: ccnl_engine.agreement.facade
    options:
      members:
        - CCNL
        - CCNLMeta
        - TaxSector
        - CoverageNote
        - NoteKind

::: ccnl_engine.compensation.models
    options:
      members:
        - Level

## Fiscal

::: ccnl_engine.surtax.jurisdiction.types
    options:
      members:
        - REGION_CODES
        - check_surtax_codes
