"""Unit tests for loading the bundled pay-item policy ruleset."""

from __future__ import annotations

import json
from datetime import date
from typing import get_args

import pytest

import ccnl_engine.pay_item.loaders as policy_loaders
from ccnl_engine.bundle.loaders import read_resource
from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.pay_item.loaders import (
    _parse_policy_rules,
    load_policy_resolver,
)
from ccnl_engine.pay_item.models import PayItem
from ccnl_engine.pay_item.policies import PolicyContext, PolicyResolver


def _ctx() -> PolicyContext:
    """Build a minimal PolicyContext for use in loader tests.

    Returns:
        A PolicyContext for 2026-01-15.
    """
    return PolicyContext(year=2026, as_of=date(2026, 1, 15))


def _data() -> list[dict[str, object]]:
    """Return a mutable copy of the bundled policy document.

    Returns:
        The decoded rules.
    """
    data = json.loads(read_resource("pay_item/italy.json"))
    assert isinstance(data, list)
    return data


class TestPolicyResolverLoad:
    """load_policy_resolver() loads and indexes the bundled Italian ruleset."""

    def test_load_returns_resolver(self) -> None:
        """load_policy_resolver() returns a PolicyResolver instance."""
        assert isinstance(load_policy_resolver(), PolicyResolver)

    def test_load_resolves_base_salary_earning(self) -> None:
        """The loaded resolver resolves base_salary_earning."""
        resolver = load_policy_resolver()
        result = resolver.resolve("base_salary_earning", _ctx())
        assert result is not None
        assert result.policy_id == "it/earning/ordinary"

    def test_every_public_kind_and_ledger_alias_resolves(self) -> None:
        """The policy set covers every PayItem plus the renewal ledger alias."""
        union = get_args(PayItem)[0]
        kinds = {
            str(model.model_fields["kind"].default) for model in get_args(union)
        } | {"contract_renewal_earning"}
        resolver = load_policy_resolver()

        assert all(resolver.resolve(kind, _ctx()) is not None for kind in kinds)


class TestRejectedPolicyDocuments:
    """Malformed or incomplete policy documents fail before use."""

    def test_document_must_be_a_list(self) -> None:
        """An object is not a policy rule sequence."""
        with pytest.raises(DataIntegrityError, match="must be a list"):
            _parse_policy_rules({})

    def test_bundled_document_must_be_valid_json(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A corrupt bundled resource is reported as a data-integrity error."""
        monkeypatch.setattr(policy_loaders, "read_resource", lambda _: "{")

        with pytest.raises(DataIntegrityError, match="is not valid JSON"):
            load_policy_resolver()

    def test_entry_must_be_an_object(self) -> None:
        """Each list entry is a policy object."""
        data = list[object](_data())
        data[0] = "invalid"
        with pytest.raises(DataIntegrityError, match="entry 0 is not an object"):
            _parse_policy_rules(data)

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("tax", "invalid"),
            ("contribution", "invalid"),
            ("tfr", "invalid"),
            ("cost", "invalid"),
        ],
    )
    def test_axis_values_are_enums(self, field: str, value: str) -> None:
        """Every treatment axis must use a declared value."""
        data = _data()
        data[0][field] = value
        with pytest.raises(DataIntegrityError, match="invalid pay-item policy"):
            _parse_policy_rules(data)

    @pytest.mark.parametrize("field", ["policy_id", "policy_version", "legal_basis"])
    def test_identity_and_legal_basis_are_required(self, field: str) -> None:
        """No rule may carry an empty identity or legal reference."""
        data = _data()
        data[0][field] = ""
        with pytest.raises(DataIntegrityError, match="empty identity or legal basis"):
            _parse_policy_rules(data)

    def test_kinds_must_be_present(self) -> None:
        """A policy with no kind can never be selected."""
        data = _data()
        data[0]["kinds"] = []
        with pytest.raises(DataIntegrityError, match="no non-empty kind"):
            _parse_policy_rules(data)

    def test_a_rule_cannot_repeat_a_kind(self) -> None:
        """Duplicate kinds in one rule are rejected."""
        data = _data()
        kinds = data[0]["kinds"]
        assert isinstance(kinds, list)
        kinds.append(kinds[0])
        with pytest.raises(DataIntegrityError, match="repeats a kind"):
            _parse_policy_rules(data)

    def test_period_cannot_end_before_it_starts(self) -> None:
        """An inverted period never resolves and is rejected."""
        data = _data()
        data[0]["effective_until"] = "1999-12-31"
        with pytest.raises(DataIntegrityError, match="ends before it starts"):
            _parse_policy_rules(data)

    def test_kind_coverage_is_exact(self) -> None:
        """Unknown and missing kinds are reported together."""
        data = _data()
        data[-1]["kinds"] = ["unknown_kind"]
        with pytest.raises(DataIntegrityError, match="coverage mismatch"):
            _parse_policy_rules(data)

    def test_effective_periods_cannot_overlap(self) -> None:
        """Two simultaneously applicable rules would make order change results."""
        data = _data()
        duplicate = dict(data[0])
        duplicate["policy_id"] = "it/earning/ordinary-duplicate"
        data.append(duplicate)
        with pytest.raises(DataIntegrityError, match="periods overlap"):
            _parse_policy_rules(data)

    def test_consecutive_effective_periods_are_allowed(self) -> None:
        """A kind may change policy on the day after its prior period ends."""
        data = _data()
        data[0]["effective_until"] = "2025-12-31"
        successor = dict(data[0])
        successor["policy_id"] = "it/earning/ordinary-2026"
        successor["effective_from"] = "2026-01-01"
        successor["effective_until"] = None
        data.append(successor)

        assert len(_parse_policy_rules(data)) == len(data)
