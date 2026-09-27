"""Bundled CCNL data files load with their expected values.

Covers Metalmeccanico, Metalmeccanico Confapi, Chimica Federchimica.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.apprenticeship import (
    ApprenticeshipUnderClassification,
)
from ccnl_engine.contract.domain.identity import CCNL
from ccnl_engine.contract.service.loaders import load_ccnl


class TestLoadMetalmeccanico:
    """Unit tests for the bundled Metalmeccanico data file."""

    def test_metalmeccanico_loads(self) -> None:
        """File parses, id and cnel_code are correct."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.ccnl_id == "metalmeccanico-federmeccanica"
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
            assert level.fixed_allowances == (), (
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
        assert by_name["professionalizzante_24"].destination_levels == ("D2",)
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
        assert ccnl.meta.ccnl_id == "metalmeccanico-confapi"
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
        assert track.destination_levels == ("3", "4", "5", "6", "7", "8", "9")
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
            assert level.fixed_allowances == (), (
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
        assert ccnl.meta.ccnl_id == "chimica-farmaceutica-federchimica"
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
            assert level.fixed_allowances == (), (
                f"Level {level.code} should have no fixed_allowances "
                "(TEM is already embedded in base_salary)"
            )

    def test_chimica_hourly_divisor(self) -> None:
        """Hourly divisor must be 175 (chimico-farmaceutico standard)."""
        ccnl = load_ccnl("chimica-farmaceutica-federchimica.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(175)
