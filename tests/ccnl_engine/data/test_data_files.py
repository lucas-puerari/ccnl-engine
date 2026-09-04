"""Tests for CCNL data loaders and bundled data files."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.engine.compute import ComputeRequest, compute
from ccnl_engine.models.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.models.ccnl import CCNL, TaxSector
from ccnl_engine.models.employment import Apprentice
from ccnl_engine.tax.loaders import load_year_rules
from ccnl_engine.tax.models import YearRules

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
        assert ccnl.meta.id


# ---------------------------------------------------------------------------
# load_ccnl helper
# ---------------------------------------------------------------------------


class TestLoadCcnl:
    """Unit tests for the load_ccnl helper."""

    def test_commercio_loads(self) -> None:
        """load_ccnl loads the commercio JSON and returns a CCNL instance."""
        ccnl = load_ccnl("commercio-confcommercio.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.id == "commercio-confcommercio"
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
        """A year with no data file must raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_year_rules(1900, TaxSector.TERZIARIO, 50)


# ---------------------------------------------------------------------------
# CCNL Metalmeccanico Federmeccanica
# ---------------------------------------------------------------------------


class TestLoadMetalmeccanico:
    """Unit tests for the bundled Metalmeccanico data file."""

    def test_metalmeccanico_loads(self) -> None:
        """File parses, id and cnel_code are correct."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.id == "metalmeccanico-federmeccanica"
        assert ccnl.meta.cnel_code == "C011"

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

    def test_metalmeccanico_federmeccanica_pre_2024_salary(self) -> None:
        """Base salary available from Jun 2021 (all 4 pre-2025 tranches present).

        D1 values from lexplain.it (cross-verified: Jun 2024 = 1719.67 matches
        the known value exactly): Jun-2021=1488.89, Jun-2022=1509.07, Jun-2023=1608.67.
        """
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        d1 = next(lv for lv in ccnl.levels if lv.code == "D1")
        assert d1.base_salary.value_at(date(2021, 6, 1)) == Decimal("1488.89")
        assert d1.base_salary.value_at(date(2022, 6, 1)) == Decimal("1509.07")
        assert d1.base_salary.value_at(date(2023, 6, 1)) == Decimal("1608.67")
        assert d1.base_salary.value_at(date(2024, 6, 1)) == Decimal("1719.67")

    def test_metalmeccanico_federmeccanica_apprenticeship_tracks(self) -> None:
        """Three percentage tracks (85/90/95/100%) at 36, 30, 24 months."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        # All eligible levels in 36m and 30m tracks
        elig = {"D2", "C1", "C2", "C3", "B1", "B2", "B3"}
        assert set(by_name["professionalizzante_36"].destination_levels) == elig
        assert set(by_name["professionalizzante_30"].destination_levels) == elig
        # 24m track is D2-only
        assert by_name["professionalizzante_24"].destination_levels == ["D2"]
        # All tracks have 85/90/95/100% progression
        for track in ccnl.apprenticeship:
            pcts = [p.percentage for p in track.periods]  # type: ignore[union-attr]
            assert pcts[0] == Decimal("0.85")
            assert pcts[1] == Decimal("0.90")
            assert pcts[2] == Decimal("0.95")
            assert pcts[3] == Decimal("1.00")
            assert track.periods[-1].months_until is None


# ---------------------------------------------------------------------------
# CCNL Metalmeccanico Confapi (Piccola Industria)
# ---------------------------------------------------------------------------


class TestLoadMetalmeccanicoConfapi:
    """Unit tests for the bundled Metalmeccanico Confapi (PMI) data file."""

    def test_confapi_loads(self) -> None:
        """File parses, id and cnel_code are correct."""
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.id == "metalmeccanico-confapi"
        assert ccnl.meta.cnel_code == "C018"

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
        """Apprenticeship uses under-classification (Art. 10 CCNL), not percentage.

        Eligible destinations: levels 3-9 (categories 3a-9a). Levels 1 and 2
        are not eligible (Art. 10, rinnovo 26/05/2021). Three equal-length
        periods (12+12+12 for 36m): 2 levels below / 1 level below / destination pay.
        """
        ccnl = load_ccnl("metalmeccanico-confapi.json")
        track = ccnl.apprenticeship[0]
        assert isinstance(track, ApprenticeshipUnderClassification)
        assert track.destination_levels == ["3", "4", "5", "6", "7", "8", "9"]
        periods = track.periods
        assert len(periods) == 3
        assert periods[0].levels_below == 2
        assert periods[1].levels_below == 1
        assert periods[2].levels_below == 0

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
        assert ccnl.meta.id == "chimica-farmaceutica-federchimica"
        assert ccnl.meta.cnel_code == "B011"

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
        """Single UC track covers E3-B1 (10 dest); 2 below → 1 below."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        assert len(ccnl.apprenticeship) == 1
        track = ccnl.apprenticeship[0]
        assert isinstance(track, ApprenticeshipUnderClassification)
        assert track.name == "professionalizzante"
        eligible = {
            "E3",
            "E2",
            "E1",
            "D3",
            "D2",
            "D1",
            "C2",
            "C1",
            "B2",
            "B1",
        }
        assert set(track.destination_levels) == eligible
        assert len(track.periods) == 2
        assert track.periods[0].levels_below == 2
        assert track.periods[0].months_until == 18
        assert track.periods[1].levels_below == 1
        assert track.periods[1].months_until is None

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(175)


# ---------------------------------------------------------------------------
# CCNL Turismo — Confcommercio (H052)
# ---------------------------------------------------------------------------


class TestLoadTurismoConfcommercio:
    """Structural and data-integrity tests for turismo-confcommercio.json."""

    def test_turismo_loads(self) -> None:
        """File must parse without errors; id and CNEL code must match."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert ccnl.meta.id == "turismo-confcommercio"
        assert ccnl.meta.cnel_code == "H052"

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
        """Apprenticeship uses percentage model: 80/85/90/100% (rinnovo 2024).

        The 36-month track covers levels 5, 4, 3, 2, 6S (4 periods including
        open-ended 100% at month 36+); the 24-month track covers level 6.
        """
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipPercentage)
        assert ccnl.apprenticeship[0].destination_levels == ["5", "4", "3", "2", "6S"]
        periods = ccnl.apprenticeship[0].periods
        assert len(periods) == 4
        assert periods[0].percentage == Decimal("0.80")
        assert periods[1].percentage == Decimal("0.85")
        assert periods[2].percentage == Decimal("0.90")
        assert periods[3].percentage == Decimal("1.00")
        assert periods[3].months_until is None

    def test_turismo_hourly_divisor(self) -> None:
        """Hourly divisor must be 172 (40 h/week standard for turismo)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(172)


# ---------------------------------------------------------------------------
# CCNL Edilizia — ANCE (F012)
# ---------------------------------------------------------------------------


class TestLoadEdiliziaAnce:
    """Structural and data-integrity tests for edilizia-ance.json."""

    def test_edilizia_loads(self) -> None:
        """load_ccnl loads the edilizia JSON and returns the expected identifiers."""
        ccnl = load_ccnl("edilizia-ance.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.id == "edilizia-ance"
        assert ccnl.meta.cnel_code == "F012"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

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
        assert ccnl.meta.tax_sector == TaxSector.EDILIZIA

    def test_edilizia_seniority_cadence(self) -> None:
        """Seniority increments must be biennale (24 months), max 5 scatti."""
        ccnl = load_ccnl("edilizia-ance.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_edilizia_apprenticeship_standard_percentage(self) -> None:
        """Apprenticeship: 1 track, levels 2-7, percentage 72/72/78/78/85/90/100%.

        Since CNCE n.660/2019 the CCNL abolished under-classification and uses
        percentage-based pay on the destination level for all levels 2-7 over 36 months
        (6 semesters at 72/72/78/78/85/90%, then 100%). Level 1 is not eligible.
        """
        ccnl = load_ccnl("edilizia-ance.json")
        assert len(ccnl.apprenticeship) == 1
        track = ccnl.apprenticeship[0]
        assert isinstance(track, ApprenticeshipPercentage)
        assert track.name == "standard"
        assert set(track.destination_levels) == {"2", "3", "4", "5", "6", "7"}
        pcts = [p.percentage for p in track.periods]
        assert pcts[:6] == [
            Decimal("0.72"),
            Decimal("0.72"),
            Decimal("0.78"),
            Decimal("0.78"),
            Decimal("0.85"),
            Decimal("0.90"),
        ]
        assert pcts[-1] == Decimal("1.00")
        assert track.periods[-1].months_until is None


# ---------------------------------------------------------------------------
# CCNL Cooperative Sociali — T151
# ---------------------------------------------------------------------------


class TestLoadCooperativeSociali:
    """Unit tests for CCNL Cooperative Sociali (T151) data file."""

    def test_cooperative_sociali_loads(self) -> None:
        """File loads as valid CCNL with correct id and CNEL code T151."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.id == "cooperative-sociali"
        assert ccnl.meta.cnel_code == "T151"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(165)

    def test_cooperative_sociali_q_levels_funzione_allowance(self) -> None:
        """E2Q/F1Q/F2Q must carry exactly one IDF fixed allowance each."""
        ccnl = load_ccnl("cooperative-sociali.json")
        expected = {"E2Q": "77.47", "F1Q": "154.94", "F2Q": "232.41"}
        for code, amount in expected.items():
            lv = next(lvl for lvl in ccnl.levels if lvl.code == code)
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "IND_FUN"
            val = lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1))
            assert val == Decimal(amount)

    def test_cooperative_sociali_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_cooperative_sociali_seniority_cadence(self) -> None:
        """Seniority increments: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("cooperative-sociali.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_cooperative_sociali_apprenticeship_three_tracks(self) -> None:
        """Three tracks by category duration: 18m (A2), 24m (B/C), 36m (D/E)."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        # 18m track: A2 only, split at 9m
        t18 = by_name["professionalizzante_18m"]
        assert t18.destination_levels == ["A2"]
        assert t18.periods[0].months_until == 9
        assert t18.periods[0].percentage == Decimal("0.85")  # type: ignore[union-attr]
        # 24m track: B, C1, C2, C3
        t24 = by_name["professionalizzante_24m"]
        assert set(t24.destination_levels) == {"B", "C1", "C2", "C3"}
        assert t24.periods[0].months_until == 12
        # 36m track: D and E levels
        t36 = by_name["professionalizzante_36m"]
        assert set(t36.destination_levels) == {"D1", "D2", "D3", "E1", "E2"}
        assert t36.periods[0].months_until == 18
        assert t36.periods[-1].months_until is None


class TestLoadLogisticaTrasportoConfetra:
    """Tests for CCNL Logistica, Trasporto Merci e Spedizione (I100)."""

    def test_logistica_trasporto_confetra_loads(self) -> None:
        """CCNL id must be logistica-trasporto-confetra, CNEL code I100."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert ccnl.meta.id == "logistica-trasporto-confetra"
        assert ccnl.meta.cnel_code == "I100"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(168)

    def test_logistica_trasporto_confetra_no_fixed_allowances(self) -> None:
        """All levels must have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_logistica_trasporto_confetra_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_logistica_trasporto_confetra_seniority_cadence(self) -> None:
        """Seniority increments: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_logistica_trasporto_confetra_apprenticeship_all_levels(self) -> None:
        """Single track covers levels 1-6, 3S, 4J at 75/85/100%."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert len(ccnl.apprenticeship) == 1
        track = ccnl.apprenticeship[0]
        assert track.name == "standard"
        assert set(track.destination_levels) == {
            "1",
            "2",
            "3",
            "3S",
            "4",
            "4J",
            "5",
            "6",
        }
        pcts = [p.percentage for p in track.periods]  # type: ignore[union-attr]
        assert pcts[0] == Decimal("0.75")
        assert pcts[1] == Decimal("0.85")
        assert pcts[2] == Decimal("1.00")
        assert track.periods[-1].months_until is None


