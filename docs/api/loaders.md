# Loaders

Functions to load CCNL contract data and tax year rules from the bundled JSON files.

## Contracts

::: ccnl_engine.contract.service.loaders
    options:
      members:
        - load_ccnl

## Tax

::: ccnl_engine.tax.service.loaders
    options:
      members:
        - load_year_rules

::: ccnl_engine.tax.domain.rules
    options:
      members:
        - YearRules
        - InpsRates
        - IrpefBracket
        - DeductionBreakpoint
