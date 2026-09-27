"""Bundled CCNL data files load with their expected values.

Covers Cemento Calce Gesso Industria, Lapidei Industria, Marittimi Industria
Armatoriale, Industria Turistica Federturismo.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl


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
