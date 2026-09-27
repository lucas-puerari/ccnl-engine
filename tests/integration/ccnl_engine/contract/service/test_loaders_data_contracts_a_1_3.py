"""Bundled CCNL data files load with their expected values.

Covers Logistica Trasporto Confetra, Multiservizi Anip, Studi Professionali
Confprofessioni, Bancari Abi.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl


class TestLoadLogisticaTrasportoConfetra:
    """Tests for CCNL Logistica, Trasporto Merci e Spedizione (I100)."""

    def test_logistica_trasporto_confetra_loads(self) -> None:
        """CCNL id must be logistica-trasporto-confetra, CNEL code I100."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert ccnl.meta.ccnl_id == "logistica-trasporto-confetra"
        assert ccnl.meta.cnel_code == "I100"

    def test_logistica_trasporto_confetra_has_9_levels(self) -> None:
        """Contract must have exactly 9 levels (6J excluded, abolished Dec 2025)."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3S", "3", "4", "4J", "5", "6"}

    def test_logistica_trasporto_confetra_level_3s_salary_jan2025(self) -> None:
        """3S conglobated minimum at first tranche (Jan 2025) must be 2070.37."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        lv = next(lvl for lvl in ccnl.levels if lvl.code == "3S")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("2070.37")

    def test_logistica_trasporto_confetra_level_3s_salary_jan2026(self) -> None:
        """3S conglobated minimum at second tranche (Jan 2026) must be 2160.37."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        lv = next(lvl for lvl in ccnl.levels if lvl.code == "3S")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("2160.37")

    def test_logistica_trasporto_confetra_level_ordering(self) -> None:
        """Quadro must have the highest order; 6° livello the lowest."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "Q"

    def test_logistica_trasporto_confetra_additional_months(self) -> None:
        """14 additional months (tredicesima Art. 18 + quattordicesima Art. 19)."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 1, 1)) == Decimal(14)

    def test_logistica_trasporto_confetra_hourly_divisor(self) -> None:
        """Hourly divisor must be 168 (Art. 61 co.3 testo unico Sept 2025)."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(168)

    def test_logistica_trasporto_confetra_no_fixed_allowances(self) -> None:
        """All levels must have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_logistica_trasporto_confetra_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_logistica_trasporto_confetra_seniority_cadence(self) -> None:
        """Seniority increments: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_logistica_trasporto_confetra_apprenticeship_all_levels(self) -> None:
        """Single track covers levels 1-6, 3S, 4J at 75/85/100%."""
        ccnl = load_ccnl("logistica-trasporto-confetra.json")
        assert len(ccnl.apprenticeship) == 1
        track = ccnl.apprenticeship[0]
        assert track.name == "standard"
        assert set(track.destination_levels) == {
            "1",
            "2",
            "3",
            "3S",
            "4",
            "4J",
            "5",
            "6",
        }
        pcts = [p.percentage for p in track.periods]  # type: ignore[union-attr]
        assert pcts[0] == Decimal("0.75")
        assert pcts[1] == Decimal("0.85")
        assert pcts[2] == Decimal("1.00")
        assert track.periods[-1].months_until is None


