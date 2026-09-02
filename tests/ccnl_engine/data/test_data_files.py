"""Tests for CCNL data loaders and bundled data files."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.engine.compute import compute
from ccnl_engine.models.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.models.ccnl import CCNL, TaxSector
from ccnl_engine.models.employment import Apprentice
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


class TestLoadTessileSmi:
    """Tests for CCNL Tessile Abbigliamento Moda SMI (D014)."""

    def test_tessile_smi_loads(self) -> None:
        """Contract id == 'tessile-smi', CNEL code == 'D014'."""
        ccnl = load_ccnl("tessile-smi.json")
        assert ccnl.ccnl.id == "tessile-smi"
        assert ccnl.ccnl.cnel_code == "D014"

    def test_tessile_smi_has_10_levels(self) -> None:
        """10 livelli: 1, 2, 2S, 3, 3S, 4, 5, 6, 7, 8."""
        ccnl = load_ccnl("tessile-smi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 10
        assert codes == {"1", "2", "2S", "3", "3S", "4", "5", "6", "7", "8"}

    def test_tessile_smi_level4_salary_tranche1(self) -> None:
        """Level 4 pre-Dec 2024 ERN: 1786.95 EUR (lexplain.it)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        val = level.base_salary.value_at(date(2025, 6, 1))
        assert val == Decimal("1786.95")

    def test_tessile_smi_level4_salary_tranche2(self) -> None:
        """Level 4 Jan 2026 ERN: 1938.95 EUR (kitech.it)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        val = level.base_salary.value_at(date(2026, 1, 1))
        assert val == Decimal("1938.95")

    def test_tessile_smi_level_ordering(self) -> None:
        """Level 1 must be lowest (order 1), level 8 must be highest."""
        ccnl = load_ccnl("tessile-smi.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "8"

    def test_tessile_smi_additional_months(self) -> None:
        """13 additional months (tredicesima only)."""
        ccnl = load_ccnl("tessile-smi.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 1, 1)) == Decimal(13)

    def test_tessile_smi_hourly_divisor(self) -> None:
        """Hourly divisor must be 173 (40h/week standard)."""
        ccnl = load_ccnl("tessile-smi.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_tessile_smi_level8_has_fixed_allowance(self) -> None:
        """Level 8 has exactly one fixed allowance: Indennita funzione 51.65."""
        ccnl = load_ccnl("tessile-smi.json")
        level8 = next(lv for lv in ccnl.levels if lv.code == "8")
        assert len(level8.fixed_allowances) == 1
        fa = level8.fixed_allowances[0]
        assert fa.code == "IND_FUN"
        assert fa.monthly.value_at(date(2026, 1, 1)) == Decimal("51.65")

    def test_tessile_smi_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("tessile-smi.json")
        assert ccnl.ccnl.tax_sector == TaxSector.INDUSTRIA

    def test_tessile_smi_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 4 scatti."""
        ccnl = load_ccnl("tessile-smi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 4

    def test_tessile_smi_apprentice_raises(self) -> None:
        """Apprentice compute on null-apprenticeship CCNL raises ValueError."""
        ccnl = load_ccnl("tessile-smi.json")
        rules = load_year_rules(2026, TaxSector.INDUSTRIA, num_employees=50)
        with pytest.raises(ValueError, match="no apprenticeship rules"):
            compute(ccnl, "4", date(2026, 1, 1), rules, Apprentice(months_elapsed=12))


class TestLoadAlimentariFederalimentare:
    """Tests for CCNL Alimentari Industria — Federalimentare (E012)."""

    def test_alimentari_federalimentare_loads(self) -> None:
        """CCNL id == 'alimentari-federalimentare', cnel_code == 'E012'."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert ccnl.ccnl.id == "alimentari-federalimentare"
        assert ccnl.ccnl.cnel_code == "E012"

    def test_alimentari_federalimentare_has_8_levels(self) -> None:
        """8 levels: 6, 5, 4, 3, 3A, 2, 1, 1S."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "1S",
            "1",
            "2",
            "3A",
            "3",
            "4",
            "5",
            "6",
        }

    def test_alimentari_federalimentare_level3_salary_tranche1(self) -> None:
        """Level 3 TEM at tranche 1 (2023-12-01): 1419.08 EUR."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        level = next(lv for lv in ccnl.levels if lv.code == "3")
        assert level.base_salary.value_at(date(2023, 12, 1)) == Decimal("1419.08")

    def test_alimentari_federalimentare_level3_salary_tranche4(self) -> None:
        """Level 3 TEM at tranche 4 (2026-01-01): 1566.16 EUR."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        level = next(lv for lv in ccnl.levels if lv.code == "3")
        assert level.base_salary.value_at(date(2026, 1, 1)) == Decimal("1566.16")

    def test_alimentari_federalimentare_level_ordering(self) -> None:
        """Level 6 (order 1) is lowest; level 1S (order 8) is highest."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "1S"

    def test_alimentari_federalimentare_additional_months(self) -> None:
        """14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 1, 1)) == Decimal(14)

    def test_alimentari_federalimentare_hourly_divisor(self) -> None:
        """Hourly divisor must be 173 (40h/week standard industria)."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_alimentari_federalimentare_split_allowances(self) -> None:
        """Split model: every level has CONT, EDR, IAR allowances."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert codes == {"CONT", "EDR", "IAR"}, (
                f"level {lv.code} allowances: {codes}"
            )

    def test_alimentari_federalimentare_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert ccnl.ccnl.tax_sector == TaxSector.INDUSTRIA

    def test_alimentari_federalimentare_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_alimentari_federalimentare_apprenticeship_type(self) -> None:
        """Apprenticeship is under_classification, destination_level 3A."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert isinstance(ccnl.apprenticeship, ApprenticeshipUnderClassification)
        assert ccnl.apprenticeship.destination_level == "3A"

    def test_alimentari_federalimentare_apprentice_under_classification(self) -> None:
        """Apprentice 5 months elapsed → under level 4 (period 0-9 months)."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        rules = load_year_rules(2026, TaxSector.INDUSTRIA, num_employees=50)
        result = compute(
            ccnl, "3A", date(2026, 1, 1), rules, Apprentice(months_elapsed=5)
        )
        assert result.apprenticeship_under_level_code == "4"
        assert result.apprenticeship_pct is None


