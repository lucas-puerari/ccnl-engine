"""Bundled CCNL data files load with their expected values.

Covers Forze Polizia Ordinamento Civile, Informatica Pmi Unimatica, Scuole
Private Agidae, Assicurazioni Ania.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl


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
