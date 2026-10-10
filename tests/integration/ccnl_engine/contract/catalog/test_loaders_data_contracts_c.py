"""Bundled CCNL data files load with their expected values.

Covers Radiotelevisive Televisivo G 091, Radiotelevisive Radiofonico G 091,
Vetro Meccanizzato Assovetro, Tessile Pmi Uniontessile, Tabacco Apti.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.identity.facade import TaxSector


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
        """Fonchim at 1.5%, 2.0% from 2027-01-01, plus the 0.25% insurance."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        funds = {f.code: f for f in ccnl.parameters.employer_funds}
        assert "FONCHIM" in funds
        assert funds["FONCHIM"].rate.value_at(date(2027, 1, 1)) == Decimal("0.0225")
        assert funds["FONCHIM"].rate.value_at(date(2026, 12, 31)) == Decimal("0.0175")


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

    def test_tessile_pmi_uniontessile_fondapi_on_the_minimum(self) -> None:
        """FONDAPI 2.00% employer, 1.60% employee, on the contractual minimum."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        (fund,) = ccnl.parameters.employer_funds
        assert fund.code == "FONDAPI"
        assert fund.contribution_base == "contractual_minimum"


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
