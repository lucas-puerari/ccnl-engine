"""CCNL contract bounded context: domain models + data loader.

The engine never stores CCNL data; :func:`load_ccnl` reads the versioned
datasets from :mod:`ccnl_engine.knowledge`.
"""

from ccnl_engine.engine.contract.domain.ccnl import CCNL as CCNL
from ccnl_engine.engine.contract.service.loaders import load_ccnl as load_ccnl

__all__ = ["CCNL", "load_ccnl"]