class TestLoadMultiserviziAnip:
    """Tests for CCNL Multiservizi K511 (ANIP-Confindustria) data file."""

    def test_multiservizi_anip_loads(self) -> None:
        """File must load and carry the correct id and CNEL code."""
        ccnl = load_ccnl("multiservizi-anip.json")
        assert ccnl.meta.id == "multiservizi-anip"
        assert ccnl.meta.cnel_code == "K511"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_multiservizi_anip_split_model_allowances(self) -> None:
        """Split model: every level must have contingenza and EDR allowances."""
        ccnl = load_ccnl("multiservizi-anip.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "CONTINGENZA" in codes, f"level {lv.code} missing CONTINGENZA"
            assert "EDR" in codes, f"level {lv.code} missing EDR"

    def test_multiservizi_anip_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO (CNEL K-prefix contract)."""
        ccnl = load_ccnl("multiservizi-anip.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

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
        assert ccnl.meta.id == "studi-professionali-confprofessioni"
        assert ccnl.meta.cnel_code == "H442"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(170)

    def test_studi_professionali_confprofessioni_no_fixed_allowances(
        self,
    ) -> None:
        """Conglobated model: standard levels have no unconditional allowances.

        Levels 1, 2, 3S carry the ENAC role-scoped allowance (role
        'confedertecnica_pre_2004', Art. 141) which is excluded here.
        """
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        for lv in ccnl.levels:
            unconditional = [a for a in lv.fixed_allowances if a.role is None]
            assert unconditional == [], f"level {lv.code} has unconditional allowances"

    def test_studi_professionali_confprofessioni_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO (CNEL H-prefix contract)."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

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
        assert ccnl.meta.id == "bancari-abi"
        assert ccnl.meta.cnel_code == "J241"

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
        """Hourly divisor: 162 until 2024-07-01, then 160 (37h/week rinnovo 2024)."""
        ccnl = load_ccnl("bancari-abi.json")
        divisor = ccnl.parameters.hourly_divisor
        assert len(divisor.periods) == 2
        assert divisor.periods[0].value == Decimal(162)
        assert divisor.periods[1].value == Decimal(160)

    def test_bancari_abi_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels must have no fixed allowances."""
        ccnl = load_ccnl("bancari-abi.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == [], f"level {lv.code} has allowances"

    def test_bancari_abi_tax_sector(self) -> None:
        """CCNL must declare tax_sector CREDITO (ABI banking sector)."""
        ccnl = load_ccnl("bancari-abi.json")
        assert ccnl.meta.tax_sector == TaxSector.CREDITO

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
        assert ccnl.meta.id == "tessile-smi"
        assert ccnl.meta.cnel_code == "D014"

    def test_tessile_smi_has_10_levels(self) -> None:
        """10 livelli: 1, 2, 2S, 3, 3S, 4, 5, 6, 7, 8."""
        ccnl = load_ccnl("tessile-smi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 10
        assert codes == {"1", "2", "2S", "3", "3S", "4", "5", "6", "7", "8"}

    def test_tessile_smi_level4_salary_tranche1(self) -> None:
        """Level 4 Nov 2024 ERN (pre-Dec 2024): 1786.95 EUR (lexplain.it)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        val = level.base_salary.value_at(date(2024, 11, 15))
        assert val == Decimal("1786.95")

    def test_tessile_smi_level4_salary_tranche_dec2024(self) -> None:
        """Level 4 Dec 2024 ERN: 1881.95 EUR (+95 tranche, proportionally derived)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        val = level.base_salary.value_at(date(2025, 6, 1))
        assert val == Decimal("1881.95")

    def test_tessile_smi_level4_salary_tranche_jan2026(self) -> None:
        """Level 4 Jan 2026 ERN: 1938.95 EUR (kitech.it)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        val = level.base_salary.value_at(date(2026, 1, 1))
        assert val == Decimal("1938.95")

    def test_tessile_smi_level1_salary_dec2024(self) -> None:
        """Level 1 Dec 2024 ERN: 1401.94 EUR (proportionally derived from +95 at L4)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "1")
        val = level.base_salary.value_at(date(2025, 1, 1))
        assert val == Decimal("1401.94")

    def test_tessile_smi_level8_salary_dec2024(self) -> None:
        """Level 8 Dec 2024 ERN: 2385.33 EUR (proportionally derived, +120.65)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "8")
        val = level.base_salary.value_at(date(2025, 1, 1))
        assert val == Decimal("2385.33")

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

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
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_tessile_smi_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 4 scatti."""
        ccnl = load_ccnl("tessile-smi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 4

    def test_tessile_smi_apprenticeship_tracks(self) -> None:
        """7 UC apprenticeship tracks; prof_L6_L8 covers levels 6, 7, 8."""
        ccnl = load_ccnl("tessile-smi.json")
        assert len(ccnl.apprenticeship) == 7
        by_name = {t.name: t for t in ccnl.apprenticeship}
        assert set(by_name["prof_L6_L8"].destination_levels) == {"6", "7", "8"}
        # prof_L6_L8: 0-15m 2 below, 15-30m 1 below, 30m+ at destination
        t = by_name["prof_L6_L8"]
        assert t.periods[0].months_until == 15
        assert t.periods[0].levels_below == 2  # type: ignore[union-attr]
        assert t.periods[1].months_until == 30
        assert t.periods[1].levels_below == 1  # type: ignore[union-attr]
        assert t.periods[2].months_until is None
        assert t.periods[2].levels_below == 0  # type: ignore[union-attr]
        # prof_L2: 0-12m 1 below, 12m+ at destination
        t2 = by_name["prof_L2"]
        assert t2.destination_levels == ["2"]
        assert t2.periods[0].levels_below == 1  # type: ignore[union-attr]
        assert t2.periods[1].months_until is None

    def test_tessile_smi_level4_salary_jan2027(self) -> None:
        """Level 4 base salary from Jan 2027: EUR 1986.95."""
        ccnl = load_ccnl("tessile-smi.json")
        lv4 = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv4.base_salary.value_at(date(2027, 1, 1)) == Decimal("1986.95")


class TestLoadAlimentariFederalimentare:
    """Tests for CCNL Alimentari Industria — Federalimentare (E012)."""

    def test_alimentari_federalimentare_loads(self) -> None:
        """CCNL id == 'alimentari-federalimentare', cnel_code == 'E012'."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert ccnl.meta.id == "alimentari-federalimentare"
        assert ccnl.meta.cnel_code == "E012"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_alimentari_federalimentare_split_allowances(self) -> None:
        """Split model: every level has CONT, EDR, IAR allowances.

        Level 1S (quadro) additionally carries ind_funzione_quadro; the base
        three components must be present on all levels.
        """
        ccnl = load_ccnl("alimentari-federalimentare.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert {"CONTINGENZA", "EDR", "IAR"}.issubset(codes), (
                f"level {lv.code} missing base allowances: {codes}"
            )

    def test_alimentari_federalimentare_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_alimentari_federalimentare_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_alimentari_federalimentare_apprenticeship_type(self) -> None:
        """Apprenticeship: two UC tracks (36-month covering 1-4/3A; 24-month for 5).

        The 36-month track covers all levels where the full 3-period table
        applies: destinations 4, 3, 3A, 2, 1.
        """
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipUnderClassification)
        assert ccnl.apprenticeship[0].destination_levels == ["4", "3", "3A", "2", "1"]

    def test_alimentari_federalimentare_apprentice_under_classification(self) -> None:
        """Apprentice 5 months elapsed → under level 4 (period 0-9 months)."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        rules = load_year_rules(2026, TaxSector.INDUSTRIA, num_employees=50)
        result = compute(
            ccnl,
            rules,
            ComputeRequest(
                level_code="3A",
                as_of=date(2026, 1, 1),
                employment=Apprentice(months_elapsed=5),
            ),
        )
        assert result.apprenticeship_under_level_code == "4"
        assert result.apprenticeship_pct is None


class TestLoadDmoFederdistribuzione:
    """Tests for CCNL DMO Federdistribuzione (H008) data file."""

    def test_dmo_federdistribuzione_loads(self) -> None:
        """Loads dmo-federdistribuzione and verifies id and CNEL code H008."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        assert ccnl.meta.id == "dmo-federdistribuzione"
        assert ccnl.meta.cnel_code == "H008"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(168)

    def test_dmo_federdistribuzione_fixed_allowances_split(self) -> None:
        """Split model: all levels have contingenza and terzo_elemento_nazionale."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONTINGENZA" in codes, f"level {lv.code} missing CONTINGENZA"
            assert "TERZO_ELEMENTO_NAZIONALE" in codes, (
                f"level {lv.code} missing TERZO_ELEMENTO_NAZIONALE"
            )

    def test_dmo_federdistribuzione_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_dmo_federdistribuzione_seniority_cadence(self) -> None:
        """Seniority: triennale cadence (36 months), maximum 10 scatti."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10

    def test_dmo_federdistribuzione_apprenticeship_tracks(self) -> None:
        """Two UC tracks: standard_II_V (dest II-V, 18/18m) and standard_VI (12/12m)."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        assert len(ccnl.apprenticeship) == 2
        by_name = {t.name: t for t in ccnl.apprenticeship}
        t_ii_v = by_name["standard_II_V"]
        assert set(t_ii_v.destination_levels) == {"II", "III", "IV", "V"}
        assert t_ii_v.periods[0].levels_below == 2  # type: ignore[union-attr]
        assert t_ii_v.periods[0].months_until == 18
        assert t_ii_v.periods[1].levels_below == 1  # type: ignore[union-attr]
        assert t_ii_v.periods[1].months_until is None
        t_vi = by_name["standard_VI"]
        assert t_vi.destination_levels == ["VI"]
        assert t_vi.periods[0].levels_below == 1  # type: ignore[union-attr]
        assert t_vi.periods[0].months_until == 12
        assert t_vi.periods[1].levels_below == 0  # type: ignore[union-attr]
        assert t_vi.periods[1].months_until is None


class TestLoadMetalmeccanicoArtigianato:
    """Tests for CCNL Metalmeccanica Artigianato (Confartigianato/CNA, C030)."""

    def test_metalmeccanico_artigianato_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        assert ccnl.meta.id == "metalmeccanico-artigianato"
        assert ccnl.meta.cnel_code == "C030"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_metalmeccanico_artigianato_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have empty fixed_allowances."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_metalmeccanico_artigianato_tax_sector(self) -> None:
        """CCNL must declare tax_sector ARTIGIANATO."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_metalmeccanico_artigianato_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_metalmeccanico_artigianato_apprenticeship_impiegati(self) -> None:
        """Impiegati track: dest=[2,1], 3 years, 70/77/87/100%."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        by_name = {t.name: t for t in ccnl.apprenticeship}
        assert "impiegati" in by_name
        t = by_name["impiegati"]
        assert set(t.destination_levels) == {"2", "1"}
        pcts = [p.percentage for p in t.periods]  # type: ignore[union-attr]
        assert pcts == [
            Decimal("0.70"),
            Decimal("0.77"),
            Decimal("0.87"),
            Decimal("1.00"),
        ]
        assert t.periods[-1].months_until is None


class TestLoadGommaPlasticaFederazioneGommaPlastica:
    """Tests for CCNL Gomma e Plastica Industria (Federazione Gomma Plastica, B371)."""

    def test_gomma_plastica_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        assert ccnl.meta.id == "gomma-plastica-federazione-gomma-plastica"
        assert ccnl.meta.cnel_code == "B371"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

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
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_gomma_plastica_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_gomma_plastica_seniority_amounts_pre_2026(self) -> None:
        """Seniority amounts are the same before and after the 2026 rinnovo.

        The December 2025 rinnovo left Art.23 (scatti) untouched, so the amounts
        at 01.01.2023 equal those at 01.01.2026. Level F amount confirmed 13.94 EUR.
        """
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        si = ccnl.parameters.seniority_increments
        assert si.amount_by_level is not None
        f_amount_2023 = si.amount_by_level["F"].value_at(date(2023, 1, 1))
        f_amount_2026 = si.amount_by_level["F"].value_at(date(2026, 1, 1))
        assert f_amount_2023 == f_amount_2026
        assert f_amount_2023 == Decimal("13.94")


class TestLoadGraficaEditoriaAieg:
    """Tests for CCNL Grafica e Editoria Industria (AIEG-Acigraf, G011)."""

    def test_grafica_editoria_aieg_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert ccnl.meta.id == "grafica-editoria-aieg"
        assert ccnl.meta.cnel_code == "G011"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_grafica_editoria_aieg_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (total modelled as base_salary)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_grafica_editoria_aieg_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_grafica_editoria_aieg_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_grafica_editoria_aieg_apprenticeship_tracks(self) -> None:
        """Two apprenticeship tracks per CCNL 19/01/2021 Art.26e (pag.42).

        Triennale (36m, gruppi C/B/A/Q): 6 semestri 70/75/80/85/90/95/100%.
        Biennale (24m, gruppo D): 6 quadrimestri (4m) 70/75/80/85/90/95/100%.
        Level E is not eligible (not cited in CCNL apprenticeship provisions).
        """
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert len(ccnl.apprenticeship) == 2
        by_name = {t.name: t for t in ccnl.apprenticeship}

        tri = by_name["triennale"]
        assert isinstance(tri, ApprenticeshipPercentage)
        assert set(tri.destination_levels) == {
            "C2",
            "C1",
            "B3",
            "B2",
            "B1",
            "B1S",
            "A",
            "AS",
            "Q",
        }
        assert len(tri.periods) == 7  # 6 semestri + open 100%
        assert tri.periods[0].months_until == 6
        assert tri.periods[0].percentage == Decimal("0.70")
        assert tri.periods[5].months_until == 36
        assert tri.periods[5].percentage == Decimal("0.95")
        assert tri.periods[-1].months_until is None

        bi = by_name["biennale"]
        assert isinstance(bi, ApprenticeshipPercentage)
        assert set(bi.destination_levels) == {"D2", "D1"}
        assert len(bi.periods) == 7  # 6 quadrimestri (4m) + open 100%
        assert bi.periods[0].months_until == 4
        assert bi.periods[0].percentage == Decimal("0.70")
        assert bi.periods[5].months_until == 24
        assert bi.periods[5].percentage == Decimal("0.95")
        assert bi.periods[-1].months_until is None


class TestLoadCartaCartoneAssocarta:
    """Tests for CCNL Carta e Cartone Industria (Assocarta, CNEL G022)."""

    def test_carta_cartone_assocarta_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        assert ccnl.meta.id == "carta-cartone-assocarta"
        assert ccnl.meta.cnel_code == "G022"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_carta_cartone_assocarta_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_carta_cartone_assocarta_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

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
        assert ccnl.meta.id == "telecomunicazioni-asstel"
        assert ccnl.meta.cnel_code == "K411"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

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
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_telecomunicazioni_asstel_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 7 scatti."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 7

    def test_telecomunicazioni_asstel_apprenticeship_under_classification(
        self,
    ) -> None:
        """Apprenticeship: under_classification covering levels B1, B2, C1, C2, C3."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipUnderClassification)
        expected = ["B1", "B2", "C1", "C2", "C3"]
        assert ccnl.apprenticeship[0].destination_levels == expected


class TestLoadVigilanzaPrivataAssiv:
    """Unit tests for CCNL Vigilanza Privata ASSIV (HV40, GPG section)."""

    def test_vigilanza_privata_assiv_loads(self) -> None:
        """Contract loads with correct id and CNEL code HV40."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert ccnl.meta.id == "vigilanza-privata-assiv"
        assert ccnl.meta.cnel_code == "HV40"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_vigilanza_privata_assiv_no_fixed_allowances(self) -> None:
        """All GPG levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_vigilanza_privata_assiv_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector (non-Confindustria)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_vigilanza_privata_assiv_seniority_cadence(self) -> None:
        """Seniority: triennale cadence (36 months), maximum 6 scatti."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 6

    def test_vigilanza_privata_assiv_apprenticeship_percentage(self) -> None:
        """Apprenticeship: percentage type, destination levels 6-1 (all GPG)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipPercentage)
        expected = ["6", "5", "4", "3", "2", "1"]
        assert ccnl.apprenticeship[0].destination_levels == expected
        assert ccnl.apprenticeship[0].periods[0].percentage == Decimal("1.00")


class TestLoadLegnoArredamentoFederlegno:
    """CCNL Legno e Arredamento Industria (Federlegno-Arredo, CNEL F051)."""

    def test_legno_arredamento_federlegno_loads(self) -> None:
        """Contract loads with id='legno-arredamento-federlegno', code F051."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert ccnl.meta.id == "legno-arredamento-federlegno"
        assert ccnl.meta.cnel_code == "F051"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(174)

    def test_legno_arredamento_federlegno_fixed_allowances_split(self) -> None:
        """All levels carry CONTINGENZA and EDR allowances (split salary model)."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
            assert "EDR" in codes

    def test_legno_arredamento_federlegno_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_legno_arredamento_federlegno_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_legno_arredamento_federlegno_apprenticeship_under(self) -> None:
        """Apprenticeship: 6 under_classification tracks covering all areas.

        Track 0 (professionalizzante_1) covers AE3 and AE4 (Esecutivo area).
        Track 3 (professionalizzante_4) covers AS3 and AC3.
        """
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert len(ccnl.apprenticeship) == 6
        assert all(
            isinstance(t, ApprenticeshipUnderClassification)
            for t in ccnl.apprenticeship
        )
        assert ccnl.apprenticeship[0].destination_levels == ["AE3", "AE4"]
        # Track 3 covers the Specializzato area including AS3
        assert "AS3" in ccnl.apprenticeship[3].destination_levels


class TestLoadEdiliziaArtigianatoCna:
    """CCNL Edilizia Artigianato (CNA/Confartigianato/Casartigiani, F015)."""

    def test_edilizia_artigianato_cna_loads(self) -> None:
        """Contract loads and reports correct id and CNEL code."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert ccnl.meta.id == "edilizia-artigianato-cna"
        assert ccnl.meta.cnel_code == "F015"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_edilizia_artigianato_cna_fixed_allowances_split(self) -> None:
        """All levels carry CONTINGENZA and EDR allowances (split salary model)."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
            assert "EDR" in codes

    def test_edilizia_artigianato_cna_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_edilizia_artigianato_cna_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_edilizia_artigianato_cna_apprenticeship_percentage(self) -> None:
        """Apprenticeship: Gruppo 4 track; 7 periods (6 semestri + open 100%).

        Gruppo 4 track has 6 increasing-percentage semesters then an open-ended
        destination period at 100%.  Two tracks exist: standard_gruppo_4 (dest 4)
        and standard_gruppi_1_3 (dest 3, 4, 5).
        """
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipPercentage)
        assert ccnl.apprenticeship[0].destination_levels == ["4"]
        assert len(ccnl.apprenticeship[0].periods) == 7
        assert ccnl.apprenticeship[0].periods[0].percentage == Decimal("0.74")
        assert ccnl.apprenticeship[0].periods[-1].percentage == Decimal("1.00")

    def test_edilizia_artigianato_cna_specialistico_tracks(self) -> None:
        """Apprenticeship specialistico tracks (Allegato D, verbale 05/09/2023, Art.9).

        Track 1Sp (54m, livelli 4-5): 78/80/86/91/96/96/100%.
        Track 2Sp (45m, livelli 3-4): 78/80/86/91/96/100% (last period 3m, SIMPLIF.).
        Track 3Sp (42m, livello 3):   78/80/86/91/100%.
        """
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert len(ccnl.apprenticeship) == 5  # 2 standard + 3 specialistico
        by_name = {t.name: t for t in ccnl.apprenticeship}

        sp1 = by_name["specialistico_1sp"]
        assert set(sp1.destination_levels) == {"4", "5"}
        assert isinstance(sp1, ApprenticeshipPercentage)
        assert len(sp1.periods) == 7  # 6 active + open 100%
        assert sp1.periods[0].percentage == Decimal("0.78")
        assert sp1.periods[4].percentage == Decimal("0.96")
        assert sp1.periods[5].months_until == 54
        assert sp1.periods[-1].months_until is None

        sp2 = by_name["specialistico_2sp"]
        assert set(sp2.destination_levels) == {"3", "4"}
        assert isinstance(sp2, ApprenticeshipPercentage)
        assert sp2.periods[-2].months_until == 45  # last active period ends at 45m

        sp3 = by_name["specialistico_3sp"]
        assert sp3.destination_levels == ["3"]
        assert isinstance(sp3, ApprenticeshipPercentage)
        assert len(sp3.periods) == 5  # 4 active + open 100%
        assert sp3.periods[3].percentage == Decimal("0.91")
        assert sp3.periods[3].months_until == 42


class TestLoadGasAcquaUtilitalia:
    """Tests for CCNL Gas e Acqua — Utilitalia/Proxigas/Anfida (K321)."""

    def test_gas_acqua_utilitalia_loads(self) -> None:
        """Contract loads with id='gas-acqua-utilitalia' and CNEL K321."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert ccnl.meta.id == "gas-acqua-utilitalia"
        assert ccnl.meta.cnel_code == "K321"

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
        assert lv.base_salary.value_at(date(2024, 9, 1)) == Decimal("2204.68")

    def test_gas_acqua_utilitalia_jul2025_tranche(self) -> None:
        """Level 1 at Jul 2025 tranche (parametric, 90:60 ratio)."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "1")
        assert lv.base_salary.value_at(date(2025, 7, 1)) == Decimal("1740.34")

    def test_gas_acqua_utilitalia_q_ind_fun_months_per_year(self) -> None:
        """Q indennita di funzione is paid 12 months per year (Art. 2.1)."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        lv_q = next(lx for lx in ccnl.levels if lx.code == "Q")
        ind_fun = next(fa for fa in lv_q.fixed_allowances if fa.code == "IND_FUN")
        assert ind_fun.months_per_year == 12

    def test_gas_acqua_utilitalia_apprenticeship_tracks(self) -> None:
        """Three per-duration tracks: professionalizzante_24/30/36."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert len(ccnl.apprenticeship) == 3
        names = {t.name for t in ccnl.apprenticeship}
        assert names == {
            "professionalizzante_24",
            "professionalizzante_30",
            "professionalizzante_36",
        }
        t24 = ccnl.apprenticeship_track_named("professionalizzante_24")
        assert set(t24.destination_levels) == {"7", "8"}
        t36 = ccnl.apprenticeship_track_named("professionalizzante_36")
        assert t36.destination_levels == ["3"]

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(167)

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
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

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
        assert ccnl.meta.id == "uneba-uneba"
        assert ccnl.meta.cnel_code == "T141"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(164)

    def test_uneba_uneba_level_q_ind_fun_allowance(self) -> None:
        """Level Q carries IND_FUN allowance EUR 100.00/month (Art. 43)."""
        ccnl = load_ccnl("uneba-uneba.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "Q")
        ind_fun = next(fa for fa in lv.fixed_allowances if fa.code == "IND_FUN")
        assert ind_fun.monthly.periods[0].value == Decimal("100.00")

    def test_uneba_uneba_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

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
        assert ccnl.meta.id == "acconciatura-estetica-confartigianato"
        assert ccnl.meta.cnel_code == "H515"

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
        assert lv.base_salary.value_at(date(2024, 5, 1)) == Decimal("1379.00")

    def test_acconciatura_estetica_confartigianato_level3_salary_tranche2(self) -> None:
        """Level 3 minimo at Jan 2025 tranche: EUR 1429.00."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "3")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1429.00")

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_acconciatura_estetica_confartigianato_no_fixed_allowances(self) -> None:
        """All levels have no unconditional allowances (conglobated salary model).

        Levels 1 and 2 carry the role-scoped Responsabile Tecnico allowance
        (role='responsabile_tecnico'), which is excluded from this check.
        """
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        for lv in ccnl.levels:
            unconditional = [a for a in lv.fixed_allowances if a.role is None]
            assert unconditional == [], f"level {lv.code} has unconditional allowances"

    def test_acconciatura_estetica_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_acconciatura_estetica_confartigianato_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_acconciatura_estetica_confartigianato_gruppo3_apprenticeship(
        self,
    ) -> None:
        """Gruppo 3 track: dest=['2'], 6 semestri, 70/70/70/78/85/85."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        track = next(t for t in ccnl.apprenticeship if t.name == "gruppo_3")
        assert track.destination_levels == ["2"]
        assert len(track.periods) == 6
        pcts = [p.percentage for p in track.periods]  # type: ignore[union-attr]
        assert pcts == [
            Decimal("0.70"),
            Decimal("0.70"),
            Decimal("0.70"),
            Decimal("0.78"),
            Decimal("0.85"),
            Decimal("0.85"),
        ]
        assert track.periods[-1].months_until is None


class TestLoadPanificazioneArtigianatoConfartigianato:
    """Tests for CCNL Panificazione Artigianato (E015)."""

    def test_panificazione_artigianato_confartigianato_loads(self) -> None:
        """Loads with id='panificazione-artigianato-confartigianato', code E015."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert ccnl.meta.id == "panificazione-artigianato-confartigianato"
        assert ccnl.meta.cnel_code == "E015"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

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
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_panificazione_artigianato_confartigianato_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti (Art. 34-bis)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_panificazione_artigianato_confartigianato_apprenticeship_tracks(
        self,
    ) -> None:
        """7 tracks total: gruppo_1 (existing) + 6 new (A2, A3, B1, B2, B3S, B3)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert len(ccnl.apprenticeship) == 7
        by_name = {t.name: t for t in ccnl.apprenticeship}
        # Existing gruppo 1 unchanged
        assert by_name["gruppo_1_panificatori"].destination_levels == ["A1"]
        # Gruppo A2: 54m, 6 periods
        t_a2 = by_name["gruppo_a2_panificatori"]
        assert t_a2.destination_levels == ["A2"]
        assert len(t_a2.periods) == 6
        assert t_a2.periods[0].percentage == Decimal("0.70")  # type: ignore[union-attr]
        assert t_a2.periods[-1].months_until is None
        # Gruppo B1: 36m, 4 periods (70/75/84/100)
        t_b1 = by_name["gruppo_b1_addetti"]
        assert t_b1.destination_levels == ["B1"]
        pcts_b1 = [p.percentage for p in t_b1.periods]  # type: ignore[union-attr]
        assert pcts_b1[2] == Decimal("0.84")


class TestLoadAutoferrotranvieriInternavigatori:
    """Tests for CCNL Autoferrotranvieri e Internavigatori (I022)."""

    def test_autoferrotranvieri_internavigatori_loads(self) -> None:
        """Contract id is autoferrotranvieri-internavigatori, CNEL code I022."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert ccnl.meta.id == "autoferrotranvieri-internavigatori"
        assert ccnl.meta.cnel_code == "I022"

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
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(195)

    def test_autoferrotranvieri_internavigatori_edr_allowance(self) -> None:
        """Each level has one fixed_allowance (edr_2024); par.175 = 40.00."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "EDR_2024"
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
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_autoferrotranvieri_internavigatori_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 6 scatti."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 6


class TestLoadBccCreditoCooperativo:
    """Tests for CCNL BCC Credito Cooperativo (J271)."""

    def test_bcc_credito_cooperativo_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert ccnl.meta.id == "bcc-credito-cooperativo"
        assert ccnl.meta.cnel_code == "J271"

    def test_bcc_credito_cooperativo_has_11_levels(self) -> None:
        """Contract has exactly 11 levels across QD and Aree Professionali."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 11
        assert codes == {
            "QD4",
            "QD3",
            "QD2",
            "QD1",
            "3AP4",
            "3AP3",
            "3AP2",
            "3AP1",
            "2AP2",
            "2AP1",
            "1AP",
        }

    def test_bcc_credito_cooperativo_level_3ap4_salary_tranche1(self) -> None:
        """3AP4 base salary at first tranche (2024-09-01): 3206.90."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "3AP4")
        p = next(x for x in lv.base_salary.periods if x.valid_from == date(2024, 9, 1))
        assert p.value == Decimal("3206.90")

    def test_bcc_credito_cooperativo_level_3ap4_salary_tranche3(self) -> None:
        """3AP4 base salary at third tranche (2026-01-01): 3341.90."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "3AP4")
        p = next(x for x in lv.base_salary.periods if x.valid_from == date(2026, 1, 1))
        assert p.value == Decimal("3341.90")

    def test_bcc_credito_cooperativo_level_ordering(self) -> None:
        """QD4 is highest-order level; 1AP is lowest-order level."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "1AP"
        assert by_order[-1].code == "QD4"

    def test_bcc_credito_cooperativo_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only per Art. 46)."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_bcc_credito_cooperativo_hourly_divisor(self) -> None:
        """Hourly divisor: 160 (Art. 114 formula, arrotondamento a 5)."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(160)

    def test_bcc_credito_cooperativo_no_fixed_allowances(self) -> None:
        """All levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_bcc_credito_cooperativo_tax_sector(self) -> None:
        """Contract declares CREDITO tax sector."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert ccnl.meta.tax_sector == TaxSector.CREDITO

    def test_bcc_credito_cooperativo_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months); global max 8 (AP area), QD* max 12."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 8
        for code in ("QD1", "QD2", "QD3", "QD4"):
            assert si.maximum_count_by_level[code] == 12

    def test_bcc_credito_cooperativo_apprenticeship_type(self) -> None:
        """Apprenticeship: under_classification track covers all 4 Terza Area levels."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert ccnl.apprenticeship
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipUnderClassification)
        assert ccnl.apprenticeship[0].destination_levels == [
            "3AP1",
            "3AP2",
            "3AP3",
            "3AP4",
        ]

    def test_bcc_credito_cooperativo_apprenticeship_periods(self) -> None:
        """Months 0-18 at 2AP-2° pay level, months 18+ at destination 3AP1."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipUnderClassification)
        periods = ccnl.apprenticeship[0].periods
        assert len(periods) == 2
        assert periods[0].months_from == 0
        assert periods[0].months_until == 18
        assert periods[0].levels_below == 1
        assert periods[1].months_from == 18
        assert periods[1].months_until is None
        assert periods[1].levels_below == 0

    def test_bcc_credito_cooperativo_apprentice_compute(self) -> None:
        """Apprentice 12 months elapsed → salary at 2AP2 level."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)
        result = compute(
            ccnl,
            rules,
            ComputeRequest(
                level_code="3AP1",
                as_of=date(2026, 6, 1),
                employment=Apprentice(months_elapsed=12),
            ),
        )
        # At 12 months, pay level is 2AP2 (under-classification)
        assert result.apprenticeship_under_level_code == "2AP2"
        assert result.gross_monthly > 0


class TestLoadElettricoElettricita:
    """Tests for CCNL Elettrico Elettricita Futura (K051)."""

    def test_elettrico_elettricita_futura_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        assert ccnl.meta.id == "elettrico-elettricita-futura"
        assert ccnl.meta.cnel_code == "K051"

    def test_elettrico_elettricita_futura_has_14_levels(self) -> None:
        """Contract has exactly 14 levels from C1 to QS."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 14
        assert codes == {
            "QS",
            "Q",
            "ASS",
            "AS",
            "A1S",
            "A1",
            "BSS",
            "BS",
            "B1S",
            "B1",
            "B2S",
            "B2",
            "CS",
            "C1",
        }

    def test_elettrico_elettricita_futura_level_a1_salary_tranche1(self) -> None:
        """A1 base salary at first tranche (2025-04-01): 2788.67."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "A1")
        p = next(x for x in lv.base_salary.periods if x.valid_from == date(2025, 4, 1))
        assert p.value == Decimal("2788.67")

    def test_elettrico_elettricita_futura_level_a1_salary_tranche2(self) -> None:
        """A1 base salary at second tranche (2026-04-01): 2851.16."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "A1")
        p = next(x for x in lv.base_salary.periods if x.valid_from == date(2026, 4, 1))
        assert p.value == Decimal("2851.16")

    def test_elettrico_elettricita_futura_level_ordering(self) -> None:
        """QS is highest-order level; C1 is lowest-order level."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "C1"
        assert by_order[-1].code == "QS"

    def test_elettrico_elettricita_futura_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(14)

    def test_elettrico_elettricita_futura_hourly_divisor(self) -> None:
        """Hourly divisor: 173.33 (40h/week, 40 x 52 / 12 rounded to 2 dp)."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal("173.33")

    def test_elettrico_elettricita_futura_edr_allowance(self) -> None:
        """Each level has one fixed_allowance (EDR) at 10.33 EUR/month."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "EDR"
            assert lv.fixed_allowances[0].monthly.periods[0].value == Decimal("10.33")

    def test_elettrico_elettricita_futura_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_elettrico_elettricita_futura_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadCalzaturieroAssocalzaturifici:
    """Tests for CCNL Calzaturiero Industria (D121)."""

    def test_calzaturiero_assocalzaturifici_loads(self) -> None:
        """CCNL loads with correct id and CNEL code D121."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert ccnl.meta.id == "calzaturiero-assocalzaturifici"
        assert ccnl.meta.cnel_code == "D121"

    def test_calzaturiero_assocalzaturifici_has_10_levels(self) -> None:
        """Contract has exactly 10 classification levels."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "2S", "3", "3S", "4", "5", "6", "7", "8"}

    def test_calzaturiero_assocalzaturifici_level4_salary_aug2024(self) -> None:
        """Level 4 base salary at Aug 2024 tranche: 1879.50 EUR."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.periods[0].value == Decimal("1879.50")
        assert str(lv.base_salary.periods[0].valid_from) == "2024-08-01"

    def test_calzaturiero_assocalzaturifici_level4_salary_aug2026(self) -> None:
        """Level 4 base salary at Aug 2026 tranche: 1980.50 EUR."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.periods[-1].value == Decimal("1980.50")
        assert lv.base_salary.periods[-1].valid_until is None

    def test_calzaturiero_assocalzaturifici_level_ordering(self) -> None:
        """Level 8 has the highest order; level 1 has the lowest."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "8"

    def test_calzaturiero_assocalzaturifici_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_calzaturiero_assocalzaturifici_hourly_divisor(self) -> None:
        """Hourly divisor: 169 (kitech.it, daily divisor 26)."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(169)

    def test_calzaturiero_assocalzaturifici_no_fixed_allowances(self) -> None:
        """All levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_calzaturiero_assocalzaturifici_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_calzaturiero_assocalzaturifici_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), maximum 5 scatti."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 5

    def test_calzaturiero_assocalzaturifici_apprenticeship_tracks(self) -> None:
        """Three percentage tracks: L6-8, L3-5, L2 groups at 80/90/100%."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        assert set(by_name["prof_L6_L8"].destination_levels) == {"6", "7", "8"}
        assert set(by_name["prof_L3_L5"].destination_levels) == {"3", "3S", "4", "5"}
        assert set(by_name["prof_L2"].destination_levels) == {"2", "2S"}
        # All tracks: 80/90/100% over three periods
        for track in ccnl.apprenticeship:
            pcts = [p.percentage for p in track.periods]  # type: ignore[union-attr]
            assert pcts[0] == Decimal("0.80")
            assert pcts[1] == Decimal("0.90")
            assert pcts[2] == Decimal("1.00")
            assert track.periods[-1].months_until is None
        # Period split for L6-8: 10/10/open
        t68 = by_name["prof_L6_L8"]
        assert t68.periods[0].months_until == 10
        assert t68.periods[1].months_until == 20

    def test_elettrico_elettricita_futura_apprenticeship_tracks(self) -> None:
        """Three percentage tracks per Art. 15: C (36m), B (36m), A+BSS (24m)."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        # Gruppo C: dest=CS, 36m, 86/90/96/100%
        c = by_name["gruppo_c"]
        assert set(c.destination_levels) == {"CS"}
        pcts_c = [p.percentage for p in c.periods]  # type: ignore[union-attr]
        exp_36 = [Decimal("0.86"), Decimal("0.90"), Decimal("0.96"), Decimal("1.00")]
        assert pcts_c == exp_36
        assert c.periods[-1].months_until is None
        assert c.periods[0].months_until == 12
        # Gruppo B: dest=B1, 36m, 86/90/96/100%
        b = by_name["gruppo_b"]
        assert set(b.destination_levels) == {"B1"}
        pcts_b = [p.percentage for p in b.periods]  # type: ignore[union-attr]
        assert pcts_b == exp_36
        # Gruppo A+BSS: dest=A1+BSS, 24m, 86/96/100%
        a = by_name["gruppo_a_bss"]
        assert set(a.destination_levels) == {"A1", "BSS"}
        pcts_a = [p.percentage for p in a.periods]  # type: ignore[union-attr]
        assert pcts_a == [Decimal("0.86"), Decimal("0.96"), Decimal("1.00")]
        assert a.periods[-1].months_until is None
        assert a.periods[0].months_until == 12
        assert a.periods[1].months_until == 24


