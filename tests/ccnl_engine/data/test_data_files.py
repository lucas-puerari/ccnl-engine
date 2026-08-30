"""Tests for CCNL data loaders and bundled data files.

Validates that every JSON in ``ccnl_engine/data/`` parses correctly and that
the load_ccnl / load_year_rules helpers work end-to-end.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ccnl_engine.data import load_ccnl, load_year_rules
from ccnl_engine.models.ccnl import CCNL
from ccnl_engine.tax.models import YearRules

# ---------------------------------------------------------------------------
# Parametrised: every JSON in src/ccnl_engine/data/ must validate
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "src" / "ccnl_engine" / "data"
_JSON_FILES = sorted(_DATA_DIR.glob("*.json"))


class TestCCNLDataFilesValidate:
    """Every JSON file in the data bundle must parse as a valid CCNL."""

    @pytest.mark.parametrize("json_file", _JSON_FILES, ids=lambda p: p.name)
    def test_file_validates(self, json_file: Path) -> None:
        """Each data file must deserialise into a valid CCNL without errors."""
        ccnl = CCNL.model_validate_json(json_file.read_text(encoding="utf-8"))
        assert ccnl.ccnl.id


# ---------------------------------------------------------------------------
# load_ccnl helper
# ---------------------------------------------------------------------------


class TestLoadCcnl:
    """Unit tests for the load_ccnl helper."""

    def test_commercio_loads(self) -> None:
        """load_ccnl loads the commercio JSON and returns a CCNL instance."""
        ccnl = load_ccnl("commercio-confcommercio.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.ccnl.id == "commercio-confcommercio"
        assert ccnl.ccnl.cnel_code == "H011"

    def test_commercio_has_eight_levels(self) -> None:
        """Commercio CCNL must contain exactly 8 classification levels."""
        ccnl = load_ccnl("commercio-confcommercio.json")
        assert len(ccnl.levels) == 8

    def test_commercio_level4_november_2025_salary(self) -> None:
        """Level 4 paga base on 2025-11-01 must be EUR 1,257.46."""
        ccnl = load_ccnl("commercio-confcommercio.json")
        level4 = next(lv for lv in ccnl.levels if lv.code == "4")
        assert level4.base_salary.value_at(date(2025, 11, 1)) == Decimal("1257.46")

    def test_commercio_level4_march_2025_salary(self) -> None:
        """Level 4 paga base on 2025-03-01 must be EUR 1,222.46."""
        ccnl = load_ccnl("commercio-confcommercio.json")
        level4 = next(lv for lv in ccnl.levels if lv.code == "4")
        assert level4.base_salary.value_at(date(2025, 3, 1)) == Decimal("1222.46")

    def test_commercio_level4_april_2024_salary(self) -> None:
        """Level 4 paga base on 2024-04-01 must be EUR 1,192.46."""
        ccnl = load_ccnl("commercio-confcommercio.json")
        level4 = next(lv for lv in ccnl.levels if lv.code == "4")
        assert level4.base_salary.value_at(date(2024, 4, 1)) == Decimal("1192.46")


# ---------------------------------------------------------------------------
# load_year_rules helper
# ---------------------------------------------------------------------------


class TestLoadYearRules:
    """Unit tests for the load_year_rules helper."""

    def test_2026_loads(self) -> None:
        """load_year_rules(2026) returns a valid YearRules for 2026."""
        yr = load_year_rules(2026)
        assert isinstance(yr, YearRules)
        assert yr.year == 2026

    def test_missing_year_raises(self) -> None:
        """A year with no data file must raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_year_rules(1900)
