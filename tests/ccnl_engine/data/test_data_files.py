"""Tests for CCNL data loaders and bundled data files."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ccnl_engine.data.loaders import _resolve_employer_tier, load_ccnl, load_year_rules
from ccnl_engine.models.apprenticeship import (
    ApprenticeshipUnderClassification,
)
from ccnl_engine.models.ccnl import CCNL, TaxSector
from ccnl_engine.tax.models import YearRules, _InpsEmployerTier

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
        assert yr_small.inps.employer_rate < yr_medium.inps.employer_rate

    def test_employer_tier_boundary(self) -> None:
        """Firms exactly at tier boundary are included in the lower tier."""
        yr_at = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        yr_above = load_year_rules(2026, TaxSector.TERZIARIO, 51)
        assert yr_at.inps.employer_rate < yr_above.inps.employer_rate

    def test_missing_year_raises(self) -> None:
        """A year with no data file must raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_year_rules(1900, TaxSector.TERZIARIO, 50)

    def test_no_open_tier_raises(self) -> None:
        """_resolve_employer_tier raises ValueError when no tier is open."""
        tiers = [_InpsEmployerTier(max_employees=10, rate=Decimal("0.30"))]
        with pytest.raises(ValueError, match="No employer-rate tier"):
            _resolve_employer_tier(tiers, 100)


# ---------------------------------------------------------------------------
# CCNL Metalmeccanico Federmeccanica
# ---------------------------------------------------------------------------


class TestLoadMetalmeccanico:
    """Unit tests for the bundled Metalmeccanico data file."""

    def test_metalmeccanico_loads(self) -> None:
        """File parses, id and cnel_code are correct."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.ccnl.id == "metalmeccanico-federmeccanica"
        assert ccnl.ccnl.cnel_code == "C011"

    def test_metalmeccanico_has_nine_levels(self) -> None:
        """Contract must have exactly 9 levels (D1…A1)."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"D1", "D2", "C1", "C2", "C3", "B1", "B2", "B3", "A1"}

    def test_metalmeccanico_c3_salary_june_2026(self) -> None:
        """Level C3 base salary from 2026-06-01 onward must be 2211.43 €."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        c3 = next(lv for lv in ccnl.levels if lv.code == "C3")
        assert c3.base_salary.value_at(date(2026, 6, 1)) == Decimal("2211.43")

    def test_metalmeccanico_a1_highest_d1_lowest(self) -> None:
        """A1 must have the highest order; D1 the lowest."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "D1"
        assert by_order[-1].code == "A1"

    def test_metalmeccanico_seniority_cadence(self) -> None:
        """Seniority increments are biennial (24 months), max 5."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_metalmeccanico_thirteen_months(self) -> None:
        """Contract has 13 monthly salaries per year."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        value = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert value == Decimal(13)

    def test_metalmeccanico_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (minimi conglobati)."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        for level in ccnl.levels:
            assert level.fixed_allowances == [], (
                f"Level {level.code} should have no fixed_allowances "
                "(base_salary is already the minimo conglobato)"
            )


# ---------------------------------------------------------------------------
# CCNL Metalmeccanico Confapi (Piccola Industria)
# ---------------------------------------------------------------------------


class TestLoadMetalmeccanicoConfapi:
    """Unit tests for the bundled Metalmeccanico Confapi (PMI) data file."""

    def test_confapi_loads(self) -> None:
        """File parses, id and cnel_code are correct."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.ccnl.id == "metalmeccanico-confapi"
        assert ccnl.ccnl.cnel_code == "C018"

    def test_confapi_has_nine_levels(self) -> None:
        """Contract must have exactly 9 levels (1-9)."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7", "8", "9"}

    def test_confapi_level5_salary_june_2026(self) -> None:
        """Level 5 base salary from 2026-06-01 onward must be 2245.87 €."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        l5 = next(lv for lv in ccnl.levels if lv.code == "5")
        assert l5.base_salary.value_at(date(2026, 6, 1)) == Decimal("2245.87")

    def test_confapi_level5_salary_june_2025(self) -> None:
        """Level 5 base salary from 2025-06-01 must be 2173.76 €."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        l5 = next(lv for lv in ccnl.levels if lv.code == "5")
        assert l5.base_salary.value_at(date(2025, 6, 1)) == Decimal("2173.76")

    def test_confapi_level5_salary_september_2025(self) -> None:
        """Level 5 base salary from 2025-09-01 must be 2195.86 €."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        l5 = next(lv for lv in ccnl.levels if lv.code == "5")
        assert l5.base_salary.value_at(date(2025, 9, 1)) == Decimal("2195.86")

    def test_confapi_level1_salary_september_2025(self) -> None:
        """Level 1 base salary from 2025-09-01 must be 1603.40 €."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        l1 = next(lv for lv in ccnl.levels if lv.code == "1")
        assert l1.base_salary.value_at(date(2025, 9, 1)) == Decimal("1603.40")

    def test_confapi_apprenticeship_under_classification(self) -> None:
        """Apprenticeship uses under-classification (Art. 10 CCNL), not percentage."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        assert isinstance(ccnl.apprenticeship, ApprenticeshipUnderClassification)
        assert ccnl.apprenticeship.destination_level == "5"
        periods = ccnl.apprenticeship.periods
        assert len(periods) == 3
        assert periods[0].pay_level_code == "3"
        assert periods[1].pay_level_code == "4"
        assert periods[2].pay_level_code == "5"

    def test_confapi_level9_highest_level1_lowest(self) -> None:
        """Level 9 must have the highest order; level 1 the lowest."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "9"

    def test_confapi_seniority_cadence(self) -> None:
        """Seniority increments are biennial (24 months), max 5 (Art. 41)."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_confapi_thirteen_months(self) -> None:
        """Contract has 13 monthly salaries per year (no quattordicesima)."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        value = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert value == Decimal(13)

    def test_confapi_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (minimi conglobati)."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        for level in ccnl.levels:
            assert level.fixed_allowances == [], (
                f"Level {level.code} should have no fixed_allowances "
                "(base_salary is already the minimo conglobato)"
            )