class TestLoadTessileModaArtigianatoConfartigianato:
    """Tests for CCNL Tessile-Moda Artigianato Confartigianato (V751)."""

    def test_tessile_moda_artigianato_confartigianato_loads(self) -> None:
        """Contract loads with correct id and CNEL code V751."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert ccnl.meta.id == "tessile-moda-artigianato-confartigianato"
        assert ccnl.meta.cnel_code == "V751"

    def test_tessile_moda_artigianato_confartigianato_has_7_levels(self) -> None:
        """Contract has exactly 7 levels: 1, 2, 3, 4, 5, 6, 6S."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert len(ccnl.levels) == 7
        assert {lv.code for lv in ccnl.levels} == {"1", "2", "3", "4", "5", "6", "6S"}

    def test_tessile_moda_artigianato_confartigianato_level4_salary_jul2024(
        self,
    ) -> None:
        """Level 4 base salary at Jul 2024 tranche is 1524.87 EUR."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2024, 7, 1)) == Decimal("1524.87")

    def test_tessile_moda_artigianato_confartigianato_level4_salary_jan2025(
        self,
    ) -> None:
        """Level 4 base salary at Jan 2025 tranche is 1566.69 EUR."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1566.69")

    def test_tessile_moda_artigianato_confartigianato_level_ordering(self) -> None:
        """Level 6S has the highest order; level 1 has the lowest."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "6S"

    def test_tessile_moda_artigianato_confartigianato_additional_months(
        self,
    ) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_tessile_moda_artigianato_confartigianato_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (40h/week, Art. 9)."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_tessile_moda_artigianato_confartigianato_no_fixed_allowances(
        self,
    ) -> None:
        """All levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_tessile_moda_artigianato_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_tessile_moda_artigianato_confartigianato_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennale (24 months), maximum 4 scatti."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 4

    def test_tessile_moda_artigianato_confartigianato_apprenticeship_tracks(
        self,
    ) -> None:
        """Three percentage tracks per Art. 68: gruppi 1, 2, 3."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        g1 = by_name["gruppo_1_abb"]
        assert set(g1.destination_levels) == {"4", "5", "6", "6S"}
        assert g1.periods[0].percentage == Decimal("0.70")  # type: ignore[union-attr]
        assert g1.periods[-1].percentage == Decimal("1.00")  # type: ignore[union-attr]
        assert g1.periods[-1].months_until is None
        g2 = by_name["gruppo_2_abb"]
        assert set(g2.destination_levels) == {"3"}
        g3 = by_name["gruppo_3_abb"]
        assert set(g3.destination_levels) == {"2"}


class TestLoadLegnoLapideiArtigianatoConfartigianato:
    """Tests for CCNL Area Legno-Lapidei Artigianato (CNEL F060)."""

    def test_legno_lapidei_artigianato_confartigianato_loads(self) -> None:
        """Contract loads with correct id and CNEL code F060."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert ccnl.meta.id == "legno-lapidei-artigianato-confartigianato"
        assert ccnl.meta.cnel_code == "F060"

    def test_legno_lapidei_artigianato_confartigianato_has_8_levels(self) -> None:
        """Contract has exactly 8 levels: F, E, D, C, CS, B, A, AS."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "F",
            "E",
            "D",
            "C",
            "CS",
            "B",
            "A",
            "AS",
        }

    def test_legno_lapidei_artigianato_confartigianato_level_d_salary_mar2024(
        self,
    ) -> None:
        """Level D base salary at Mar 2024 tranche = 1549.71 EUR."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        lv = ccnl.level_by_code("D")
        assert lv.base_salary.value_at(date(2024, 3, 1)) == Decimal("1549.71")

    def test_legno_lapidei_artigianato_confartigianato_level_d_salary_jan2026(
        self,
    ) -> None:
        """Level D base salary at Jan 2026 tranche = 1639.71 EUR."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        lv = ccnl.level_by_code("D")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1639.71")

    def test_legno_lapidei_artigianato_confartigianato_level_ordering(self) -> None:
        """Level AS has highest order; level F has lowest order."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "F"
        assert by_order[-1].code == "AS"

    def test_legno_lapidei_artigianato_confartigianato_additional_months(
        self,
    ) -> None:
        """Additional months: 13 (tredicesima only, no quattordicesima)."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_legno_lapidei_artigianato_confartigianato_hourly_divisor(
        self,
    ) -> None:
        """Hourly divisor: 174 (per contract clause, 40h/week)."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(174)

    def test_legno_lapidei_artigianato_confartigianato_no_fixed_allowances(
        self,
    ) -> None:
        """All levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_legno_lapidei_artigianato_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_legno_lapidei_artigianato_confartigianato_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_legno_lapidei_artigianato_confartigianato_apprenticeship_tracks(
        self,
    ) -> None:
        """Three percentage tracks per CCNL: gruppi 1, 2, 3."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        g1 = by_name["gruppo_1_legno"]
        assert set(g1.destination_levels) == {"AS", "A", "B"}
        assert g1.periods[0].percentage == Decimal("0.70")  # type: ignore[union-attr]
        assert g1.periods[-1].percentage == Decimal("1.00")  # type: ignore[union-attr]
        assert g1.periods[-1].months_until is None
        g2 = by_name["gruppo_2_legno"]
        assert set(g2.destination_levels) == {"CS", "C", "D"}
        g3 = by_name["gruppo_3_legno"]
        assert set(g3.destination_levels) == {"E"}


