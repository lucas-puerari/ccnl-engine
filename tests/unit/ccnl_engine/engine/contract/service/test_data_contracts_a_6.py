"""CCNL contract data tests (A): Metalmeccanico through Assicurazioni."""

import importlib.resources
from datetime import date
from decimal import Decimal

from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.contract.service.loaders import load_ccnl

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


class TestLoadTrasportoAereoAssaeroporti:
    """Tests for CCNL Trasporto Aereo — Gestori Aeroportuali (I810)."""

    def test_trasporto_aereo_assaeroporti_loads(self) -> None:
        """Contract loads with correct id and CNEL code I810."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        assert ccnl.meta.ccnl_id == "trasporto-aereo-assaeroporti"
        assert ccnl.meta.cnel_code == "I810"

    def test_trasporto_aereo_assaeroporti_has_11_levels(self) -> None:
        """Contract has exactly 11 levels: 9 through 1S."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"9", "8", "7", "6", "5", "4", "3", "2B", "2A", "1", "1S"}

    def test_trasporto_aereo_assaeroporti_level4_salary_2025(self) -> None:
        """Level 4 base salary at Jan 2025 (pre-Jul tranche) is 1207.47."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        lv4 = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv4.base_salary.value_at(date(2025, 3, 1)) == Decimal("1207.47")

    def test_trasporto_aereo_assaeroporti_level4_salary_2026(self) -> None:
        """Level 4 base salary at Jul 2026 tranche is 1367.47."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        lv4 = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv4.base_salary.value_at(date(2026, 9, 1)) == Decimal("1367.47")

    def test_trasporto_aereo_assaeroporti_level_ordering(self) -> None:
        """Level 9 is lowest-order; level 1S is highest-order."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "9"
        assert levels_by_order[-1].code == "1S"

    def test_trasporto_aereo_assaeroporti_additional_months(self) -> None:
        """Contract has 14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            14
        )

    def test_trasporto_aereo_assaeroporti_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (Art. G28)."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == Decimal(173)

    def test_trasporto_aereo_assaeroporti_split_allowances(self) -> None:
        """Every level carries CONTINGENZA and EDR fixed allowances."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert codes == {"CONTINGENZA", "EDR"}, lv.code

    def test_trasporto_aereo_assaeroporti_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_trasporto_aereo_assaeroporti_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 8 scatti (Art. G23)."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 8

    def test_trasporto_aereo_assaeroporti_level9_seniority_zero(self) -> None:
        """Level 9 seniority amount is 0.00 (Art. G23 table omits level 9)."""
        ccnl = load_ccnl("trasporto-aereo-assaeroporti.json")
        si = ccnl.parameters.seniority_increments
        assert si.amount_by_level["9"].value_at(date(2026, 9, 1)) == Decimal("0.00")


class TestLoadIgieneAmbientaleUtilitalia:
    """Tests for CCNL Igiene Ambientale — Servizi Ambientali (K540)."""

    def test_igiene_ambientale_utilitalia_loads(self) -> None:
        """Contract loads with correct id and CNEL code K540."""
        ccnl = load_ccnl("igiene-ambientale-utilitalia.json")
        assert ccnl.meta.ccnl_id == "igiene-ambientale-utilitalia"
        assert ccnl.meta.cnel_code == "K540"

    def test_igiene_ambientale_utilitalia_has_16_levels(self) -> None:
        """Contract has exactly 16 levels from Q down to D2."""
        ccnl = load_ccnl("igiene-ambientale-utilitalia.json")
        assert len(ccnl.levels) == 16
        codes = {lv.code for lv in ccnl.levels}
        expected = {
            "Q",
            "A1",
            "A2s",
            "A2",
            "B1s",
            "B1",
            "B2s",
            "B2",
            "C1s",
            "C1",
            "C2s",
            "C2",
            "D1s",
            "D1",
            "D2s",
            "D2",
        }
        assert codes == expected

    def test_igiene_ambientale_utilitalia_level_c1s_salary_2026(self) -> None:
        """Level C1s base salary at 01/02/2026 is 2216.13 (post-reclassification)."""
        ccnl = load_ccnl("igiene-ambientale-utilitalia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1s")
        assert lv.base_salary.value_at(date(2026, 2, 1)) == Decimal("2216.13")

    def test_igiene_ambientale_utilitalia_level_c1s_salary_2027(self) -> None:
        """Level C1s base salary at 01/01/2027 (+36) is 2252.13."""
        ccnl = load_ccnl("igiene-ambientale-utilitalia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1s")
        assert lv.base_salary.value_at(date(2027, 1, 1)) == Decimal("2252.13")

    def test_igiene_ambientale_utilitalia_level_ordering(self) -> None:
        """Level D2 is lowest-order (1); level Q is highest-order (16)."""
        ccnl = load_ccnl("igiene-ambientale-utilitalia.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "D2"
        assert levels_by_order[-1].code == "Q"

    def test_igiene_ambientale_utilitalia_additional_months(self) -> None:
        """Contract has 14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("igiene-ambientale-utilitalia.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 6, 1)) == Decimal(
            14
        )

    def test_igiene_ambientale_utilitalia_hourly_divisor(self) -> None:
        """Hourly divisor is 169 (Art. 28)."""
        ccnl = load_ccnl("igiene-ambientale-utilitalia.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1)) == Decimal(169)

    def test_igiene_ambientale_utilitalia_allowances_edr_indemn(self) -> None:
        """Every level carries EDR (10.33) and INDEMN_INT (50.00) allowances."""
        ccnl = load_ccnl("igiene-ambientale-utilitalia.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert codes == {"EDR", "INDEMN_INT"}, lv.code

    def test_igiene_ambientale_utilitalia_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("igiene-ambientale-utilitalia.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_igiene_ambientale_utilitalia_seniority_cadence(self) -> None:
        """Seniority triennale (36m), max 10 globally; B=11, A=12 per level."""
        ccnl = load_ccnl("igiene-ambientale-utilitalia.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10
        assert si.maximum_count_by_level["B1"] == 11
        assert si.maximum_count_by_level["A1"] == 12


class TestLoadImpiegatiTecniciAgricoli:
    """Tests for CCNL Impiegati e Tecnici Agricoli (A021)."""

    def test_impiegati_tecnici_agricoli_loads(self) -> None:
        """Contract loads with correct id and CNEL code A021."""
        ccnl = load_ccnl("impiegati-tecnici-agricoli.json")
        assert ccnl.meta.ccnl_id == "impiegati-tecnici-agricoli"
        assert ccnl.meta.cnel_code == "A021"

    def test_impiegati_tecnici_agricoli_has_7_levels(self) -> None:
        """Contract has exactly 7 levels: 1Q, 1, 2, 3, 4, 5, 6."""
        ccnl = load_ccnl("impiegati-tecnici-agricoli.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1Q", "1", "2", "3", "4", "5", "6"}

    def test_impiegati_tecnici_agricoli_level3_salary_2024(self) -> None:
        """Level 3 base salary from 01/07/2024 is 1417.89 EUR."""
        ccnl = load_ccnl("impiegati-tecnici-agricoli.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 7, 1)) == Decimal("1417.89")

    def test_impiegati_tecnici_agricoli_level1q_salary_2026(self) -> None:
        """Level 1Q base salary at 01/09/2026 is 1788.38 EUR."""
        ccnl = load_ccnl("impiegati-tecnici-agricoli.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1Q")
        assert lv.base_salary.value_at(date(2026, 9, 1)) == Decimal("1788.38")

    def test_impiegati_tecnici_agricoli_level_ordering(self) -> None:
        """Level 6 is lowest-order (1); level 1Q is highest-order (7)."""
        ccnl = load_ccnl("impiegati-tecnici-agricoli.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "6"
        assert levels_by_order[-1].code == "1Q"

    def test_impiegati_tecnici_agricoli_additional_months(self) -> None:
        """Contract has 14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("impiegati-tecnici-agricoli.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            14
        )

    def test_impiegati_tecnici_agricoli_hourly_divisor(self) -> None:
        """Hourly divisor is 169 (39 h/week x 52/12)."""
        ccnl = load_ccnl("impiegati-tecnici-agricoli.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == Decimal(169)

    def test_impiegati_tecnici_agricoli_no_fixed_allowances(self) -> None:
        """Levels 1-6 have no allowances; 1Q has IND_FUN 100.00."""
        ccnl = load_ccnl("impiegati-tecnici-agricoli.json")
        for lv in ccnl.levels:
            if lv.code == "1Q":
                assert len(lv.fixed_allowances) == 1
                assert lv.fixed_allowances[0].code == "IND_FUN"
            else:
                assert lv.fixed_allowances == (), lv.code

    def test_impiegati_tecnici_agricoli_tax_sector(self) -> None:
        """Contract declares AGRICOLTURA tax sector."""
        ccnl = load_ccnl("impiegati-tecnici-agricoli.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_impiegati_tecnici_agricoli_seniority_cadence(self) -> None:
        """Seniority biennale (24m), maximum 12 scatti for all levels."""
        ccnl = load_ccnl("impiegati-tecnici-agricoli.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 12


class TestLoadForzePoliziaOrdinamentoCivile:
    """Tests for DPR 53/2025 — Forze di Polizia ad ordinamento civile."""

    def test_forze_polizia_ordinamento_civile_loads(self) -> None:
        """Contract id and cnel_code match DPR 53/2025 identifier."""
        ccnl = load_ccnl("forze-polizia-ordinamento-civile.json")
        assert ccnl.meta.ccnl_id == "forze-polizia-ordinamento-civile"
        assert ccnl.meta.cnel_code == "N/A"

    def test_forze_polizia_ordinamento_civile_has_21_levels(self) -> None:
        """Contract has exactly 21 qualifiche, codes match DPR 53/2025 Art. 6."""
        ccnl = load_ccnl("forze-polizia-ordinamento-civile.json")
        assert len(ccnl.levels) == 21
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "AGENTE",
            "AGENTE_SCELTO",
            "ASSISTENTE",
            "ASSISTENTE_CAPO",
            "VICE_SOV",
            "ASSISTENTE_CAPO_5A",
            "SOVRINTENDENTE",
            "ASSISTENTE_CAPO_COORD",
            "SOV_CAPO",
            "VICE_ISP",
            "SOV_CAPO_4A",
            "ISPETTORE",
            "SOV_CAPO_COORD",
            "ISP_CAPO",
            "VICE_COMM",
            "ISP_SUPERIORE",
            "ISP_SUP_8A",
            "SOST_COMM",
            "COMMISSARIO",
            "SOST_COMM_COORD",
            "COMM_CAPO",
        }

    def test_forze_polizia_ordinamento_civile_agente_salary_t1(self) -> None:
        """Agente T1 monthly (2022-04-01) = 1611.20 (param 105,25 x 183,6993/12)."""
        ccnl = load_ccnl("forze-polizia-ordinamento-civile.json")
        lv = ccnl.level_by_code("AGENTE")
        assert lv.base_salary.value_at(date(2022, 4, 1)) == Decimal("1611.20")

    def test_forze_polizia_ordinamento_civile_agente_salary_t3(self) -> None:
        """Agente T3 monthly from 2024-01-01 = 1714.70 (param 105,25 x 195,50/12)."""
        ccnl = load_ccnl("forze-polizia-ordinamento-civile.json")
        lv = ccnl.level_by_code("AGENTE")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1714.70")

    def test_forze_polizia_ordinamento_civile_level_ordering(self) -> None:
        """AGENTE order 1, COMM_CAPO order 21; VICE_SOV > ASSISTENTE_CAPO."""
        ccnl = load_ccnl("forze-polizia-ordinamento-civile.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "AGENTE"
        assert levels_by_order[-1].code == "COMM_CAPO"
        # Parameter inversion: Vice Sovrintendente (116.75) > Assistente Capo (116.50)
        # so VICE_SOV must have higher order than ASSISTENTE_CAPO.
        vice_sov = ccnl.level_by_code("VICE_SOV")
        ass_capo = ccnl.level_by_code("ASSISTENTE_CAPO")
        assert vice_sov.order > ass_capo.order

    def test_forze_polizia_ordinamento_civile_additional_months(self) -> None:
        """Contract has 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("forze-polizia-ordinamento-civile.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_forze_polizia_ordinamento_civile_hourly_divisor(self) -> None:
        """Hourly divisor is 156 (36 h/week per DPR 164/2002)."""
        ccnl = load_ccnl("forze-polizia-ordinamento-civile.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_forze_polizia_ordinamento_civile_no_fixed_allowances(self) -> None:
        """All 21 levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("forze-polizia-ordinamento-civile.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == (), lv.code

    def test_forze_polizia_ordinamento_civile_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("forze-polizia-ordinamento-civile.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_forze_polizia_ordinamento_civile_seniority_cadence(self) -> None:
        """No automatic scatti: maximum_count=0 (progression via qualifica)."""
        ccnl = load_ccnl("forze-polizia-ordinamento-civile.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadInformaticaPmiUnimatica:
    """Tests for informatica-pmi-unimatica (CCNL G029 Settore Informatico)."""

    def test_informatica_pmi_unimatica_loads(self) -> None:
        """Contract id and CNEL code are correct."""
        ccnl = load_ccnl("informatica-pmi-unimatica.json")
        assert ccnl.meta.ccnl_id == "informatica-pmi-unimatica"
        assert ccnl.meta.cnel_code == "G029"

    def test_informatica_pmi_unimatica_has_11_levels(self) -> None:
        """Contract has 11 levels: Q and 1 through 10."""
        ccnl = load_ccnl("informatica-pmi-unimatica.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}

    def test_informatica_pmi_unimatica_level5_salary_2025(self) -> None:
        """Level 5 base_salary at Jan 2025 (reference tranche, +60 EUR)."""
        ccnl = load_ccnl("informatica-pmi-unimatica.json")
        lv = next(lev for lev in ccnl.levels if lev.code == "5")
        val = lv.base_salary.value_at(date(2025, 1, 1))
        assert val == Decimal("2005.18")

    def test_informatica_pmi_unimatica_level5_salary_2026(self) -> None:
        """Level 5 base_salary at Jan 2026 (second tranche, +60 EUR)."""
        ccnl = load_ccnl("informatica-pmi-unimatica.json")
        lv = next(lev for lev in ccnl.levels if lev.code == "5")
        val = lv.base_salary.value_at(date(2026, 1, 1))
        assert val == Decimal("2065.18")

    def test_informatica_pmi_unimatica_level_ordering(self) -> None:
        """Q is the highest-order level; level 10 is the lowest."""
        ccnl = load_ccnl("informatica-pmi-unimatica.json")
        by_order = sorted(ccnl.levels, key=lambda lev: lev.order)
        assert by_order[0].code == "10"
        assert by_order[-1].code == "Q"

    def test_informatica_pmi_unimatica_additional_months(self) -> None:
        """Contract has 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("informatica-pmi-unimatica.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_informatica_pmi_unimatica_hourly_divisor(self) -> None:
        """Hourly divisor is 169 (39 h/week from 01/01/2019, Art. 113)."""
        ccnl = load_ccnl("informatica-pmi-unimatica.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(169)

    def test_informatica_pmi_unimatica_no_fixed_allowances(self) -> None:
        """All 11 levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("informatica-pmi-unimatica.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == (), lv.code

    def test_informatica_pmi_unimatica_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector (Confapi)."""
        ccnl = load_ccnl("informatica-pmi-unimatica.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_informatica_pmi_unimatica_seniority_cadence(self) -> None:
        """Seniority: 5 biennial scatti (cadence 24 months, Art. 45)."""
        ccnl = load_ccnl("informatica-pmi-unimatica.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadScuolePrivateAgidae:
    """Tests for scuole-private-agidae (CCNL T241 Scuole Private Religiose)."""

    def test_scuole_private_agidae_loads(self) -> None:
        """Contract id and CNEL code are correct."""
        ccnl = load_ccnl("scuole-private-agidae.json")
        assert ccnl.meta.ccnl_id == "scuole-private-agidae"
        assert ccnl.meta.cnel_code == "T241"

    def test_scuole_private_agidae_has_6_levels(self) -> None:
        """Contract has 6 levels: L1 through L6."""
        ccnl = load_ccnl("scuole-private-agidae.json")
        assert len(ccnl.levels) == 6
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"L1", "L2", "L3", "L4", "L5", "L6"}

    def test_scuole_private_agidae_level_l1_salary_2024(self) -> None:
        """Level L1 base salary at Sep 2024 first tranche."""
        ccnl = load_ccnl("scuole-private-agidae.json")
        lv = next(lev for lev in ccnl.levels if lev.code == "L1")
        val = lv.base_salary.value_at(date(2024, 9, 1))
        assert val == Decimal("1642.99")

    def test_scuole_private_agidae_level_l6_salary_2026(self) -> None:
        """Level L6 base salary at Sep 2026 third tranche."""
        ccnl = load_ccnl("scuole-private-agidae.json")
        lv = next(lev for lev in ccnl.levels if lev.code == "L6")
        val = lv.base_salary.value_at(date(2026, 9, 1))
        assert val == Decimal("2138.71")

    def test_scuole_private_agidae_level_ordering(self) -> None:
        """L1 is lowest order; L6 is highest order."""
        ccnl = load_ccnl("scuole-private-agidae.json")
        by_order = sorted(ccnl.levels, key=lambda lev: lev.order)
        assert by_order[0].code == "L1"
        assert by_order[-1].code == "L6"

    def test_scuole_private_agidae_additional_months(self) -> None:
        """Contract has 13 additional months (tredicesima, Art. 23.6)."""
        ccnl = load_ccnl("scuole-private-agidae.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 9, 1))
        assert val == Decimal(13)

    def test_scuole_private_agidae_hourly_divisor(self) -> None:
        """Hourly divisor is 164 (Art. 49, 38h/week non-teaching staff)."""
        ccnl = load_ccnl("scuole-private-agidae.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1))
        assert val == Decimal(164)

    def test_scuole_private_agidae_no_fixed_allowances(self) -> None:
        """All 6 levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("scuole-private-agidae.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == (), lv.code

    def test_scuole_private_agidae_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("scuole-private-agidae.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_scuole_private_agidae_seniority_cadence(self) -> None:
        """Seniority frozen at 31/12/2005 (Art. 29+32): maximum_count=0."""
        ccnl = load_ccnl("scuole-private-agidae.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadAssicurazioniAnia:
    """Tests for assicurazioni-ania (CCNL J121 ANIA, Rinnovo 13/05/2026)."""

    def test_assicurazioni_ania_loads(self) -> None:
        """Contract id and CNEL code are correct (J121)."""
        ccnl = load_ccnl("assicurazioni-ania.json")
        assert ccnl.meta.ccnl_id == "assicurazioni-ania"
        assert ccnl.meta.cnel_code == "J121"

    def test_assicurazioni_ania_has_7_levels(self) -> None:
        """Contract has 7 levels: L1 through L7."""
        ccnl = load_ccnl("assicurazioni-ania.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"L1", "L2", "L3", "L4", "L5", "L6", "L7"}

    def test_assicurazioni_ania_level_l4_salary_2026(self) -> None:
        """L4 base salary at 01/01/2026 first tranche (Allegato 2/B)."""
        ccnl = load_ccnl("assicurazioni-ania.json")
        lv = ccnl.level_by_code("L4")
        val = lv.base_salary.value_at(date(2026, 1, 1))
        assert val == Decimal("2170.82")

    def test_assicurazioni_ania_level_l4_salary_2027(self) -> None:
        """L4 base salary at 01/01/2027 second tranche (Allegato 2/B)."""
        ccnl = load_ccnl("assicurazioni-ania.json")
        lv = ccnl.level_by_code("L4")
        val = lv.base_salary.value_at(date(2027, 1, 1))
        assert val == Decimal("2256.28")

    def test_assicurazioni_ania_level_ordering(self) -> None:
        """L1 is lowest order; L7 is highest order."""
        ccnl = load_ccnl("assicurazioni-ania.json")
        by_order = sorted(ccnl.levels, key=lambda lev: lev.order)
        assert by_order[0].code == "L1"
        assert by_order[-1].code == "L7"

    def test_assicurazioni_ania_additional_months(self) -> None:
        """Contract has 14 mensilità (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("assicurazioni-ania.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_assicurazioni_ania_hourly_divisor(self) -> None:
        """Hourly divisor is 160 (37h/week, Art. orario CCNL ANIA)."""
        ccnl = load_ccnl("assicurazioni-ania.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(160)

    def test_assicurazioni_ania_fixed_allowances(self) -> None:
        """L4: IND_PROFILO_J (profilo_j); L6: IND_QUADRO_6 (quadro_6); others empty."""
        ccnl = load_ccnl("assicurazioni-ania.json")
        for lv in ccnl.levels:
            if lv.code == "L4":
                assert len(lv.fixed_allowances) == 1
                assert lv.fixed_allowances[0].code == "IND_PROFILO_J"
                assert lv.fixed_allowances[0].role == "profilo_j"
            elif lv.code == "L6":
                assert len(lv.fixed_allowances) == 1
                assert lv.fixed_allowances[0].code == "IND_QUADRO_6"
                assert lv.fixed_allowances[0].role == "quadro_6"
            else:
                assert lv.fixed_allowances == (), lv.code

    def test_assicurazioni_ania_tax_sector(self) -> None:
        """Contract uses CREDITO tax sector (Credito e Assicurazioni)."""
        ccnl = load_ccnl("assicurazioni-ania.json")
        assert ccnl.meta.tax_sector == TaxSector.CREDITO

    def test_assicurazioni_ania_seniority_cadence(self) -> None:
        """Seniority: 48-month first class then 36-month; 11 max advances."""
        ccnl = load_ccnl("assicurazioni-ania.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 11
        assert si.first_cadence_months == 48
        assert si.maximum_count_by_level.get("L7") == 7
