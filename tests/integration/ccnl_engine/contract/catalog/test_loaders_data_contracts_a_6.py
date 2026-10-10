"""Bundled CCNL data files load with their expected values.

Covers Operai Agricoli, Chimica Affini Pmi Unionichimica, Panificazione
Assipan, Trasporto Ferroviario Agens.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.identity.facade import TaxSector


class TestLoadOperaiAgricoli:
    """Unit tests for operai-agricoli-florovivaisti.json."""

    def test_operai_agricoli_loads(self) -> None:
        """Contract loads and id/cnel_code are correct."""
        ccnl = load_ccnl("operai-agricoli-florovivaisti.json")
        assert ccnl.meta.ccnl_id == "operai-agricoli-florovivaisti"
        assert ccnl.meta.cnel_code == "A011"

    def test_operai_agricoli_has_3_levels(self) -> None:
        """Contract has exactly 3 national professional areas."""
        ccnl = load_ccnl("operai-agricoli-florovivaisti.json")
        assert len(ccnl.levels) == 3
        assert {lv.code for lv in ccnl.levels} == {"Area1", "Area2", "Area3"}

    def test_operai_agricoli_level_area2_salary_2026(self) -> None:
        """Area2 base salary at June 2026 tranche is 1375.48 EUR."""
        ccnl = load_ccnl("operai-agricoli-florovivaisti.json")
        area2 = next(lv for lv in ccnl.levels if lv.code == "Area2")
        assert area2.base_salary.value_at(date(2026, 9, 1)) == Decimal("1375.48")

    def test_operai_agricoli_level_area2_salary_2027(self) -> None:
        """Area2 base salary at Jan 2027 tranche is 1398.86 EUR."""
        ccnl = load_ccnl("operai-agricoli-florovivaisti.json")
        area2 = next(lv for lv in ccnl.levels if lv.code == "Area2")
        assert area2.base_salary.value_at(date(2027, 1, 1)) == Decimal("1398.86")

    def test_operai_agricoli_level_ordering(self) -> None:
        """Area1 (specializzati) has highest order; Area3 (comuni) lowest."""
        ccnl = load_ccnl("operai-agricoli-florovivaisti.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "Area3"
        assert by_order[-1].code == "Area1"

    def test_operai_agricoli_additional_months(self) -> None:
        """Contract has 14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("operai-agricoli-florovivaisti.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            14
        )

    def test_operai_agricoli_hourly_divisor(self) -> None:
        """Hourly divisor is 169 (39 h/week x 52 / 12)."""
        ccnl = load_ccnl("operai-agricoli-florovivaisti.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == Decimal(169)

    def test_operai_agricoli_no_fixed_allowances(self) -> None:
        """All levels have no fixed allowances (conglobated salary model)."""
        ccnl = load_ccnl("operai-agricoli-florovivaisti.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_operai_agricoli_tax_sector(self) -> None:
        """Contract declares AGRICOLTURA tax sector."""
        ccnl = load_ccnl("operai-agricoli-florovivaisti.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_operai_agricoli_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), maximum 5 scatti."""
        ccnl = load_ccnl("operai-agricoli-florovivaisti.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 5


class TestLoadChimicaAffiniPmiUnionichimica:
    """Tests for CCNL Chimica e Affini PMI Unionchimica Confapi (B018)."""

    def test_chimica_pmi_loads(self) -> None:
        """Contract loads with correct id and CNEL code B018."""
        ccnl = load_ccnl("chimica-affini-pmi-unionchimica.json")
        assert ccnl.meta.ccnl_id == "chimica-affini-pmi-unionchimica"
        assert ccnl.meta.cnel_code == "B018"

    def test_chimica_pmi_has_8_levels(self) -> None:
        """Contract has exactly 8 levels: A through H."""
        ccnl = load_ccnl("chimica-affini-pmi-unionchimica.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
        }

    def test_chimica_pmi_level_d_salary_2026(self) -> None:
        """Level D base salary at Jan 2026 is 2267.00 EUR."""
        ccnl = load_ccnl("chimica-affini-pmi-unionchimica.json")
        lv_d = next(lv for lv in ccnl.levels if lv.code == "D")
        assert lv_d.base_salary.value_at(date(2026, 9, 1)) == Decimal("2267.00")

    def test_chimica_pmi_level_h_salary_2026(self) -> None:
        """Level H base salary (minimum only) at Jan 2026 is 3168.51 EUR."""
        ccnl = load_ccnl("chimica-affini-pmi-unionchimica.json")
        lv_h = next(lv for lv in ccnl.levels if lv.code == "H")
        assert lv_h.base_salary.value_at(date(2026, 9, 1)) == Decimal("3168.51")

    def test_chimica_pmi_level_ordering(self) -> None:
        """Level A has lowest order; level H has highest order."""
        ccnl = load_ccnl("chimica-affini-pmi-unionchimica.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "A"
        assert by_order[-1].code == "H"

    def test_chimica_pmi_additional_months(self) -> None:
        """Contract has 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("chimica-affini-pmi-unionchimica.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            13
        )

    def test_chimica_pmi_hourly_divisor(self) -> None:
        """Hourly divisor is 175 (Chimica-Concia sub-sector)."""
        ccnl = load_ccnl("chimica-affini-pmi-unionchimica.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == Decimal(175)

    def test_chimica_pmi_fixed_allowances(self) -> None:
        """H has IND_FUN=160.00; G/F/E have AGG_PERSONALE; A-D have none."""
        ccnl = load_ccnl("chimica-affini-pmi-unionchimica.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        h_codes = [a.code for a in by_code["H"].fixed_allowances]
        assert h_codes == ["IND_FUN"]
        h_val = by_code["H"].fixed_allowances[0].monthly.value_at(date(2026, 9, 1))
        assert h_val == Decimal("160.00")
        for code in ("G", "F", "E"):
            fa = by_code[code].fixed_allowances
            assert len(fa) == 1
            assert fa[0].code == "AGG_PERSONALE"
        for code in ("A", "B", "C", "D"):
            assert by_code[code].fixed_allowances == ()

    def test_chimica_pmi_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("chimica-affini-pmi-unionchimica.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_chimica_pmi_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("chimica-affini-pmi-unionchimica.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadPanificazioneAssipan:
    """Tests for CCNL Panificazione e Settori Affini — Industria (E023)."""

    def test_panif_loads(self) -> None:
        """Contract loads with id panificazione-assipan and CNEL code E023."""
        ccnl = load_ccnl("panificazione-assipan.json")
        assert ccnl.meta.ccnl_id == "panificazione-assipan"
        assert ccnl.meta.cnel_code == "E023"

    def test_panif_has_7_levels(self) -> None:
        """Contract has exactly 7 levels: VI, V, IV, IIIB, IIIA, II, I."""
        ccnl = load_ccnl("panificazione-assipan.json")
        assert len(ccnl.levels) == 7
        assert {lv.code for lv in ccnl.levels} == {
            "I",
            "II",
            "IIIA",
            "IIIB",
            "IV",
            "V",
            "VI",
        }

    def test_panif_level_iiib_salary_2024(self) -> None:
        """Level IIIB base salary at Feb 2024 AFAC tranche is 1822.31 EUR."""
        ccnl = load_ccnl("panificazione-assipan.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "IIIB")
        assert lv.base_salary.value_at(date(2024, 2, 1)) == Decimal("1822.31")

    def test_panif_level_iiib_salary_2026(self) -> None:
        """Level IIIB base salary at Sep 2026 tranche is 2046.31 EUR."""
        ccnl = load_ccnl("panificazione-assipan.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "IIIB")
        assert lv.base_salary.value_at(date(2026, 9, 1)) == Decimal("2046.31")

    def test_panif_level_ordering(self) -> None:
        """Level VI has lowest order; level I has highest order."""
        ccnl = load_ccnl("panificazione-assipan.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "VI"
        assert by_order[-1].code == "I"

    def test_panif_additional_months(self) -> None:
        """Contract has 14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("panificazione-assipan.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            14
        )

    def test_panif_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (verbatim from Art. 50 bis)."""
        ccnl = load_ccnl("panificazione-assipan.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == Decimal(173)

    def test_panif_fixed_allowances_premio(self) -> None:
        """All 7 levels carry PREMIO_PROD fixed allowance (Art. 50 ter)."""
        ccnl = load_ccnl("panificazione-assipan.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "PREMIO_PROD"

    def test_panif_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("panificazione-assipan.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_panif_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("panificazione-assipan.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadTrasportoFerroviarioAgens:
    """Tests for CCNL Attività Ferroviarie AGENS (I320)."""

    def test_trasporto_ferroviario_agens_loads(self) -> None:
        """Contract loads with correct id and CNEL code I320."""
        ccnl = load_ccnl("trasporto-ferroviario-agens.json")
        assert ccnl.meta.ccnl_id == "trasporto-ferroviario-agens"
        assert ccnl.meta.cnel_code == "I320"

    def test_trasporto_ferroviario_agens_has_16_levels(self) -> None:
        """Contract has exactly 16 levels with expected codes."""
        ccnl = load_ccnl("trasporto-ferroviario-agens.json")
        assert len(ccnl.levels) == 16
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "Q1",
            "Q2",
            "A",
            "B1",
            "B2",
            "B3",
            "C1",
            "C2",
            "D1",
            "D2",
            "D3",
            "E1",
            "E2",
            "E3",
            "F1",
            "F2",
        }

    def test_trasporto_ferroviario_agens_level_q2_salary_2025(self) -> None:
        """Q2 base salary at Jun 2025 tranche is 2353.41."""
        ccnl = load_ccnl("trasporto-ferroviario-agens.json")
        q2 = next(lv for lv in ccnl.levels if lv.code == "Q2")
        assert q2.base_salary.value_at(date(2025, 6, 1)) == Decimal("2353.41")

    def test_trasporto_ferroviario_agens_level_q2_salary_2026(self) -> None:
        """Q2 base salary at Jun 2026 tranche is 2483.02."""
        ccnl = load_ccnl("trasporto-ferroviario-agens.json")
        q2 = next(lv for lv in ccnl.levels if lv.code == "Q2")
        assert q2.base_salary.value_at(date(2026, 9, 1)) == Decimal("2483.02")

    def test_trasporto_ferroviario_agens_level_ordering(self) -> None:
        """F2 is lowest-order level; Q1 is highest-order level."""
        ccnl = load_ccnl("trasporto-ferroviario-agens.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "F2"
        assert levels_by_order[-1].code == "Q1"

    def test_trasporto_ferroviario_agens_additional_months(self) -> None:
        """Contract has 14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("trasporto-ferroviario-agens.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            14
        )

    def test_trasporto_ferroviario_agens_hourly_divisor(self) -> None:
        """Hourly divisor is 160 (40h/week contractual regime)."""
        ccnl = load_ccnl("trasporto-ferroviario-agens.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == Decimal(160)

    def test_trasporto_ferroviario_agens_q2_has_ind_fun(self) -> None:
        """Q2 carries IND_FUN fixed allowance of 130.00 (additive to base)."""
        ccnl = load_ccnl("trasporto-ferroviario-agens.json")
        q2 = next(lv for lv in ccnl.levels if lv.code == "Q2")
        assert len(q2.fixed_allowances) == 1
        assert q2.fixed_allowances[0].code == "IND_FUN"
        assert q2.fixed_allowances[0].monthly.value_at(date(2026, 9, 1)) == Decimal(
            "130.00"
        )

    def test_trasporto_ferroviario_agens_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("trasporto-ferroviario-agens.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_trasporto_ferroviario_agens_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 7 scatti."""
        ccnl = load_ccnl("trasporto-ferroviario-agens.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 7
