"""Tests for CCNL data loaders and bundled data files."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.models.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.models.ccnl import CCNL, TaxSector
from ccnl_engine.tax.loaders import _resolve_employer_tier, load_year_rules
from ccnl_engine.tax.models import YearRules, _InpsEmployerTier

# ---------------------------------------------------------------------------
# Parametrised: every JSON in src/ccnl_engine/contracts/data/ must validate
# ---------------------------------------------------------------------------

_DATA_DIR = (
    Path(__file__).parent.parent.parent.parent
    / "src"
    / "ccnl_engine"
    / "contracts"
    / "data"
)
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


# ---------------------------------------------------------------------------
# CCNL Turismo — Confcommercio (H052)
# ---------------------------------------------------------------------------


class TestLoadTurismoConfcommercio:
    """Structural and data-integrity tests for turismo-confcommercio.json."""

    def test_turismo_loads(self) -> None:
        """File must parse without errors; id and CNEL code must match."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert ccnl.ccnl.id == "turismo-confcommercio"
        assert ccnl.ccnl.cnel_code == "H052"

    def test_turismo_has_ten_levels(self) -> None:
        """CCNL Turismo defines exactly 10 classification levels."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert len(ccnl.levels) == 10
        assert {lv.code for lv in ccnl.levels} == {
            "QA",
            "QB",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6S",
            "6",
            "7",
        }

    def test_turismo_level3_salary_july_2024(self) -> None:
        """Level 3 base salary from 2024-07-01 must be 1717.55 (first tranche)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        l3 = next(lv for lv in ccnl.levels if lv.code == "3")
        assert l3.base_salary.value_at(date(2024, 7, 1)) == Decimal("1717.55")

    def test_turismo_level3_salary_june_2025(self) -> None:
        """Level 3 base salary from 2025-06-01 must be 1759.94 (second tranche)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        l3 = next(lv for lv in ccnl.levels if lv.code == "3")
        assert l3.base_salary.value_at(date(2025, 6, 1)) == Decimal("1759.94")

    def test_turismo_level_ordering(self) -> None:
        """QA must have the highest order; level 7 the lowest."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "7"
        assert by_order[-1].code == "QA"

    def test_turismo_seniority_cadence(self) -> None:
        """Scatti are quadriennali (48 months), maximum 6."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 48
        assert si.maximum_count == 6

    def test_turismo_fourteen_months(self) -> None:
        """Contract has 14 monthly salaries per year (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        value = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert value == Decimal(14)

    def test_turismo_no_fixed_allowances(self) -> None:
        """All levels have no fixed_allowances (minimum conglobated in base_salary)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        for level in ccnl.levels:
            assert level.fixed_allowances == [], (
                f"Level {level.code} should have no fixed_allowances"
            )

    def test_turismo_apprenticeship_percentage(self) -> None:
        """Apprenticeship uses percentage model: 80/85/90% per anno (rinnovo 2024)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert isinstance(ccnl.apprenticeship, ApprenticeshipPercentage)
        assert ccnl.apprenticeship.destination_level == "5"
        periods = ccnl.apprenticeship.periods
        assert len(periods) == 3
        assert periods[0].percentage == Decimal("0.80")
        assert periods[1].percentage == Decimal("0.85")
        assert periods[2].percentage == Decimal("0.90")
        assert periods[2].months_until is None

    def test_turismo_hourly_divisor(self) -> None:
        """Hourly divisor must be 172 (40 h/week standard for turismo)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert ccnl.parameters.hourly_divisor == 172


# ---------------------------------------------------------------------------
# CCNL Edilizia — ANCE (F012)
# ---------------------------------------------------------------------------


class TestLoadEdiliziaAnce:
    """Structural and data-integrity tests for edilizia-ance.json."""

    def test_edilizia_loads(self) -> None:
        """load_ccnl loads the edilizia JSON and returns the expected identifiers."""
        ccnl = load_ccnl("edilizia-ance.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.ccnl.id == "edilizia-ance"
        assert ccnl.ccnl.cnel_code == "F012"

    def test_edilizia_has_seven_levels(self) -> None:
        """Edilizia ANCE CCNL must contain exactly 7 classification levels."""
        ccnl = load_ccnl("edilizia-ance.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7"}

    def test_edilizia_level3_salary_feb_2025(self) -> None:
        """Level 3 conglobated minimum on 2025-02-01 must be EUR 1917.05."""
        ccnl = load_ccnl("edilizia-ance.json")
        lv3 = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv3.base_salary.value_at(date(2025, 2, 1)) == Decimal("1917.05")

    def test_edilizia_level3_salary_march_2026(self) -> None:
        """Level 3 conglobated minimum on 2026-03-01 must be EUR 1982.05."""
        ccnl = load_ccnl("edilizia-ance.json")
        lv3 = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv3.base_salary.value_at(date(2026, 3, 1)) == Decimal("1982.05")

    def test_edilizia_level_ordering(self) -> None:
        """Level 7 must have the highest order; level 1 the lowest."""
        ccnl = load_ccnl("edilizia-ance.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "7"

    def test_edilizia_thirteen_months(self) -> None:
        """Contract must have 13 monthly salaries per year (gratifica natalizia)."""
        ccnl = load_ccnl("edilizia-ance.json")
        value = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert value == Decimal(13)

    def test_edilizia_hourly_divisor(self) -> None:
        """Hourly divisor must be 173 (40 h/week, verified from official tariff)."""
        ccnl = load_ccnl("edilizia-ance.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_edilizia_no_fixed_allowances(self) -> None:
        """All levels have no fixed_allowances (minimum conglobated in base_salary)."""
        ccnl = load_ccnl("edilizia-ance.json")
        for level in ccnl.levels:
            assert level.fixed_allowances == [], (
                f"Level {level.code} should have no fixed_allowances"
            )

    def test_edilizia_tax_sector(self) -> None:
        """CCNL must declare tax_sector EDILIZIA."""
        ccnl = load_ccnl("edilizia-ance.json")
        assert ccnl.ccnl.tax_sector == TaxSector.EDILIZIA

    def test_edilizia_seniority_cadence(self) -> None:
        """Seniority increments must be biennale (24 months), max 5 scatti."""
        ccnl = load_ccnl("edilizia-ance.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


# ---------------------------------------------------------------------------
# CCNL Cooperative Sociali — T151
# ---------------------------------------------------------------------------


class TestLoadCooperativeSociali:
    """Unit tests for CCNL Cooperative Sociali (T151) data file."""

    def test_cooperative_sociali_loads(self) -> None:
        """File loads as valid CCNL with correct id and CNEL code T151."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.ccnl.id == "cooperative-sociali"
        assert ccnl.ccnl.cnel_code == "T151"

    def test_cooperative_sociali_has_16_levels(self) -> None:
        """Contract must contain exactly 16 levels (13 base + 3 Quadro)."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert len(ccnl.levels) == 16
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "A1",
            "A2",
            "B",
            "C1",
            "C2",
            "C3",
            "D1",
            "D2",
            "D3",
            "E1",
            "E2",
            "E2Q",
            "F1",
            "F1Q",
            "F2",
            "F2Q",
        }

    def test_cooperative_sociali_level_d2_salary_feb2024(self) -> None:
        """D2 conglobated minimum at first tranche (Feb 2024) must be 1660.99."""
        ccnl = load_ccnl("cooperative-sociali.json")
        d2 = next(lv for lv in ccnl.levels if lv.code == "D2")
        assert d2.base_salary.value_at(date(2024, 2, 1)) == Decimal("1660.99")

    def test_cooperative_sociali_level_d2_salary_oct2024(self) -> None:
        """D2 conglobated minimum at second tranche (Oct 2024) must be 1694.41."""
        ccnl = load_ccnl("cooperative-sociali.json")
        d2 = next(lv for lv in ccnl.levels if lv.code == "D2")
        assert d2.base_salary.value_at(date(2024, 10, 1)) == Decimal("1694.41")

    def test_cooperative_sociali_level_ordering(self) -> None:
        """F2Q must have the highest order; A1 the lowest."""
        ccnl = load_ccnl("cooperative-sociali.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "A1"
        assert by_order[-1].code == "F2Q"

    def test_cooperative_sociali_additional_months(self) -> None:
        """13 months before 2025, 13.5 from January 2025 (quattordicesima)."""
        ccnl = load_ccnl("cooperative-sociali.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2024, 6, 1)) == Decimal(13)
        assert am.value_at(date(2025, 1, 1)) == Decimal("13.5")

    def test_cooperative_sociali_hourly_divisor(self) -> None:
        """Hourly divisor must be 165 (38 h/week, art. 75 CCNL)."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert ccnl.parameters.hourly_divisor == 165

    def test_cooperative_sociali_q_levels_funzione_allowance(self) -> None:
        """E2Q/F1Q/F2Q must carry exactly one IDF fixed allowance each."""
        ccnl = load_ccnl("cooperative-sociali.json")
        expected = {"E2Q": "77.47", "F1Q": "154.94", "F2Q": "232.41"}
        for code, amount in expected.items():
            lv = next(lvl for lvl in ccnl.levels if lvl.code == code)
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "IDF"
            val = lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1))
            assert val == Decimal(amount)

    def test_cooperative_sociali_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert ccnl.ccnl.tax_sector == TaxSector.TERZIARIO

    def test_cooperative_sociali_seniority_cadence(self) -> None:
        """Seniority increments: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("cooperative-sociali.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadLogisticaTrasportoConfetra:
    """Tests for CCNL Logistica, Trasporto Merci e Spedizione (I100)."""

    def test_logistica_trasporto_confetra_loads(self) -> None:
        """CCNL id must be logistica-trasporto-confetra, CNEL code I100."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert ccnl.ccnl.id == "logistica-trasporto-confetra"
        assert ccnl.ccnl.cnel_code == "I100"

    def test_logistica_trasporto_confetra_has_9_levels(self) -> None:
        """Contract must have exactly 9 levels (6J excluded, abolished Dec 2025)."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3S", "3", "4", "4J", "5", "6"}

    def test_logistica_trasporto_confetra_level_3s_salary_jan2025(self) -> None:
        """3S conglobated minimum at first tranche (Jan 2025) must be 2070.37."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        lv = next(lvl for lvl in ccnl.levels if lvl.code == "3S")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("2070.37")

    def test_logistica_trasporto_confetra_level_3s_salary_jan2026(self) -> None:
        """3S conglobated minimum at second tranche (Jan 2026) must be 2160.37."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        lv = next(lvl for lvl in ccnl.levels if lvl.code == "3S")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("2160.37")

    def test_logistica_trasporto_confetra_level_ordering(self) -> None:
        """Quadro must have the highest order; 6° livello the lowest."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "Q"

    def test_logistica_trasporto_confetra_additional_months(self) -> None:
        """14 additional months (tredicesima Art. 18 + quattordicesima Art. 19)."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 1, 1)) == Decimal(14)

    def test_logistica_trasporto_confetra_hourly_divisor(self) -> None:
        """Hourly divisor must be 168 (Art. 61 co.3 testo unico Sept 2025)."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert ccnl.parameters.hourly_divisor == 168

    def test_logistica_trasporto_confetra_no_fixed_allowances(self) -> None:
        """All levels must have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_logistica_trasporto_confetra_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert ccnl.ccnl.tax_sector == TaxSector.INDUSTRIA

    def test_logistica_trasporto_confetra_seniority_cadence(self) -> None:
        """Seniority increments: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadMultiserviziAnip:
    """Tests for CCNL Multiservizi K511 (ANIP-Confindustria) data file."""

    def test_multiservizi_anip_loads(self) -> None:
        """File must load and carry the correct id and CNEL code."""
        ccnl = load_ccnl("multiservizi-anip.json")
        assert ccnl.ccnl.id == "multiservizi-anip"
        assert ccnl.ccnl.cnel_code == "K511"

    def test_multiservizi_anip_has_10_levels(self) -> None:
        """Must have exactly 10 levels including par sub-levels."""
        ccnl = load_ccnl("multiservizi-anip.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "2par115", "3", "4par125", "4", "5", "6", "7", "Q"}

    def test_multiservizi_anip_level4_salary_tranche1(self) -> None:
        """Level 4 paga base at first tranche (July 2021) = 821.08."""
        ccnl = load_ccnl("multiservizi-anip.json")
        lvl = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lvl.base_salary.value_at(date(2021, 7, 1)) == Decimal("821.08")

    def test_multiservizi_anip_level4_salary_tranche2(self) -> None:
        """Level 4 paga base at May 2026 tranche (2025-2028 renewal) = 1003.10."""
        ccnl = load_ccnl("multiservizi-anip.json")
        lvl = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lvl.base_salary.value_at(date(2026, 5, 1)) == Decimal("1003.10")

    def test_multiservizi_anip_level_ordering(self) -> None:
        """Level 1 must be lowest order; Q must be highest order."""
        ccnl = load_ccnl("multiservizi-anip.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_multiservizi_anip_additional_months(self) -> None:
        """14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("multiservizi-anip.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 5, 1)) == Decimal(14)

    def test_multiservizi_anip_hourly_divisor(self) -> None:
        """Hourly divisor must be 173 per CCNL text."""
        ccnl = load_ccnl("multiservizi-anip.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_multiservizi_anip_split_model_allowances(self) -> None:
        """Split model: every level must have contingenza and EDR allowances."""
        ccnl = load_ccnl("multiservizi-anip.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "contingenza" in codes, f"level {lv.code} missing contingenza"
            assert "edr" in codes, f"level {lv.code} missing edr"

    def test_multiservizi_anip_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO (CNEL K-prefix contract)."""
        ccnl = load_ccnl("multiservizi-anip.json")
        assert ccnl.ccnl.tax_sector == TaxSector.TERZIARIO

    def test_multiservizi_anip_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 8 scatti."""
        ccnl = load_ccnl("multiservizi-anip.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 8


class TestLoadStudiProfessionaliConfprofessioni:
    """Tests for CCNL Studi Professionali — Confprofessioni (H442)."""

    def test_studi_professionali_confprofessioni_loads(self) -> None:
        """CCNL must load with correct id and CNEL code."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        assert ccnl.ccnl.id == "studi-professionali-confprofessioni"
        assert ccnl.ccnl.cnel_code == "H442"

    def test_studi_professionali_confprofessioni_has_8_levels(self) -> None:
        """CCNL must have exactly 8 levels: 5, 4, 4S, 3, 3S, 2, 1, Q."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 8
        assert codes == {"5", "4", "4S", "3", "3S", "2", "1", "Q"}

    def test_studi_professionali_confprofessioni_level4_salary_tranche1(
        self,
    ) -> None:
        """Level 4 minimo tabellare at tranche 1 (2024-03-01): 1511.28."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        assert level.base_salary.value_at(date(2024, 3, 1)) == Decimal("1511.28")

    def test_studi_professionali_confprofessioni_level4_salary_tranche3(
        self,
    ) -> None:
        """Level 4 minimo tabellare at tranche 3 (2025-10-01): 1595.42."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        assert level.base_salary.value_at(date(2026, 1, 1)) == Decimal("1595.42")

    def test_studi_professionali_confprofessioni_level_ordering(self) -> None:
        """Level 5 must be lowest (order 1), Q must be highest."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "5"
        assert by_order[-1].code == "Q"

    def test_studi_professionali_confprofessioni_additional_months(self) -> None:
        """14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 10, 1)) == Decimal(14)

    def test_studi_professionali_confprofessioni_hourly_divisor(self) -> None:
        """Hourly divisor must be 170 per Art. 45 and Art. 137 CCNL."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        assert ccnl.parameters.hourly_divisor == 170

    def test_studi_professionali_confprofessioni_no_fixed_allowances(
        self,
    ) -> None:
        """Conglobated model: all levels must have no fixed allowances."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == [], f"level {lv.code} has allowances"

    def test_studi_professionali_confprofessioni_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO (CNEL H-prefix contract)."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        assert ccnl.ccnl.tax_sector == TaxSector.TERZIARIO

    def test_studi_professionali_confprofessioni_seniority_cadence(
        self,
    ) -> None:
        """Seniority: triennale cadence (36 months), maximum 8 scatti."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 8


class TestLoadBancariAbi:
    """Tests for CCNL Bancari ABI (J241) data file."""

    def test_bancari_abi_loads(self) -> None:
        """Loads bancari-abi and verifies id and CNEL code J241."""
        ccnl = load_ccnl("bancari-abi.json")
        assert ccnl.ccnl.id == "bancari-abi"
        assert ccnl.ccnl.cnel_code == "J241"

    def test_bancari_abi_has_9_levels(self) -> None:
        """Nine levels: QD4, QD3, QD2, QD1, 3A4, 3A3, 3A2, 3A1, 1e2A."""
        ccnl = load_ccnl("bancari-abi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 9
        assert codes == {
            "QD4",
            "QD3",
            "QD2",
            "QD1",
            "3A4",
            "3A3",
            "3A2",
            "3A1",
            "1e2A",
        }

    def test_bancari_abi_level_3a3_salary_tranche1(self) -> None:
        """Level 3A3 conglobato at tranche 1 (2023-12-01): 2899.88."""
        ccnl = load_ccnl("bancari-abi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "3A3")
        assert level.base_salary.value_at(date(2023, 12, 1)) == Decimal("2899.88")

    def test_bancari_abi_level_3a3_salary_tranche2(self) -> None:
        """Level 3A3 conglobato at tranche 2 (2024-09-01): 2986.15."""
        ccnl = load_ccnl("bancari-abi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "3A3")
        assert level.base_salary.value_at(date(2024, 9, 1)) == Decimal("2986.15")

    def test_bancari_abi_level_ordering(self) -> None:
        """1e2A must be lowest (order 1), QD4 must be highest."""
        ccnl = load_ccnl("bancari-abi.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1e2A"
        assert by_order[-1].code == "QD4"

    def test_bancari_abi_additional_months(self) -> None:
        """13 additional months (tredicesima only)."""
        ccnl = load_ccnl("bancari-abi.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 1, 1)) == Decimal(13)

    def test_bancari_abi_hourly_divisor(self) -> None:
        """Hourly divisor must be 160 (37h/week from July 2024)."""
        ccnl = load_ccnl("bancari-abi.json")
        assert ccnl.parameters.hourly_divisor == 160

    def test_bancari_abi_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels must have no fixed allowances."""
        ccnl = load_ccnl("bancari-abi.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == [], f"level {lv.code} has allowances"

    def test_bancari_abi_tax_sector(self) -> None:
        """CCNL must declare tax_sector CREDITO (ABI banking sector)."""
        ccnl = load_ccnl("bancari-abi.json")
        assert ccnl.ccnl.tax_sector == TaxSector.CREDITO

    def test_bancari_abi_seniority_cadence(self) -> None:
        """Seniority: triennale cadence (36 months), maximum 8 scatti."""
        ccnl = load_ccnl("bancari-abi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 8
