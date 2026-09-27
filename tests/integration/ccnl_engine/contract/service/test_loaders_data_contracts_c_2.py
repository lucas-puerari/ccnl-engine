"""Bundled CCNL data files load with their expected values.

Covers Edilizia Pmi Confapi Aniem, Edilizia Cooperative Ancpl, Metalmeccanico
Confimi Pmi, Noleggio Autobus Conducente Anav, Materiali Costruzione Lapidei
Confapi.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl


class TestLoadEdiliziaPmiConfapiAniem:
    """Unit tests for edilizia-pmi-confapi-aniem.json (CNEL F018)."""

    def test_edilizia_pmi_confapi_aniem_loads(self) -> None:
        """Contract loads with correct id and CNEL code F018."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        assert ccnl.meta.ccnl_id == "edilizia-pmi-confapi-aniem"
        assert ccnl.meta.cnel_code == "F018"

    def test_edilizia_pmi_confapi_aniem_has_7_levels(self) -> None:
        """Seven levels: 1, 2, 3, 4, 5, 6, 7."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7"}

    def test_edilizia_pmi_confapi_aniem_level4_salary_2025(self) -> None:
        """Level 4 base salary at 01/04/2025 tranche: 1523.17 EUR."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2025, 4, 1)) == Decimal("1523.17")

    def test_edilizia_pmi_confapi_aniem_level4_salary_2027(self) -> None:
        """Level 4 base salary at 01/03/2027 tranche: 1628.17 EUR."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2027, 3, 1)) == Decimal("1628.17")

    def test_edilizia_pmi_confapi_aniem_level_ordering(self) -> None:
        """Level 1 has lowest order; level 7 has highest order."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "7"

    def test_edilizia_pmi_confapi_aniem_additional_months(self) -> None:
        """Tredicesima only: 13 additional months."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        assert ccnl.parameters.additional_months.value_at(date(2025, 4, 1)) == Decimal(
            13
        )

    def test_edilizia_pmi_confapi_aniem_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (Art. 25 CCNL, 40h/week)."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2025, 4, 1)) == Decimal(173)

    def test_edilizia_pmi_confapi_aniem_split_model_fixed_allowances(self) -> None:
        """All levels carry CONTINGENZA + EDR (split salary model)."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
            assert "EDR" in codes

    def test_edilizia_pmi_confapi_aniem_tax_sector(self) -> None:
        """Tax sector is edilizia."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        assert ccnl.meta.tax_sector == TaxSector.EDILIZIA

    def test_edilizia_pmi_confapi_aniem_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), max 5 increments (Art. 49)."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadEdiliziaCooperativeAncpl:
    """Unit tests for CCNL Edilizia Cooperative ANCPL (F016)."""

    def test_edilizia_cooperative_ancpl_loads(self) -> None:
        """Contract loads with correct id and CNEL code F016."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        assert ccnl.meta.ccnl_id == "edilizia-cooperative-ancpl"
        assert ccnl.meta.cnel_code == "F016"

    def test_edilizia_cooperative_ancpl_has_10_levels(self) -> None:
        """Contract has 10 levels including Q variants."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7", "7Q", "8", "8Q"}

    def test_edilizia_cooperative_ancpl_level4_salary_t1(self) -> None:
        """Level 4 paga base is 1485.49 EUR at T1 tranche (01/02/2025)."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        lv4 = next(lv for lv in ccnl.levels if lv.code == "4")
        period = next(
            p
            for p in lv4.base_salary.periods
            if p.valid_from.isoformat() == "2025-02-01"
        )
        assert period.value == Decimal("1485.49")

    def test_edilizia_cooperative_ancpl_level4_salary_t2(self) -> None:
        """Level 4 paga base is 1553.74 EUR at T2 tranche (01/03/2026)."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        lv4 = next(lv for lv in ccnl.levels if lv.code == "4")
        period = next(
            p
            for p in lv4.base_salary.periods
            if p.valid_from.isoformat() == "2026-03-01"
        )
        assert period.value == Decimal("1553.74")

    def test_edilizia_cooperative_ancpl_level4_salary_t3(self) -> None:
        """Level 4 paga base is 1621.99 EUR at T3 tranche (01/03/2027)."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        lv4 = next(lv for lv in ccnl.levels if lv.code == "4")
        period = next(
            p
            for p in lv4.base_salary.periods
            if p.valid_from.isoformat() == "2027-03-01"
        )
        assert period.value == Decimal("1621.99")

    def test_edilizia_cooperative_ancpl_level_ordering(self) -> None:
        """Level 1 is lowest, 8Q is highest."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        sorted_lvs = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_lvs[0].code == "1"
        assert sorted_lvs[-1].code == "8Q"

    def test_edilizia_cooperative_ancpl_additional_months(self) -> None:
        """Additional months is 13."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_edilizia_cooperative_ancpl_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_edilizia_cooperative_ancpl_split_model_fixed_allowances(self) -> None:
        """All levels carry CONTINGENZA + EDR; Q levels also carry INDENNITA_FUNZIONE."""  # noqa: E501
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
            assert "EDR" in codes
            if lv.code in {"7Q", "8Q"}:
                assert "INDENNITA_FUNZIONE" in codes
            else:
                assert "INDENNITA_FUNZIONE" not in codes

    def test_edilizia_cooperative_ancpl_tax_sector(self) -> None:
        """Tax sector is edilizia."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        assert ccnl.meta.tax_sector == TaxSector.EDILIZIA

    def test_edilizia_cooperative_ancpl_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), max 5 increments."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadMetalmeccanicoConfimiPmi:
    """Tests for CCNL Metalmeccanici Piccola Industria CONFIMI (C01A)."""

    def test_metalmeccanico_confimi_pmi_loads(self) -> None:
        """File loads; ccnl_id and CNEL code are correct."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        assert ccnl.meta.ccnl_id == "metalmeccanico-confimi-pmi"
        assert ccnl.meta.cnel_code == "C01A"

    def test_metalmeccanico_confimi_pmi_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: 2-7, 8, 8Q, 9, 9Q."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 10
        assert codes == {"2", "3", "4", "5", "6", "7", "8", "8Q", "9", "9Q"}

    def test_metalmeccanico_confimi_pmi_level5_salary_t1(self) -> None:
        """Level 5 base salary is 2251.35 EUR at T1 tranche (01/06/2026)."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        lv5 = next(lv for lv in ccnl.levels if lv.code == "5")
        period = next(
            p
            for p in lv5.base_salary.periods
            if p.valid_from.isoformat() == "2026-06-01"
        )
        assert period.value == Decimal("2251.35")

    def test_metalmeccanico_confimi_pmi_level5_salary_t2(self) -> None:
        """Level 5 base salary is 2306.35 EUR at T2 tranche (01/06/2027)."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        lv5 = next(lv for lv in ccnl.levels if lv.code == "5")
        period = next(
            p
            for p in lv5.base_salary.periods
            if p.valid_from.isoformat() == "2027-06-01"
        )
        assert period.value == Decimal("2306.35")

    def test_metalmeccanico_confimi_pmi_level_ordering(self) -> None:
        """Level 2 is lowest-order; 9Q is highest-order."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        sorted_lvs = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_lvs[0].code == "2"
        assert sorted_lvs[-1].code == "9Q"

    def test_metalmeccanico_confimi_pmi_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 6, 1))
        assert val == Decimal(13)

    def test_metalmeccanico_confimi_pmi_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1)) == Decimal(173)

    def test_metalmeccanico_confimi_pmi_conglobated_levels_2_to_7(self) -> None:
        """Levels 2-7 have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        for code in ("2", "3", "4", "5", "6", "7"):
            lv = next(lv for lv in ccnl.levels if lv.code == code)
            assert lv.fixed_allowances == ()

    def test_metalmeccanico_confimi_pmi_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_metalmeccanico_confimi_pmi_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), max 5 increments."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadNoleggioAutobusConducenteAnav:
    """Tests for CCNL Noleggio Autobus con Conducente ANAV (IC36)."""

    def test_noleggio_autobus_conducente_anav_loads(self) -> None:
        """CCNL id and CNEL code match."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        assert ccnl.meta.ccnl_id == "noleggio-autobus-conducente-anav"
        assert ccnl.meta.cnel_code == "IC36"

    def test_noleggio_autobus_conducente_anav_has_11_levels(self) -> None:
        """Eleven levels: C4-C1, B3-B1, A2-A1, Q2-Q1."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "C4",
            "C3",
            "C2",
            "C1",
            "B3",
            "B2",
            "B1",
            "A2",
            "A1",
            "Q2",
            "Q1",
        }

    def test_noleggio_autobus_conducente_anav_level_c2_salary_t1(self) -> None:
        """C2 base_salary at 2025-07-01 tranche = 1126.97."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C2")
        assert lv.base_salary.value_at(date(2025, 7, 1)) == Decimal("1126.97")

    def test_noleggio_autobus_conducente_anav_level_c2_salary_t2(self) -> None:
        """C2 base_salary at 2026-08-01 tranche = 1226.97."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C2")
        assert lv.base_salary.value_at(date(2026, 8, 1)) == Decimal("1226.97")

    def test_noleggio_autobus_conducente_anav_level_ordering(self) -> None:
        """Q1 is highest order; C4 is lowest order."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "C4"
        assert ordered[-1].code == "Q1"

    def test_noleggio_autobus_conducente_anav_additional_months(self) -> None:
        """Fourteen mensilita (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            14
        )

    def test_noleggio_autobus_conducente_anav_hourly_divisor(self) -> None:
        """Hourly divisor = 173."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == 173

    def test_noleggio_autobus_conducente_anav_split_model_c2(self) -> None:
        """C2 has CONTINGENZA, EDR, EDR_RINNOVO as fixed allowances."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C2")
        codes = {a.code for a in lv.fixed_allowances}
        assert codes == {"CONTINGENZA", "EDR", "EDR_RINNOVO"}

    def test_noleggio_autobus_conducente_anav_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_noleggio_autobus_conducente_anav_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), max 9 increments."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 9