class TestLoadMultiserviziAnip:
    """Tests for CCNL Multiservizi K511 (ANIP-Confindustria) data file."""

    def test_multiservizi_anip_loads(self) -> None:
        """File must load and carry the correct id and CNEL code."""
        ccnl = load_ccnl("multiservizi-anip.json")
        assert ccnl.meta.ccnl_id == "multiservizi-anip"
        assert ccnl.meta.cnel_code == "K511"

    def test_multiservizi_anip_has_10_levels(self) -> None:
        """Must have exactly 10 levels including par sub-levels."""
        ccnl = load_ccnl("multiservizi-anip.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "2par115", "3", "4par125", "4", "5", "6", "7", "Q"}

    def test_multiservizi_anip_level4_salary_tranche1(self) -> None:
        """Level 4 paga base at first tranche (July 2021) = 821.08."""
        ccnl = load_ccnl("multiservizi-anip.json")
        lvl = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lvl.base_salary.value_at(date(2021, 7, 1)) == Decimal("821.08")

    def test_multiservizi_anip_level4_salary_tranche2(self) -> None:
        """Level 4 paga base at May 2026 tranche (2025-2028 renewal) = 1003.10."""
        ccnl = load_ccnl("multiservizi-anip.json")
        lvl = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lvl.base_salary.value_at(date(2026, 5, 1)) == Decimal("1003.10")

    def test_multiservizi_anip_level_ordering(self) -> None:
        """Level 1 must be lowest order; Q must be highest order."""
        ccnl = load_ccnl("multiservizi-anip.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_multiservizi_anip_additional_months(self) -> None:
        """14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("multiservizi-anip.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 5, 1)) == Decimal(14)

    def test_multiservizi_anip_hourly_divisor(self) -> None:
        """Hourly divisor must be 173 per CCNL text."""
        ccnl = load_ccnl("multiservizi-anip.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_multiservizi_anip_split_model_allowances(self) -> None:
        """Split model: every level must have contingenza and EDR allowances."""
        ccnl = load_ccnl("multiservizi-anip.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "CONTINGENZA" in codes, f"level {lv.code} missing CONTINGENZA"
            assert "EDR" in codes, f"level {lv.code} missing EDR"

    def test_multiservizi_anip_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO (CNEL K-prefix contract)."""
        ccnl = load_ccnl("multiservizi-anip.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_multiservizi_anip_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 8 scatti."""
        ccnl = load_ccnl("multiservizi-anip.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 8


class TestLoadStudiProfessionaliConfprofessioni:
    """Tests for CCNL Studi Professionali — Confprofessioni (H442)."""

    def test_studi_professionali_confprofessioni_loads(self) -> None:
        """CCNL must load with correct id and CNEL code."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        assert ccnl.meta.ccnl_id == "studi-professionali-confprofessioni"
        assert ccnl.meta.cnel_code == "H442"

    def test_studi_professionali_confprofessioni_has_8_levels(self) -> None:
        """CCNL must have exactly 8 levels: 5, 4, 4S, 3, 3S, 2, 1, Q."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 8
        assert codes == {"5", "4", "4S", "3", "3S", "2", "1", "Q"}

    def test_studi_professionali_confprofessioni_level4_salary_tranche1(
        self,
    ) -> None:
        """Level 4 minimo tabellare at tranche 1 (2024-03-01): 1511.28."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        assert level.base_salary.value_at(date(2024, 3, 1)) == Decimal("1511.28")

    def test_studi_professionali_confprofessioni_level4_salary_tranche3(
        self,
    ) -> None:
        """Level 4 minimo tabellare at tranche 3 (2025-10-01): 1595.42."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        assert level.base_salary.value_at(date(2026, 1, 1)) == Decimal("1595.42")

    def test_studi_professionali_confprofessioni_level_ordering(self) -> None:
        """Level 5 must be lowest (order 1), Q must be highest."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "5"
        assert by_order[-1].code == "Q"

    def test_studi_professionali_confprofessioni_additional_months(self) -> None:
        """14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 10, 1)) == Decimal(14)

    def test_studi_professionali_confprofessioni_hourly_divisor(self) -> None:
        """Hourly divisor must be 170 per Art. 45 and Art. 137 CCNL."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(170)

    def test_studi_professionali_confprofessioni_no_fixed_allowances(
        self,
    ) -> None:
        """Conglobated model: standard levels have no unconditional allowances.

        Levels 1, 2, 3S carry the ENAC role-scoped allowance (role
        'confedertecnica_pre_2004', Art. 141) which is excluded here.
        """
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        for lv in ccnl.levels:
            unconditional = [a for a in lv.fixed_allowances if a.role is None]
            assert unconditional == [], f"level {lv.code} has unconditional allowances"

    def test_studi_professionali_confprofessioni_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO (CNEL H-prefix contract)."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_studi_professionali_confprofessioni_seniority_cadence(
        self,
    ) -> None:
        """Seniority: triennale cadence (36 months), maximum 8 scatti."""
        ccnl = load_ccnl("studi-professionali-confprofessioni.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 8


class TestLoadBancariAbi:
    """Tests for CCNL Bancari ABI (J241) data file."""

    def test_bancari_abi_loads(self) -> None:
        """Loads bancari-abi and verifies id and CNEL code J241."""
        ccnl = load_ccnl("bancari-abi.json")
        assert ccnl.meta.ccnl_id == "bancari-abi"
        assert ccnl.meta.cnel_code == "J241"

    def test_bancari_abi_has_9_levels(self) -> None:
        """Nine levels: QD4, QD3, QD2, QD1, 3A4, 3A3, 3A2, 3A1, 1e2A."""
        ccnl = load_ccnl("bancari-abi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 9
        assert codes == {
            "QD4",
            "QD3",
            "QD2",
            "QD1",
            "3A4",
            "3A3",
            "3A2",
            "3A1",
            "1e2A",
        }

    def test_bancari_abi_level_3a3_salary_tranche1(self) -> None:
        """Level 3A3 conglobato at tranche 1 (2023-12-01): 2899.88."""
        ccnl = load_ccnl("bancari-abi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "3A3")
        assert level.base_salary.value_at(date(2023, 12, 1)) == Decimal("2899.88")

    def test_bancari_abi_level_3a3_salary_tranche2(self) -> None:
        """Level 3A3 conglobato at tranche 2 (2024-09-01): 2986.15."""
        ccnl = load_ccnl("bancari-abi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "3A3")
        assert level.base_salary.value_at(date(2024, 9, 1)) == Decimal("2986.15")

    def test_bancari_abi_level_ordering(self) -> None:
        """1e2A must be lowest (order 1), QD4 must be highest."""
        ccnl = load_ccnl("bancari-abi.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1e2A"
        assert by_order[-1].code == "QD4"

    def test_bancari_abi_additional_months(self) -> None:
        """13 additional months (tredicesima only)."""
        ccnl = load_ccnl("bancari-abi.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 1, 1)) == Decimal(13)

    def test_bancari_abi_hourly_divisor(self) -> None:
        """Hourly divisor: 162 until 2024-07-01, then 160 (37h/week rinnovo 2024)."""
        ccnl = load_ccnl("bancari-abi.json")
        divisor = ccnl.parameters.hourly_divisor
        assert len(divisor.periods) == 2
        assert divisor.periods[0].value == Decimal(162)
        assert divisor.periods[1].value == Decimal(160)

    def test_bancari_abi_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels must have no fixed allowances."""
        ccnl = load_ccnl("bancari-abi.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == (), f"level {lv.code} has allowances"

    def test_bancari_abi_tax_sector(self) -> None:
        """CCNL must declare tax_sector CREDITO (ABI banking sector)."""
        ccnl = load_ccnl("bancari-abi.json")
        assert ccnl.meta.tax_sector == TaxSector.CREDITO

    def test_bancari_abi_seniority_cadence(self) -> None:
        """Seniority: triennale cadence (36 months), maximum 8 scatti."""
        ccnl = load_ccnl("bancari-abi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 8
