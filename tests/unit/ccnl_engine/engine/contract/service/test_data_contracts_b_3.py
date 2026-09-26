"""CCNL contract data tests (B): Energia through ServiziAmministrativi."""

from datetime import date
from decimal import Decimal

from ccnl_engine.engine.contract.domain.category import WorkerCategory
from ccnl_engine.engine.contract.domain.identity import TaxSector
from ccnl_engine.engine.contract.service.loaders import load_ccnl


class TestLoadRecapitoCorrispondenzaFise:
    """Tests for CCNL Recapito Corrispondenza FISE-ARE (K711)."""

    def test_recapito_corrispondenza_fise_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert ccnl.meta.ccnl_id == "recapito-corrispondenza-fise"
        assert ccnl.meta.cnel_code == "K711"

    def test_recapito_corrispondenza_fise_has_8_levels(self) -> None:
        """Contract has exactly 8 levels with codes 1,2,3S,3,4,5S,5,6."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3S", "3", "4", "5S", "5", "6"}

    def test_recapito_corrispondenza_fise_level3_salary_feb2024(self) -> None:
        """Level 3 base salary at 2024-02-01: 1567.29 EUR (1st tranche)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 2, 1)) == Decimal("1567.29")

    def test_recapito_corrispondenza_fise_level3_salary_jun2026(self) -> None:
        """Level 3 base salary at 2026-06-01: 1687.29 EUR (4th tranche)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("1687.29")

    def test_recapito_corrispondenza_fise_level_ordering(self) -> None:
        """Level 1 is highest; level 6 is lowest."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "6"
        assert ordered[-1].code == "1"

    def test_recapito_corrispondenza_fise_additional_months(self) -> None:
        """14 mensilita: tredicesima + quattordicesima."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_recapito_corrispondenza_fise_hourly_divisor(self) -> None:
        """Hourly divisor 173 (confirmed from ilccnl.it cross-check)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 173

    def test_recapito_corrispondenza_fise_edr_allowance(self) -> None:
        """All 8 levels have EDR=10.33 as fixed_allowance (split model)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "EDR"

    def test_recapito_corrispondenza_fise_tax_sector(self) -> None:
        """tax_sector == TERZIARIO."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_recapito_corrispondenza_fise_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), max 8 scatti."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 8


class TestLoadServiziPostaliAppaltoFise:
    """Tests for CCNL Servizi Postali in Appalto (FISE-ARE, K721)."""

    def test_servizi_postali_appalto_fise_loads(self) -> None:
        """Contract loads with correct id and CNEL code K721."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert ccnl.meta.ccnl_id == "servizi-postali-appalto-fise"
        assert ccnl.meta.cnel_code == "K721"

    def test_servizi_postali_appalto_fise_has_7_levels(self) -> None:
        """7 levels: 1, 2, 3S, 3, 4S, 4, 5."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3S", "3", "4S", "4", "5"}

    def test_servizi_postali_appalto_fise_level3_salary_jan2024(self) -> None:
        """Level 3 base salary at 2024-01-01: 1448.09 EUR (1st tranche)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1448.09")

    def test_servizi_postali_appalto_fise_level3_salary_dec2025(self) -> None:
        """Level 3 base salary at 2025-12-01: 1509.09 EUR (3rd tranche)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2025, 12, 1)) == Decimal("1509.09")

    def test_servizi_postali_appalto_fise_level_ordering(self) -> None:
        """Level 1 is highest (order=7); level 5 is lowest (order=1)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "5"
        assert ordered[-1].code == "1"

    def test_servizi_postali_appalto_fise_additional_months(self) -> None:
        """14 mensilita: tredicesima (Art. 37) + quattordicesima (Art. 38)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_servizi_postali_appalto_fise_hourly_divisor(self) -> None:
        """Hourly divisor 173 (Art. 33 explicit)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 173

    def test_servizi_postali_appalto_fise_fixed_allowances(self) -> None:
        """All 7 levels have IND-INT and EDR as fixed allowances (split model)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert codes == {"IND-INT", "EDR"}

    def test_servizi_postali_appalto_fise_tax_sector(self) -> None:
        """tax_sector == TERZIARIO."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_servizi_postali_appalto_fise_seniority_cadence(self) -> None:
        """Seniority: biennale (24 mo), max=10, first at 48 mo (impiegati)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 10
        assert si.first_cadence_months == 48

    def test_servizi_postali_appalto_fise_operaio_seniority_max_1(self) -> None:
        """Operaio maximum_count=1 (Art. 35A single premio)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        si = ccnl.parameters.seniority_increments
        assert si.maximum_count_by_category.get(WorkerCategory.OPERAIO) == 1

    def test_servizi_postali_appalto_fise_seniority_category_amounts(
        self,
    ) -> None:
        """Operaio and impiegato have different seniority amounts at L2."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        si = ccnl.parameters.seniority_increments
        op = si.amount_by_level_by_category[WorkerCategory.OPERAIO]["2"]
        imp = si.amount_by_level_by_category[WorkerCategory.IMPIEGATO]["2"]
        assert op.value_at(date(2026, 1, 1)) == Decimal("56.66")
        assert imp.value_at(date(2026, 1, 1)) == Decimal("62.62")