class TestLoadDmoFederdistribuzione:
    """Tests for CCNL DMO Federdistribuzione (H008) data file."""

    def test_dmo_federdistribuzione_loads(self) -> None:
        """Loads dmo-federdistribuzione and verifies id and CNEL code H008."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        assert ccnl.ccnl.id == "dmo-federdistribuzione"
        assert ccnl.ccnl.cnel_code == "H008"

    def test_dmo_federdistribuzione_has_8_levels(self) -> None:
        """Eight levels: VII, VI, V, IV, III, II, I, Q."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 8
        assert codes == {
            "VII",
            "VI",
            "V",
            "IV",
            "III",
            "II",
            "I",
            "Q",
        }

    def test_dmo_federdistribuzione_level_iv_salary_tranche1(self) -> None:
        """Level IV paga base at tranche 1 (2023-04-01): 1122.46 EUR."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        level = next(lv for lv in ccnl.levels if lv.code == "IV")
        assert level.base_salary.value_at(date(2023, 4, 1)) == Decimal("1122.46")

    def test_dmo_federdistribuzione_level_iv_salary_tranche2(self) -> None:
        """Level IV paga base at tranche 2 (2024-04-01): 1192.46 EUR."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        level = next(lv for lv in ccnl.levels if lv.code == "IV")
        assert level.base_salary.value_at(date(2024, 4, 1)) == Decimal("1192.46")

    def test_dmo_federdistribuzione_level_ordering(self) -> None:
        """VII must be lowest (order 1), Q must be highest."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "VII"
        assert by_order[-1].code == "Q"

    def test_dmo_federdistribuzione_additional_months(self) -> None:
        """14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 1, 1)) == Decimal(14)

    def test_dmo_federdistribuzione_hourly_divisor(self) -> None:
        """Hourly divisor must be 168 (40h/week, Art. 194)."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        assert ccnl.parameters.hourly_divisor == 168

    def test_dmo_federdistribuzione_fixed_allowances_split(self) -> None:
        """Split model: all levels have contingenza and terzo_elemento_nazionale."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "contingenza" in codes, f"level {lv.code} missing contingenza"
            assert "terzo_elemento_nazionale" in codes, (
                f"level {lv.code} missing terzo_elemento_nazionale"
            )

    def test_dmo_federdistribuzione_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        assert ccnl.ccnl.tax_sector == TaxSector.TERZIARIO

    def test_dmo_federdistribuzione_seniority_cadence(self) -> None:
        """Seniority: triennale cadence (36 months), maximum 10 scatti."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadMetalmeccanicoArtigianato:
    """Tests for CCNL Metalmeccanica Artigianato (Confartigianato/CNA, C030)."""

    def test_metalmeccanico_artigianato_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        assert ccnl.ccnl.id == "metalmeccanico-artigianato"
        assert ccnl.ccnl.cnel_code == "C030"

    def test_metalmeccanico_artigianato_has_8_levels(self) -> None:
        """Contract has exactly 8 levels with expected codes."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1Q", "1", "2", "2bis", "3", "4", "5", "6"}

    def test_metalmeccanico_artigianato_level4_salary_first_tranche(self) -> None:
        """Level 4° salary at first tranche date (2022-01-01)."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        val = lv.base_salary.value_at(date(2022, 1, 1))
        assert val == Decimal("1416.41")

    def test_metalmeccanico_artigianato_level4_salary_2026(self) -> None:
        """Level 4° salary at March 2026 tranche (kitech-confirmed)."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        val = lv.base_salary.value_at(date(2026, 3, 1))
        assert val == Decimal("1656.98")

    def test_metalmeccanico_artigianato_level_ordering(self) -> None:
        """1Q has highest order; 6 has lowest order."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "1Q"

    def test_metalmeccanico_artigianato_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_metalmeccanico_artigianato_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (Art. 28 CCNL 17.12.2021)."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_metalmeccanico_artigianato_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have empty fixed_allowances."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_metalmeccanico_artigianato_tax_sector(self) -> None:
        """CCNL must declare tax_sector ARTIGIANATO."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        assert ccnl.ccnl.tax_sector == TaxSector.ARTIGIANATO

    def test_metalmeccanico_artigianato_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadGommaPlasticaFederazioneGommaPlastica:
    """Tests for CCNL Gomma e Plastica Industria (Federazione Gomma Plastica, B371)."""

    def test_gomma_plastica_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        assert ccnl.ccnl.id == "gomma-plastica-federazione-gomma-plastica"
        assert ccnl.ccnl.cnel_code == "B371"

    def test_gomma_plastica_has_10_levels(self) -> None:
        """Contract has exactly 10 levels with expected codes."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "A", "B", "C", "D", "E", "F", "G", "H", "I"}

    def test_gomma_plastica_level_f_salary_first_tranche(self) -> None:
        """Level F salary at first tranche date 2023-01-01 (lexplain.it)."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "F")
        val = lv.base_salary.value_at(date(2023, 1, 1))
        assert val == Decimal("1869.12")

    def test_gomma_plastica_level_f_salary_2026(self) -> None:
        """Level F salary at 2026-01-01 tranche (kitech.it confirmed)."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "F")
        val = lv.base_salary.value_at(date(2026, 1, 1))
        assert val == Decimal("2021.12")

    def test_gomma_plastica_level_ordering(self) -> None:
        """I has lowest order (1); Q has highest order (10)."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "I"
        assert by_order[-1].code == "Q"

    def test_gomma_plastica_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_gomma_plastica_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week standard)."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_gomma_plastica_q_has_funzione_allowance(self) -> None:
        """Level Q has exactly one fixed allowance of 50 EUR/month."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        q = next(lv for lv in ccnl.levels if lv.code == "Q")
        assert len(q.fixed_allowances) == 1
        val = q.fixed_allowances[0].monthly.value_at(date(2026, 1, 1))
        assert val == Decimal("50.00")

    def test_gomma_plastica_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        assert ccnl.ccnl.tax_sector == TaxSector.INDUSTRIA

    def test_gomma_plastica_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadGraficaEditoriaAieg:
    """Tests for CCNL Grafica e Editoria Industria (AIEG-Acigraf, G011)."""

    def test_grafica_editoria_aieg_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert ccnl.ccnl.id == "grafica-editoria-aieg"
        assert ccnl.ccnl.cnel_code == "G011"

    def test_grafica_editoria_aieg_has_12_levels(self) -> None:
        """Grafici sector has exactly 12 levels with expected codes."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert len(ccnl.levels) == 12
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "Q",
            "AS",
            "A",
            "B1S",
            "B1",
            "B2",
            "B3",
            "C1",
            "C2",
            "D1",
            "D2",
            "E",
        }

    def test_grafica_editoria_aieg_level_c1_salary_first_tranche(self) -> None:
        """Level C1 salary at first tranche date 2024-03-01 (lexplain.it)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        val = lv.base_salary.value_at(date(2024, 3, 1))
        assert val == Decimal("1852.88")

    def test_grafica_editoria_aieg_level_c1_salary_jul2026(self) -> None:
        """Level C1 salary at July 2026 tranche (kitech.it confirmed)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        val = lv.base_salary.value_at(date(2026, 7, 1))
        assert val == Decimal("2002.49")

    def test_grafica_editoria_aieg_level_ordering(self) -> None:
        """E has lowest order (1); Q has highest order (12)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "E"
        assert by_order[-1].code == "Q"

    def test_grafica_editoria_aieg_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 7, 1))
        assert val == Decimal(13)

    def test_grafica_editoria_aieg_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week standard assumption)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_grafica_editoria_aieg_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (total modelled as base_salary)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_grafica_editoria_aieg_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert ccnl.ccnl.tax_sector == TaxSector.INDUSTRIA

    def test_grafica_editoria_aieg_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadCartaCartoneAssocarta:
    """Tests for CCNL Carta e Cartone Industria (Assocarta, CNEL G022)."""

    def test_carta_cartone_assocarta_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        assert ccnl.ccnl.id == "carta-cartone-assocarta"
        assert ccnl.ccnl.cnel_code == "G022"

    def test_carta_cartone_assocarta_has_13_levels(self) -> None:
        """Contract has exactly 13 levels with correct codes."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 13
        assert codes == {
            "Q",
            "AS",
            "A",
            "B1",
            "B2S",
            "B2",
            "C1S",
            "C1",
            "C2",
            "C3",
            "D1",
            "D2",
            "E",
        }

    def test_carta_cartone_assocarta_level_c1_salary_2024(self) -> None:
        """Level C1 total at 2024-07-01 equals 1855.11 EUR."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        val = lv.base_salary.value_at(date(2024, 7, 1))
        assert val == Decimal("1855.11")

    def test_carta_cartone_assocarta_level_c1_salary_2026(self) -> None:
        """Level C1 conglobated total at 2026-04-01 equals 1960.11 EUR."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        val = lv.base_salary.value_at(date(2026, 4, 1))
        assert val == Decimal("1960.11")

    def test_carta_cartone_assocarta_level_ordering(self) -> None:
        """Q is the highest-order level; E is the lowest-order level."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "E"
        assert by_order[-1].code == "Q"

    def test_carta_cartone_assocarta_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 4, 1))
        assert val == Decimal(13)

    def test_carta_cartone_assocarta_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week convention)."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_carta_cartone_assocarta_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_carta_cartone_assocarta_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        assert ccnl.ccnl.tax_sector == TaxSector.INDUSTRIA

    def test_carta_cartone_assocarta_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadTelecomunicazioniAsstel:
    """Tests for CCNL Telecomunicazioni — Asstel (K411)."""

    def test_telecomunicazioni_asstel_loads(self) -> None:
        """Contract id == 'telecomunicazioni-asstel', cnel_code == 'K411'."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        assert ccnl.ccnl.id == "telecomunicazioni-asstel"
        assert ccnl.ccnl.cnel_code == "K411"

    def test_telecomunicazioni_asstel_has_9_levels(self) -> None:
        """9 livelli: A1, A2, B1, B2, C1, C2, C3, C4, D1."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 9
        assert codes == {"A1", "A2", "B1", "B2", "C1", "C2", "C3", "C4", "D1"}

    def test_telecomunicazioni_asstel_levelc1_salary_tranche1(self) -> None:
        """C1 TEM at Tranche 1 (2026-01-01): 1988.73 EUR."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        level = next(lv for lv in ccnl.levels if lv.code == "C1")
        assert level.base_salary.value_at(date(2026, 1, 1)) == Decimal("1988.73")

    def test_telecomunicazioni_asstel_levelc1_salary_tranche2(self) -> None:
        """C1 TEM at Tranche 2 (2026-12-01): 2038.73 EUR."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        level = next(lv for lv in ccnl.levels if lv.code == "C1")
        assert level.base_salary.value_at(date(2026, 12, 1)) == Decimal("2038.73")

    def test_telecomunicazioni_asstel_level_ordering(self) -> None:
        """A1 is the lowest-order level; D1 is the highest-order level."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "A1"
        assert by_order[-1].code == "D1"

    def test_telecomunicazioni_asstel_additional_months(self) -> None:
        """13 additional months (tredicesima only, Art. 42 CCNL TLC)."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_telecomunicazioni_asstel_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week, Art. 40 CCNL TLC)."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_telecomunicazioni_asstel_c4_d1_fixed_allowances(self) -> None:
        """C4 has ERS=59.39; D1 has IND_FUN=98.13; others have none."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        c4 = next(lv for lv in ccnl.levels if lv.code == "C4")
        d1 = next(lv for lv in ccnl.levels if lv.code == "D1")
        assert len(c4.fixed_allowances) == 1
        assert c4.fixed_allowances[0].code == "ERS"
        assert c4.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "59.39"
        )
        assert len(d1.fixed_allowances) == 1
        assert d1.fixed_allowances[0].code == "IND_FUN"
        assert d1.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "98.13"
        )
        for lv in ccnl.levels:
            if lv.code not in {"C4", "D1"}:
                assert lv.fixed_allowances == []

    def test_telecomunicazioni_asstel_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA (Asstel/Confindustria)."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        assert ccnl.ccnl.tax_sector == TaxSector.INDUSTRIA

    def test_telecomunicazioni_asstel_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 7 scatti."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 7

    def test_telecomunicazioni_asstel_apprenticeship_under_classification(
        self,
    ) -> None:
        """Apprenticeship is under_classification, destination_level C1."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        assert isinstance(ccnl.apprenticeship, ApprenticeshipUnderClassification)
        assert ccnl.apprenticeship.destination_level == "C1"


class TestLoadVigilanzaPrivataAssiv:
    """Unit tests for CCNL Vigilanza Privata ASSIV (HV40, GPG section)."""

    def test_vigilanza_privata_assiv_loads(self) -> None:
        """Contract loads with correct id and CNEL code HV40."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert ccnl.ccnl.id == "vigilanza-privata-assiv"
        assert ccnl.ccnl.cnel_code == "HV40"

    def test_vigilanza_privata_assiv_has_7_levels(self) -> None:
        """GPG section has exactly 7 levels: Q, 1, 2, 3, 4, 5, 6."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3", "4", "5", "6"}

    def test_vigilanza_privata_assiv_level4_salary_tranche1(self) -> None:
        """4th level salary at 01/06/2023 (1st tranche) = 1328.88 EUR."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2023, 6, 1)) == Decimal("1328.88")

    def test_vigilanza_privata_assiv_level4_salary_tranche5(self) -> None:
        """4th level salary at 01/04/2026 (5th tranche) = 1468.88 EUR."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2026, 4, 1)) == Decimal("1468.88")

    def test_vigilanza_privata_assiv_level_ordering(self) -> None:
        """Level 6 is the lowest-order level; Q is the highest-order level."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "Q"

    def test_vigilanza_privata_assiv_additional_months(self) -> None:
        """14 additional months (tredicesima + quattordicesima, Art. 117)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        val = ccnl.parameters.additional_months.value_at(date(2023, 6, 1))
        assert val == Decimal(14)

    def test_vigilanza_privata_assiv_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week, Art. 115 base CCNL 2013)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_vigilanza_privata_assiv_no_fixed_allowances(self) -> None:
        """All GPG levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_vigilanza_privata_assiv_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector (non-Confindustria)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert ccnl.ccnl.tax_sector == TaxSector.TERZIARIO

    def test_vigilanza_privata_assiv_seniority_cadence(self) -> None:
        """Seniority: triennale cadence (36 months), maximum 6 scatti."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 6

    def test_vigilanza_privata_assiv_apprenticeship_percentage(self) -> None:
        """Apprenticeship: percentage type, 100%, destination level 4."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert isinstance(ccnl.apprenticeship, ApprenticeshipPercentage)
        assert ccnl.apprenticeship.destination_level == "4"
        assert ccnl.apprenticeship.periods[0].percentage == Decimal("1.00")


