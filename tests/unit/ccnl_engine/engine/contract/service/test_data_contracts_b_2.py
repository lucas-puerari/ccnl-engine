"""CCNL contract data tests (B): Energia through ServiziAmministrativi."""

from datetime import date
from decimal import Decimal

from ccnl_engine.engine.contract.domain.apprenticeship import (
    ApprenticeshipUnderClassification,
    UnderClassificationPeriod,
)
from ccnl_engine.engine.contract.domain.identity import TaxSector
from ccnl_engine.engine.contract.service.loaders import load_ccnl


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


class TestLoadLateriziIndustriaF021:
    """Tests for CCNL Laterizi e Manufatti Cementizi - Industria (F021)."""

    def test_laterizi_industria_f021_loads(self) -> None:
        """Contract loads with correct id and CNEL code F021."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        assert ccnl.meta.ccnl_id == "laterizi-industria-f021"
        assert ccnl.meta.cnel_code == "F021"

    def test_laterizi_industria_f021_has_9_levels(self) -> None:
        """9 levels: ASQ AS A B CS C D E F (thaler.it livelli e qualifiche)."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"ASQ", "AS", "A", "B", "CS", "C", "D", "E", "F"}

    def test_laterizi_industria_f021_level_as_salary_2022(self) -> None:
        """Level AS paga tabellare 2095.27 at 2022-04-01 (previgente)."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "AS")
        assert lv.base_salary.value_at(date(2022, 4, 1)) == Decimal("2095.27")

    def test_laterizi_industria_f021_level_b_salary_2026(self) -> None:
        """Level B paga tabellare 1710.15 at 2026-07-01 (2nd 2025 tranche)."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B")
        assert lv.base_salary.value_at(date(2026, 7, 1)) == Decimal("1710.15")

    def test_laterizi_industria_f021_level_ordering(self) -> None:
        """Highest order is ASQ (Quadri); lowest order is F."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "F"
        assert sorted_levels[-1].code == "ASQ"

    def test_laterizi_industria_f021_additional_months(self) -> None:
        """13 mensililita': tredicesima only (quattordicesima: non prevista)."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_laterizi_industria_f021_hourly_divisor(self) -> None:
        """Divisore orario 174 per 40h/week (thaler.it parametri contrattuali)."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(174)

    def test_laterizi_industria_f021_asq_has_three_allowances(self) -> None:
        """ASQ level has CONTINGENZA + EDR + IND_FUNZIONE_QUADRI allowances."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        asq = next(lv for lv in ccnl.levels if lv.code == "ASQ")
        codes = {a.code for a in asq.fixed_allowances}
        assert codes == {"CONTINGENZA", "EDR", "IND_FUNZIONE_QUADRI"}

    def test_laterizi_industria_f021_tax_sector(self) -> None:
        """Contract uses edilizia tax sector (CNEL macrosector F)."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        assert ccnl.meta.tax_sector == TaxSector.EDILIZIA

    def test_laterizi_industria_f021_seniority_cadence(self) -> None:
        """5 scatti biennali (cadence 24 months, max 5; thaler.it scatti)."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        assert ccnl.parameters.seniority_increments.cadence_months == 24
        assert ccnl.parameters.seniority_increments.maximum_count == 5


