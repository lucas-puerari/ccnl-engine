"""Default knowledge sources for the engine: the package-bundled data.

The API layer builds its defaults through these factories so that it depends
on the application layer only, never on the concrete loaders.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.service.policy_loader import load_policy_resolver

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.domain.policy import PolicyResolver

__all__ = ["bundled_policies", "bundled_repository"]


def bundled_repository() -> KnowledgeRepository:
    """Return the repository backed by the package-bundled JSON files.

    Returns:
        A new :class:`~ccnl_engine.payroll.service.bundled_knowledge_repository\
.BundledKnowledgeRepository`.
    """
    return BundledKnowledgeRepository()


def bundled_policies() -> PolicyResolver:
    """Return the pay-item policy resolver of the bundled Italian ruleset.

    Returns:
        A freshly loaded :class:`~ccnl_engine.payroll.domain.policy\
.PolicyResolver`.
    """
    return load_policy_resolver()
