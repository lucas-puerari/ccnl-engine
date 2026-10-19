"""Catalog use cases: list the contracts of a repository and inspect a ruleset.

Each answers before any payroll run: which contracts exist, and how far the
ruleset of one of them is cleared.  The readiness reported here is the one a
run of the same CCNL reports in ``result.rulesets``: both are built by
:func:`~ccnl_engine.catalog.models.ccnl_ruleset_assurance`.  Every use case
reads the injected repository, never the bundle directly.
"""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from ccnl_engine.catalog.loaders import SLUG, LevelSummary, resolve_contract
from ccnl_engine.catalog.models import ccnl_ruleset_assurance
from ccnl_engine.errors import DataIntegrityError, UnknownCcnlError
from ccnl_engine.validators import require_str

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.catalog.loaders import ContractSummary
    from ccnl_engine.period.ports import KnowledgeRepository
    from ccnl_engine.provenance.ruleset.assurance.models import RulesetAssurance

__all__ = ["inspect_ruleset", "list_contracts", "list_levels", "resolve_ccnl"]


def list_contracts(repo: KnowledgeRepository) -> tuple[ContractSummary, ...]:
    """Return the summary of every contract of *repo*, sorted by ``ccnl_id``.

    Args:
        repo: Repository the contracts are listed from.

    Returns:
        One summary per CCNL of the repository, with its readiness tier.
    """
    return repo.load_contracts()


def resolve_ccnl(repo: KnowledgeRepository, ccnl_id: str) -> CCNL:
    """Load the CCNL named by *ccnl_id* from *repo*.

    A slug is loaded directly, without listing the repository; a CNEL code
    is resolved to its slug through the contracts of *repo*.

    Args:
        repo: Repository the CCNL is loaded from.
        ccnl_id: Slug (e.g. ``"metalmeccanico-federmeccanica"``) or CNEL
            code (e.g. ``"E042"``) of a CCNL of *repo*.

    Returns:
        The CCNL.

    An id that names no CCNL of *repo*, or a CNEL code shared by several of
    them, raises :class:`~ccnl_engine.errors.UnknownCcnlError` with similar
    identifiers as suggestions.
    """
    require_str(ccnl_id, "ccnl_id", feature="catalog")
    if SLUG.fullmatch(ccnl_id):
        with suppress(UnknownCcnlError):
            return repo.load_ccnl(ccnl_id)
    summary = resolve_contract(repo.load_contracts(), ccnl_id)
    return repo.load_ccnl(summary.ccnl_id)


def inspect_ruleset(repo: KnowledgeRepository, ccnl_id: str) -> RulesetAssurance:
    """Return the assurance of the ruleset of one CCNL.

    Args:
        repo: Repository the CCNL is loaded from, integrity checked.
        ccnl_id: Slug (e.g. ``"metalmeccanico-federmeccanica"``) or CNEL
            code of a CCNL of *repo*.

    Returns:
        Identity, hash, readiness and confidence of the CCNL ruleset.

    Raises:
        DataIntegrityError: When the CCNL records no ruleset identity.
    """
    ccnl = resolve_ccnl(repo, ccnl_id)
    assurance = ccnl_ruleset_assurance(ccnl)
    if assurance is None:
        msg = f"CCNL {ccnl.meta.ccnl_id!r} records no ruleset identity"
        raise DataIntegrityError(
            msg, remediation="add the ruleset block to the CCNL data file"
        )
    return assurance


def list_levels(repo: KnowledgeRepository, ccnl_id: str) -> tuple[LevelSummary, ...]:
    """Return the levels of one CCNL, in the order of its data.

    Args:
        repo: Repository the CCNL is loaded from, integrity checked.
        ccnl_id: Slug or CNEL code of a CCNL of *repo*.

    Returns:
        One summary per level, its code as ``Employment.level_code`` takes
        it.
    """
    ccnl = resolve_ccnl(repo, ccnl_id)
    levels = sorted(ccnl.levels, key=lambda level: level.order)
    return tuple(
        LevelSummary(level.code, level.description, level.category) for level in levels
    )