# ---------------------------------------------------------------------------
# CCNL Area Comunicazione — Artigianato (G016)
# ---------------------------------------------------------------------------


class TestLoadComunicazioneArtigianatoConfartigianato:
    """Tests for CCNL Area Comunicazione Artigianato (CNEL G016)."""

    def test_comunicazione_artigianato_confartigianato_loads(self) -> None:
        """Contract loads with correct id and CNEL code G016."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        assert ccnl.meta.id == "comunicazione-artigianato-confartigianato"
        assert ccnl.meta.cnel_code == "G016"

    def test_comunicazione_artigianato_confartigianato_has_8_levels(self) -> None:
        """Contract has exactly 8 levels with the correct codes."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "1A",
            "1B",
            "2",
            "3",
            "4",
            "5bis",
            "5",
            "6",
        }

    def test_comunicazione_artigianato_confartigianato_level4_salary_dec2024(
        self,
    ) -> None:
        """Level 4 base salary at Dec 2024 tranche is 1718.56 EUR."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        lv = next(lvl for lvl in ccnl.levels if lvl.code == "4")
        val = lv.base_salary.value_at(date(2024, 12, 1))
        assert val == Decimal("1718.56")

    def test_comunicazione_artigianato_confartigianato_level4_salary_mar2026(
        self,
    ) -> None:
        """Level 4 base salary at Mar 2026 tranche is 1808.56 EUR."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        lv = next(lvl for lvl in ccnl.levels if lvl.code == "4")
        val = lv.base_salary.value_at(date(2026, 3, 1))
        assert val == Decimal("1808.56")

    def test_comunicazione_artigianato_confartigianato_level_ordering(self) -> None:
        """Level 1A has highest order, level 6 has lowest order."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        assert by_code["1A"].order > by_code["1B"].order
        assert by_code["6"].order == 1
        assert by_code["1A"].order == 8

    def test_comunicazione_artigianato_confartigianato_additional_months(
        self,
    ) -> None:
        """Contract has 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_comunicazione_artigianato_confartigianato_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(173)

    def test_comunicazione_artigianato_confartigianato_allowances_structure(
        self,
    ) -> None:
        """Level 1A has 1 function allowance; all other levels have none."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        for lv in ccnl.levels:
            if lv.code == "1A":
                assert len(lv.fixed_allowances) == 1
                assert lv.fixed_allowances[0].code == "IND_FUN"
            else:
                assert lv.fixed_allowances == []

    def test_comunicazione_artigianato_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_comunicazione_artigianato_confartigianato_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_comunicazione_artigianato_confartigianato_apprenticeship_tracks(
        self,
    ) -> None:
        """Two percentage tracks: operai_tecnici (5y) and amministrativi (3y)."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        assert len(ccnl.apprenticeship) == 2
        by_name = {t.name: t for t in ccnl.apprenticeship}
        ot = by_name["operai_tecnici"]
        assert isinstance(ot, ApprenticeshipPercentage)
        assert ot.periods[0].percentage == Decimal("0.70")
        assert ot.periods[-1].percentage == Decimal("1.00")
        assert ot.periods[-1].months_until is None
        adm = by_name["amministrativi"]
        assert isinstance(adm, ApprenticeshipPercentage)
        assert adm.periods[0].percentage == Decimal("0.70")
        assert adm.periods[-1].percentage == Decimal("0.90")


