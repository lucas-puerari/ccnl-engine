"""CCNL contract data tests (C): Radiotelevisive through overtime invariants."""

import importlib.resources
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.contract.service.loaders import load_ccnl

# ---------------------------------------------------------------------------
# Parametrised: every JSON in ccnl_engine.knowledge.ccnl.data must validate
# ---------------------------------------------------------------------------

_DATA_PKG = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
_JSON_FILES = sorted(
    (entry for entry in _DATA_PKG.iterdir() if entry.name.endswith(".json")),
    key=lambda e: e.name,
)


class TestLoadRadiotelevisiveTelevisivoG091:
    """Tests for CCNL Radiotelevisivo — Settore Televisivo (G091)."""

    def test_radiotelevisive_televisivo_loads(self) -> None:
        """Loads radiotelevisive-televisivo and verifies id and CNEL code G091."""
        ccnl = load_ccnl("radiotelevisive-televisivo.json")
        assert ccnl.meta.ccnl_id == "radiotelevisive-televisivo"
        assert ccnl.meta.cnel_code == "G091"

    def test_radiotelevisive_televisivo_has_9_levels(self) -> None:
        """Has exactly 9 levels: 1 through 9 (Art. 43)."""
        ccnl = load_ccnl("radiotelevisive-televisivo.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7", "8", "9"}

    def test_radiotelevisive_televisivo_level5_salary_tranche1(self) -> None:
        """Level 5 paga base at 01/01/2026 is 1571.00 EUR (Art. 43)."""
        ccnl = load_ccnl("radiotelevisive-televisivo.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "5")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1571.00")

    def test_radiotelevisive_televisivo_level5_salary_tranche2(self) -> None:
        """Level 5 paga base at 01/06/2027 is 1651.00 EUR (Art. 43)."""
        ccnl = load_ccnl("radiotelevisive-televisivo.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "5")
        assert lv.base_salary.value_at(date(2027, 6, 1)) == Decimal("1651.00")

    def test_radiotelevisive_televisivo_level_ordering(self) -> None:
        """Level 1 is lowest (order 1), level 9 is highest (order 9)."""
        ccnl = load_ccnl("radiotelevisive-televisivo.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "9"

    def test_radiotelevisive_televisivo_additional_months(self) -> None:
        """Additional months is 13 (Art. 45 — tredicesima only)."""
        ccnl = load_ccnl("radiotelevisive-televisivo.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_radiotelevisive_televisivo_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (Art. 43)."""
        ccnl = load_ccnl("radiotelevisive-televisivo.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_radiotelevisive_televisivo_level5_contingenza(self) -> None:
        """Level 5 CONTINGENZA allowance is 525.80 EUR/month (Allegato A)."""
        ccnl = load_ccnl("radiotelevisive-televisivo.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "5")
        assert len(lv.fixed_allowances) == 1
        fa = lv.fixed_allowances[0]
        assert fa.code == "CONTINGENZA"
        assert fa.monthly.value_at(date(2026, 1, 1)) == Decimal("525.80")

    def test_radiotelevisive_televisivo_tax_sector(self) -> None:
        """Tax sector is industria (Confindustria Radio TV signatory)."""
        ccnl = load_ccnl("radiotelevisive-televisivo.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_radiotelevisive_televisivo_seniority_cadence(self) -> None:
        """Seniority: biennial cadence (24 months), 5 increments (Art. 46)."""
        ccnl = load_ccnl("radiotelevisive-televisivo.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadRadiotelevisiveRadiofonicoG091:
    """Tests for CCNL Radiotelevisivo — Settore Radiofonico (G091)."""

    def test_radiotelevisive_radiofonico_loads(self) -> None:
        """Loads radiotelevisive-radiofonico and verifies id and CNEL code G091."""
        ccnl = load_ccnl("radiotelevisive-radiofonico.json")
        assert ccnl.meta.ccnl_id == "radiotelevisive-radiofonico"
        assert ccnl.meta.cnel_code == "G091"

    def test_radiotelevisive_radiofonico_has_6_levels(self) -> None:
        """Has exactly 6 levels: 1 through 6 (Art. 43 — settore radiofonico)."""
        ccnl = load_ccnl("radiotelevisive-radiofonico.json")
        assert len(ccnl.levels) == 6
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6"}

    def test_radiotelevisive_radiofonico_level3_salary_tranche1(self) -> None:
        """Level 3 paga base at 01/01/2026 is 1028.70 EUR (Art. 43)."""
        ccnl = load_ccnl("radiotelevisive-radiofonico.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1028.70")

    def test_radiotelevisive_radiofonico_level3_salary_tranche2(self) -> None:
        """Level 3 paga base at 01/06/2027 is 1103.70 EUR (Art. 43)."""
        ccnl = load_ccnl("radiotelevisive-radiofonico.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2027, 6, 1)) == Decimal("1103.70")

    def test_radiotelevisive_radiofonico_level_ordering(self) -> None:
        """Level 1 is lowest (order 1), level 6 is highest (order 6)."""
        ccnl = load_ccnl("radiotelevisive-radiofonico.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "6"

    def test_radiotelevisive_radiofonico_additional_months(self) -> None:
        """Additional months is 13 (Art. 45 — tredicesima only)."""
        ccnl = load_ccnl("radiotelevisive-radiofonico.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_radiotelevisive_radiofonico_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (Art. 43)."""
        ccnl = load_ccnl("radiotelevisive-radiofonico.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_radiotelevisive_radiofonico_level3_contingenza(self) -> None:
        """Level 3 CONTINGENZA allowance is 513.11 EUR/month (Allegato A)."""
        ccnl = load_ccnl("radiotelevisive-radiofonico.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert len(lv.fixed_allowances) == 1
        fa = lv.fixed_allowances[0]
        assert fa.code == "CONTINGENZA"
        assert fa.monthly.value_at(date(2026, 1, 1)) == Decimal("513.11")

    def test_radiotelevisive_radiofonico_tax_sector(self) -> None:
        """Tax sector is industria (Confindustria Radio TV signatory)."""
        ccnl = load_ccnl("radiotelevisive-radiofonico.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_radiotelevisive_radiofonico_seniority_cadence(self) -> None:
        """Seniority: biennial cadence (24 months), 5 increments (Art. 46)."""
        ccnl = load_ccnl("radiotelevisive-radiofonico.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadVetroMeccanizzatoAssovetro:
    """Unit tests for vetro-meccanizzato-assovetro.json (CNEL B132)."""

    def test_vetro_meccanizzato_assovetro_loads(self) -> None:
        """Contract id is vetro-meccanizzato-assovetro, CNEL code is B132."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        assert ccnl.meta.ccnl_id == "vetro-meccanizzato-assovetro"
        assert ccnl.meta.cnel_code == "B132"

    def test_vetro_meccanizzato_assovetro_has_6_levels(self) -> None:
        """Has exactly 6 base levels: A, B, C, D, E, F."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        assert len(ccnl.levels) == 6
        assert {lv.code for lv in ccnl.levels} == {"A", "B", "C", "D", "E", "F"}

    def test_vetro_meccanizzato_assovetro_level_d_salary_tranche1(self) -> None:
        """Level D minimo at 2024-01-01 is 1983.92 EUR (CCNL 2023-2025)."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        lv = ccnl.level_by_code("D")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1983.92")

    def test_vetro_meccanizzato_assovetro_level_d_salary_tranche2(self) -> None:
        """Level D minimo at 2026-01-01 is 2080.92 EUR (rinnovo Apr 2026, ilccnl.it)."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        lv = ccnl.level_by_code("D")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("2080.92")

    def test_vetro_meccanizzato_assovetro_level_ordering(self) -> None:
        """Level F is lowest (order 1), level A is highest (order 6)."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "F"
        assert by_order[-1].code == "A"

    def test_vetro_meccanizzato_assovetro_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_vetro_meccanizzato_assovetro_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (confirmed ilccnl.it 2026-01-01)."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_vetro_meccanizzato_assovetro_ter_allowance(self) -> None:
        """Every level has a single TER allowance of 10.33 EUR (EDR frozen)."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            fa = lv.fixed_allowances[0]
            assert fa.code == "TER"
            assert fa.monthly.value_at(date(2026, 1, 1)) == Decimal("10.33")

    def test_vetro_meccanizzato_assovetro_tax_sector(self) -> None:
        """Tax sector is industria (Assovetro — Confindustria sector)."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_vetro_meccanizzato_assovetro_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), 5 increments max."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_vetro_meccanizzato_assovetro_fonchim_fund(self) -> None:
        """Fonchim employer fund at 2.0% from 2026-01-01 (was 1.5% pre-renewal)."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        funds = {f.code: f for f in ccnl.parameters.employer_funds}
        assert "FONCHIM" in funds
        assert funds["FONCHIM"].rate.value_at(date(2026, 1, 1)) == Decimal("0.0200")
        assert funds["FONCHIM"].rate.value_at(date(2025, 1, 1)) == Decimal("0.0150")


class TestLoadTessilePmiUniontessile:
    """Unit tests for tessile-pmi-uniontessile.json (CNEL D018)."""

    def test_tessile_pmi_uniontessile_loads(self) -> None:
        """Contract loads with correct id and CNEL code D018."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        assert ccnl.meta.ccnl_id == "tessile-pmi-uniontessile"
        assert ccnl.meta.cnel_code == "D018"

    def test_tessile_pmi_uniontessile_has_10_levels(self) -> None:
        """Ten levels: 1, 2, 2bis, 3, 3bis, 4, 5, 6, 7, 8."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "2bis", "3", "3bis", "4", "5", "6", "7", "8"}

    def test_tessile_pmi_uniontessile_level4_salary_2025(self) -> None:
        """Level 4 at Jan 2025 tranche: 1902.56 EUR (kitech.it)."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1902.56")

    def test_tessile_pmi_uniontessile_level4_salary_2026(self) -> None:
        """Level 4 at Jan 2026 tranche: 1962.56 EUR (kitech.it)."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1962.56")

    def test_tessile_pmi_uniontessile_level_ordering(self) -> None:
        """Level 8 is highest order; level 1 is lowest order."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "8"

    def test_tessile_pmi_uniontessile_additional_months(self) -> None:
        """Tredicesima only: 13 additional months."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_tessile_pmi_uniontessile_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week; lavoro-economia.it)."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_tessile_pmi_uniontessile_level8_idf_allowance(self) -> None:
        """Level 8 has IDF 51.65 EUR; all other levels have no fixed allowances."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        for lv in ccnl.levels:
            if lv.code == "8":
                assert len(lv.fixed_allowances) == 1
                assert lv.fixed_allowances[0].code == "IND_FUN"
                assert lv.fixed_allowances[0].monthly.value_at(
                    date(2026, 1, 1)
                ) == Decimal("51.65")
            else:
                assert len(lv.fixed_allowances) == 0

    def test_tessile_pmi_uniontessile_tax_sector(self) -> None:
        """Tax sector is industria (Confapi/INPS settore industria)."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_tessile_pmi_uniontessile_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), 4 increments max."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 4

    def test_tessile_pmi_uniontessile_fondapi_fund(self) -> None:
        """FONDAPI rate 1.90% until Mar 2025, 2.00% from Mar 2025 (adapt.it)."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        funds = {f.code: f for f in ccnl.parameters.employer_funds}
        assert "FONDAPI" in funds
        assert funds["FONDAPI"].rate.value_at(date(2024, 4, 1)) == Decimal("0.0190")
        assert funds["FONDAPI"].rate.value_at(date(2025, 3, 1)) == Decimal("0.0200")


class TestLoadTabaccoApti:
    """Unit tests for tabacco-apti.json (CNEL E042)."""

    def test_tabacco_apti_loads(self) -> None:
        """Contract loads with correct id and CNEL code E042."""
        ccnl = load_ccnl("tabacco-apti.json")
        assert ccnl.meta.ccnl_id == "tabacco-apti"
        assert ccnl.meta.cnel_code == "E042"

    def test_tabacco_apti_has_9_levels(self) -> None:
        """Nine levels: 1S, 1, 2, 3A, 3B, 4A, 4B, 5, 6."""
        ccnl = load_ccnl("tabacco-apti.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1S", "1", "2", "3A", "3B", "4A", "4B", "5", "6"}

    def test_tabacco_apti_level4a_salary_2025(self) -> None:
        """Level 4A at Jan 2025 tranche: 1194.90 EUR (Allegato A)."""
        ccnl = load_ccnl("tabacco-apti.json")
        lv = ccnl.level_by_code("4A")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1194.90")

    def test_tabacco_apti_level4a_salary_2026(self) -> None:
        """Level 4A at Jan 2026 tranche: 1244.90 EUR (Allegato A)."""
        ccnl = load_ccnl("tabacco-apti.json")
        lv = ccnl.level_by_code("4A")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1244.90")

    def test_tabacco_apti_level_ordering(self) -> None:
        """Level 1S is highest order; level 6 is lowest order."""
        ccnl = load_ccnl("tabacco-apti.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "1S"

    def test_tabacco_apti_additional_months(self) -> None:
        """Tredicesima + quattordicesima: 14 additional months."""
        ccnl = load_ccnl("tabacco-apti.json")
        assert ccnl.parameters.additional_months.value_at(date(2025, 1, 1)) == Decimal(
            14
        )

    def test_tabacco_apti_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week; CCNL text)."""
        ccnl = load_ccnl("tabacco-apti.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2025, 1, 1)) == Decimal(173)

    def test_tabacco_apti_split_model_fixed_allowances(self) -> None:
        """All levels have CONTINGENZA + EDR; no level has zero allowances."""
        ccnl = load_ccnl("tabacco-apti.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
            assert "EDR" in codes

    def test_tabacco_apti_tax_sector(self) -> None:
        """Tax sector is industria (INPS settore industria)."""
        ccnl = load_ccnl("tabacco-apti.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_tabacco_apti_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), 5 increments max."""
        ccnl = load_ccnl("tabacco-apti.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


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


class TestOvertimeBandInvariants:
    """Parametric invariants over all 125 bundled CCNL JSON files.

    Every CCNL must satisfy the no-ambiguous-collision invariant: two or more
    bands for the same WorkKind without a threshold or conditional predicate
    cannot be applied deterministically.

    This test validates that the bundle validator in TimeSupplements is in sync
    with the actual data — i.e. no file triggers the validator at load time.
    """

    @pytest.mark.parametrize("entry", _JSON_FILES, ids=lambda e: e.name)
    def test_no_ambiguous_band_collisions(self, entry: object) -> None:
        """Loading every CCNL file must not raise DataIntegrityError or ValueError.

        The TimeSupplements.no_ambiguous_collisions validator rejects ambiguous
        band layouts.  Passing here proves all 125 files are collision-free.
        """
        ccnl = load_ccnl(getattr(entry, "name", str(entry)))
        wr = ccnl.work_rules
        if wr is None or wr.time_supplements is None:
            return
        # Validator already ran during load_ccnl; reaching here means it passed.
        assert wr.time_supplements is not None