class TestLoadPortieriFabbricatiConfedilizia:
    """Tests for CCNL Dipendenti da Proprietari di Fabbricati (H401)."""

    def test_portieri_fabbricati_confedilizia_loads(self) -> None:
        """Contract loads with correct id and CNEL code H401."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert ccnl.meta.ccnl_id == "portieri-fabbricati-confedilizia"
        assert ccnl.meta.cnel_code == "H401"

    def test_portieri_fabbricati_confedilizia_has_11_levels(self) -> None:
        """11 levels: B1-B5, C3, C4, D1-D4 (A and C1/C2 excluded)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "B1",
            "B2",
            "B3",
            "B4",
            "B5",
            "C3",
            "C4",
            "D1",
            "D2",
            "D3",
            "D4",
        }

    def test_portieri_fabbricati_confedilizia_level_b1_salary_2026(
        self,
    ) -> None:
        """B1 base salary at 2026-01-01: 1519.10 EUR (1st tranche)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B1")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1519.10")

    def test_portieri_fabbricati_confedilizia_level_c3_salary_2028(
        self,
    ) -> None:
        """C3 base salary at 2028-01-01: 1868.50 EUR (3rd tranche)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C3")
        assert lv.base_salary.value_at(date(2028, 1, 1)) == Decimal("1868.50")

    def test_portieri_fabbricati_confedilizia_level_ordering(self) -> None:
        """C3 is highest (order=11); B5 is lowest (order=1)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "B5"
        assert ordered[-1].code == "C3"

    def test_portieri_fabbricati_confedilizia_additional_months(self) -> None:
        """13 mensilita: tredicesima only (Art. 130 Gratifica natalizia)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 6, 1))
        assert val == Decimal(13)

    def test_portieri_fabbricati_confedilizia_hourly_divisor(self) -> None:
        """Hourly divisor 173 (40 h/week, Art. 60/62/69 CCNL)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1)) == 173

    def test_portieri_fabbricati_confedilizia_no_fixed_allowances(
        self,
    ) -> None:
        """All 11 levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_portieri_fabbricati_confedilizia_tax_sector(self) -> None:
        """tax_sector == TERZIARIO."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_portieri_fabbricati_confedilizia_seniority_cadence(self) -> None:
        """Seniority: triennale (36 mo), max=12 scatti."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 12