# ---------------------------------------------------------------------------
# CCNL Industria Chimica-Farmaceutica (Federchimica)
# ---------------------------------------------------------------------------


class TestLoadChimicaFederchimica:
    """Unit tests for the bundled Chimica-Farmaceutica data file."""

    def test_chimica_loads(self) -> None:
        """File parses, id and cnel_code are correct."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.ccnl.id == "chimica-farmaceutica-federchimica"
        assert ccnl.ccnl.cnel_code == "B011"

    def test_chimica_has_fifteen_levels(self) -> None:
        """Contract must have exactly 15 classification levels."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        assert len(ccnl.levels) == 15
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "A1",
            "A2",
            "A3",
            "B1",
            "B2",
            "C1",
            "C2",
            "D1",
            "D2",
            "D3",
            "E1",
            "E2",
            "E3",
            "E4",
            "F",
        }

    def test_chimica_d1_tem_july_2026(self) -> None:
        """D1 TEM from 2026-07-01 onward must be 2420.26 (base + IPO)."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        d1 = next(lv for lv in ccnl.levels if lv.code == "D1")
        assert d1.base_salary.value_at(date(2026, 7, 1)) == Decimal("2420.26")

    def test_chimica_d1_tem_july_2025(self) -> None:
        """D1 TEM from 2025-07-01 must be 2340.26 (first tranche CCNL 2025-2028)."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        d1 = next(lv for lv in ccnl.levels if lv.code == "D1")
        assert d1.base_salary.value_at(date(2025, 7, 1)) == Decimal("2340.26")

    def test_chimica_d1_tem_december_2025(self) -> None:
        """D1 TEM from 2025-12-01 must be 2360.26 (Min=2008.03 + IPO=352.23)."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        d1 = next(lv for lv in ccnl.levels if lv.code == "D1")
        assert d1.base_salary.value_at(date(2025, 12, 1)) == Decimal("2360.26")

    def test_chimica_a1_highest_f_lowest(self) -> None:
        """A1 must have the highest order; F the lowest."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "F"
        assert by_order[-1].code == "A1"

    def test_chimica_a1_tem_july_2026(self) -> None:
        """A1 TEM from 2026-07-01 must be 3528.48 (base + EAR 190 + IPO 626.96)."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        a1 = next(lv for lv in ccnl.levels if lv.code == "A1")
        assert a1.base_salary.value_at(date(2026, 7, 1)) == Decimal("3528.48")

    def test_chimica_no_seniority_increments(self) -> None:
        """Scatti di anzianita are abolished: maximum_count=0, amount_by_level empty."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        si = ccnl.parameters.seniority_increments
        assert si.maximum_count == 0
        assert si.amount_by_level == {}

    def test_chimica_apprenticeship_under_classification(self) -> None:
        """Apprenticeship uses under-classification model, destination D1."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        assert isinstance(ccnl.apprenticeship, ApprenticeshipUnderClassification)
        assert ccnl.apprenticeship.destination_level == "D1"
        periods = ccnl.apprenticeship.periods
        assert len(periods) == 2
        assert periods[0].pay_level_code == "E1"
        assert periods[1].pay_level_code == "D1"
        assert periods[1].months_until is None

    def test_chimica_thirteen_months(self) -> None:
        """Contract has 13 monthly salaries per year (tredicesima only)."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        value = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert value == Decimal(13)

    def test_chimica_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (TEM modelled as base_salary)."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        for level in ccnl.levels:
            assert level.fixed_allowances == [], (
                f"Level {level.code} should have no fixed_allowances "
                "(TEM is already embedded in base_salary)"
            )

    def test_chimica_hourly_divisor(self) -> None:
        """Hourly divisor must be 175 (chimico-farmaceutico standard)."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        assert ccnl.parameters.hourly_divisor == 175