class TestLoadCeramicaIndustriaConfindustria:
    """Tests for CCNL Ceramica Industria (Confindustria-Assopiastrelle, B122)."""

    def test_ceramica_industria_confindustria_loads(self) -> None:
        """Contract loads with correct id and CNEL code B122."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        assert ccnl.meta.id == "ceramica-industria-confindustria"
        assert ccnl.meta.cnel_code == "B122"

    def test_ceramica_industria_confindustria_has_12_levels(self) -> None:
        """Contract has 12 levels: A B1 B2 C1 C2 C3 D1 D2 D3 E1 E2 F."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        assert len(ccnl.levels) == 12
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "A",
            "B1",
            "B2",
            "C1",
            "C2",
            "C3",
            "D1",
            "D2",
            "D3",
            "E1",
            "E2",
            "F",
        }

    def test_ceramica_industria_confindustria_level_a_salary_sep2024(
        self,
    ) -> None:
        """Level A base salary at Sep 2024 tranche is 2600.08 EUR/month."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        val = by_code["A"].base_salary.value_at(date(2024, 9, 1))
        assert val == Decimal("2600.08")

    def test_ceramica_industria_confindustria_level_a_salary_jul2026(
        self,
    ) -> None:
        """Level A base salary at Jul 2026 tranche is 2716.41 EUR/month."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        val = by_code["A"].base_salary.value_at(date(2026, 7, 1))
        assert val == Decimal("2716.41")

    def test_ceramica_industria_confindustria_level_ordering(self) -> None:
        """Level A has highest order; level F has order 1 (lowest)."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        assert by_code["A"].order == 12
        assert by_code["F"].order == 1

    def test_ceramica_industria_confindustria_additional_months(self) -> None:
        """Contract has 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 7, 1))
        assert val == Decimal(13)

    def test_ceramica_industria_confindustria_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 7, 1))
        assert val == Decimal(173)

    def test_ceramica_industria_confindustria_ipo_allowances(self) -> None:
        """B1 C1 C2 D1 D2 E1 have IPO; A B2 C3 D3 E2 F have none."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        levels_with_ipo = {"B1", "C1", "C2", "D1", "D2", "E1"}
        for code, lv in by_code.items():
            if code in levels_with_ipo:
                assert len(lv.fixed_allowances) == 1
                assert lv.fixed_allowances[0].code == "IPO"
            else:
                assert lv.fixed_allowances == []

    def test_ceramica_industria_confindustria_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_ceramica_industria_confindustria_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_ceramica_industria_confindustria_apprenticeship_track(
        self,
    ) -> None:
        """Single percentage track at 95% covering all 12 levels."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        assert len(ccnl.apprenticeship) == 1
        track = ccnl.apprenticeship[0]
        assert isinstance(track, ApprenticeshipPercentage)
        assert len(track.destination_levels) == 12
        assert track.periods[0].percentage == Decimal("0.95")
        assert track.periods[0].months_until is None


