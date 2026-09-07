"""Tests for the knowledge base version metadata."""

from ccnl_engine.knowledge import __version__


class TestKnowledgeVersion:
    """The knowledge base must export a stable data-set version."""

    def test_version_exported(self) -> None:
        """__version__ is exposed at ccnl_engine.knowledge level."""
        assert __version__ == "2026.1"
