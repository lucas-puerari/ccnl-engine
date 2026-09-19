"""CCNL discovery — list, search and resolve CCNL contracts."""

from __future__ import annotations

import importlib.resources
import json
from dataclasses import dataclass
from functools import cache
from typing import NewType

from ccnl_engine.engine.errors import UnknownCcnlError
from ccnl_engine.engine.io.service.bundled_resources import BundledResourceStore

CcnlId = NewType("CcnlId", str)


@dataclass(frozen=True)
class CcnlInfo:
    """Lightweight descriptor for one CCNL contract.

    Attributes:
        ccnl_id: Human-readable slug
            (e.g. ``"metalmeccanico-federmeccanica"``).
        name: Full display name
            (e.g. ``"CCNL Metalmeccanico Federmeccanica"``).
        cnel_code: Official CNEL classification code (e.g. ``"E042"``).
    """

    ccnl_id: CcnlId
    name: str
    cnel_code: str


@cache
def _load_all() -> tuple[CcnlInfo, ...]:
    """Load metadata for every bundled CCNL file (result is cached).

    Returns:
        Tuple of :class:`CcnlInfo` sorted by ccnl_id.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
    store = BundledResourceStore(pkg)
    items: list[CcnlInfo] = []
    for filename in store.list_json():
        meta = json.loads(store.read_json(filename)).get("meta", {})
        items.append(
            CcnlInfo(
                ccnl_id=CcnlId(meta["ccnl_id"]),
                name=meta["name"],
                cnel_code=meta["cnel_code"],
            )
        )
    return tuple(items)


def list_ccnls() -> tuple[CcnlInfo, ...]:
    """Return all available CCNL contracts, sorted by ccnl_id.

    Returns:
        Tuple of :class:`CcnlInfo` for every bundled CCNL.
    """
    return _load_all()


def get_ccnl(ccnl_id: str) -> CcnlInfo:
    """Resolve a CCNL by slug or CNEL code.

    Args:
        ccnl_id: A slug (e.g. ``"metalmeccanico-federmeccanica"``) or CNEL
            code (e.g. ``"E042"``).

    Returns:
        The matching :class:`CcnlInfo`.

    Raises:
        UnknownCcnlError: When no CCNL matches *ccnl_id*, with up to five
            similar identifiers attached as suggestions.
    """
    for info in _load_all():
        if ccnl_id in {info.ccnl_id, info.cnel_code}:
            return info
    query = ccnl_id.lower()
    suggestions = tuple(
        info.ccnl_id
        for info in _load_all()
        if query in info.ccnl_id.lower() or query in info.name.lower()
    )[:5]
    raise UnknownCcnlError(ccnl_id, suggestions)


def search_ccnls(query: str) -> tuple[CcnlInfo, ...]:
    """Return all CCNLs whose name or slug contains *query*.

    The comparison is case-insensitive.

    Args:
        query: Substring to match against :attr:`CcnlInfo.ccnl_id` and
            :attr:`CcnlInfo.name`.

    Returns:
        A tuple of matching :class:`CcnlInfo`, in slug order.
    """
    q = query.lower()
    return tuple(
        info
        for info in _load_all()
        if q in info.ccnl_id.lower() or q in info.name.lower()
    )
