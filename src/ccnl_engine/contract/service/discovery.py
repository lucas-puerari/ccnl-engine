"""CCNL discovery: list, search and resolve the bundled CCNL contracts."""

from __future__ import annotations

import importlib.resources
import json
from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING, NewType

from ccnl_engine.contract.domain.identity import CCNLVerification
from ccnl_engine.knowledge.service.bundled_resources import BundledResourceStore
from ccnl_engine.shared.domain.errors import UnknownCcnlError
from ccnl_engine.shared.domain.validation import require_str

if TYPE_CHECKING:
    from ccnl_engine.provenance.domain.ruleset_identity import RulesetReadiness

CcnlId = NewType("CcnlId", str)


@dataclass(frozen=True, slots=True)
class ContractSummary:
    """Summary of one bundled CCNL: who it is and how far it is cleared.

    Attributes:
        ccnl_id: Human-readable slug
            (e.g. ``"metalmeccanico-federmeccanica"``).
        name: Full display name
            (e.g. ``"CCNL Metalmeccanico Federmeccanica"``).
        cnel_code: Official CNEL classification code (e.g. ``"E042"``).
        readiness: Readiness tier of the CCNL ruleset; only ``production``
            is payable in ``operational`` mode.
    """

    ccnl_id: CcnlId
    name: str
    cnel_code: str
    readiness: RulesetReadiness


@cache
def _load_all() -> tuple[ContractSummary, ...]:
    """Load the summary of every bundled CCNL file (result is cached).

    Returns:
        Tuple of :class:`ContractSummary` sorted by ccnl_id.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
    store = BundledResourceStore(pkg)
    items: list[ContractSummary] = []
    for filename in store.list_json():
        raw = json.loads(store.read_json(filename))
        meta = raw.get("meta", {})
        verification = CCNLVerification.model_validate(raw.get("verification", {}))
        items.append(
            ContractSummary(
                ccnl_id=CcnlId(meta["ccnl_id"]),
                name=meta["name"],
                cnel_code=meta["cnel_code"],
                readiness=verification.readiness,
            )
        )
    return tuple(items)


def list_contracts() -> tuple[ContractSummary, ...]:
    """Return every bundled CCNL contract, sorted by ccnl_id.

    Returns:
        Tuple of :class:`ContractSummary` for every bundled CCNL.
    """
    return _load_all()


def get_ccnl(ccnl_id: str) -> ContractSummary:
    """Resolve a CCNL by slug or CNEL code.

    Args:
        ccnl_id: A slug (e.g. ``"metalmeccanico-federmeccanica"``) or CNEL
            code (e.g. ``"E042"``).

    Returns:
        The matching :class:`ContractSummary`.

    Raises:
        UnknownCcnlError: When no CCNL matches *ccnl_id*, with up to five
            similar identifiers attached as suggestions.
    """
    require_str(ccnl_id, "ccnl_id", feature="catalog")
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


def search_ccnls(query: str) -> tuple[ContractSummary, ...]:
    """Return all CCNLs whose name or slug contains *query*.

    The comparison is case-insensitive.

    Args:
        query: Substring to match against :attr:`ContractSummary.ccnl_id` and
            :attr:`ContractSummary.name`.

    Returns:
        A tuple of matching :class:`ContractSummary`, in slug order.
    """
    require_str(query, "query", feature="catalog")
    q = query.lower()
    return tuple(
        info
        for info in _load_all()
        if q in info.ccnl_id.lower() or q in info.name.lower()
    )
