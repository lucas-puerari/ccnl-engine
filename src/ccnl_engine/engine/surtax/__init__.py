"""Addizionale regionale e comunale IRPEF — surtax rules + data loader.

The engine never stores surtax data; :func:`load_surtax_rules` reads the
versioned datasets from :mod:`ccnl_engine.knowledge`.
"""

from ccnl_engine.engine.surtax.domain.rules import SurtaxRules as SurtaxRules
from ccnl_engine.engine.surtax.service.loaders import (
    load_surtax_rules as load_surtax_rules,
)

__all__ = ["SurtaxRules", "load_surtax_rules"]
