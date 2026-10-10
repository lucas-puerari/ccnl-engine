"""Bundled CCNL data files load with their expected values.

Covers Consorzi Di Bonifica Snebi, Consorzi Agrari Assocap, Organizzazioni
Allevatori Aia, Ortofrutticoli Agrumari, Alimentari Pmi Unionalimentari.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.payroll.service.seniority import seniority_maximum


class TestLoadConsorziDiBonificaSnebi:
    """Tests for CCNL Consorzi di Bonifica (SNEBI) — CNEL A131."""

    def test_consorzi_di_bonifica_snebi_loads(self) -> None:
        """Contract loads with correct id and CNEL code A131."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        assert ccnl.meta.ccnl_id == "consorzi-di-bonifica-snebi"
        assert ccnl.meta.cnel_code == "A131"

    def test_consorzi_di_bonifica_snebi_has_25_levels(self) -> None:
        """Contract has 25 levels including 4 B-sub-levels."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 25
        assert {
            "D100",
            "C127",
            "B128",
            "B128_ex52",
            "B132",
            "B132_ex51",
            "AQ162",
            "AQ187",
        }.issubset(codes)

    def test_consorzi_di_bonifica_snebi_level_c127_salary_jul2025(self) -> None:
        """C127 post-2000 Jul 2025 salary is 1906.71 (redigo.info)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        lv = ccnl.level_by_code("C127")
        assert lv.base_salary.value_at(date(2025, 7, 1)) == Decimal("1906.71")

    def test_consorzi_di_bonifica_snebi_level_c127_salary_jan2026(self) -> None:
        """C127 post-2000 Jan 2026 salary is 1948.38 (redigo.info)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        lv = ccnl.level_by_code("C127")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1948.38")

    def test_consorzi_di_bonifica_snebi_level_ordering(self) -> None:
        """D100 has lowest order (1); AQ187 has highest order (25)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "D100"
        assert by_order[-1].code == "AQ187"

    def test_consorzi_di_bonifica_snebi_additional_months(self) -> None:
        """Contract has 14 mensilita (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_consorzi_di_bonifica_snebi_hourly_divisor(self) -> None:
        """Hourly divisor 164.67 h/month (38h/week, ilccnl.it source)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal("164.67")

    def test_consorzi_di_bonifica_snebi_no_fixed_allowances(self) -> None:
        """All levels have no fixed allowances (contingenza frozen at 0)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_consorzi_di_bonifica_snebi_tax_sector(self) -> None:
        """Contract uses AGRICOLTURA tax sector."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_consorzi_di_bonifica_snebi_seniority_tiers(self) -> None:
        """Ten scatti in three tiers: 6 biennial, 1 dodecennial, 3 quadrennial."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        si = ccnl.parameters.seniority_increments
        assert len(si.tiers) == 3
        assert si.tiers[0].cadence_months == 24
        assert si.tiers[0].maximum_count == 6
        assert si.tiers[1].cadence_months == 144
        assert si.tiers[1].maximum_count == 1
        assert si.tiers[2].cadence_months == 48
        assert si.tiers[2].maximum_count == 3
        assert seniority_maximum(si, "C127") == 10


class TestLoadConsorziAgrariAssocap:
    """Tests for CCNL Consorzi Agrari (ASSOCAP) A141."""

    def test_consorzi_agrari_assocap_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        assert ccnl.meta.ccnl_id == "consorzi-agrari-assocap"
        assert ccnl.meta.cnel_code == "A141"

    def test_consorzi_agrari_assocap_has_9_levels(self) -> None:
        """Contract has 9 levels: Q, 1, 2, 3S, 3, 4S, 4, 5, 6."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 9
        assert codes == {
            "Q",
            "1",
            "2",
            "3S",
            "3",
            "4S",
            "4",
            "5",
            "6",
        }

    def test_consorzi_agrari_assocap_level3_salary_2025(self) -> None:
        """Level 3 paga base Jan 2025: 1529.42 (Wolters Kluwer)."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1529.42")

    def test_consorzi_agrari_assocap_level3_salary_2026(self) -> None:
        """Level 3 paga base Jan 2026: 1574.42 (kitech)."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1574.42")

    def test_consorzi_agrari_assocap_level_ordering(self) -> None:
        """Highest order level is Q; lowest is 6."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "6"
        assert sorted_levels[-1].code == "Q"

    def test_consorzi_agrari_assocap_additional_months(self) -> None:
        """Contract has 14 mensilita (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_consorzi_agrari_assocap_hourly_divisor(self) -> None:
        """Hourly divisor 169 h/month (ilccnl.it source)."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(169)

    def test_consorzi_agrari_assocap_split_model_contingenza(self) -> None:
        """Level 3 has CONTINGENZA fixed allowance of 530.19 EUR/month."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        cont = next(a for a in lv.fixed_allowances if a.code == "CONTINGENZA")
        assert cont.monthly.value_at(date(2026, 1, 1)) == Decimal("530.19")

    def test_consorzi_agrari_assocap_tax_sector(self) -> None:
        """Contract uses AGRICOLTURA tax sector."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_consorzi_agrari_assocap_seniority_cadence(self) -> None:
        """Five biennial scatti per Art. 34 CCNL (FLAI-CGIL PDF)."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadOrganizzazioniAllevatoriAia:
    """Tests for CCNL Organizzazioni Allevatori A221."""

    def test_organizzazioni_allevatori_aia_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        assert ccnl.meta.ccnl_id == "organizzazioni-allevatori-aia"
        assert ccnl.meta.cnel_code == "A221"

    def test_organizzazioni_allevatori_aia_has_13_levels(self) -> None:
        """Contract has 13 levels: 1/2 through 3/2."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 13
        assert codes == {
            "1/2",
            "1/3",
            "1/4",
            "1/5",
            "2/1",
            "2/2",
            "2/3",
            "2/4A",
            "2/4B",
            "2/5",
            "2/6",
            "3/1",
            "3/2",
        }

    def test_organizzazioni_allevatori_aia_level23_salary_sep2025(self) -> None:
        """Level 2/3 minimo Sep 2025: 1895.67 (Wolters Kluwer 2026 ed.)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "2/3")
        assert lv.base_salary.value_at(date(2025, 9, 1)) == Decimal("1895.67")

    def test_organizzazioni_allevatori_aia_level12_salary_sep2025(self) -> None:
        """Level 1/2 minimo Sep 2025: 2392.51 (Wolters Kluwer 2026 ed.)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1/2")
        assert lv.base_salary.value_at(date(2025, 9, 1)) == Decimal("2392.51")

    def test_organizzazioni_allevatori_aia_level_ordering(self) -> None:
        """Highest order level is 1/2; lowest is 3/2."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "3/2"
        assert sorted_levels[-1].code == "1/2"

    def test_organizzazioni_allevatori_aia_additional_months(self) -> None:
        """Contract has 14 mensilita (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_organizzazioni_allevatori_aia_hourly_divisor(self) -> None:
        """Hourly divisor 164.67 h/month (38h/week per Art. 11 CCNL)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal("164.67")

    def test_organizzazioni_allevatori_aia_no_fixed_allowances(self) -> None:
        """All 13 levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_organizzazioni_allevatori_aia_tax_sector(self) -> None:
        """Contract uses AGRICOLTURA tax sector."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_organizzazioni_allevatori_aia_seniority_cadence(self) -> None:
        """Ten biennial scatti per Art. 18 CCNL (FLAI + Confederdia)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 10


class TestLoadOrtofrutticoliAgrumari:
    """Tests for CCNL Ortofrutticoli ed Agrumari Import-Export H341."""

    def test_ortofrutticoli_agrumari_loads(self) -> None:
        """Contract loads with correct id and CNEL code H341."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        assert ccnl.meta.ccnl_id == "ortofrutticoli-agrumari"
        assert ccnl.meta.cnel_code == "H341"

    def test_ortofrutticoli_agrumari_has_9_levels(self) -> None:
        """Contract has exactly 9 levels: Q, 1-5, 6S, 6, 7."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3", "4", "5", "6S", "6", "7"}

    def test_ortofrutticoli_agrumari_level6_salary_tranche1(self) -> None:
        """Level 6 at 2024-09-01 is 1559.53 EUR (confirmed primary source)."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        lv = ccnl.level_by_code("6")
        assert lv.base_salary.value_at(date(2024, 9, 1)) == Decimal("1559.53")

    def test_ortofrutticoli_agrumari_level_q_salary_tranche3(self) -> None:
        """Level Q at 2026-06-01 is 2396.59 EUR (confirmed from kitech.it)."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        lv = ccnl.level_by_code("Q")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("2396.59")

    def test_ortofrutticoli_agrumari_level_ordering(self) -> None:
        """Q is highest-order level; 7 is lowest-order level."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "7"
        assert by_order[-1].code == "Q"

    def test_ortofrutticoli_agrumari_additional_months(self) -> None:
        """Additional months is 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_ortofrutticoli_agrumari_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week, lavoro-economia.it quote)."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_ortofrutticoli_agrumari_level_q_ind_fun(self) -> None:
        """Level Q has IND_FUN allowance of 154.94 EUR/month."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        lv = ccnl.level_by_code("Q")
        codes = {fa.code for fa in lv.fixed_allowances}
        assert "IND_FUN" in codes
        ind = next(fa for fa in lv.fixed_allowances if fa.code == "IND_FUN")
        assert ind.monthly.value_at(date(2026, 6, 1)) == Decimal("154.94")

    def test_ortofrutticoli_agrumari_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_ortofrutticoli_agrumari_seniority_cadence(self) -> None:
        """Seniority: 36-month cadence (triennale), 13 increments maximum."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 13


class TestLoadAlimentariPmiUnionalimentari:
    """Tests for CCNL PMI Alimentare E018 (Unionalimentari-Confapi)."""

    def test_alimentari_pmi_unionalimentari_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        assert ccnl.meta.ccnl_id == "alimentari-pmi-unionalimentari"
        assert ccnl.meta.cnel_code == "E018"

    def test_alimentari_pmi_unionalimentari_has_9_levels(self) -> None:
        """Settore alimentare has exactly 9 levels."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3", "4", "5", "6", "7", "8"}

    def test_alimentari_pmi_unionalimentari_level4_salary_jun2025(self) -> None:
        """Level 4 paga base Jun 2025: 1672.78 (Unionalimentari circular)."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2025, 6, 1)) == Decimal("1672.78")

    def test_alimentari_pmi_unionalimentari_level4_salary_jan2026(self) -> None:
        """Level 4 paga base Jan 2026: 1746.87 (Unionalimentari circular)."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1746.87")

    def test_alimentari_pmi_unionalimentari_level_ordering(self) -> None:
        """Highest order level is Q; lowest is 8."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "8"
        assert sorted_levels[-1].code == "Q"

    def test_alimentari_pmi_unionalimentari_additional_months(self) -> None:
        """Contract has 14 mensilita (Art. 4.1 CCNL text)."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_alimentari_pmi_unionalimentari_hourly_divisor(self) -> None:
        """Hourly divisor 173 h/month (Art. 4.3 CCNL text)."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(173)

    def test_alimentari_pmi_unionalimentari_split_allowances(self) -> None:
        """All 9 levels carry CONTINGENZA and EDR allowances (split model)."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert codes == {"CONTINGENZA", "EDR"}

    def test_alimentari_pmi_unionalimentari_tax_sector(self) -> None:
        """Contract uses INDUSTRIA tax sector."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_alimentari_pmi_unionalimentari_seniority_cadence(self) -> None:
        """Five biennial scatti per Art. 5.5 CCNL text."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5