class TestLoadLegnoArredamentoFederlegno:
    """CCNL Legno e Arredamento Industria (Federlegno-Arredo, CNEL F051)."""

    def test_legno_arredamento_federlegno_loads(self) -> None:
        """Contract loads with id='legno-arredamento-federlegno', code F051."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert ccnl.ccnl.id == "legno-arredamento-federlegno"
        assert ccnl.ccnl.cnel_code == "F051"

    def test_legno_arredamento_federlegno_has_16_levels(self) -> None:
        """16 level codes across 12 salary bands (AE, AS, AC, AD areas)."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert len(ccnl.levels) == 16
        codes = {lv.code for lv in ccnl.levels}
        expected = {
            "AE1",
            "AE2",
            "AE3",
            "AE4",
            "AS1",
            "AS2",
            "AS3",
            "AS4",
            "AC1",
            "AC2",
            "AC3",
            "AC4",
            "AC5",
            "AD1",
            "AD2",
            "AD3",
        }
        assert codes == expected

    def test_legno_arredamento_federlegno_level_ac4_salary_tranche1(self) -> None:
        """AC4 paga base at 2023-07-01 (1st tranche) = 1888.07 EUR."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "AC4")
        assert lv.base_salary.value_at(date(2023, 7, 1)) == Decimal("1888.07")

    def test_legno_arredamento_federlegno_level_ac4_salary_tranche3(self) -> None:
        """AC4 paga base at 2025-01-01 (3rd tranche) = 2061.83 EUR."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "AC4")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("2061.83")

    def test_legno_arredamento_federlegno_level_ordering(self) -> None:
        """AE1 is lowest-order level; AD3 is highest-order level."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "AE1"
        assert by_order[-1].code == "AD3"

    def test_legno_arredamento_federlegno_additional_months(self) -> None:
        """13 mensilita (tredicesima only, CNEL F051 PDF)."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        val = ccnl.parameters.additional_months.value_at(date(2025, 1, 1))
        assert val == Decimal(13)

    def test_legno_arredamento_federlegno_hourly_divisor(self) -> None:
        """Hourly divisor 174 (40h/week: 40 x 52 / 12 ≈ 173.33 → 174)."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert ccnl.parameters.hourly_divisor == 174

    def test_legno_arredamento_federlegno_fixed_allowances_split(self) -> None:
        """All levels carry CONT and EDR allowances (split salary model)."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONT" in codes
            assert "EDR" in codes

    def test_legno_arredamento_federlegno_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert ccnl.ccnl.tax_sector == TaxSector.INDUSTRIA

    def test_legno_arredamento_federlegno_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_legno_arredamento_federlegno_apprenticeship_under(self) -> None:
        """Apprenticeship: under_classification, destination AS3."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert isinstance(ccnl.apprenticeship, ApprenticeshipUnderClassification)
        assert ccnl.apprenticeship.destination_level == "AS3"


class TestLoadEdiliziaArtigianatoCna:
    """CCNL Edilizia Artigianato (CNA/Confartigianato/Casartigiani, F015)."""

    def test_edilizia_artigianato_cna_loads(self) -> None:
        """Contract loads and reports correct id and CNEL code."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert ccnl.ccnl.id == "edilizia-artigianato-cna"
        assert ccnl.ccnl.cnel_code == "F015"

    def test_edilizia_artigianato_cna_has_8_levels(self) -> None:
        """Contract has exactly 8 levels: 1-7 plus 7Q."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7", "7Q"}

    def test_edilizia_artigianato_cna_level4_salary_tranche1(self) -> None:
        """Level 4 paga base at May 2025 tranche: EUR 1485.23."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4")
        assert lv.base_salary.periods[0].value == Decimal("1485.23")

    def test_edilizia_artigianato_cna_level4_salary_tranche2(self) -> None:
        """Level 4 paga base at Jan 2026 tranche: EUR 1533.88."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4")
        assert lv.base_salary.periods[1].value == Decimal("1533.88")

    def test_edilizia_artigianato_cna_level_ordering(self) -> None:
        """Level 7Q has higher order than level 1 (highest vs lowest)."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "7Q"

    def test_edilizia_artigianato_cna_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_edilizia_artigianato_cna_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (edilizia 40h/week standard)."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_edilizia_artigianato_cna_fixed_allowances_split(self) -> None:
        """All levels carry CONT and EDR allowances (split salary model)."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONT" in codes
            assert "EDR" in codes

    def test_edilizia_artigianato_cna_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert ccnl.ccnl.tax_sector == TaxSector.ARTIGIANATO

    def test_edilizia_artigianato_cna_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_edilizia_artigianato_cna_apprenticeship_percentage(self) -> None:
        """Apprenticeship: percentage type, destination level 4, 6 periods."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert isinstance(ccnl.apprenticeship, ApprenticeshipPercentage)
        assert ccnl.apprenticeship.destination_level == "4"
        assert len(ccnl.apprenticeship.periods) == 6
        assert ccnl.apprenticeship.periods[0].percentage == Decimal("0.74")


