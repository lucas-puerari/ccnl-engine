"""Tests for loader_utils: verify_ruleset_hash, as_ruleset, try_ruleset."""

from __future__ import annotations

import pytest

from ccnl_engine.knowledge.service.loader_utils import (
    as_ruleset,
    try_ruleset,
    verify_ruleset_hash,
)
from ccnl_engine.provenance.domain.ruleset_identity import source_hash
from ccnl_engine.shared.domain.errors import DataIntegrityError


class TestVerifyRulesetHash:
    """verify_ruleset_hash raises on tampered files and skips absent/invalid blocks."""

    def test_no_ruleset_block_is_skipped(self) -> None:
        """A payload without a ruleset key passes without error."""
        verify_ruleset_hash({"levels": []})

    def test_non_dict_ruleset_is_skipped(self) -> None:
        """A non-dict ruleset value (e.g. a string) is not verified."""
        verify_ruleset_hash({"ruleset": "not-a-dict"})

    def test_missing_source_hash_is_skipped(self) -> None:
        """A ruleset dict without source_hash passes without error."""
        verify_ruleset_hash({"ruleset": {}})

    def test_non_string_source_hash_is_skipped(self) -> None:
        """A non-string source_hash (e.g. int) is ignored."""
        verify_ruleset_hash({"a": 1, "ruleset": {"source_hash": 123}})

    def test_matching_hash_passes(self) -> None:
        """A payload whose source_hash matches the recomputed hash passes."""
        payload: dict[str, object] = {"a": 1}
        payload["ruleset"] = {"source_hash": source_hash({"a": 1, "ruleset": {}})}
        verify_ruleset_hash(payload)

    def test_mismatched_hash_raises(self) -> None:
        """A wrong source_hash raises DataIntegrityError."""
        payload = {"a": 2, "ruleset": {"source_hash": "0" * 64}}
        with pytest.raises(DataIntegrityError, match="source_hash mismatch"):
            verify_ruleset_hash(payload)

    def test_mismatched_hash_includes_filename(self) -> None:
        """The error message includes the filename when provided."""
        payload = {"a": 2, "ruleset": {"source_hash": "0" * 64}}
        with pytest.raises(DataIntegrityError, match=r"in my-file\.json"):
            verify_ruleset_hash(payload, "my-file.json")

    def test_default_filename_used_when_omitted(self) -> None:
        """The default filename '<unknown>' appears in the error message."""
        payload = {"a": 2, "ruleset": {"source_hash": "0" * 64}}
        with pytest.raises(DataIntegrityError, match="<unknown>"):
            verify_ruleset_hash(payload)


class TestAsRuleset:
    """as_ruleset parses the ruleset block or returns None."""

    def test_no_ruleset_key_returns_none(self) -> None:
        """A payload without a ruleset key returns None."""
        assert as_ruleset({"year": 2026}) is None

    def test_non_dict_ruleset_returns_none(self) -> None:
        """A non-dict ruleset value returns None."""
        assert as_ruleset({"ruleset": "not-a-dict"}) is None

    def test_valid_block_parses(self) -> None:
        """A valid ruleset block is parsed into a RulesetIdentity."""
        result = as_ruleset({
            "ruleset": {
                "id": "test/2026",
                "version": "2026.1",
                "effective_from": "2026-01-01",
                "published_at": "2026-01-01",
                "source": "unavailable",
                "source_type": "derived",
                "source_hash": "a" * 64,
                "verification_status": "unverified",
            }
        })
        assert result is not None
        assert result.version == "2026.1"


class TestTryRuleset:
    """try_ruleset parses the ruleset block, returning None on any error."""

    def test_no_ruleset_key_returns_none(self) -> None:
        """A payload without a ruleset key returns None."""
        assert try_ruleset({"year": 2026}) is None

    def test_non_dict_ruleset_returns_none(self) -> None:
        """A non-dict ruleset value returns None."""
        assert try_ruleset({"ruleset": "not-a-dict"}) is None

    def test_invalid_block_returns_none(self) -> None:
        """A dict that fails RulesetIdentity validation returns None."""
        assert try_ruleset({"ruleset": {"bad_field": True}}) is None

    def test_valid_block_parses(self) -> None:
        """A valid ruleset block is parsed into a RulesetIdentity."""
        result = try_ruleset({
            "ruleset": {
                "id": "test/2026",
                "version": "2026.1",
                "effective_from": "2026-01-01",
                "published_at": "2026-01-01",
                "source": "unavailable",
                "source_type": "derived",
                "source_hash": "a" * 64,
                "verification_status": "unverified",
            }
        })
        assert result is not None
        assert result.version == "2026.1"
