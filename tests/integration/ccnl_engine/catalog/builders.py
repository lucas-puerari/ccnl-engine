"""Knowledge repositories that differ from the bundle for catalog tests.

:class:`AnonymousCcnlRepository` strips the ruleset block of every CCNL, so
tests can check that a run and the catalog fail closed without one.
:class:`SyntheticCcnlRepository` holds one CCNL the bundle does not, so
tests can check that the engine reads the injected repository only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.catalog.loaders import contract_summary, load_ccnl
from ccnl_engine.period.repositories import (
    BundledKnowledgeRepository,
)

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.catalog.loaders import ContractSummary

__all__ = [
    "SYNTHETIC_BUNDLE_VERSION",
    "SYNTHETIC_CNEL_CODE",
    "SYNTHETIC_ID",
    "AnonymousCcnlRepository",
    "SyntheticCcnlRepository",
]

#: Slug of the CCNL only :class:`SyntheticCcnlRepository` holds.
SYNTHETIC_ID = "synthetic-metalmeccanico"
#: CNEL code of that CCNL, held by no bundled CCNL.
SYNTHETIC_CNEL_CODE = "Z999"
#: Bundle version of :class:`SyntheticCcnlRepository`.
SYNTHETIC_BUNDLE_VERSION = "synthetic-1"


class AnonymousCcnlRepository(BundledKnowledgeRepository):
    """Bundled rules whose CCNL records no ruleset identity."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        """Return the bundled CCNL without its ruleset block.

        Returns:
            The CCNL.
        """
        return super().load_ccnl(ccnl_id).model_copy(update={"ruleset": None})


def _synthetic_ccnl() -> CCNL:
    """Return the bundled Federmeccanica CCNL under the synthetic identity.

    Returns:
        The CCNL, its slug, CNEL code and ruleset id replaced.
    """
    ccnl = load_ccnl("metalmeccanico-federmeccanica")
    meta = ccnl.meta.model_copy(
        update={"ccnl_id": SYNTHETIC_ID, "cnel_code": SYNTHETIC_CNEL_CODE}
    )
    assert ccnl.ruleset is not None
    ruleset = ccnl.ruleset.model_copy(update={"id": f"ccnl/{SYNTHETIC_ID}"})
    return ccnl.model_copy(update={"meta": meta, "ruleset": ruleset})


class SyntheticCcnlRepository(BundledKnowledgeRepository):
    """Bundled rules plus one CCNL the bundle does not hold."""

    def __init__(self) -> None:
        """Build the synthetic CCNL once."""
        self._synthetic = _synthetic_ccnl()

    @property
    def bundle_version(self) -> str:
        """Version of this repository, not of the package bundle."""
        return SYNTHETIC_BUNDLE_VERSION

    def load_contracts(self) -> tuple[ContractSummary, ...]:
        """Return the bundled contracts and the synthetic one.

        Returns:
            Every summary, sorted by ``ccnl_id``.
        """
        contracts = (*super().load_contracts(), contract_summary(self._synthetic))
        return tuple(sorted(contracts, key=lambda summary: summary.ccnl_id))

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        """Return the synthetic CCNL for its slug, a bundled one otherwise.

        Returns:
            The CCNL.
        """
        if ccnl_id == SYNTHETIC_ID:
            return self._synthetic
        return super().load_ccnl(ccnl_id)
