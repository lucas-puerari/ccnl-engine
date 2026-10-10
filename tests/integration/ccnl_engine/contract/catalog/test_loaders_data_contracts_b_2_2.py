"""Bundled CCNL data files load with their expected values.

Covers Laterizi Industria F 021, Esercizi Cinematografici Anec, Farmacie
Municipali ASSO.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.employment.models_apprenticeship import (
    ApprenticeshipUnderClassification,
    UnderClassificationPeriod,
)
from ccnl_engine.contract.identity.facade import TaxSector


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
