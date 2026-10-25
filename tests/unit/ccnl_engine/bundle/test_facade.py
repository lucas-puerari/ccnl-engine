"""Tests for the knowledge base version metadata."""

from ccnl_engine.bundle.facade import SERIES


class TestKnowledgeVersion:
    """The knowledge base exports the release series of its data."""

    def test_series_exported(self) -> None:
        """SERIES names the year and the release of the bundled data."""
        assert SERIES == "2026.3"
