"""Tests for BundledKnowledgeRepository."""

from __future__ import annotations

import pytest

from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.engine.knowledge_repository import KnowledgeRepository


@pytest.fixture
def repo() -> BundledKnowledgeRepository:
    """Return a fresh BundledKnowledgeRepository instance.

    Returns:
        A new :class:`BundledKnowledgeRepository` for this test.
    """
    return BundledKnowledgeRepository()


class TestKnowledgeRepositoryProtocol:
    """KnowledgeRepository Protocol is importable and BundledRepo satisfies it."""

    def test_bundled_repo_is_importable(self) -> None:
        """KnowledgeRepository can be imported and BundledKnowledgeRepository used."""
        assert KnowledgeRepository is not None
        repo: KnowledgeRepository = BundledKnowledgeRepository()
        assert repo is not None


class TestBundledKnowledgeRepository:
    """BundledKnowledgeRepository delegates each call to the matching loader."""

    def test_load_ccnl_delegates(
        self, repo: BundledKnowledgeRepository, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_ccnl returns whatever the underlying load_ccnl function returns."""
        sentinel = object()
        monkeypatch.setattr(
            "ccnl_engine.engine.io.service.bundled_knowledge_repository.load_ccnl",
            lambda _: sentinel,
        )
        assert repo.load_ccnl("some.json") is sentinel

    def test_load_year_rules_delegates(
        self, repo: BundledKnowledgeRepository, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_year_rules returns whatever the underlying load_year_rules returns."""
        sentinel = object()
        monkeypatch.setattr(
            "ccnl_engine.engine.io.service.bundled_knowledge_repository.load_year_rules",
            lambda *_: sentinel,
        )
        assert repo.load_year_rules(2026, TaxSector.TERZIARIO, 10) is sentinel

    def test_load_surtax_rules_delegates(
        self, repo: BundledKnowledgeRepository, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_surtax_rules returns whatever load_surtax_rules returns."""
        sentinel = object()
        monkeypatch.setattr(
            "ccnl_engine.engine.io.service.bundled_knowledge_repository"
            ".load_surtax_rules",
            lambda _: sentinel,
        )
        assert repo.load_surtax_rules(2026) is sentinel

    def test_load_capability_catalog_delegates(
        self, repo: BundledKnowledgeRepository, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_capability_catalog delegates to load_capability_catalog function."""
        sentinel = object()
        monkeypatch.setattr(
            "ccnl_engine.engine.io.service.bundled_knowledge_repository"
            ".load_capability_catalog",
            lambda _: sentinel,
        )
        assert repo.load_capability_catalog(2026) is sentinel