class TestLoadEserciziCinematograficiAnec:
    """Tests for CCNL Esercizi Cinematografici e Cinema-Teatrali ANEC (G211)."""

    def test_esercizi_cinematografici_anec_loads(self) -> None:
        """Contract id and CNEL code G211 (ANEC, cinema)."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        assert ccnl.meta.ccnl_id == "esercizi-cinematografici-anec"
        assert ccnl.meta.cnel_code == "G211"

    def test_esercizi_cinematografici_anec_has_15_levels(self) -> None:
        """15 levels: 7 monosala + 8 multiplex (both systems in one file)."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        assert len(ccnl.levels) == 15
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "1",
            "2",
            "3",
            "4",
            "5",
            "5S",
            "Q",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "QB",
            "QA",
        }

    def test_esercizi_cinematografici_anec_level3_salary_tranche1(self) -> None:
        """Monosala level 3: 1288.01 at 2023-01-01 (first tranche)."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2023, 6, 1)) == Decimal("1288.01")

    def test_esercizi_cinematografici_anec_level3_salary_tranche2(self) -> None:
        """Monosala level 3: 1337.82 at 2024-11-01 (second tranche)."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 11, 1)) == Decimal("1337.82")

    def test_esercizi_cinematografici_anec_level_ordering(self) -> None:
        """Lowest order is monosala 1 (parametro 100); highest is multiplex QA."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "1"
        assert sorted_levels[-1].code == "QA"

    def test_esercizi_cinematografici_anec_additional_months(self) -> None:
        """14 mensilita': tredicesima (Art. 20) + quattordicesima (Art. 21)."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_esercizi_cinematografici_anec_hourly_divisor(self) -> None:
        """Divisore 173 h/month (Art. 63 explicit: 'coefficiente 173')."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(173)

    def test_esercizi_cinematografici_anec_no_fixed_allowances(self) -> None:
        """All 15 levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        assert all(lv.fixed_allowances == () for lv in ccnl.levels)

    def test_esercizi_cinematografici_anec_tax_sector(self) -> None:
        """tax_sector TERZIARIO (cinema exhibitions; SIMPLIFICATION: FPLS)."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_esercizi_cinematografici_anec_seniority_cadence(self) -> None:
        """5 scatti biennali (cadence 24 months, max 5) per Art. 22."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_laterizi_industria_f021_apprenticeship_tracks(self) -> None:
        """4 under_classification tracks (Art. 9 CCNL 12/02/2020)."""
        ccnl = load_ccnl("laterizi-industria-f021.json")
        tracks = ccnl.apprenticeship
        assert len(tracks) == 4
        assert all(isinstance(t, ApprenticeshipUnderClassification) for t in tracks)
        track36 = next(t for t in tracks if t.name == "professionalizzante_36")
        assert set(track36.destination_levels) == {"ASQ", "AS", "A", "B"}
        assert track36.periods[0].levels_below == 2  # type: ignore[union-attr]
        track12 = next(t for t in tracks if t.name == "professionalizzante_12")
        assert track12.destination_levels == ("E",)
        assert track12.periods[0].levels_below == 1  # type: ignore[union-attr]

    def test_esercizi_cinematografici_anec_multiplex_level_c_tranche3(
        self,
    ) -> None:
        """Multiplex level C third tranche (01/07/2025): 1436.95 EUR/month."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C")
        assert lv.base_salary.value_at(date(2025, 8, 1)) == Decimal("1436.95")

    def test_esercizi_cinematografici_anec_5s_f_equal_tranche3(self) -> None:
        """5S and F share salary at tranche 3; adjacency is intentional."""
        ccnl = load_ccnl("esercizi-cinematografici-anec.json")
        lv_5s = next(lv for lv in ccnl.levels if lv.code == "5S")
        lv_f = next(lv for lv in ccnl.levels if lv.code == "F")
        val = Decimal("1736.47")
        assert lv_5s.base_salary.value_at(date(2025, 8, 1)) == val
        assert lv_f.base_salary.value_at(date(2025, 8, 1)) == val


class TestLoadFarmacieMunicipaliASSO:
    """Tests for CCNL Farmacie Municipalizzate ASSOFARM (H124)."""

    def test_farmacie_municipalizzate_assofarm_loads(self) -> None:
        """Contract loads with correct id and CNEL code H124."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        assert ccnl.meta.ccnl_id == "farmacie-municipalizzate-assofarm"
        assert ccnl.meta.cnel_code == "H124"

    def test_farmacie_municipalizzate_assofarm_has_11_levels(self) -> None:
        """11 levels: 1Q 1S 1C 1_12 1_2 1 and livelli 2-6."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "1Q",
            "1S",
            "1C",
            "1_12",
            "1_2",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
        }

    def test_farmacie_municipalizzate_assofarm_level3_salary_tranche1(
        self,
    ) -> None:
        """Level 3 base 1749.50 at first tranche (01/07/2022, Allegato B)."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2022, 8, 1)) == Decimal("1749.50")

    def test_farmacie_municipalizzate_assofarm_level3_salary_tranche3(
        self,
    ) -> None:
        """Level 3 base 1777.29 at third tranche (01/07/2024, Allegato B)."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1777.29")

    def test_farmacie_municipalizzate_assofarm_level_ordering(self) -> None:
        """Highest order is 1Q (area manager); lowest is 6o livello."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "6"
        assert sorted_levels[-1].code == "1Q"

    def test_farmacie_municipalizzate_assofarm_additional_months(self) -> None:
        """14 mensilita: quattordicesima (luglio) + tredicesima (Art. 20)."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_farmacie_municipalizzate_assofarm_hourly_divisor(self) -> None:
        """Divisore 173 (Art. 18 explicit)."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(173)

    def test_farmacie_municipalizzate_assofarm_levels_2_to_6_no_allowances(
        self,
    ) -> None:
        """Levels 2-6 have no fixed allowances (conglobated, no IQ or IS)."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        no_allowance_codes = {"2", "3", "4", "5", "6", "1"}
        for lv in ccnl.levels:
            if lv.code in no_allowance_codes:
                assert lv.fixed_allowances == ()

    def test_farmacie_municipalizzate_assofarm_tax_sector(self) -> None:
        """Contract uses terziario tax sector (ASSOFARM/FILCAMS)."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_farmacie_municipalizzate_assofarm_seniority_cadence(self) -> None:
        """15 scatti biennali (cadence 24 months, max 15, Allegato E)."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 15

    def test_farmacie_municipalizzate_assofarm_iq_allowances(self) -> None:
        """Levels 1Q/1S/1C each have one IQ allowance (Allegato C)."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        for code, expected_monthly in [
            ("1Q", "160.00"),
            ("1S", "150.00"),
            ("1C", "145.00"),
        ]:
            lv = next(lv for lv in ccnl.levels if lv.code == code)
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "iq"
            val = lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1))
            assert val == Decimal(expected_monthly)

    def test_farmacie_municipalizzate_assofarm_apprenticeship_two_tracks(
        self,
    ) -> None:
        """Two under_classification tracks per Allegato F."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        tracks = ccnl.apprenticeship
        assert len(tracks) == 2
        assert all(isinstance(t, ApprenticeshipUnderClassification) for t in tracks)
        farmacista = next(t for t in tracks if t.name == "farmacista_collaboratore")
        assert farmacista.destination_levels == ("1",)
        p0 = farmacista.periods[0]
        assert isinstance(p0, UnderClassificationPeriod)
        assert p0.levels_below == 0

    def test_farmacie_municipalizzate_assofarm_1_12_shares_base_salary(
        self,
    ) -> None:
        """Levels 1_12, 1_2 and 1 share identical base_salary (Allegato B)."""
        ccnl = load_ccnl("farmacie-municipalizzate-assofarm.json")
        ref = next(lv for lv in ccnl.levels if lv.code == "1")
        for code in ("1_12", "1_2"):
            lv = next(lv for lv in ccnl.levels if lv.code == code)
            assert lv.base_salary.value_at(
                date(2026, 1, 1)
            ) == ref.base_salary.value_at(date(2026, 1, 1))


class TestLoadFunivieAnef:
    """Tests for CCNL Trasporto a Fune ANEF (I911)."""

    def test_funivie_anef_loads(self) -> None:
        """Id == 'funivie-anef', cnel_code == 'I911'."""
        ccnl = load_ccnl("funivie-anef.json")
        assert ccnl.meta.ccnl_id == "funivie-anef"
        assert ccnl.meta.cnel_code == "I911"

    def test_funivie_anef_has_8_levels(self) -> None:
        """8 livelli retributivi: 1S 1 2 3 4 5 6 7."""
        ccnl = load_ccnl("funivie-anef.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "1S",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
        }

    def test_funivie_anef_level4_salary_tranche1(self) -> None:
        """Level 4 paga base at first tranche 2025-05-01 = 1464.59."""
        ccnl = load_ccnl("funivie-anef.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2025, 6, 1)) == Decimal("1464.59")

    def test_funivie_anef_level4_salary_tranche2(self) -> None:
        """Level 4 paga base at second tranche 2025-10-01 = 1504.59."""
        ccnl = load_ccnl("funivie-anef.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1504.59")

    def test_funivie_anef_level_ordering(self) -> None:
        """Highest order = 1S (8), lowest = 7 (1)."""
        ccnl = load_ccnl("funivie-anef.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "7"
        assert by_order[-1].code == "1S"

    def test_funivie_anef_additional_months(self) -> None:
        """14 mensilita: tredicesima natalizia + quattordicesima luglio."""
        ccnl = load_ccnl("funivie-anef.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_funivie_anef_hourly_divisor(self) -> None:
        """Hourly divisor = 173 (Art. 18, CCNL ANEF 2025)."""
        ccnl = load_ccnl("funivie-anef.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 173

    def test_funivie_anef_contingenza_only_no_edr(self) -> None:
        """Each level has exactly one fixed allowance (contingenza, no EDR)."""
        ccnl = load_ccnl("funivie-anef.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "contingenza"

    def test_funivie_anef_tax_sector(self) -> None:
        """tax_sector == INDUSTRIA (SIMPLIFICATION)."""
        ccnl = load_ccnl("funivie-anef.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_funivie_anef_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), max 5 scatti (Allegato 3)."""
        ccnl = load_ccnl("funivie-anef.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_funivie_anef_apprenticeship(self) -> None:
        """One under_classification track; level 7 excluded from destinations."""
        ccnl = load_ccnl("funivie-anef.json")
        tracks = ccnl.apprenticeship
        assert len(tracks) == 1
        assert isinstance(tracks[0], ApprenticeshipUnderClassification)
        track = tracks[0]
        assert track.name == "professionalizzante"
        assert "7" not in track.destination_levels
        assert "1S" not in track.destination_levels
        assert len(track.periods) == 2
        assert track.periods[0].levels_below == 1
        assert track.periods[1].levels_below == 0


class TestLoadFedercasa:
    """CCNL Dipendenti Aziende Enti Pubblici Economici Federcasa (T611)."""

    def test_federcasa_loads(self) -> None:
        """Contract loads and id/cnel_code match."""
        ccnl = load_ccnl("federcasa.json")
        assert ccnl.meta.ccnl_id == "federcasa"
        assert ccnl.meta.cnel_code == "T611"

    def test_federcasa_has_16_levels(self) -> None:
        """Exactly 16 levels covering all four areas plus Quadri."""
        ccnl = load_ccnl("federcasa.json")
        assert len(ccnl.levels) == 16
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "Q1",
            "Q2",
            "As",
            "A1",
            "A2",
            "A3",
            "Bs",
            "B1",
            "B2",
            "B3",
            "C1",
            "C2",
            "C3",
            "Ds",
            "D1",
            "D2",
        }

    def test_federcasa_level_b1_salary_dec2024(self) -> None:
        """B1 base salary from 01/12/2024 = 2084.39 (Art.72, ilccnl.it)."""
        ccnl = load_ccnl("federcasa.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B1")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("2084.39")

    def test_federcasa_level_a1_salary_dec2024(self) -> None:
        """A1 base salary from 01/12/2024 = 2542.96 (Art.72, ilccnl.it)."""
        ccnl = load_ccnl("federcasa.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "A1")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("2542.96")

    def test_federcasa_level_ordering(self) -> None:
        """Highest order = Q1 (16), lowest = D2 (1)."""
        ccnl = load_ccnl("federcasa.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "D2"
        assert by_order[-1].code == "Q1"

    def test_federcasa_additional_months(self) -> None:
        """14 mensilita: tredicesima dicembre + quattordicesima giugno (Art.76)."""
        ccnl = load_ccnl("federcasa.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_federcasa_hourly_divisor(self) -> None:
        """Hourly divisor = 156 (Art.71.5: 1/156 retribuzione mensile)."""
        ccnl = load_ccnl("federcasa.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 156

    def test_federcasa_no_fixed_allowances(self) -> None:
        """All 16 levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("federcasa.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_federcasa_tax_sector(self) -> None:
        """tax_sector == TERZIARIO (SIMPLIFICATION: actual sector unverified)."""
        ccnl = load_ccnl("federcasa.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_federcasa_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), max 14 scatti (Art.73.1-2)."""
        ccnl = load_ccnl("federcasa.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 14


class TestLoadFioriRecisiAncef:
    """Unit tests for CCNL Fiori Freschi Recisi ANCEF (H201)."""

    def test_fiori_recisi_ancef_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        assert ccnl.meta.ccnl_id == "fiori-recisi-ancef"
        assert ccnl.meta.cnel_code == "H201"

    def test_fiori_recisi_ancef_has_8_levels(self) -> None:
        """8 levels: Q, 1S, 1, 2, 3, 4, 5, 6."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "Q",
            "1S",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
        }

    def test_fiori_recisi_ancef_level_3_salary_jan2023(self) -> None:
        """Level 3 at 2023-01-01 == 1712.57 (first tranche, reference level)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2023, 1, 1)) == Decimal("1712.57")

    def test_fiori_recisi_ancef_level_3_salary_jan2026(self) -> None:
        """Level 3 at 2026-01-01 == 1792.57 (fourth tranche)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1792.57")

    def test_fiori_recisi_ancef_level_ordering(self) -> None:
        """Highest order = Q (8), lowest = 6 (1)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "Q"

    def test_fiori_recisi_ancef_additional_months(self) -> None:
        """14 mensilita: tredicesima + quattordicesima (Art.38-39)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_fiori_recisi_ancef_hourly_divisor(self) -> None:
        """Hourly divisor = 170 (Art.45)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 170

    def test_fiori_recisi_ancef_no_fixed_allowances(self) -> None:
        """All 8 levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_fiori_recisi_ancef_tax_sector(self) -> None:
        """tax_sector == TERZIARIO (flower import-export commercial trade)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_fiori_recisi_ancef_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), max 10 scatti (Art.48)."""
        ccnl = load_ccnl("fiori-recisi-ancef.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadOossUnsicConfsal:
    """Tests for CCNL OO.SS. UNSIC/CONFSAL (V925)."""

    def test_ooss_unsic_confsal_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        assert ccnl.meta.ccnl_id == "ooss-unsic-confsal"
        assert ccnl.meta.cnel_code == "V925"

    def test_ooss_unsic_confsal_has_6_levels(self) -> None:
        """Contract has exactly 6 levels with codes 1-6."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        assert len(ccnl.levels) == 6
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6"}

    def test_ooss_unsic_confsal_level3_salary_jan2023(self) -> None:
        """Level 3 base salary at 2023-01-19: 2065.40 EUR (primary source)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2023, 2, 1)) == Decimal("2065.40")

    def test_ooss_unsic_confsal_level3_salary_jan2026(self) -> None:
        """Level 3 base salary at 2026-01-01: 2096.38 EUR (proxy source)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("2096.38")

    def test_ooss_unsic_confsal_level_ordering(self) -> None:
        """Level 1 (Direttore Generale) is highest; level 6 is lowest."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "6"
        assert ordered[-1].code == "1"

    def test_ooss_unsic_confsal_additional_months(self) -> None:
        """14 mensilita: 13ma (Art.52) + 14ma (quattordicesima)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_ooss_unsic_confsal_hourly_divisor(self) -> None:
        """Hourly divisor 170 (Art.49: 'divisore convenzionale 170')."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 170

    def test_ooss_unsic_confsal_no_fixed_allowances(self) -> None:
        """All 6 levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_ooss_unsic_confsal_tax_sector(self) -> None:
        """tax_sector == TERZIARIO (sindacali organizations, no dedicated INPS code)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_ooss_unsic_confsal_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), max 5 scatti (Art.51)."""
        ccnl = load_ccnl("ooss-unsic-confsal.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 5