class TestLoadOrafiArgentieriIndustriaFederorafi:
    """Tests for CCNL Orafi e Argentieri Industria (Federorafi, C021)."""

    def test_orafi_argentieri_industria_federorafi_loads(self) -> None:
        """Contract loads with correct id and CNEL code C021."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        assert ccnl.meta.id == "orafi-argentieri-industria-federorafi"
        assert ccnl.meta.cnel_code == "C021"

    def test_orafi_argentieri_industria_federorafi_has_8_levels(self) -> None:
        """Contract has 8 levels: 2 3 4 5 5S 6 7 7Q."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"2", "3", "4", "5", "5S", "6", "7", "7Q"}

    def test_orafi_argentieri_industria_federorafi_level5_salary_jun2022(
        self,
    ) -> None:
        """Level 5 base salary at Jun 2022 tranche is 1670.37 EUR/month."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        val = by_code["5"].base_salary.value_at(date(2022, 6, 1))
        assert val == Decimal("1670.37")

    def test_orafi_argentieri_industria_federorafi_level5_salary_dec2024(
        self,
    ) -> None:
        """Level 5 base salary at Dec 2024 tranche is 1744.37 EUR/month."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        val = by_code["5"].base_salary.value_at(date(2024, 12, 1))
        assert val == Decimal("1744.37")

    def test_orafi_argentieri_industria_federorafi_level_ordering(
        self,
    ) -> None:
        """Level 7Q has highest order (8); level 2 has order 1 (lowest)."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        assert by_code["7Q"].order == 8
        assert by_code["2"].order == 1

    def test_orafi_argentieri_industria_federorafi_additional_months(
        self,
    ) -> None:
        """Contract has 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 6, 1))
        assert val == Decimal(13)

    def test_orafi_argentieri_industria_federorafi_hourly_divisor(
        self,
    ) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1))
        assert val == Decimal(173)

    def test_orafi_argentieri_industria_federorafi_no_fixed_allowances_l5(
        self,
    ) -> None:
        """Levels 2-6 have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        for code in ("2", "3", "4", "5", "5S", "6"):
            assert by_code[code].fixed_allowances == []

    def test_orafi_argentieri_industria_federorafi_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_orafi_argentieri_industria_federorafi_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_orafi_argentieri_industria_federorafi_apprenticeship_track(
        self,
    ) -> None:
        """Single percentage track: 85%/90%/95% over 36 months, all 8 levels."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        assert len(ccnl.apprenticeship) == 1
        track = ccnl.apprenticeship[0]
        assert isinstance(track, ApprenticeshipPercentage)
        assert len(track.destination_levels) == 8
        assert track.periods[0].percentage == Decimal("0.85")
        assert track.periods[1].percentage == Decimal("0.90")
        assert track.periods[2].percentage == Decimal("0.95")
        assert track.periods[2].months_until is None


class TestLoadPelliCuoioIndustriaAssopellettieri:
    """Tests for CCNL Pelli e Cuoio Industria — Assopellettieri (D111)."""

    def test_pelli_cuoio_industria_assopellettieri_loads(self) -> None:
        """Contract loads with correct id and CNEL code D111."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert ccnl.meta.id == "pelli-cuoio-industria-assopellettieri"
        assert ccnl.meta.cnel_code == "D111"

    def test_pelli_cuoio_industria_assopellettieri_has_7_levels(self) -> None:
        """Contract has exactly 7 levels: 1, 2, 3, 4, 4S, 5, 6."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "4S", "5", "6"}

    def test_pelli_cuoio_industria_assopellettieri_level4_salary_tranche1(
        self,
    ) -> None:
        """Level 4 first tranche (Apr 2023): 1810.42 EUR/month."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2023, 6, 1)) == Decimal("1810.42")

    def test_pelli_cuoio_industria_assopellettieri_level4_salary_tranche2(
        self,
    ) -> None:
        """Level 4 second tranche (Dec 2023): 1873.70 EUR/month."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1873.70")

    def test_pelli_cuoio_industria_assopellettieri_level_ordering(self) -> None:
        """Level 6 is highest order; level 1 is lowest order."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["6"] == max(orders.values())
        assert orders["1"] == min(orders.values())

    def test_pelli_cuoio_industria_assopellettieri_additional_months(
        self,
    ) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_pelli_cuoio_industria_assopellettieri_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (Art. 35 CCNL CNEL PDF)."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_pelli_cuoio_industria_assopellettieri_no_fixed_allowances(
        self,
    ) -> None:
        """Conglobated model: all levels have empty fixed_allowances."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_pelli_cuoio_industria_assopellettieri_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_pelli_cuoio_industria_assopellettieri_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennale (24 months), maximum 4 scatti."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 4

    def test_pelli_cuoio_industria_assopellettieri_apprenticeship_tracks(
        self,
    ) -> None:
        """6 under_classification tracks, one per destination level."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert len(ccnl.apprenticeship) == 6
        for track in ccnl.apprenticeship:
            assert isinstance(track, ApprenticeshipUnderClassification)
        dest_levels = {t.name: t.destination_levels for t in ccnl.apprenticeship}
        assert dest_levels["dest_6"] == ["6"]
        assert dest_levels["dest_2"] == ["2"]


class TestLoadPubbliciEserciziRistorazioneFipeAngem:
    """CCNL Pubblici Esercizi, Ristorazione Collettiva e Turismo (FIPE/ANGEM, H05Y)."""

    def test_pubblici_esercizi_fipe_angem_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        assert ccnl.meta.id == "pubblici-esercizi-fipe-angem"
        assert ccnl.meta.cnel_code == "H05Y"

    def test_pubblici_esercizi_fipe_angem_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: 1, 2, 3, 4, 5, 6, 6s, 7, Qa, Qb."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "6s", "7", "Qa", "Qb"}

    def test_pubblici_esercizi_fipe_angem_level4_salary_tranche1(self) -> None:
        """Level 4 first tranche (Jun 2024): 1612.69 EUR/month."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2024, 6, 1)) == Decimal("1612.69")

    def test_pubblici_esercizi_fipe_angem_level4_salary_tranche2(self) -> None:
        """Level 4 second tranche (Jun 2026): 1692.69 EUR/month."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("1692.69")

    def test_pubblici_esercizi_fipe_angem_level_ordering(self) -> None:
        """Qa is highest-order level; 7 is lowest-order level."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["Qa"] == max(orders.values())
        assert orders["7"] == min(orders.values())

    def test_pubblici_esercizi_fipe_angem_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_pubblici_esercizi_fipe_angem_hourly_divisor(self) -> None:
        """Hourly divisor: 172 (Art. 160 CCNL FIPE/ANGEM 2024)."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(172)

    def test_pubblici_esercizi_fipe_angem_quadri_fixed_allowances(self) -> None:
        """Qa has IDF_A=75, Qb has IDF_B=70; all other levels have no allowances."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        qa = ccnl.level_by_code("Qa")
        qb = ccnl.level_by_code("Qb")
        assert len(qa.fixed_allowances) == 1
        assert qa.fixed_allowances[0].code == "IND_FUN"
        assert qa.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "75.00"
        )
        assert len(qb.fixed_allowances) == 1
        assert qb.fixed_allowances[0].code == "IND_FUN"
        assert qb.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "70.00"
        )
        for lv in ccnl.levels:
            if lv.code not in {"Qa", "Qb"}:
                assert lv.fixed_allowances == []

    def test_pubblici_esercizi_fipe_angem_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_pubblici_esercizi_fipe_angem_seniority_cadence(self) -> None:
        """Seniority: quadriennale (48 months), maximum 6 scatti."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 48
        assert si.maximum_count == 6


class TestLoadAgenzieDiViaggioFiavet:
    """CCNL Agenzie di Viaggio e Turismo — Fiavet/Confcommercio (H052)."""

    def test_agenzie_viaggio_fiavet_loads(self) -> None:
        """Contract loads with id and CNEL code H052."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        assert ccnl.meta.id == "agenzie-viaggio-fiavet"
        assert ccnl.meta.cnel_code == "H052"

    def test_agenzie_viaggio_fiavet_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: QA QB 1 2 3 4 5 6S 6 7."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"QA", "QB", "1", "2", "3", "4", "5", "6S", "6", "7"}

    def test_agenzie_viaggio_fiavet_level4_salary_tranche1(self) -> None:
        """Level 4 first tranche (Jun 2024): 1550.69 EUR/month."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2024, 6, 1)) == Decimal("1550.69")

    def test_agenzie_viaggio_fiavet_level4_salary_tranche2(self) -> None:
        """Level 4 second tranche (Sep 2026): 1680.69 EUR/month."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2026, 9, 1)) == Decimal("1680.69")

    def test_agenzie_viaggio_fiavet_level_ordering(self) -> None:
        """QA is highest-order level; 7 is lowest-order level."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["QA"] == max(orders.values())
        assert orders["7"] == min(orders.values())

    def test_agenzie_viaggio_fiavet_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_agenzie_viaggio_fiavet_hourly_divisor(self) -> None:
        """Hourly divisor: 172 (Art. 146 CCNL Fiavet 2019)."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(172)

    def test_agenzie_viaggio_fiavet_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_agenzie_viaggio_fiavet_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_agenzie_viaggio_fiavet_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), maximum 6 scatti."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 6