class TestLoadGasAcquaUtilitalia:
    """Tests for CCNL Gas e Acqua — Utilitalia/Proxigas/Anfida (K321)."""

    def test_gas_acqua_utilitalia_loads(self) -> None:
        """Contract loads with id='gas-acqua-utilitalia' and CNEL K321."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert ccnl.ccnl.id == "gas-acqua-utilitalia"
        assert ccnl.ccnl.cnel_code == "K321"

    def test_gas_acqua_utilitalia_has_9_levels(self) -> None:
        """Contract has exactly 9 levels: 1-8 plus Q."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7", "8", "Q"}

    def test_gas_acqua_utilitalia_level4_salary_tranche1(self) -> None:
        """Level 4 minimo at Oct 2022 tranche: EUR 2056.35."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4")
        assert lv.base_salary.periods[0].value == Decimal("2056.35")

    def test_gas_acqua_utilitalia_level4_salary_tranche2(self) -> None:
        """Level 4 minimo at Sep 2024 tranche: EUR 2204.68."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4")
        assert lv.base_salary.periods[2].value == Decimal("2204.68")

    def test_gas_acqua_utilitalia_level_ordering(self) -> None:
        """Level Q has highest order; level 1 has lowest order."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_gas_acqua_utilitalia_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(14)

    def test_gas_acqua_utilitalia_hourly_divisor(self) -> None:
        """Hourly divisor: 167 (38h 30min contractual week, CCNL §4.3)."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert ccnl.parameters.hourly_divisor == 167

    def test_gas_acqua_utilitalia_edr_allowance(self) -> None:
        """All levels carry EDR 10.33 fixed allowance (separate from minimo)."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        for lv in ccnl.levels:
            edr = next((fa for fa in lv.fixed_allowances if fa.code == "EDR"), None)
            assert edr is not None
            assert edr.monthly.periods[0].value == Decimal("10.33")

    def test_gas_acqua_utilitalia_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert ccnl.ccnl.tax_sector == TaxSector.INDUSTRIA

    def test_gas_acqua_utilitalia_seniority_cadence(self) -> None:
        """Seniority abolished 2015: cadence 24 months, maximum_count 0."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 0


