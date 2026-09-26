"""Tax rules for Italian payroll computation: domain models and data loader.

The engine never stores tax data;
:func:`~ccnl_engine.engine.tax.service.tax_annual_assembler.load_year_rules`
reads the versioned datasets from :mod:`ccnl_engine.knowledge`.
"""
