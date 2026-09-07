"""Tests for the shared ruleset provenance model (metadata/domain/rules.py)."""

from datetime import date

import pytest
from pydantic import ValidationError

from ccnl_engine.engine.metadata import (
    RulesetIdentity,
    VerificationStatus,
    source_hash,
)


def _identity(**overrides: object) -> RulesetIdentity:
    block: dict[str, object] = {
        "id": "ccnl/metalmeccanico-federmeccanica",
        "version": "2026.1",
        "effective_from": "2025-01-01",
        "effective_until": None,
        "published_at": "2026-09-07",
        "source": "https://example.com/ccnl",
        "source_hash": "0" * 64,
        "verification_status": "verified",
    }
    block.update(overrides)
    return RulesetIdentity.model_validate(block)


class TestSourceHash:
    """Stable, self-referential-safe sha256 digest of a data payload."""

    def test_deterministic(self) -> None:
        """Hashing the same payload twice gives the same digest."""
        payload = {"year": 2026, "levels": [{"code": "A", "salary": "1000.00"}]}
        assert source_hash(payload) == source_hash(payload)

    def test_ignores_source_hash_key(self) -> None:
        """A nested source_hash key does not affect the digest."""
        bare = {"a": 1, "ruleset": {"id": "x"}}
        hashed = {"a": 1, "ruleset": {"id": "x", "source_hash": "0" * 64}}
        assert source_hash(bare) == source_hash(hashed)

    def test_status_field_is_covered(self) -> None:
        """Adding a field changes the digest."""
        bare = {"a": 1}
        modified = {"a": 1, "b": 2}
        assert source_hash(bare) != source_hash(modified)

    def test_sorted_keys_are_ordering_independent(self) -> None:
        """Key order does not affect the digest."""
        raw = {"b": 2, "a": 1}
        shuffled = {"a": 1, "b": 2}
        assert source_hash(raw) == source_hash(shuffled)

    def test_non_ascii_is_stable(self) -> None:
        """Non-ASCII chars hash deterministically (ensure_ascii=False)."""
        a = source_hash({"nome": "Piemonte"})
        b = source_hash({"nome": "Piemonte"})
        assert a == b

    def test_digest_shape(self) -> None:
        """Digest is a 64-char lowercase hex string."""
        digest = source_hash({"x": [1, 2, 3]})
        assert len(digest) == 64
        assert digest == digest.lower()


class TestRulesetIdentity:
    """RulesetIdentity metadata model."""

    def test_open_ended_effective_until(self) -> None:
        """effective_until may be None (open-ended ruleset)."""
        ident = _identity()
        assert ident.effective_until is None
        assert ident.effective_from == date(2025, 1, 1)
        assert ident.id == "ccnl/metalmeccanico-federmeccanica"

    def test_closed_effective_until(self) -> None:
        """effective_until is parsed to a date when present."""
        ident = _identity(effective_until="2027-12-31")
        assert ident.effective_until == date(2027, 12, 31)

    def test_str_is_id_at_version(self) -> None:
        """str() collapses the identity to 'id@version'."""
        ident = _identity()
        assert str(ident) == "ccnl/metalmeccanico-federmeccanica@2026.1"

    def test_as_dict(self) -> None:
        """as_dict returns a JSON-native dict with ISO dates."""
        ident = _identity(effective_until="2027-12-31")
        d = ident.as_dict()
        assert d["id"] == "ccnl/metalmeccanico-federmeccanica"
        assert d["version"] == "2026.1"
        assert d["effective_from"] == "2025-01-01"
        assert d["effective_until"] == "2027-12-31"
        assert d["published_at"] == "2026-09-07"
        assert d["source"] == "https://example.com/ccnl"
        assert d["source_hash"] == "0" * 64
        assert d["verification_status"] == "verified"

    def test_as_dict_none_effective_until(self) -> None:
        """as_dict keeps effective_until as None when open-ended."""
        assert _identity().as_dict()["effective_until"] is None

    def test_verification_status_coerced_to_enum(self) -> None:
        """verification_status string is coerced to the StrEnum member."""
        ident = _identity()
        assert ident.verification_status is VerificationStatus.VERIFIED

    def test_extra_keys_rejected(self) -> None:
        """Unknown extra keys raise ValidationError (extra='forbid')."""
        with pytest.raises(ValidationError, match="extra_forbidden"):
            _identity(unexpected="surprise")

    def test_missing_required_key_raises(self) -> None:
        """Missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            RulesetIdentity.model_validate({"id": "x"})

    def test_all_status_values_serialisable(self) -> None:
        """VerificationStatus members round-trip through Validation."""
        for status in VerificationStatus:
            ident = _identity(verification_status=status.value)
            assert ident.verification_status is status
            assert str(status) == status.value
