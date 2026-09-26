"""Tax rules for Italian payroll computation: domain models and data loaders.

Covers IRPEF, INPS contributions, TFR, statutory variable pay and the
addizionale regionale e comunale (surtax). The engine never stores tax data;
:func:`~ccnl_engine.tax.service.tax_annual_assembler.load_year_rules` and
:func:`~ccnl_engine.tax.service.surtax_loaders.load_surtax_rules` read the
versioned datasets from :mod:`ccnl_engine.knowledge`.
"""
