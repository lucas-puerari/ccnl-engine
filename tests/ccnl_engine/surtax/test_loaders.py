"""Tests for surtax.loaders — load_surtax_rules()."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.surtax.loaders import load_surtax_rules
from ccnl_engine.surtax.models import ComunaleEntry, RegionaleEntry, SurtaxRules


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

    def test_comunale_agordo_brackets_and_soglia(self) -> None:
        """Agordo (A083) has 4 brackets and a soglia."""
        rules = load_surtax_rules(2026)
        agordo = rules.comunale["A083"]
        assert len(agordo.brackets) == 4
        assert agordo.soglia == Decimal("10000.00")

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


class TestSurtaxModelsValidation:
    """Tests for model validators in surtax.models."""

    def test_regionale_entry_empty_brackets_raises(self) -> None:
        """RegionaleEntry with empty brackets raises ValidationError."""
        with pytest.raises(ValidationError, match="must not be empty"):
            RegionaleEntry(brackets=[])

    def test_comunale_entry_empty_brackets_raises(self) -> None:
        """ComunaleEntry with empty brackets raises ValidationError."""
        with pytest.raises(ValidationError, match="must not be empty"):
            ComunaleEntry(nome="Test", brackets=[])
