"""CCNL contract bounded context."""

from ccnl_engine.contract.domain.ccnl import CCNL as CCNL
from ccnl_engine.contract.service.loaders import load_ccnl as load_ccnl

__all__ = ["CCNL", "load_ccnl"]
