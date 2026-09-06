"""Addizionale regionale e comunale IRPEF — surtax data and loader."""

from ccnl_engine.surtax.domain.rules import SurtaxRules as SurtaxRules
from ccnl_engine.surtax.service.loaders import load_surtax_rules as load_surtax_rules

__all__ = ["SurtaxRules", "load_surtax_rules"]