class TestLoadUnebaUneba:
    """CCNL Istituzioni Socio-Assistenziali UNEBA (T141) data-layer tests."""

    def test_uneba_uneba_loads(self) -> None:
        """Loads with id='uneba-uneba' and CNEL code T141."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert ccnl.ccnl.id == "uneba-uneba"
        assert ccnl.ccnl.cnel_code == "T141"

    def test_uneba_uneba_has_11_levels(self) -> None:
        """Contract has exactly 11 levels: Q, 1, 2, 3S, 3, 4S, 4, 5S, 5, 6S, 6."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3S", "3", "4S", "4", "5S", "5", "6S", "6"}

    def test_uneba_uneba_level_4s_salary_tranche1(self) -> None:
        """Level 4S (OSS) minimo at Oct 2024 tranche: EUR 1467.86."""
        ccnl = load_ccnl("uneba-uneba.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4S")
        assert lv.base_salary.periods[0].value == Decimal("1467.86")

    def test_uneba_uneba_level_4s_salary_tranche2(self) -> None:
        """Level 4S (OSS) minimo at Jul 2025 tranche: EUR 1517.86."""
        ccnl = load_ccnl("uneba-uneba.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4S")
        assert lv.base_salary.periods[1].value == Decimal("1517.86")

    def test_uneba_uneba_level_ordering(self) -> None:
        """Level Q has highest order; level 6 has lowest order."""
        ccnl = load_ccnl("uneba-uneba.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "Q"

    def test_uneba_uneba_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima, Art. 46)."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(14)

    def test_uneba_uneba_hourly_divisor(self) -> None:
        """Hourly divisor: 164 (38-hour week, Art. 50)."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert ccnl.parameters.hourly_divisor == 164

    def test_uneba_uneba_level_q_ind_fun_allowance(self) -> None:
        """Level Q carries IND_FUN allowance EUR 100.00/month (Art. 43)."""
        ccnl = load_ccnl("uneba-uneba.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "Q")
        ind_fun = next(fa for fa in lv.fixed_allowances if fa.code == "IND_FUN")
        assert ind_fun.monthly.periods[0].value == Decimal("100.00")

    def test_uneba_uneba_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert ccnl.ccnl.tax_sector == TaxSector.TERZIARIO

    def test_uneba_uneba_seniority_cadence(self) -> None:
        """Seniority: triennial (36 months), maximum 10 scatti (Art. 48)."""
        ccnl = load_ccnl("uneba-uneba.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadAcconciaturaesteticaConfartigianato:
    """Unit tests for CCNL Acconciatura ed Estetica Confartigianato (H515)."""

    def test_acconciatura_estetica_confartigianato_loads(self) -> None:
        """Loads with id='acconciatura-estetica-confartigianato', code H515."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert ccnl.ccnl.id == "acconciatura-estetica-confartigianato"
        assert ccnl.ccnl.cnel_code == "H515"

    def test_acconciatura_estetica_confartigianato_has_4_levels(self) -> None:
        """Contract has exactly 4 levels: 1, 2, 3, 4."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert len(ccnl.levels) == 4
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4"}

    def test_acconciatura_estetica_confartigianato_level3_salary_tranche1(self) -> None:
        """Level 3 minimo at May 2024 tranche: EUR 1379.00."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "3")
        assert lv.base_salary.periods[0].value == Decimal("1379.00")

    def test_acconciatura_estetica_confartigianato_level3_salary_tranche2(self) -> None:
        """Level 3 minimo at Jan 2025 tranche: EUR 1429.00."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "3")
        assert lv.base_salary.periods[1].value == Decimal("1429.00")

    def test_acconciatura_estetica_confartigianato_level_ordering(self) -> None:
        """Level 1 has highest order; level 4 has lowest order."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "4"
        assert by_order[-1].code == "1"

    def test_acconciatura_estetica_confartigianato_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only, Art. 40)."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_acconciatura_estetica_confartigianato_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (40-hour week, Art. 12)."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_acconciatura_estetica_confartigianato_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (conglobated salary model)."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_acconciatura_estetica_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert ccnl.ccnl.tax_sector == TaxSector.ARTIGIANATO

    def test_acconciatura_estetica_confartigianato_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadPanificazioneArtigianatoConfartigianato:
    """Tests for CCNL Panificazione Artigianato (E015)."""

    def test_panificazione_artigianato_confartigianato_loads(self) -> None:
        """Loads with id='panificazione-artigianato-confartigianato', code E015."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert ccnl.ccnl.id == "panificazione-artigianato-confartigianato"
        assert ccnl.ccnl.cnel_code == "E015"

    def test_panificazione_artigianato_confartigianato_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: B4 A4 B3 B3S A3 B2 A2 A1 B1 A1S."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"B4", "A4", "B3", "B3S", "A3", "B2", "A2", "A1", "B1", "A1S"}

    def test_panificazione_artigianato_confartigianato_level_a2_salary_tranche1(
        self,
    ) -> None:
        """Level A2 TOTALE at Apr 2024 tranche: EUR 1788.61."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "A2")
        assert lv.base_salary.periods[0].value == Decimal("1788.61")

    def test_panificazione_artigianato_confartigianato_level_a2_salary_tranche2(
        self,
    ) -> None:
        """Level A2 TOTALE at Jan 2025 tranche: EUR 1828.61."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "A2")
        assert lv.base_salary.periods[1].value == Decimal("1828.61")

    def test_panificazione_artigianato_confartigianato_level_ordering(self) -> None:
        """Level A1S has highest order; level B4 has lowest order."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "B4"
        assert by_order[-1].code == "A1S"

    def test_panificazione_artigianato_confartigianato_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only; Art. 33 ter replaced 14th)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_panificazione_artigianato_confartigianato_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (40-hour work week)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert ccnl.parameters.hourly_divisor == 173

    def test_panificazione_artigianato_confartigianato_no_fixed_allowances(
        self,
    ) -> None:
        """All levels have empty fixed_allowances (unified TOTALE model)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_panificazione_artigianato_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert ccnl.ccnl.tax_sector == TaxSector.ARTIGIANATO

    def test_panificazione_artigianato_confartigianato_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti (Art. 34-bis)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadAutoferrotranvieriInternavigatori:
    """Tests for CCNL Autoferrotranvieri e Internavigatori (I022)."""

    def test_autoferrotranvieri_internavigatori_loads(self) -> None:
        """Contract id is autoferrotranvieri-internavigatori, CNEL code I022."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert ccnl.ccnl.id == "autoferrotranvieri-internavigatori"
        assert ccnl.ccnl.cnel_code == "I022"

    def test_autoferrotranvieri_internavigatori_has_33_levels(self) -> None:
        """Contract has exactly 33 levels (parametri 100 to 250)."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert len(ccnl.levels) == 33
        codes = {lv.code for lv in ccnl.levels}
        assert "100" in codes
        assert "175" in codes
        assert "250" in codes

    def test_autoferrotranvieri_internavigatori_level175_salary_tranche1(
        self,
    ) -> None:
        """Par.175 TOTALE at Dec 2024 (period 1): EUR 1805.57."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "175")
        assert lv.base_salary.periods[0].value == Decimal("1805.57")

    def test_autoferrotranvieri_internavigatori_level175_salary_tranche2(
        self,
    ) -> None:
        """Par.175 TOTALE at Mar 2025 (+60 EUR tabellare): EUR 1865.57."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "175")
        assert lv.base_salary.periods[1].value == Decimal("1865.57")

    def test_autoferrotranvieri_internavigatori_level_ordering(self) -> None:
        """Par.100 has lowest order; par.250 has highest order."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "100"
        assert by_order[-1].code == "250"

    def test_autoferrotranvieri_internavigatori_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(14)

    def test_autoferrotranvieri_internavigatori_hourly_divisor(self) -> None:
        """Hourly divisor: 195 (CCNL Art. 15 formula, 39h/week / 6 days)."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert ccnl.parameters.hourly_divisor == 195

    def test_autoferrotranvieri_internavigatori_edr_allowance(self) -> None:
        """Each level has one fixed_allowance (edr_2024); par.175 = 40.00."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "edr_2024"
        lv175 = next(lx for lx in ccnl.levels if lx.code == "175")
        edr = lv175.fixed_allowances[0].monthly
        active = next(
            p
            for p in edr.periods
            if p.valid_until is not None and p.valid_from.year == 2025
        )
        assert active.value == Decimal("40.00")

    def test_autoferrotranvieri_internavigatori_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert ccnl.ccnl.tax_sector == TaxSector.TERZIARIO

    def test_autoferrotranvieri_internavigatori_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 6 scatti."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 6
