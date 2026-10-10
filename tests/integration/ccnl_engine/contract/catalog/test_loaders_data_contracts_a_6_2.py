"""Bundled CCNL data files load with their expected values.

Covers Trasporto Aereo Assaeroporti, Igiene Ambientale Utilitalia, Impiegati
Tecnici Agricoli.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.identity.facade import TaxSector


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
