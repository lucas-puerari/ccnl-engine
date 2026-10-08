"""load_somma_esente_rules: the bundled 2026 file and its checks."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from unittest.mock import patch

import pytest

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.provenance.domain.chain import ProvenanceStatus
from ccnl_engine.provenance.domain.ruleset_identity import SourceType
from ccnl_engine.shared.domain.errors import DataIntegrityError, UnsupportedTaxYearError
from ccnl_engine.tax.service.tax_annual_assembler import load_year_rules
from ccnl_engine.tax.service.tax_optional_loaders import load_somma_esente_rules

_READER = "ccnl_engine.tax.service.tax_optional_loaders.read_year_json"


class TestBundled2026:
    """The bands of L. 207/2024 art. 1 c. 4, read from their own ruleset."""

    def test_bands_are_those_of_the_law(self) -> None:
        """L. 207/2024 art. 1 c. 4, Gazzetta Ufficiale of 31 December 2024.

        Lett. a) 7,1 per cento up to 8.500 euro of employment income; lett.
        b) 5,3 per cento above 8.500 and up to 15.000; lett. c) 4,8 per
        cento above 15.000.  Only a reddito complessivo up to 20.000 euro
        gives right to the somma: the last band ends there.
        """
        rules = load_somma_esente_rules(2026)
        assert [(b.up_to, b.rate) for b in rules.bands] == [
            (Decimal(8500), Decimal("0.071")),
            (Decimal(15000), Decimal("0.053")),
            (Decimal(20000), Decimal("0.048")),
        ]

    def test_record_is_derived_from_an_official_primary_ruleset(self) -> None:
        """The record quotes the law and no estimated ruleset holds it."""
        rules = load_somma_esente_rules(2026)
        assert rules.ruleset is not None
        assert rules.ruleset.id == "tax/2026/somma-esente"
        assert rules.ruleset.source_type is SourceType.OFFICIAL_PRIMARY
        record = rules.provenance
        assert record is not None
        assert record.status is ProvenanceStatus.DERIVED
        assert record.location is not None
        assert record.location.section == "art. 1 cc. 4-5"
        assert "a) 7,1 per cento" in (record.location.quote or "")

    @pytest.mark.parametrize("sector", list(TaxSector))
    def test_every_sector_reads_the_same_rules(self, sector: TaxSector) -> None:
        """The somma esente does not depend on the sector."""
        rules = load_year_rules(2026, sector, 50).somma_esente
        assert rules == load_somma_esente_rules(2026)


class TestChecks:
    """A missing, mislabelled or malformed file never yields rules."""

    def test_unbundled_year_raises(self) -> None:
        """No file for 2027: the year is not supported."""
        with pytest.raises(UnsupportedTaxYearError):
            load_somma_esente_rules(2027)

    def test_year_mismatch_raises(self) -> None:
        """A file of another year under the 2026 name is rejected."""
        bands = [{"up_to": "8500", "rate": "0.071"}]
        raw = {"year": 2025, "somma_esente": {"bands": bands}}
        with (
            patch(_READER, return_value=raw),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_somma_esente_rules(2026)

    @pytest.mark.parametrize(
        "raw",
        [
            pytest.param({"year": 2026}, id="no_block"),
            pytest.param({"year": 2026, "somma_esente": {"bands": []}}, id="no_band"),
        ],
    )
    def test_invalid_table_raises(self, raw: dict[str, Any]) -> None:
        """A file without a valid somma esente block is an integrity error."""
        with (
            patch(_READER, return_value=raw),
            pytest.raises(DataIntegrityError, match="not a valid somma esente"),
        ):
            load_somma_esente_rules(2026)
