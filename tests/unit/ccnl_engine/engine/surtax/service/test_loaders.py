"""Tests for surtax.loaders -- load_surtax_rules()."""

import json
from decimal import Decimal
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from ccnl_engine.engine.primitives import Bracket
from ccnl_engine.engine.surtax.domain.rules import (
    ComunaleEntry,
    RegionaleEntry,
    SurtaxRules,
)
from ccnl_engine.engine.surtax.service.loaders import (
    _load_surtax_rules_cached,
    load_surtax_rules,
)


class TestLoadSurtaxRules:
    """Smoke tests for load_surtax_rules()."""

    def test_load_2026_returns_surtax_rules(self) -> None:
        """load_surtax_rules(2026) returns a SurtaxRules instance."""
        rules = load_surtax_rules(2026)
        assert isinstance(rules, SurtaxRules)
        assert rules.year == 2026

    def test_regionale_contains_all_regions(self) -> None:
        """All 21 regions/autonomous provinces are present."""
        rules = load_surtax_rules(2026)
        expected_regions = {
            "Piemonte",
            "Valle d'Aosta",
            "Lombardia",
            "Provincia Autonoma di Bolzano",
            "Provincia Autonoma di Trento",
            "Veneto",
            "Friuli-Venezia Giulia",
            "Liguria",
            "Emilia-Romagna",
            "Toscana",
            "Umbria",
            "Marche",
            "Lazio",
            "Abruzzo",
            "Molise",
            "Campania",
            "Puglia",
            "Basilicata",
            "Calabria",
            "Sicilia",
            "Sardegna",
        }
        assert expected_regions.issubset(rules.regionale.keys())

    def test_regionale_lombardia_brackets(self) -> None:
        """Lombardia has at least one bracket with a positive rate."""
        rules = load_surtax_rules(2026)
        lom = rules.regionale["Lombardia"]
        assert len(lom.brackets) >= 1
        assert any(b.rate > Decimal(0) for b in lom.brackets)

    def test_regionale_last_bracket_unbounded(self) -> None:
        """Last bracket of every region has up_to=None."""
        rules = load_surtax_rules(2026)
        for name, entry in rules.regionale.items():
            assert entry.brackets[-1].up_to is None, (
                f"{name}: last bracket is not unbounded"
            )

    def test_comunale_contains_known_codes(self) -> None:
        """Common municipalities are present (Agordo A083, Abbateggio A008)."""
        rules = load_surtax_rules(2026)
        assert "A083" in rules.comunale  # Agordo
        assert "A008" in rules.comunale  # Abbateggio

    def test_comunale_agordo_brackets_and_exemption_threshold(self) -> None:
        """Agordo (A083) has 4 brackets and an exemption threshold."""
        rules = load_surtax_rules(2026)
        agordo = rules.comunale["A083"]
        assert len(agordo.brackets) == 4
        assert agordo.exemption_threshold == Decimal("10000.00")

    def test_comunale_last_bracket_unbounded(self) -> None:
        """Last bracket of every municipality has up_to=None."""
        rules = load_surtax_rules(2026)
        for code, entry in rules.comunale.items():
            assert entry.brackets[-1].up_to is None, (
                f"{code}: last bracket is not unbounded"
            )

    def test_unknown_year_raises_file_not_found(self) -> None:
        """Requesting a non-bundled year raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_surtax_rules(1900)


class TestSurtaxLoaderIdentity:
    """_load_surtax_rules_cached rejects mismatched year in data files."""

    def test_regionale_year_mismatch_raises(self) -> None:
        """Regionale file with wrong year raises ValueError."""
        tampered_reg = json.dumps({"year": 9999}).encode()
        valid_com = json.dumps({"year": 2026}).encode()
        _load_surtax_rules_cached.cache_clear()
        with (
            patch(
                "ccnl_engine.engine.surtax.service.loaders.read_bundled",
                side_effect=[tampered_reg, valid_com],
            ),
            pytest.raises(ValueError, match="does not match requested year"),
        ):
            load_surtax_rules(2026)
        _load_surtax_rules_cached.cache_clear()

    def test_comunale_year_mismatch_raises(self) -> None:
        """Comunale file with wrong year raises ValueError."""
        valid_reg = json.dumps({"year": 2026}).encode()
        tampered_com = json.dumps({"year": 9999}).encode()
        _load_surtax_rules_cached.cache_clear()
        with (
            patch(
                "ccnl_engine.engine.surtax.service.loaders.read_bundled",
                side_effect=[valid_reg, tampered_com],
            ),
            pytest.raises(ValueError, match="does not match requested year"),
        ):
            load_surtax_rules(2026)
        _load_surtax_rules_cached.cache_clear()


class TestSurtaxModelsValidation:
    """Tests for model validators in surtax.models."""

    def test_regionale_entry_empty_brackets_raises(self) -> None:
        """RegionaleEntry with empty brackets raises ValidationError."""
        with pytest.raises(ValidationError, match="must not be empty"):
            RegionaleEntry(brackets=())

    def test_comunale_entry_empty_brackets_raises(self) -> None:
        """ComunaleEntry with empty brackets raises ValidationError."""
        with pytest.raises(ValidationError, match="must not be empty"):
            ComunaleEntry(nome="Test", brackets=())


class TestLoaderCaching:
    """Cache isolates callers: each call returns a fresh container object."""

    def test_load_surtax_rules_container_isolated(self) -> None:
        """Two calls return different SurtaxRules containers (dict isolation)."""
        first = load_surtax_rules(2026)
        second = load_surtax_rules(2026)
        assert first is not second
        assert first.regionale is not second.regionale
        assert first.comunale is not second.comunale

    def test_load_surtax_rules_entries_shared(self) -> None:
        """Inner RegionaleEntry/ComunaleEntry objects are shared (frozen, no copy)."""
        first = load_surtax_rules(2026)
        second = load_surtax_rules(2026)
        assert first.regionale["Lombardia"] is second.regionale["Lombardia"]

    def test_mutation_of_regionale_dict_isolated(self) -> None:
        """Adding a key to one call's regionale dict does not affect the next."""
        first = load_surtax_rules(2026)
        original_count = len(first.regionale)
        first.regionale["__test__"] = first.regionale["Lombardia"]
        second = load_surtax_rules(2026)
        assert "__test__" not in second.regionale
        assert len(second.regionale) == original_count

    def test_mutation_of_comunale_dict_isolated(self) -> None:
        """Clearing the comunale dict from one call does not affect the next."""
        first = load_surtax_rules(2026)
        original_count = len(first.comunale)
        first.comunale.clear()
        second = load_surtax_rules(2026)
        assert len(second.comunale) == original_count