class TestLoadMetalmeccanicaCooperative:
    """Tests for CCNL Metalmeccanica - Cooperative (C016)."""

    def test_metalmeccanica_cooperative_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        assert ccnl.meta.ccnl_id == "metalmeccanica-cooperative"
        assert ccnl.meta.cnel_code == "C016"

    def test_metalmeccanica_cooperative_has_9_levels(self) -> None:
        """Contract has exactly 9 levels with correct codes."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"D1", "D2", "C1", "C2", "C3", "B1", "B2", "B3", "A1"}

    def test_metalmeccanica_cooperative_level_d1_salary_2025(self) -> None:
        """D1 base salary at first tranche (2025-06-01)."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        d1 = next(lv for lv in ccnl.levels if lv.code == "D1")
        assert d1.base_salary.value_at(date(2025, 6, 1)) == Decimal("1754.06")

    def test_metalmeccanica_cooperative_level_a1_salary_2026(self) -> None:
        """A1 base salary at second tranche (2026-06-01)."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        a1 = next(lv for lv in ccnl.levels if lv.code == "A1")
        assert a1.base_salary.value_at(date(2026, 6, 1)) == Decimal("3054.52")

    def test_metalmeccanica_cooperative_level_ordering(self) -> None:
        """A1 is the highest-order level; D1 is the lowest."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "D1"
        assert by_order[-1].code == "A1"

    def test_metalmeccanica_cooperative_additional_months(self) -> None:
        """Contract provides 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 6, 1)) == Decimal(
            13
        )

    def test_metalmeccanica_cooperative_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week, metalmeccanici standard)."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1)) == Decimal(173)

    def test_metalmeccanica_cooperative_fixed_allowances(self) -> None:
        """A1 and B3 have IND_FUN allowances; all others have none."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        a1 = next(lv for lv in ccnl.levels if lv.code == "A1")
        b3 = next(lv for lv in ccnl.levels if lv.code == "B3")
        c2 = next(lv for lv in ccnl.levels if lv.code == "C2")
        assert len(a1.fixed_allowances) == 1
        assert a1.fixed_allowances[0].code == "IND_FUN"
        assert a1.fixed_allowances[0].monthly.value_at(date(2026, 6, 1)) == Decimal(
            "180.00"
        )
        assert len(b3.fixed_allowances) == 1
        assert b3.fixed_allowances[0].monthly.value_at(date(2026, 6, 1)) == Decimal(
            "120.00"
        )
        assert c2.fixed_allowances == ()

    def test_metalmeccanica_cooperative_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_metalmeccanica_cooperative_seniority_cadence(self) -> None:
        """Seniority increments: biennali (24 months), max 5."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadScuolePrivatelaicheAninsei:
    """Tests for CCNL Scuole Private Laiche ANINSEI (T231)."""

    def test_scuole_private_laiche_aninsei_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        assert ccnl.meta.ccnl_id == "scuole-private-laiche-aninsei"
        assert ccnl.meta.cnel_code == "T231"

    def test_scuole_private_laiche_aninsei_has_9_levels(self) -> None:
        """Contract has exactly 9 levels with the expected codes."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"I", "II", "III", "IV", "V", "VI", "VII", "VIII_A", "VIII_B"}

    def test_scuole_private_laiche_aninsei_level4_salary_2024(self) -> None:
        """Level IV base salary at first tranche (2024-06-15) = 1397.56 EUR."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        lv = next(x for x in ccnl.levels if x.code == "IV")
        assert lv.base_salary.value_at(date(2024, 6, 15)) == Decimal("1397.56")

    def test_scuole_private_laiche_aninsei_level4_salary_2026(self) -> None:
        """Level IV base salary at third tranche (2026-01-01) = 1491.38 EUR."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        lv = next(x for x in ccnl.levels if x.code == "IV")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1491.38")

    def test_scuole_private_laiche_aninsei_level_ordering(self) -> None:
        """Lowest order is I (1), highest order is VIII_B (9)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "I"
        assert by_order[-1].code == "VIII_B"

    def test_scuole_private_laiche_aninsei_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_scuole_private_laiche_aninsei_hourly_divisor(self) -> None:
        """Hourly divisor = 165 (38h/week, Art. 27)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_scuole_private_laiche_aninsei_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_scuole_private_laiche_aninsei_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_scuole_private_laiche_aninsei_seniority_cadence(self) -> None:
        """Seniority frozen: maximum_count=0 (milestone-based, Art. 24)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadIstituzioniServiziSocioAssistenzialiAnaste:
    """Tests for CCNL Istituzioni e Servizi Socio-Assistenziali ANASTE (T131)."""

    def test_anaste_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        assert ccnl.meta.ccnl_id == "istituzioni-servizi-socio-assistenziali-anaste"
        assert ccnl.meta.cnel_code == "T131"

    def test_anaste_has_12_levels(self) -> None:
        """Contract has exactly 12 levels with the expected codes."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        assert len(ccnl.levels) == 12
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "10", "9", "8", "7", "6", "5", "4", "3S", "3", "2", "1"}

    def test_anaste_level6_salary_pre2025(self) -> None:
        """Level 6 base salary before 2025-08-01 = 1604.06 EUR (Art. 69)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        lv = next(x for x in ccnl.levels if x.code == "6")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1604.06")

    def test_anaste_level6_salary_2025(self) -> None:
        """Level 6 base salary from 2025-08-01 = 1696.37 EUR (CCNL rinnovo)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        lv = next(x for x in ccnl.levels if x.code == "6")
        assert lv.base_salary.value_at(date(2025, 8, 1)) == Decimal("1696.37")

    def test_anaste_level_ordering(self) -> None:
        """Lowest order is level 1 (order=1), highest is Q (order=12)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_anaste_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only, Art. 74)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        assert ccnl.parameters.additional_months.value_at(date(2025, 8, 1)) == Decimal(
            13
        )

    def test_anaste_hourly_divisor(self) -> None:
        """Hourly divisor = 164 (38h/week, Art. 72)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2025, 8, 1)) == Decimal(164)

    def test_anaste_level_q_fixed_allowance(self) -> None:
        """Level Q has indennita di funzione 77.47 EUR/month (Art. 70)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        lv_q = next(x for x in ccnl.levels if x.code == "Q")
        assert len(lv_q.fixed_allowances) == 1
        fa = lv_q.fixed_allowances[0]
        assert fa.code == "INDENNITA_FUNZIONE"
        assert fa.monthly.value_at(date(2025, 8, 1)) == Decimal("77.47")

    def test_anaste_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_anaste_seniority_cadence(self) -> None:
        """Seniority: cadence 36 months, max 10 scatti (Art. 73)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadScuoleMaternieFism:
    """Tests for CCNL Scuole Materne FISM (T271)."""

    def test_fism_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        assert ccnl.meta.ccnl_id == "scuole-materne-fism"
        assert ccnl.meta.cnel_code == "T271"

    def test_fism_has_8_levels(self) -> None:
        """Contract has exactly 8 levels with codes I through VIII."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"I", "II", "III", "IV", "V", "VI", "VII", "VIII"}

    def test_fism_level5_salary_2023(self) -> None:
        """Level V base salary at first tranche (2023-09-01) = 1564.87 EUR."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        lv = next(x for x in ccnl.levels if x.code == "V")
        assert lv.base_salary.value_at(date(2023, 9, 1)) == Decimal("1564.87")

    def test_fism_level5_salary_2026(self) -> None:
        """Level V base salary from 2026-09-01 (accord tranche) = 1679.76 EUR."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        lv = next(x for x in ccnl.levels if x.code == "V")
        assert lv.base_salary.value_at(date(2026, 9, 1)) == Decimal("1679.76")

    def test_fism_level_ordering(self) -> None:
        """Lowest order is I (1), highest order is VIII (8)."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "I"
        assert by_order[-1].code == "VIII"

    def test_fism_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only, Art. 49)."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            13
        )

    def test_fism_hourly_divisor(self) -> None:
        """Hourly divisor = 160 (37h/week, Art. 51)."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == Decimal(160)

    def test_fism_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_fism_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_fism_seniority_frozen(self) -> None:
        """Seniority frozen: maximum_count=0 (historic scatti frozen, Arts. 44-46)."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadOcchialiOcchialeriaIndustria:
    """Tests for D271 CCNL Occhiali e Occhialeria — Industria (ANFAO)."""

    def test_occhiali_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        assert ccnl.meta.ccnl_id == "occhiali-occhialeria-industria"
        assert ccnl.meta.cnel_code == "D271"

    def test_occhiali_has_10_levels(self) -> None:
        """Contract has exactly 10 levels with correct codes."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "3S", "4", "4S", "5", "5S", "6", "Q"}

    def test_occhiali_level4_salary_2023(self) -> None:
        """Level 4 tabular minimum at 01/05/2023 first tranche = 1887.96."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2023, 5, 1)) == Decimal("1887.96")

    def test_occhiali_level4_salary_2026(self) -> None:
        """Level 4 tabular minimum at 01/03/2026 renewal tranche = 2042.96."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2026, 3, 1)) == Decimal("2042.96")

    def test_occhiali_level_ordering(self) -> None:
        """Q is highest order (10); level 1 is lowest order (1)."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_occhiali_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only)."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 3, 1)) == Decimal(
            13
        )

    def test_occhiali_hourly_divisor(self) -> None:
        """Hourly divisor = 173 (standard 40h/week)."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 3, 1)) == Decimal(173)

    def test_occhiali_level_q_fixed_allowance(self) -> None:
        """Level Q carries INDENNITA_FUNZIONE allowance of 82.63 EUR/month."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "Q")
        assert len(lv.fixed_allowances) == 1
        fa = lv.fixed_allowances[0]
        assert fa.code == "INDENNITA_FUNZIONE"
        assert fa.monthly.value_at(date(2026, 3, 1)) == Decimal("82.63")

    def test_occhiali_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_occhiali_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence, max 5 scatti biennali."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_occhiali_non_q_no_fixed_allowances(self) -> None:
        """Conglobated model: all non-Q levels have no fixed allowances."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        for lv in ccnl.levels:
            if lv.code != "Q":
                assert lv.fixed_allowances == ()


class TestLoadCementoCalceGessoIndustria:
    """Tests for F032 CCNL Cemento, Calce e Gesso — Industria (Federbeton)."""

    def test_cemento_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        assert ccnl.meta.ccnl_id == "cemento-calce-gesso-industria"
        assert ccnl.meta.cnel_code == "F032"

    def test_cemento_has_12_levels(self) -> None:
        """Contract has exactly 12 levels with correct codes."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        assert len(ccnl.levels) == 12
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "AE1",
            "AQ1",
            "AQ2",
            "AS1",
            "AS2",
            "AS3",
            "AC1",
            "AC2",
            "AC3",
            "AD1",
            "AD2",
            "AD3",
        }

    def test_cemento_level_as3_salary_2024(self) -> None:
        """AS3 paga base at 31/12/2024 pre-renewal base = 1631.82."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "AS3")
        assert lv.base_salary.value_at(date(2024, 12, 31)) == Decimal("1631.82")

    def test_cemento_level_as3_salary_2025(self) -> None:
        """AS3 paga base at 01/10/2025 first renewal tranche = 1691.82."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "AS3")
        assert lv.base_salary.value_at(date(2025, 10, 1)) == Decimal("1691.82")

    def test_cemento_level_ordering(self) -> None:
        """AD3 is highest order (12); AE1 is lowest order (1)."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "AE1"
        assert by_order[-1].code == "AD3"

    def test_cemento_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only)."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        assert ccnl.parameters.additional_months.value_at(date(2025, 10, 1)) == Decimal(
            13
        )

    def test_cemento_hourly_divisor(self) -> None:
        """Hourly divisor = 175."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2025, 10, 1)) == Decimal(
            175
        )

    def test_cemento_split_model_allowances(self) -> None:
        """Split model: all levels carry CONTINGENZA and EDR fixed allowances."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
            assert "EDR" in codes

    def test_cemento_edr_uniform(self) -> None:
        """EDR = 10.33 EUR/month across all 12 levels."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        for lv in ccnl.levels:
            edr = next(fa for fa in lv.fixed_allowances if fa.code == "EDR")
            assert edr.monthly.value_at(date(2025, 10, 1)) == Decimal("10.33")

    def test_cemento_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_cemento_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence, max 5 scatti biennali (Art. 48)."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_cemento_level_ad3_fixed_allowances(self) -> None:
        """AD3 (Quadro) has INDENNITA_FUNZIONE = 41.32 EUR/month."""
        ccnl = load_ccnl("cemento-calce-gesso-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "AD3")
        fn = next(
            (fa for fa in lv.fixed_allowances if fa.code == "INDENNITA_FUNZIONE"),
            None,
        )
        assert fn is not None
        assert fn.monthly.value_at(date(2025, 10, 1)) == Decimal("41.32")


class TestLoadLapideiIndustria:
    """Tests for CCNL Lapidei — Industria (F041)."""

    def test_lapidei_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("lapidei-industria.json")
        assert ccnl.meta.ccnl_id == "lapidei-industria"
        assert ccnl.meta.cnel_code == "F041"

    def test_lapidei_has_8_levels(self) -> None:
        """Contract has exactly 8 levels: F, E, D, C, CS, B, A, AS."""
        ccnl = load_ccnl("lapidei-industria.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"F", "E", "D", "C", "CS", "B", "A", "AS"}

    def test_lapidei_level_c_salary_2025(self) -> None:
        """Level C paga base at 01/01/2025: 1502.64 EUR."""
        ccnl = load_ccnl("lapidei-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1502.64")

    def test_lapidei_level_c_salary_2026(self) -> None:
        """Level C paga base at 01/07/2026: 1662.64 EUR."""
        ccnl = load_ccnl("lapidei-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C")
        assert lv.base_salary.value_at(date(2026, 7, 1)) == Decimal("1662.64")

    def test_lapidei_level_ordering(self) -> None:
        """Level F is lowest order (1) and AS is highest order (8)."""
        ccnl = load_ccnl("lapidei-industria.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "F"
        assert ordered[-1].code == "AS"

    def test_lapidei_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("lapidei-industria.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 7, 1)) == Decimal(
            13
        )

    def test_lapidei_hourly_divisor(self) -> None:
        """Hourly divisor: 174."""
        ccnl = load_ccnl("lapidei-industria.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 7, 1)) == Decimal(174)

    def test_lapidei_split_model_allowances(self) -> None:
        """All levels have exactly CONTINGENZA and EDR fixed allowances."""
        ccnl = load_ccnl("lapidei-industria.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert codes == {"CONTINGENZA", "EDR"}

    def test_lapidei_edr_uniform(self) -> None:
        """EDR is 10.33 EUR/month across all levels."""
        ccnl = load_ccnl("lapidei-industria.json")
        for lv in ccnl.levels:
            edr = next(fa for fa in lv.fixed_allowances if fa.code == "EDR")
            assert edr.monthly.value_at(date(2026, 7, 1)) == Decimal("10.33")

    def test_lapidei_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("lapidei-industria.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_lapidei_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence, max 5 scatti biennali."""
        ccnl = load_ccnl("lapidei-industria.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_lapidei_level_f_contingenza(self) -> None:
        """Level F contingenza frozen at 512.38 EUR/month."""
        ccnl = load_ccnl("lapidei-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "F")
        cont = next(fa for fa in lv.fixed_allowances if fa.code == "CONTINGENZA")
        assert cont.monthly.value_at(date(2026, 7, 1)) == Decimal("512.38")


class TestLoadMarittimiIndustriaArmatoriale:
    """Tests for CCNL Marittimi — Industria Armatoriale (I391)."""

    def test_marittimi_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        assert ccnl.meta.ccnl_id == "marittimi-industria-armatoriale"
        assert ccnl.meta.cnel_code == "I391"

    def test_marittimi_has_8_levels(self) -> None:
        """Contract has 8 levels: I, II, III, IV, V, VI, VII, VIIQ."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"I", "II", "III", "IV", "V", "VI", "VII", "VIIQ"}

    def test_marittimi_level_iv_salary_2024(self) -> None:
        """Level IV minimo at 01/07/2024 (first tranche) = 1891.66 EUR."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "IV")
        assert lv.base_salary.value_at(date(2024, 7, 1)) == Decimal("1891.66")

    def test_marittimi_level_iv_salary_2026(self) -> None:
        """Level IV minimo at 01/07/2026 (third tranche) = 1989.32 EUR."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "IV")
        assert lv.base_salary.value_at(date(2026, 7, 1)) == Decimal("1989.32")

    def test_marittimi_level_ordering(self) -> None:
        """Level I is lowest order (1) and VIIQ is highest order (8)."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "I"
        assert ordered[-1].code == "VIIQ"

    def test_marittimi_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 7, 1)) == Decimal(
            14
        )

    def test_marittimi_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (Art. 10 para 8)."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 7, 1)) == Decimal(173)

    def test_marittimi_ear_allowance_all_levels(self) -> None:
        """All 8 levels carry an EAR fixed allowance."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "EAR" in codes

    def test_marittimi_ear_increasing(self) -> None:
        """EAR at level I increases across tranches: 18.40 -> 32.20 -> 46.01."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "I")
        ear = next(fa for fa in lv.fixed_allowances if fa.code == "EAR")
        assert ear.monthly.value_at(date(2024, 7, 1)) == Decimal("18.40")
        assert ear.monthly.value_at(date(2025, 7, 1)) == Decimal("32.20")
        assert ear.monthly.value_at(date(2026, 7, 1)) == Decimal("46.01")

    def test_marittimi_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_marittimi_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence, max 5 scatti biennali."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_marittimi_viiq_indennita_funzione(self) -> None:
        """VIIQ carries INDENNITA_FUNZIONE of 225.00 EUR/month (fixed)."""
        ccnl = load_ccnl("marittimi-industria-armatoriale.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "VIIQ")
        fn = next(
            (fa for fa in lv.fixed_allowances if fa.code == "INDENNITA_FUNZIONE"),
            None,
        )
        assert fn is not None
        assert fn.monthly.value_at(date(2026, 7, 1)) == Decimal("225.00")


class TestLoadIndustriaTuristicaFederturismo:
    """Tests for CCNL Industria Turistica — Federturismo (H05B)."""

    def test_h05b_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        assert ccnl.meta.ccnl_id == "industria-turistica-federturismo"
        assert ccnl.meta.cnel_code == "H05B"

    def test_h05b_has_9_levels(self) -> None:
        """Contract has exactly 9 levels."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 9
        assert codes == {"D2", "D1", "C3", "C2", "C1", "B2", "B1", "A2", "A1"}

    def test_h05b_level_c1_salary_2025(self) -> None:
        """Level C1 base salary at 2025-01-01 is 1739.43 EUR."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1739.43")

    def test_h05b_level_c1_salary_2026(self) -> None:
        """Level C1 base salary at 2026-05-01 is 1808.30 EUR."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        assert lv.base_salary.value_at(date(2026, 5, 1)) == Decimal("1808.30")

    def test_h05b_level_ordering(self) -> None:
        """D2 is lowest order (1), A1 is highest order (9)."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "D2"
        assert levels_by_order[-1].code == "A1"

    def test_h05b_additional_months(self) -> None:
        """Additional months is 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 5, 1)) == Decimal(
            14
        )

    def test_h05b_hourly_divisor(self) -> None:
        """Hourly divisor is 172."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 5, 1)) == Decimal(172)

    def test_h05b_d2_no_fixed_allowances(self) -> None:
        """Level D2 has no fixed allowances (conglobated)."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "D2")
        assert lv.fixed_allowances == ()

    def test_h05b_a1_indennita_funzione(self) -> None:
        """Level A1 has function allowance of 75.00 EUR/month at 14 months."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "A1")
        fa = next(
            fa for fa in lv.fixed_allowances if fa.code == "INDENNITA_FUNZIONE_A1"
        )
        assert fa.monthly.value_at(date(2026, 5, 1)) == Decimal("75.00")
        assert fa.months_per_year == 14

    def test_h05b_a2_indennita_funzione(self) -> None:
        """Level A2 has function allowance of 70.00 EUR/month at 14 months."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "A2")
        fa = next(
            fa for fa in lv.fixed_allowances if fa.code == "INDENNITA_FUNZIONE_A2"
        )
        assert fa.monthly.value_at(date(2026, 5, 1)) == Decimal("70.00")
        assert fa.months_per_year == 14

    def test_h05b_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_h05b_seniority_cadence(self) -> None:
        """Seniority: 36-month cadence, maximum 6 scatti."""
        ccnl = load_ccnl("industria-turistica-federturismo.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 6
