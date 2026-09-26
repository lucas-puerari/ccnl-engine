"""Tests for CCNL data loaders and bundled data files."""

import importlib.resources
from datetime import date
from decimal import Decimal
from pathlib import Path

import pydantic
import pytest

from ccnl_engine.engine.contract.domain.ccnl import CCNL, TaxSector
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.errors import UnsupportedTaxYearError
from ccnl_engine.engine.tax.domain.rules import YearRules
from ccnl_engine.engine.tax.service.loaders import load_year_rules

# ---------------------------------------------------------------------------
# Parametrised: every JSON in ccnl_engine.knowledge.ccnl.data must validate
# ---------------------------------------------------------------------------

# Use importlib.resources so the path is correct for both editable installs
# (plain .json) and installed wheels (.json.gz), and does not depend on the
# number of parent directories from this test file.
_DATA_PKG = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
_JSON_FILES = sorted(
    (entry for entry in _DATA_PKG.iterdir() if entry.name.endswith(".json")),
    key=lambda e: e.name,
)


class TestCCNLDataFilesValidate:
    """Every JSON file in the data bundle must parse as a valid CCNL."""

    def test_data_dir_is_non_empty(self) -> None:
        """The data package must contain at least one JSON file.

        A path typo or packaging mistake (e.g. wrong directory name in the
        build hook) would silently produce an empty list and make the
        parametrised test below run zero times without failing.  This sentinel
        catches that class of bug early.
        """
        assert len(_JSON_FILES) > 0, (
            "No .json files found in ccnl_engine.knowledge.ccnl.data — "
            "check the build hook data paths and the package structure."
        )

    @pytest.mark.parametrize("json_file", _JSON_FILES, ids=lambda p: p.name)
    def test_file_validates(self, json_file: Path) -> None:
        """Each data file must deserialise into a valid CCNL without errors."""
        ccnl = CCNL.model_validate_json(
            importlib.resources
            .files("ccnl_engine.knowledge.ccnl.data")
            .joinpath(json_file.name)
            .read_text(encoding="utf-8")
        )
        assert ccnl.meta.ccnl_id


# ---------------------------------------------------------------------------
# load_ccnl helper
# ---------------------------------------------------------------------------


class TestLoadCcnl:
    """Unit tests for the load_ccnl helper."""

    def test_commercio_loads(self) -> None:
        """load_ccnl loads the commercio JSON and returns a CCNL instance."""
        ccnl = load_ccnl("commercio-confcommercio.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.ccnl_id == "commercio-confcommercio"
        assert ccnl.meta.cnel_code == "H011"

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

    def test_load_ccnl_is_cached(self) -> None:
        """Two calls with the same filename return the identical CCNL object."""
        first = load_ccnl("commercio-confcommercio.json")
        second = load_ccnl("commercio-confcommercio.json")
        assert first is second

    def test_load_ccnl_is_immutable(self) -> None:
        """Mutating a field on the returned CCNL raises ValidationError."""
        ccnl = load_ccnl("commercio-confcommercio.json")
        with pytest.raises(pydantic.ValidationError):
            ccnl.schema_version = "0.5"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# load_year_rules helper
# ---------------------------------------------------------------------------


class TestLoadYearRules:
    """Unit tests for the load_year_rules helper."""

    def test_2026_terziario_loads(self) -> None:
        """load_year_rules(2026, terziario, 50) returns a valid YearRules."""
        yr = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert isinstance(yr, YearRules)
        assert yr.year == 2026

    def test_2026_industria_loads(self) -> None:
        """load_year_rules(2026, industria, 50) returns a valid YearRules."""
        yr = load_year_rules(2026, TaxSector.INDUSTRIA, 50)
        assert isinstance(yr, YearRules)
        assert yr.year == 2026

    def test_employer_tier_small(self) -> None:
        """Firms <=15 employees get the small-employer tier for industria."""
        yr_small = load_year_rules(2026, TaxSector.INDUSTRIA, 15)
        yr_medium = load_year_rules(2026, TaxSector.INDUSTRIA, 16)
        assert yr_small.inps is not None
        assert yr_medium.inps is not None
        assert yr_small.inps.employer_rate < yr_medium.inps.employer_rate

    def test_employer_tier_boundary(self) -> None:
        """Firms exactly at tier boundary are included in the lower tier."""
        yr_at = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        yr_above = load_year_rules(2026, TaxSector.TERZIARIO, 51)
        assert yr_at.inps is not None
        assert yr_above.inps is not None
        assert yr_at.inps.employer_rate < yr_above.inps.employer_rate

    def test_missing_year_raises(self) -> None:
        """A year with no data file raises the unsupported tax year error."""
        with pytest.raises(UnsupportedTaxYearError) as info:
            load_year_rules(1900, TaxSector.TERZIARIO, 50)
        assert info.value.year == 1900
        assert info.value.sector == "terziario"

    def test_load_year_rules_isolated(self) -> None:
        """Two calls return independent YearRules copies (mutation isolation)."""
        first = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        second = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert first is not second

    def test_load_year_rules_irpef_brackets_mutation_isolated(self) -> None:
        """Clearing irpef_brackets on one copy does not affect the next call."""
        first = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        original_count = len(first.irpef_brackets)
        first.irpef_brackets.clear()
        second = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert len(second.irpef_brackets) == original_count

    def test_load_year_rules_nested_field_mutation_isolated(self) -> None:
        """Assigning to inps.employee_rate does not affect subsequent loads."""
        first = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert first.inps is not None
        original_rate = first.inps.employee_rate
        first.inps.employee_rate = Decimal(0)
        second = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert second.inps is not None
        assert second.inps.employee_rate == original_rate


# ---------------------------------------------------------------------------
# CCNL Metalmeccanico Federmeccanica
# ---------------------------------------------------------------------------