class TestSurtaxEntryImmutability:
    """RegionaleEntry and ComunaleEntry are frozen with immutable brackets."""

    def test_regionale_entry_brackets_is_tuple(self) -> None:
        """Loaded RegionaleEntry.brackets is a tuple, not a list."""
        rules = load_surtax_rules(2026)
        entry = rules.regionale["Lombardia"]
        assert isinstance(entry.brackets, tuple)

    def test_comunale_entry_brackets_is_tuple(self) -> None:
        """Loaded ComunaleEntry.brackets is a tuple, not a list."""
        rules = load_surtax_rules(2026)
        entry = rules.comunale["H501"]
        assert isinstance(entry.brackets, tuple)

    def test_regionale_entry_field_assignment_raises(self) -> None:
        """Assigning to a RegionaleEntry field raises ValidationError (frozen)."""
        entry = RegionaleEntry(brackets=(Bracket(up_to=None, rate=Decimal("0.011")),))
        with pytest.raises(ValidationError):
            entry.brackets = (Bracket(up_to=None, rate=Decimal("0.012")),)  # type: ignore[misc]

    def test_comunale_entry_field_assignment_raises(self) -> None:
        """Assigning to a ComunaleEntry field raises ValidationError (frozen)."""
        entry = ComunaleEntry(
            nome="Test",
            brackets=(Bracket(up_to=None, rate=Decimal("0.008")),),
        )
        with pytest.raises(ValidationError):
            entry.nome = "Modified"  # type: ignore[misc]