class TestLoadTerziarioConfesercenti:
    """Tests for CCNL Terziario Distribuzione e Servizi — Confesercenti (H012)."""

    def test_terziario_confesercenti_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        assert ccnl.meta.id == "terziario-confesercenti"
        assert ccnl.meta.cnel_code == "H012"

    def test_terziario_confesercenti_has_8_levels(self) -> None:
        """Contract has exactly 8 levels: Q, I, II, III, IV, V, VI, VII."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 8
        assert codes == {"Q", "I", "II", "III", "IV", "V", "VI", "VII"}

    def test_terziario_confesercenti_level4_salary_tranche1(self) -> None:
        """Level IV first tranche (Apr 2023): 1646.68 EUR/month."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        lv = ccnl.level_by_code("IV")
        assert lv.base_salary.value_at(date(2023, 4, 1)) == Decimal("1646.68")

    def test_terziario_confesercenti_level4_salary_tranche5(self) -> None:
        """Level IV fifth tranche (Nov 2026): 1816.68 EUR/month."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        lv = ccnl.level_by_code("IV")
        assert lv.base_salary.value_at(date(2026, 11, 1)) == Decimal("1816.68")

    def test_terziario_confesercenti_level_ordering(self) -> None:
        """Q is highest-order level; VII is lowest-order level."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["Q"] == max(orders.values())
        assert orders["VII"] == min(orders.values())

    def test_terziario_confesercenti_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_terziario_confesercenti_hourly_divisor(self) -> None:
        """Hourly divisor: 168 (Art. 211 CCNL 2019, 40h/week)."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(168)

    def test_terziario_confesercenti_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_terziario_confesercenti_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_terziario_confesercenti_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), maximum 10 scatti."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadTurismoFederalberghi:
    """Tests for CCNL Turismo — Federalberghi/Faita (H052)."""

    def test_turismo_federalberghi_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        assert ccnl.meta.id == "turismo-federalberghi"
        assert ccnl.meta.cnel_code == "H052"

    def test_turismo_federalberghi_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: A, B, 1-6s, 6, 7."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 10
        assert codes == {"A", "B", "1", "2", "3", "4", "5", "6s", "6", "7"}

    def test_turismo_federalberghi_level4_salary_tranche1(self) -> None:
        """Level 4 first tranche (lug 2024): 1620.69 EUR/month."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2024, 7, 1)) == Decimal("1620.69")

    def test_turismo_federalberghi_level4_salary_tranche3(self) -> None:
        """Level 4 third tranche (mag 2026): 1695.69 EUR/month."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2026, 5, 1)) == Decimal("1695.69")

    def test_turismo_federalberghi_level_ordering(self) -> None:
        """Level A is highest-order; level 7 is lowest-order."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["A"] == max(orders.values())
        assert orders["7"] == min(orders.values())

    def test_turismo_federalberghi_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_turismo_federalberghi_hourly_divisor(self) -> None:
        """Hourly divisor: 172 (Art. 151 CCNL 2010, 40h/week)."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(172)

    def test_turismo_federalberghi_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_turismo_federalberghi_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_turismo_federalberghi_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), maximum 6 scatti."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 6


class TestLoadFunzioniCentraliAran:
    """Tests for CCNL Comparto Funzioni Centrali 2022-2024 (S005)."""

    def test_funzioni_centrali_aran_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        assert ccnl.meta.id == "funzioni-centrali-aran"
        assert ccnl.meta.cnel_code == "S005"

    def test_funzioni_centrali_aran_has_4_levels(self) -> None:
        """Contract has exactly 4 levels: OPERATORI, ASSISTENTI, FUNZIONARI, ELEVATE."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 4
        assert codes == {
            "OPERATORI",
            "ASSISTENTI",
            "FUNZIONARI",
            "ELEVATE_PROFESSIONALITA",
        }

    def test_funzioni_centrali_aran_funzionari_salary_tranche1(self) -> None:
        """FUNZIONARI first tranche (9/5/2022): 1958.49 EUR/month."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        lv = ccnl.level_by_code("FUNZIONARI")
        assert lv.base_salary.value_at(date(2022, 5, 9)) == Decimal("1958.49")

    def test_funzioni_centrali_aran_funzionari_salary_tranche2(self) -> None:
        """FUNZIONARI second tranche (1/1/2024): 2113.59 EUR/month."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        lv = ccnl.level_by_code("FUNZIONARI")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("2113.59")

    def test_funzioni_centrali_aran_level_ordering(self) -> None:
        """ELEVATE_PROFESSIONALITA is highest-order; OPERATORI is lowest-order."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["ELEVATE_PROFESSIONALITA"] == max(orders.values())
        assert orders["OPERATORI"] == min(orders.values())

    def test_funzioni_centrali_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_funzioni_centrali_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 156 (Art. 29 c.3, 36h/week)."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_funzioni_centrali_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_funzioni_centrali_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_funzioni_centrali_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (differenziali non automatici, Art. 16)."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadFunzioniLocaliAran:
    """Tests for CCNL Comparto Funzioni Locali 2022-2024 (ARAN)."""

    def test_funzioni_locali_aran_loads(self) -> None:
        """Contract loads with correct id and CNEL code S105."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        assert ccnl.meta.id == "funzioni-locali-aran"
        assert ccnl.meta.cnel_code == "S105"

    def test_funzioni_locali_aran_has_4_levels(self) -> None:
        """Contract has exactly 4 areas (Operatori, Oper.Esp., Istruttori, Funz.EQ)."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        assert len(ccnl.levels) == 4
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "OPERATORI",
            "OPERATORI_ESPERTI",
            "ISTRUTTORI",
            "FUNZIONARI_EQ",
        }

    def test_funzioni_locali_aran_istruttori_salary_tranche1(self) -> None:
        """ISTRUTTORI first tranche (2022-11-16): 1782.74 EUR/month."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        lv = ccnl.level_by_code("ISTRUTTORI")
        assert lv.base_salary.value_at(date(2022, 11, 16)) == Decimal("1782.74")

    def test_funzioni_locali_aran_istruttori_salary_tranche2(self) -> None:
        """ISTRUTTORI second tranche (1/1/2024): 1915.55 EUR/month."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        lv = ccnl.level_by_code("ISTRUTTORI")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1915.55")

    def test_funzioni_locali_aran_level_ordering(self) -> None:
        """FUNZIONARI_EQ is highest-order; OPERATORI is lowest-order."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["FUNZIONARI_EQ"] == max(orders.values())
        assert orders["OPERATORI"] == min(orders.values())

    def test_funzioni_locali_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_funzioni_locali_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 156 (Art. 74 CCNL 16.11.2022, 36h/week)."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_funzioni_locali_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_funzioni_locali_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_funzioni_locali_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (differenziali non automatici, Art. 14)."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadSanitaAran:
    """Tests for CCNL Comparto Sanità 2022-2024 (sanita-aran, CNEL S205)."""

    def test_sanita_aran_loads(self) -> None:
        """File loads successfully and has correct id and CNEL code."""
        ccnl = load_ccnl("sanita-aran.json")
        assert ccnl.meta.id == "sanita-aran"
        assert ccnl.meta.cnel_code == "S205"

    def test_sanita_aran_has_5_levels(self) -> None:
        """Contract has exactly 5 areas."""
        ccnl = load_ccnl("sanita-aran.json")
        assert len(ccnl.levels) == 5
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "SUPPORTO",
            "OPERATORI",
            "ASSISTENTI",
            "PROFESSIONISTI",
            "ELEVATA_QUALIFICAZIONE",
        }

    def test_sanita_aran_professionisti_salary_tranche1(self) -> None:
        """PROFESSIONISTI first tranche (2022-11-02): 1941.58 EUR/month."""
        ccnl = load_ccnl("sanita-aran.json")
        lv = ccnl.level_by_code("PROFESSIONISTI")
        assert lv.base_salary.value_at(date(2022, 11, 2)) == Decimal("1941.58")

    def test_sanita_aran_professionisti_salary_tranche2(self) -> None:
        """PROFESSIONISTI second tranche (1/1/2024): 2076.58 EUR/month."""
        ccnl = load_ccnl("sanita-aran.json")
        lv = ccnl.level_by_code("PROFESSIONISTI")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("2076.58")

    def test_sanita_aran_level_ordering(self) -> None:
        """ELEVATA_QUALIFICAZIONE is highest-order; SUPPORTO is lowest-order."""
        ccnl = load_ccnl("sanita-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["ELEVATA_QUALIFICAZIONE"] == max(orders.values())
        assert orders["SUPPORTO"] == min(orders.values())

    def test_sanita_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only, Art. 57)."""
        ccnl = load_ccnl("sanita-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_sanita_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 156 (Art. 26 CCNL, 36h/week)."""
        ccnl = load_ccnl("sanita-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_sanita_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("sanita-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_sanita_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("sanita-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_sanita_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (DEP non automatici, Art. 60)."""
        ccnl = load_ccnl("sanita-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadDirigenzaSanitariaMedicoVeterinariaAran:
    """Tests for CCNL Area Sanità 2022-2024 — Dirigenti Medici e Vet (S225)."""

    def test_dirigenza_sanitaria_medico_veterinaria_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        assert ccnl.meta.id == "dirigenza-sanitaria-medico-veterinaria-aran"
        assert ccnl.meta.cnel_code == "S225"

    def test_dirigenza_sanitaria_medico_veterinaria_aran_has_1_level(
        self,
    ) -> None:
        """Contract has exactly 1 level (DIRIGENTE)."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        assert len(ccnl.levels) == 1
        assert {lv.code for lv in ccnl.levels} == {"DIRIGENTE"}

    def test_dirigenza_sanitaria_medico_veterinaria_aran_salary_tranche1(
        self,
    ) -> None:
        """DIRIGENTE first tranche (2019-12-19): 3616.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2019, 12, 19)) == Decimal("3616.60")

    def test_dirigenza_sanitaria_medico_veterinaria_aran_salary_tranche2(
        self,
    ) -> None:
        """DIRIGENTE second tranche (1/1/2024): 3846.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("3846.60")

    def test_dirigenza_sanitaria_medico_veterinaria_aran_level_ordering(
        self,
    ) -> None:
        """DIRIGENTE is both highest-order and lowest-order (single level)."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["DIRIGENTE"] == max(orders.values())
        assert orders["DIRIGENTE"] == min(orders.values())

    def test_dirigenza_sanitaria_medico_veterinaria_aran_additional_months(
        self,
    ) -> None:
        """Additional months: 13 (Art. 11 — 'per 13 mensilità')."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_dirigenza_sanitaria_medico_veterinaria_aran_hourly_divisor(
        self,
    ) -> None:
        """Hourly divisor: 165 (38h/week approximation, SIMPLIFICATION)."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_dirigenza_sanitaria_medico_veterinaria_aran_specificita_allowance(
        self,
    ) -> None:
        """DIRIGENTE has one fixed allowance: SPECIFICITA_MEDICO_VETERINARIA."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert len(lv.fixed_allowances) == 1
        assert lv.fixed_allowances[0].code == "SPECIFICITA_MEDICO_VETERINARIA"
        assert lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "728.15"
        )

    def test_dirigenza_sanitaria_medico_veterinaria_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_dirigenza_sanitaria_medico_veterinaria_aran_seniority_cadence(
        self,
    ) -> None:
        """Seniority: maximum_count=0 (no automatic scatti per dirigenza)."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadDirigenzaSanitariaAreaSanitaAran:
    """Tests for CCNL Area Sanità 2022-2024 — Dirigenti Sanitari (S225)."""

    def test_dirigenza_sanitaria_area_sanita_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        assert ccnl.meta.id == "dirigenza-sanitaria-area-sanita-aran"
        assert ccnl.meta.cnel_code == "S225"

    def test_dirigenza_sanitaria_area_sanita_aran_has_1_level(self) -> None:
        """Contract has exactly 1 level (DIRIGENTE)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        assert len(ccnl.levels) == 1
        assert {lv.code for lv in ccnl.levels} == {"DIRIGENTE"}

    def test_dirigenza_sanitaria_area_sanita_aran_salary_tranche1(self) -> None:
        """DIRIGENTE first tranche (2019-12-19): 3616.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2019, 12, 19)) == Decimal("3616.60")

    def test_dirigenza_sanitaria_area_sanita_aran_salary_tranche2(self) -> None:
        """DIRIGENTE second tranche (1/1/2024): 3846.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("3846.60")

    def test_dirigenza_sanitaria_area_sanita_aran_level_ordering(self) -> None:
        """DIRIGENTE is both highest-order and lowest-order (single level)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["DIRIGENTE"] == max(orders.values())
        assert orders["DIRIGENTE"] == min(orders.values())

    def test_dirigenza_sanitaria_area_sanita_aran_additional_months(
        self,
    ) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_dirigenza_sanitaria_area_sanita_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 165 (38h/week, SIMPLIFICATION)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_dirigenza_sanitaria_area_sanita_aran_specificita_allowance(
        self,
    ) -> None:
        """DIRIGENTE has one fixed allowance: SPECIFICITA_SANITARIA (124.19)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert len(lv.fixed_allowances) == 1
        assert lv.fixed_allowances[0].code == "SPECIFICITA_SANITARIA"
        assert lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "124.19"
        )

    def test_dirigenza_sanitaria_area_sanita_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_dirigenza_sanitaria_area_sanita_aran_seniority_cadence(
        self,
    ) -> None:
        """Seniority: maximum_count=0 (no automatic scatti per dirigenza)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadDirigenzaFunzioniLocaliAran:
    """Tests for CCNL Area Dirigenza Funzioni Locali 2022-2024 (S125)."""

    def test_dirigenza_funzioni_locali_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        assert ccnl.meta.id == "dirigenza-funzioni-locali-aran"
        assert ccnl.meta.cnel_code == "S125"

    def test_dirigenza_funzioni_locali_aran_has_1_level(self) -> None:
        """Contract has exactly 1 level (DIRIGENTE)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        assert len(ccnl.levels) == 1
        assert {lv.code for lv in ccnl.levels} == {"DIRIGENTE"}

    def test_dirigenza_funzioni_locali_aran_salary_tranche1(self) -> None:
        """DIRIGENTE first tranche (2020-12-17): 3616.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2020, 12, 17)) == Decimal("3616.60")

    def test_dirigenza_funzioni_locali_aran_salary_tranche2(self) -> None:
        """DIRIGENTE second tranche (1/1/2024): 3846.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("3846.60")

    def test_dirigenza_funzioni_locali_aran_level_ordering(self) -> None:
        """DIRIGENTE is both highest-order and lowest-order (single level)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["DIRIGENTE"] == max(orders.values())
        assert orders["DIRIGENTE"] == min(orders.values())

    def test_dirigenza_funzioni_locali_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_dirigenza_funzioni_locali_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 165 (38h/week, SIMPLIFICATION)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_dirigenza_funzioni_locali_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: no fixed allowances (posizione variabile)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_dirigenza_funzioni_locali_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_dirigenza_funzioni_locali_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (no automatic scatti per dirigenza)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadDirigenzaFunzioniCentraliAran:
    """Tests for CCNL Area Dirigenza Funzioni Centrali 2022-2024 (S025)."""

    def test_dirigenza_funzioni_centrali_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        assert ccnl.meta.id == "dirigenza-funzioni-centrali-aran"
        assert ccnl.meta.cnel_code == "S025"

    def test_dirigenza_funzioni_centrali_aran_has_2_levels(self) -> None:
        """Contract has exactly 2 levels: PRIMA_FASCIA and SECONDA_FASCIA."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        assert len(ccnl.levels) == 2
        assert {lv.code for lv in ccnl.levels} == {
            "PRIMA_FASCIA",
            "SECONDA_FASCIA",
        }

    def test_dirigenza_funzioni_centrali_aran_salary_tranche1(self) -> None:
        """SECONDA_FASCIA first tranche (2023-11-16): 3616.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        lv = ccnl.level_by_code("SECONDA_FASCIA")
        assert lv.base_salary.value_at(date(2023, 11, 16)) == Decimal("3616.60")

    def test_dirigenza_funzioni_centrali_aran_salary_tranche2(self) -> None:
        """PRIMA_FASCIA second tranche (1/1/2024): 4908.30 EUR/month."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        lv = ccnl.level_by_code("PRIMA_FASCIA")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("4908.30")

    def test_dirigenza_funzioni_centrali_aran_level_ordering(self) -> None:
        """PRIMA_FASCIA has highest order; SECONDA_FASCIA has lowest."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "PRIMA_FASCIA"
        assert min(orders, key=lambda k: orders[k]) == "SECONDA_FASCIA"

    def test_dirigenza_funzioni_centrali_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_dirigenza_funzioni_centrali_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 165 (38h/week, SIMPLIFICATION)."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_dirigenza_funzioni_centrali_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: no fixed allowances (posizione variabile)."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_dirigenza_funzioni_centrali_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_dirigenza_funzioni_centrali_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (no automatic scatti)."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadDirigenzaIstruzioneRicercaAran:
    """Tests for CCNL Area Dirigenza Istruzione e Ricerca 2022-2024 (S325)."""

    def test_dirigenza_istruzione_ricerca_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        assert ccnl.meta.id == "dirigenza-istruzione-ricerca-aran"
        assert ccnl.meta.cnel_code == "S325"

    def test_dirigenza_istruzione_ricerca_aran_has_2_levels(self) -> None:
        """Contract has exactly 2 levels: PRIMA_FASCIA and SECONDA_FASCIA."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        assert len(ccnl.levels) == 2
        assert {lv.code for lv in ccnl.levels} == {
            "PRIMA_FASCIA",
            "SECONDA_FASCIA",
        }

    def test_dirigenza_istruzione_ricerca_aran_salary_tranche1(self) -> None:
        """SECONDA_FASCIA first tranche (2021-01-01): 3616.59 EUR/month."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        lv = ccnl.level_by_code("SECONDA_FASCIA")
        assert lv.base_salary.value_at(date(2021, 1, 1)) == Decimal("3616.59")

    def test_dirigenza_istruzione_ricerca_aran_salary_tranche2(self) -> None:
        """PRIMA_FASCIA second tranche (1/1/2024): 4908.30 EUR/month."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        lv = ccnl.level_by_code("PRIMA_FASCIA")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("4908.30")

    def test_dirigenza_istruzione_ricerca_aran_level_ordering(self) -> None:
        """PRIMA_FASCIA has highest order; SECONDA_FASCIA has lowest."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "PRIMA_FASCIA"
        assert min(orders, key=lambda k: orders[k]) == "SECONDA_FASCIA"

    def test_dirigenza_istruzione_ricerca_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_dirigenza_istruzione_ricerca_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 165 (38h/week, SIMPLIFICATION)."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_dirigenza_istruzione_ricerca_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: no fixed allowances (posizione variabile)."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_dirigenza_istruzione_ricerca_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_dirigenza_istruzione_ricerca_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (no automatic scatti)."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadIstruzioneRicercaAran:
    """Tests for CCNL Comparto Istruzione e Ricerca 2022-2024 (S305)."""

    def test_istruzione_ricerca_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        assert ccnl.meta.id == "istruzione-ricerca-aran"
        assert ccnl.meta.cnel_code == "S305"

    def test_istruzione_ricerca_aran_has_6_levels(self) -> None:
        """Contract has exactly 6 levels (4 ATA + 2 docente groups)."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        assert len(ccnl.levels) == 6
        assert {lv.code for lv in ccnl.levels} == {
            "COLLABORATORE_SCOLASTICO",
            "OPERATORE",
            "ASSISTENTE",
            "DOCENTE_INFANZIA_PRIMARIA",
            "DOCENTE_SECONDARIA",
            "FUNZIONARIO_ED_ESPERTO",
        }

    def test_istruzione_ricerca_aran_assistente_salary_tranche1(self) -> None:
        """ASSISTENTE first tranche (2022-01-01): 1401.28 EUR/month."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        lv = ccnl.level_by_code("ASSISTENTE")
        assert lv.base_salary.value_at(date(2022, 1, 1)) == Decimal("1401.28")

    def test_istruzione_ricerca_aran_assistente_salary_tranche2(self) -> None:
        """ASSISTENTE second tranche (1/1/2024): 1496.85 EUR/month."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        lv = ccnl.level_by_code("ASSISTENTE")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1496.85")

    def test_istruzione_ricerca_aran_level_ordering(self) -> None:
        """FUNZIONARIO_ED_ESPERTO has highest order; COLLABORATORE has lowest."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "FUNZIONARIO_ED_ESPERTO"
        assert min(orders, key=lambda k: orders[k]) == "COLLABORATORE_SCOLASTICO"

    def test_istruzione_ricerca_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_istruzione_ricerca_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 156 (36h/week standard, SIMPLIFICATION)."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_istruzione_ricerca_aran_no_fixed_allowances(self) -> None:
        """Conglobated tabellare: no fixed allowances modelled."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_istruzione_ricerca_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_istruzione_ricerca_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (fasce not automatic scatti)."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadSanitaPrivataAiopAris:
    """Tests for CCNL Case di Cura Private - Personale Non Medico (AIOP/ARIS)."""

    def test_sanita_privata_aiop_aris_loads(self) -> None:
        """Contract id and CNEL code match expected values."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        assert ccnl.meta.id == "sanita-privata-aiop-aris"
        assert ccnl.meta.cnel_code == "T011"

    def test_sanita_privata_aiop_aris_has_28_levels(self) -> None:
        """Contract has exactly 28 levels covering categories A to E."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        assert len(ccnl.levels) == 28
        assert {lv.code for lv in ccnl.levels} == {
            "A",
            "A1",
            "A2",
            "A3",
            "A4",
            "B",
            "B1",
            "B2",
            "B3",
            "B4",
            "C",
            "C1",
            "C2",
            "C3",
            "C4",
            "D",
            "D1",
            "D2",
            "D3",
            "D4",
            "DS",
            "DS1",
            "DS2",
            "DS3",
            "DS4",
            "E",
            "E1",
            "E2",
        }

    def test_sanita_privata_aiop_aris_level_a_salary(self) -> None:
        """Level A salary at 2026-01-01: 1467.45 EUR/month (Tabella 1)."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        lv = ccnl.level_by_code("A")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1467.45")

    def test_sanita_privata_aiop_aris_level_e2_salary(self) -> None:
        """Level E2 salary at 2026-01-01: 3554.39 EUR/month (Tabella 1)."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        lv = ccnl.level_by_code("E2")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("3554.39")

    def test_sanita_privata_aiop_aris_level_ordering(self) -> None:
        """E2 has highest order (order 28); A has lowest (order 1)."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "E2"
        assert min(orders, key=lambda k: orders[k]) == "A"

    def test_sanita_privata_aiop_aris_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only, Art. 50/66)."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_sanita_privata_aiop_aris_hourly_divisor(self) -> None:
        """Hourly divisor: 156 (Art. 58: monthly/26/6 for 36h/week)."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_sanita_privata_aiop_aris_no_fixed_allowances(self) -> None:
        """Conglobated tabellare (Art. 55): no fixed allowances."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == []

    def test_sanita_privata_aiop_aris_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_sanita_privata_aiop_aris_seniority_cadence(self) -> None:
        """Seniority frozen at 1993-12-31 per Art. 56; maximum_count=0."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        si = ccnl.parameters.seniority_increments
        # cadence_months is inert when maximum_count=0
        assert si.cadence_months == 24
        assert si.maximum_count == 0


class TestLoadLavoroDomesticoConvivente:
    """Tests for lavoro-domestico-convivente.json (DOMINA/FIDALDO, CNEL H501)."""

    def test_lavoro_domestico_convivente_loads(self) -> None:
        """id='lavoro-domestico-convivente', cnel_code='H501'."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        assert ccnl.meta.id == "lavoro-domestico-convivente"
        assert ccnl.meta.cnel_code == "H501"

    def test_lavoro_domestico_convivente_has_8_levels(self) -> None:
        """Eight levels: A, AS, B, BS, C, CS, D, DS."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "A",
            "AS",
            "B",
            "BS",
            "C",
            "CS",
            "D",
            "DS",
        }

    def test_lavoro_domestico_convivente_level_a_salary(self) -> None:
        """Level A salary at 2026-01-01: 908.10 EUR/month (Domina Tab.A)."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        lv = ccnl.level_by_code("A")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("908.10")

    def test_lavoro_domestico_convivente_level_ds_salary(self) -> None:
        """Level DS salary at 2026-01-01: 1474.73 EUR/month (Domina Tab.A)."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        lv = ccnl.level_by_code("DS")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1474.73")

    def test_lavoro_domestico_convivente_level_ordering(self) -> None:
        """DS has highest order (8); A has lowest (1)."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "DS"
        assert min(orders, key=lambda k: orders[k]) == "A"

    def test_lavoro_domestico_convivente_additional_months(self) -> None:
        """Additional months: 13 (tredicesima, Art. 27 CCNL)."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_lavoro_domestico_convivente_hourly_divisor(self) -> None:
        """Hourly divisor: 234 (54 h/week x 52/12, convivente Art. 10)."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(234)

    def test_lavoro_domestico_convivente_d_ds_indennita(self) -> None:
        """D and DS have indennità di funzione 207.69; A-CS have none."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        for code in ("A", "AS", "B", "BS", "C", "CS"):
            assert ccnl.level_by_code(code).fixed_allowances == []
        for code in ("D", "DS"):
            lv = ccnl.level_by_code(code)
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "INDENNITA_FUNZIONE"
            assert lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
                "207.69"
            )

    def test_lavoro_domestico_convivente_tax_sector(self) -> None:
        """Contract declares LAVORO_DOMESTICO tax sector."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        assert ccnl.meta.tax_sector == TaxSector.LAVORO_DOMESTICO

    def test_lavoro_domestico_convivente_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 7 scatti."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 7
