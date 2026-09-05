"""Addizionale regionale e comunale IRPEF — surtax data and loader."""

from ccnl_engine.surtax.loaders import load_surtax_rules
from ccnl_engine.surtax.models import SurtaxRules

__all__ = ["SurtaxRules", "load_surtax_rules"]
