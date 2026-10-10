"""Knowledge repository whose CCNLs record no ruleset identity.

Every bundled CCNL carries a ruleset block; this repository strips it so
tests can check that a run and the catalog fail closed without one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)

if TYPE_CHECKING:
    from ccnl_engine.contract.identity.facade import CCNL

__all__ = ["AnonymousCcnlRepository"]


class AnonymousCcnlRepository(BundledKnowledgeRepository):
    """Bundled rules whose CCNL records no ruleset identity."""

    def load_ccnl(self, filename: str) -> CCNL:
        """Return the bundled CCNL without its ruleset block.

        Returns:
            The CCNL.
        """
        return super().load_ccnl(filename).model_copy(update={"ruleset": None})
