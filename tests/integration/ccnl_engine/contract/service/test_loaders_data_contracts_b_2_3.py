"""Bundled CCNL data files load with their expected values.

Covers Funivie Anef, Federcasa, Fiori Recisi Ancef, Ooss Unsic Confsal.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.apprenticeship import (
    ApprenticeshipUnderClassification,
)
from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl


class TestLoadFunivieAnef:
    """Tests for CCNL Trasporto a Fune ANEF (I911)."""

    def test_funivie_anef_loads(self) -> None:
        """Id == 'funivie-anef', cnel_code == 'I911'."""
        ccnl = load_ccnl("funivie-anef.json")
        assert ccnl.meta.ccnl_id == "funivie-anef"
        assert ccnl.meta.cnel_code == "I911"

    def test_funivie_anef_has_8_levels(self) -> None:
        """8 livelli retributivi: 1S 1 2 3 4 5 6 7."""
        ccnl = load_ccnl("funivie-anef.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "1S",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
        }

    def test_funivie_anef_level4_salary_tranche1(self) -> None:
        """Level 4 paga base at first tranche 2025-05-01 = 1464.59."""
        ccnl = load_ccnl("funivie-anef.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2025, 6, 1)) == Decimal("1464.59")

    def test_funivie_anef_level4_salary_tranche2(self) -> None:
        """Level 4 paga base at second tranche 2025-10-01 = 1504.59."""
        ccnl = load_ccnl("funivie-anef.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1504.59")

    def test_funivie_anef_level_ordering(self) -> None:
        """Highest order = 1S (8), lowest = 7 (1)."""
        ccnl = load_ccnl("funivie-anef.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "7"
        assert by_order[-1].code == "1S"

    def test_funivie_anef_additional_months(self) -> None:
        """14 mensilita: tredicesima natalizia + quattordicesima luglio."""
        ccnl = load_ccnl("funivie-anef.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_funivie_anef_hourly_divisor(self) -> None:
        """Hourly divisor = 173 (Art. 18, CCNL ANEF 2025)."""
        ccnl = load_ccnl("funivie-anef.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 173

    def test_funivie_anef_contingenza_only_no_edr(self) -> None:
        """Each level has exactly one fixed allowance (contingenza, no EDR)."""
        ccnl = load_ccnl("funivie-anef.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "contingenza"

    def test_funivie_anef_tax_sector(self) -> None:
        """tax_sector == INDUSTRIA (SIMPLIFICATION)."""
        ccnl = load_ccnl("funivie-anef.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_funivie_anef_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), max 5 scatti (Allegato 3)."""
        ccnl = load_ccnl("funivie-anef.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_funivie_anef_apprenticeship(self) -> None:
        """One under_classification track; level 7 excluded from destinations."""
        ccnl = load_ccnl("funivie-anef.json")
        tracks = ccnl.apprenticeship
        assert len(tracks) == 1
        assert isinstance(tracks[0], ApprenticeshipUnderClassification)
        track = tracks[0]
        assert track.name == "professionalizzante"
        assert "7" not in track.destination_levels
        assert "1S" not in track.destination_levels
        assert len(track.periods) == 2
        assert track.periods[0].levels_below == 1
        assert track.periods[1].levels_below == 0


class TestLoadFedercasa:
    """CCNL Dipendenti Aziende Enti Pubblici Economici Federcasa (T611)."""

    def test_federcasa_loads(self) -> None:
        """Contract loads and id/cnel_code match."""
        ccnl = load_ccnl("federcasa.json")
        assert ccnl.meta.ccnl_id == "federcasa"
        assert ccnl.meta.cnel_code == "T611"

    def test_federcasa_has_16_levels(self) -> None:
        """Exactly 16 levels covering all four areas plus Quadri."""
        ccnl = load_ccnl("federcasa.json")
        assert len(ccnl.levels) == 16
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "Q1",
            "Q2",
            "As",
            "A1",
            "A2",
            "A3",
            "Bs",
            "B1",
            "B2",
            "B3",
            "C1",
            "C2",
            "C3",
            "Ds",
            "D1",
            "D2",
        }

    def test_federcasa_level_b1_salary_dec2024(self) -> None:
        """B1 base salary from 01/12/2024 = 2084.39 (Art.72, ilccnl.it)."""
        ccnl = load_ccnl("federcasa.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B1")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("2084.39")

    def test_federcasa_level_a1_salary_dec2024(self) -> None:
        """A1 base salary from 01/12/2024 = 2542.96 (Art.72, ilccnl.it)."""
        ccnl = load_ccnl("federcasa.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "A1")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("2542.96")

    def test_federcasa_level_ordering(self) -> None:
        """Highest order = Q1 (16), lowest = D2 (1)."""
        ccnl = load_ccnl("federcasa.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "D2"
        assert by_order[-1].code == "Q1"

    def test_federcasa_additional_months(self) -> None:
        """14 mensilita: tredicesima dicembre + quattordicesima giugno (Art.76)."""
        ccnl = load_ccnl("federcasa.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_federcasa_hourly_divisor(self) -> None:
        """Hourly divisor = 156 (Art.71.5: 1/156 retribuzione mensile)."""
        ccnl = load_ccnl("federcasa.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 156

    def test_federcasa_no_fixed_allowances(self) -> None:
        """All 16 levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("federcasa.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_federcasa_tax_sector(self) -> None:
        """tax_sector == TERZIARIO (SIMPLIFICATION: actual sector unverified)."""
        ccnl = load_ccnl("federcasa.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_federcasa_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), max 14 scatti (Art.73.1-2)."""
        ccnl = load_ccnl("federcasa.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 14


class TestLoadFioriRecisiAncef:
    """Unit tests for CCNL Fiori Freschi Recisi ANCEF (H201)."""

    def test_fiori_recisi_ancef_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        assert ccnl.meta.ccnl_id == "fiori-recisi-ancef"
        assert ccnl.meta.cnel_code == "H201"

    def test_fiori_recisi_ancef_has_8_levels(self) -> None:
        """8 levels: Q, 1S, 1, 2, 3, 4, 5, 6."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "Q",
            "1S",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
        }

    def test_fiori_recisi_ancef_level_3_salary_jan2023(self) -> None:
        """Level 3 at 2023-01-01 == 1712.57 (first tranche, reference level)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2023, 1, 1)) == Decimal("1712.57")

    def test_fiori_recisi_ancef_level_3_salary_jan2026(self) -> None:
        """Level 3 at 2026-01-01 == 1792.57 (fourth tranche)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1792.57")

    def test_fiori_recisi_ancef_level_ordering(self) -> None:
        """Highest order = Q (8), lowest = 6 (1)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "Q"

    def test_fiori_recisi_ancef_additional_months(self) -> None:
        """14 mensilita: tredicesima + quattordicesima (Art.38-39)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_fiori_recisi_ancef_hourly_divisor(self) -> None:
        """Hourly divisor = 170 (Art.45)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 170

    def test_fiori_recisi_ancef_no_fixed_allowances(self) -> None:
        """All 8 levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_fiori_recisi_ancef_tax_sector(self) -> None:
        """tax_sector == TERZIARIO (flower import-export commercial trade)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_fiori_recisi_ancef_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), max 10 scatti (Art.48)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadOossUnsicConfsal:
    """Tests for CCNL OO.SS. UNSIC/CONFSAL (V925)."""

    def test_ooss_unsic_confsal_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        assert ccnl.meta.ccnl_id == "ooss-unsic-confsal"
        assert ccnl.meta.cnel_code == "V925"

    def test_ooss_unsic_confsal_has_6_levels(self) -> None:
        """Contract has exactly 6 levels with codes 1-6."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        assert len(ccnl.levels) == 6
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6"}

    def test_ooss_unsic_confsal_level3_salary_jan2023(self) -> None:
        """Level 3 base salary at 2023-01-19: 2065.40 EUR (primary source)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2023, 2, 1)) == Decimal("2065.40")

    def test_ooss_unsic_confsal_level3_salary_jan2026(self) -> None:
        """Level 3 base salary at 2026-01-01: 2096.38 EUR (proxy source)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("2096.38")

    def test_ooss_unsic_confsal_level_ordering(self) -> None:
        """Level 1 (Direttore Generale) is highest; level 6 is lowest."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "6"
        assert ordered[-1].code == "1"

    def test_ooss_unsic_confsal_additional_months(self) -> None:
        """14 mensilita: 13ma (Art.52) + 14ma (quattordicesima)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_ooss_unsic_confsal_hourly_divisor(self) -> None:
        """Hourly divisor 170 (Art.49: 'divisore convenzionale 170')."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 170

    def test_ooss_unsic_confsal_no_fixed_allowances(self) -> None:
        """All 6 levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_ooss_unsic_confsal_tax_sector(self) -> None:
        """tax_sector == TERZIARIO (sindacali organizations, no dedicated INPS code)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_ooss_unsic_confsal_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), max 5 scatti (Art.51)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 5
