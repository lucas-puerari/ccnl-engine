# Loaders

Functions to load CCNL contract data and tax year rules from the bundled JSON files.

See [Get started](../getting-started/index.md) for the typical loading sequence and
[Contracts](../contracts/index.md) for the list of available `filename` values.

## Contracts

::: ccnl_engine.engine.contract.service.loaders
    options:
      members:
        - load_ccnl

## Tax

::: ccnl_engine.engine.tax.service.tax_annual_assembler
    options:
      members:
        - load_year_rules

::: ccnl_engine.engine.tax.domain.ruleset
    options:
      members:
        - YearRules

::: ccnl_engine.engine.tax.domain.contribution_rules
    options:
      members:
        - InpsRates

::: ccnl_engine.engine.tax.domain.irpef_rules
    options:
      members:
        - IrpefBracket
        - DeductionBreakpoint
