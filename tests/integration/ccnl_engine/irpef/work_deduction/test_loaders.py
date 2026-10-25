"""load_work_deduction_rules: one file of art. 13 TUIR constants per year."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from unittest.mock import patch

import pytest

from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.errors import DataIntegrityError, UnsupportedTaxYearError
from ccnl_engine.irpef.work_deduction.loaders import load_work_deduction_rules
from ccnl_engine.sector.loaders import load_year_rules

_READER = "ccnl_engine.irpef.work_deduction.loaders.read_year_json"


class TestBundled2026:
    """Art. 13 c. 1 lett. a) TUIR: 1,955 EUR up to 15,000, at least 690."""

    def test_constants_are_those_of_the_law(self) -> None:
        """The flat amount, the band limits and the minima of 2026."""
        rules = load_work_deduction_rules(2026)
        assert (rules.detr_flat, rules.detr_lo, rules.detr_mid, rules.detr_high) == (
            Decimal(1955),
            Decimal(15000),
            Decimal(28000),
            Decimal(50000),
        )
        assert (rules.minimum.open_ended, rules.minimum.fixed_term) == (
            Decimal(690),
            Decimal(1380),
        )

    @pytest.mark.parametrize("sector", list(TaxSector))
    def test_every_sector_reads_the_same_constants(self, sector: TaxSector) -> None:
        """The deduction does not depend on the sector."""
        rules = load_year_rules(2026, sector, 50).work_deduction
        assert rules == load_work_deduction_rules(2026)


class TestChecks:
    """A missing, mislabelled or incomplete file never yields constants."""

    def test_unbundled_year_raises(self) -> None:
        """No file for 2028: the year is not supported."""
        with pytest.raises(UnsupportedTaxYearError):
            load_work_deduction_rules(2028)

    def test_year_mismatch_raises(self) -> None:
        """A file of another year under the 2026 name is rejected."""
        raw = {"year": 2025, "work_deduction": {}}
        with (
            patch(_READER, return_value=raw),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_work_deduction_rules(2026)

    @pytest.mark.parametrize(
        "raw",
        [
            pytest.param({"year": 2026}, id="no_block"),
            pytest.param(
                {"year": 2026, "work_deduction": {"detr_flat": "1955"}},
                id="missing_constants",
            ),
        ],
    )
    def test_incomplete_table_raises(self, raw: dict[str, Any]) -> None:
        """A constant the file does not state fails the load, no default."""
        with (
            patch(_READER, return_value=raw),
            pytest.raises(DataIntegrityError, match="not a valid work deduction"),
        ):
            load_work_deduction_rules(2026)
