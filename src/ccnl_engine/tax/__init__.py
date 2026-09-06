"""Tax rules for Italian payroll computation."""

from ccnl_engine.tax.loaders import load_year_rules
from ccnl_engine.tax.models import YearRules

__all__ = ["YearRules", "load_year_rules"]
