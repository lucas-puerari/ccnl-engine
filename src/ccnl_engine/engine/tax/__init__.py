"""Tax rules for Italian payroll computation: domain models + data loader.

The engine never stores tax data; :func:`load_year_rules` reads the versioned
datasets from :mod:`ccnl_engine.knowledge`.
"""

from ccnl_engine.engine.tax.domain.rules import YearRules as YearRules
from ccnl_engine.engine.tax.service.loaders import load_year_rules as load_year_rules

__all__ = ["YearRules", "load_year_rules"]
