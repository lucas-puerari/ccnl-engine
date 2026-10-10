"""Bundled CCNL data files load with their expected values.

Covers Poste Italiane K 700, Autorimesse IC 35, Agenzie Maritime, Farmacie
Private H 121.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.employment.models_apprenticeship import (
    ApprenticeshipUnderClassification,
    UnderClassificationPeriod,
)
from ccnl_engine.contract.identity.facade import TaxSector


class TestLoadPosteItalianeK700:
    """Tests for CCNL Poste Italiane S.p.A. (K700)."""

    def test_k700_loads(self) -> None:
        """Contract loads with correct id and CNEL code K700."""
        ccnl = load_ccnl("poste-italiane-k700.json")
        assert ccnl.meta.ccnl_id == "poste-italiane-k700"
        assert ccnl.meta.cnel_code == "K700"

    def test_k700_has_7_levels(self) -> None:
        """7 pay levels: F E D C B A2 A1 (Art. 21; A has two posizioni)."""
        ccnl = load_ccnl("poste-italiane-k700.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"F", "E", "D", "C", "B", "A2", "A1"}

    def test_k700_level_c_salary_tranche1(self) -> None:
        """Level C paga base at 2024-07-23: 1330.56 (Allegato 9 CCNL)."""
        ccnl = load_ccnl("poste-italiane-k700.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C")
        assert lv.base_salary.value_at(date(2024, 7, 23)) == Decimal("1330.56")

    def test_k700_level_c_salary_tranche2(self) -> None:
        """Level C paga base at 2025-09-01: 1381.56 (Allegato 9 CCNL)."""
        ccnl = load_ccnl("poste-italiane-k700.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C")
        assert lv.base_salary.value_at(date(2025, 9, 1)) == Decimal("1381.56")

    def test_k700_level_ordering(self) -> None:
        """Highest order is A1 (Quadri); lowest is F."""
        ccnl = load_ccnl("poste-italiane-k700.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "F"
        assert sorted_levels[-1].code == "A1"

    def test_k700_additional_months(self) -> None:
        """14 mensilità: tredicesima (Art. 67) + quattordicesima (Art. 68)."""
        ccnl = load_ccnl("poste-italiane-k700.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_k700_hourly_divisor(self) -> None:
        """Hourly divisor 156 h/month (Art. 65 III, 36h/week)."""
        ccnl = load_ccnl("poste-italiane-k700.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(156)

    def test_k700_contingenza_allowances(self) -> None:
        """Every level carries CONTINGENZA; A1/A2 add funzione at staff floor rate."""
        ccnl = load_ccnl("poste-italiane-k700.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
        a1 = next(lv for lv in ccnl.levels if lv.code == "A1")
        a1_codes = {a.code for a in a1.fixed_allowances}
        assert "IND_FUNZIONE_A1" in a1_codes
        a2 = next(lv for lv in ccnl.levels if lv.code == "A2")
        a2_codes = {a.code for a in a2.fixed_allowances}
        assert "IND_FUNZIONE_A2" in a2_codes

    def test_k700_tax_sector(self) -> None:
        """Contract uses INDUSTRIA tax sector (private employer post-1998)."""
        ccnl = load_ccnl("poste-italiane-k700.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_k700_seniority_cadence(self) -> None:
        """No traditional scatti: maximum_count=0 (Art. 25, legacy RIA only)."""
        ccnl = load_ccnl("poste-italiane-k700.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 0


class TestLoadAutorimesseIC35:
    """Tests for CCNL Autorimesse, Noleggio Automezzi e Parcheggi (IC35)."""

    def test_ic35_loads(self) -> None:
        """Contract loads with correct id and CNEL code IC35."""
        ccnl = load_ccnl("autorimesse-ic35.json")
        assert ccnl.meta.ccnl_id == "autorimesse-ic35"
        assert ccnl.meta.cnel_code == "IC35"

    def test_ic35_has_11_levels(self) -> None:
        """11 levels: Q1 Q2 A1 A2 B1 B2 B3 C1 C2 C3 C4 (Allegato 1)."""
        ccnl = load_ccnl("autorimesse-ic35.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "Q1",
            "Q2",
            "A1",
            "A2",
            "B1",
            "B2",
            "B3",
            "C1",
            "C2",
            "C3",
            "C4",
        }

    def test_ic35_level_b1_salary_tranche1(self) -> None:
        """B1 paga base inside gen-26 tranche: 1809.37 (Allegato 1)."""
        ccnl = load_ccnl("autorimesse-ic35.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B1")
        assert lv.base_salary.value_at(date(2026, 3, 1)) == Decimal("1809.37")

    def test_ic35_level_b1_salary_tranche2(self) -> None:
        """B1 paga base inside ott-26 tranche: 1854.79 (Allegato 1)."""
        ccnl = load_ccnl("autorimesse-ic35.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B1")
        assert lv.base_salary.value_at(date(2026, 11, 1)) == Decimal("1854.79")

    def test_ic35_level_ordering(self) -> None:
        """Highest order is Q1 (Quadro di primo livello); lowest is C4."""
        ccnl = load_ccnl("autorimesse-ic35.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "C4"
        assert sorted_levels[-1].code == "Q1"

    def test_ic35_additional_months(self) -> None:
        """14 mensilita': tredicesima + quattordicesima (verbale p.5)."""
        ccnl = load_ccnl("autorimesse-ic35.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_ic35_hourly_divisor(self) -> None:
        """Hourly divisor 173 h/month (40h/week, 2019 CCNL source)."""
        ccnl = load_ccnl("autorimesse-ic35.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(173)

    def test_ic35_three_fixed_allowances(self) -> None:
        """Every level carries CONTINGENZA, EDR and EAR allowances."""
        ccnl = load_ccnl("autorimesse-ic35.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert codes == {"CONTINGENZA", "EDR", "EAR"}

    def test_ic35_tax_sector(self) -> None:
        """Contract uses TERZIARIO tax sector (service/transport sector)."""
        ccnl = load_ccnl("autorimesse-ic35.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_ic35_seniority_cadence(self) -> None:
        """9 biennial scatti di anzianita' (2019 CCNL, Art. anzianita')."""
        ccnl = load_ccnl("autorimesse-ic35.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 9


class TestLoadAgenzieMaritime:
    """Tests for CCNL Agenzie Marittime Raccomandatarie (I481)."""

    def test_i481_loads(self) -> None:
        """Contract loads with id=agenzie-marittime-i481 and cnel=I481."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        assert ccnl.meta.ccnl_id == "agenzie-marittime-i481"
        assert ccnl.meta.cnel_code == "I481"

    def test_i481_has_7_levels(self) -> None:
        """Contract has exactly 7 levels coded '1' through '7'."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        assert len(ccnl.levels) == 7
        assert {lv.code for lv in ccnl.levels} == {"1", "2", "3", "4", "5", "6", "7"}

    def test_i481_level4_salary_tranche1(self) -> None:
        """Level 4 conglobata at 01/09/2024 = 2052.70 EUR (2024 renewal)."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2024, 9, 1)) == Decimal("2052.70")

    def test_i481_level4_salary_tranche3(self) -> None:
        """Level 4 conglobata at 01/01/2026 = 2137.70 EUR (third tranche)."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("2137.70")

    def test_i481_level_ordering(self) -> None:
        """Lowest order is '1' (entry); highest order is '7' (Quadro)."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        sorted_lvs = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_lvs[0].code == "1"
        assert sorted_lvs[-1].code == "7"

    def test_i481_additional_months(self) -> None:
        """14 mensilita': tredicesima (Art. 24) + quattordicesima (Art. 25)."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_i481_hourly_divisor(self) -> None:
        """Hourly divisor 168 (Art. 20: retribuzione / 168 = paga oraria)."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(168)

    def test_i481_levels1_to_6_no_fixed_allowances(self) -> None:
        """Levels 1-6 have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        for lv in ccnl.levels:
            if lv.code != "7":
                assert lv.fixed_allowances == ()

    def test_i481_tax_sector(self) -> None:
        """Contract uses TERZIARIO tax sector (agenzie marittime/aeree)."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_i481_seniority_cadence(self) -> None:
        """8 biennial scatti di anzianita' (Art. 23, 2021 CCNL)."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 8

    def test_i481_level7_funzione_allowance(self) -> None:
        """L7 has FUNZIONE allowance 51.65 EUR/month (Art. 5, 2021 CCNL)."""
        ccnl = load_ccnl("agenzie-marittime-i481.json")
        lv7 = next(lv for lv in ccnl.levels if lv.code == "7")
        assert len(lv7.fixed_allowances) == 1
        fa = lv7.fixed_allowances[0]
        assert fa.code == "FUNZIONE"
        assert fa.monthly.value_at(date(2026, 1, 1)) == Decimal("51.65")


class TestLoadFarmaciePrivateH121:
    """Tests for CCNL Dipendenti delle Farmacie Private (H121)."""

    def test_farmacie_private_h121_loads(self) -> None:
        """Contract loads with correct id and CNEL code H121."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        assert ccnl.meta.ccnl_id == "farmacie-private-h121"
        assert ccnl.meta.cnel_code == "H121"

    def test_farmacie_private_h121_has_9_levels(self) -> None:
        """9 levels: Q1 Q2 Q3 and livelli 1-6 (Tabella A, Art. 3)."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q1", "Q2", "Q3", "1", "2", "3", "4", "5", "6"}

    def test_farmacie_private_h121_level3_salary_2022(self) -> None:
        """Level 3 paga base 1130.17 at 2022-01-01 (single tranche)."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2022, 1, 1)) == Decimal("1130.17")

    def test_farmacie_private_h121_level1_salary_2022(self) -> None:
        """Level 1 paga base 1429.19 at 2022-01-01 (same as Q3, Tabella A)."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1")
        assert lv.base_salary.value_at(date(2022, 1, 1)) == Decimal("1429.19")

    def test_farmacie_private_h121_level_ordering(self) -> None:
        """Highest order is Q1 (Direttore responsabile); lowest is 6o livello."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "6"
        assert sorted_levels[-1].code == "Q1"

    def test_farmacie_private_h121_additional_months(self) -> None:
        """14 mensilita': tredicesima (Art. 62) + quattordicesima (Art. 63)."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_farmacie_private_h121_hourly_divisor(self) -> None:
        """Divisore convenzionale 173 h/month for 40h/week (Art. 57)."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(173)

    def test_farmacie_private_h121_q1_has_isq(self) -> None:
        """Q1 level has three allowances: contingenza, edr, and isq."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        q1 = next(lv for lv in ccnl.levels if lv.code == "Q1")
        codes = {a.code for a in q1.fixed_allowances}
        assert codes == {"contingenza", "edr", "isq"}

    def test_farmacie_private_h121_tax_sector(self) -> None:
        """Contract uses terziario tax sector (INPS-CNEL: TERZIARIO E SERVIZI)."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_farmacie_private_h121_seniority_cadence(self) -> None:
        """15 scatti biennali (cadence 24 months, max 15) per Art. 53."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 15

    def test_farmacie_private_h121_apprenticeship_under_classification(
        self,
    ) -> None:
        """Two under_classification tracks (Allegato II, accord 14/06/2012)."""
        ccnl = load_ccnl("farmacie-private-h121.json")
        tracks = ccnl.apprenticeship
        assert len(tracks) == 2
        assert all(isinstance(t, ApprenticeshipUnderClassification) for t in tracks)
        farmacista = next(t for t in tracks if t.name == "farmacista_collaboratore")
        assert farmacista.destination_levels == ("1",)
        period = farmacista.periods[0]
        assert isinstance(period, UnderClassificationPeriod)
        assert period.levels_below == 0