class TestLoadMaterialiCostruzioneLapideiConfapi:
    """Tests for CCNL Materiali da Costruzione PMI Lapidei CONFAPI ANIEM (F020)."""

    def test_materiali_costruzione_lapidei_confapi_loads(self) -> None:
        """CCNL id and CNEL code match."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        assert ccnl.meta.ccnl_id == "materiali-costruzione-lapidei-confapi"
        assert ccnl.meta.cnel_code == "F020"

    def test_materiali_costruzione_lapidei_confapi_has_8_levels(self) -> None:
        """Eight levels: 1 (highest) through 8 (lowest)."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7", "8"}

    def test_materiali_costruzione_lapidei_confapi_level1_salary_2022(self) -> None:
        """Level 1 base_salary at 2022-01-01 tranche = 2605.54."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1")
        assert lv.base_salary.value_at(date(2022, 1, 1)) == Decimal("2605.54")

    def test_materiali_costruzione_lapidei_confapi_level1_salary_2025(self) -> None:
        """Level 1 base_salary at 2025-01-01 tranche = 2795.46."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("2795.46")

    def test_materiali_costruzione_lapidei_confapi_level_ordering(self) -> None:
        """Level 1 is highest order; level 8 is lowest order."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "8"
        assert ordered[-1].code == "1"

    def test_materiali_costruzione_lapidei_confapi_additional_months(self) -> None:
        """Thirteen mensilita (tredicesima only)."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        assert ccnl.parameters.additional_months.value_at(date(2025, 1, 1)) == Decimal(
            13
        )

    def test_materiali_costruzione_lapidei_confapi_hourly_divisor(self) -> None:
        """Hourly divisor = 174 (Art. 24 Disciplina Lapidei)."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2025, 1, 1)) == 174

    def test_materiali_costruzione_lapidei_confapi_split_model_edr(self) -> None:
        """All levels have EDR as fixed allowance (split model)."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "EDR" in codes

    def test_materiali_costruzione_lapidei_confapi_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_materiali_costruzione_lapidei_confapi_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), max 5 increments."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5
