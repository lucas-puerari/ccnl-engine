"""Tax rules for Italian payroll computation."""

from ccnl_engine.tax.domain.rules import YearRules as YearRules
from ccnl_engine.tax.service.loaders import load_year_rules as load_year_rules

__all__ = ["YearRules", "load_year_rules"]
