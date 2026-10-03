"""Catalog use cases: list the bundled contracts and inspect a ruleset.

Both answer before any payroll run: which contracts exist, and how far the
ruleset of one of them is cleared.  The readiness reported here is the one a
run of the same CCNL reports in ``result.rulesets``: both are built by
:func:`~ccnl_engine.contract.domain.ruleset_readiness.ccnl_ruleset_assurance`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.ruleset_readiness import ccnl_ruleset_assurance
from ccnl_engine.contract.service.discovery import get_ccnl
from ccnl_engine.contract.service.discovery import (
    list_contracts as _bundled_contracts,
)
from ccnl_engine.shared.domain.errors import DataIntegrityError

if TYPE_CHECKING:
    from ccnl_engine.contract.service.discovery import ContractSummary
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.provenance.domain.ruleset_assurance import RulesetAssurance

__all__ = ["inspect_ruleset", "list_contracts"]


def list_contracts() -> tuple[ContractSummary, ...]:
    """Return the summary of every bundled contract, sorted by ``ccnl_id``.

    Returns:
        One summary per bundled CCNL, with its readiness tier.
    """
    return _bundled_contracts()


def inspect_ruleset(repo: KnowledgeRepository, ccnl_id: str) -> RulesetAssurance:
    """Return the assurance of the ruleset of one CCNL.

    Args:
        repo: Repository the CCNL is loaded from, integrity checked.
        ccnl_id: Slug (e.g. ``"metalmeccanico-federmeccanica"``) or CNEL
            code of a bundled CCNL.

    Returns:
        Identity, hash, readiness and confidence of the CCNL ruleset.

    Raises:
        DataIntegrityError: When the CCNL records no ruleset identity.
    """
    summary = get_ccnl(ccnl_id)
    ccnl = repo.load_ccnl(f"{summary.ccnl_id}.json")
    assurance = ccnl_ruleset_assurance(ccnl)
    if assurance is None:
        msg = f"CCNL {summary.ccnl_id!r} records no ruleset identity"
        raise DataIntegrityError(
            msg, remediation="add the ruleset block to the CCNL data file"
        )
    return assurance
