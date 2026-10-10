"""Bundled CCNL data files load with their expected values.

Covers Legno Lapidei Artigianato Confartigianato, Comunicazione Artigianato
Confartigianato, Ceramica Industria Confindustria, Orafi Argentieri Industria
Federorafi.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.employment.models_apprenticeship import (
    ApprenticeshipPercentage,
)
from ccnl_engine.contract.identity.facade import TaxSector


class TestLoadLegnoLapideiArtigianatoConfartigianato:
    """Tests for CCNL Area Legno-Lapidei Artigianato (CNEL F060)."""

    def test_legno_lapidei_artigianato_confartigianato_loads(self) -> None:
        """Contract loads with correct id and CNEL code F060."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert ccnl.meta.ccnl_id == "legno-lapidei-artigianato-confartigianato"
        assert ccnl.meta.cnel_code == "F060"

    def test_legno_lapidei_artigianato_confartigianato_has_8_levels(self) -> None:
        """Contract has exactly 8 levels: F, E, D, C, CS, B, A, AS."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "F",
            "E",
            "D",
            "C",
            "CS",
            "B",
            "A",
            "AS",
        }

    def test_legno_lapidei_artigianato_confartigianato_level_d_salary_mar2024(
        self,
    ) -> None:
        """Level D base salary at Mar 2024 tranche = 1549.71 EUR."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        lv = ccnl.level_by_code("D")
        assert lv.base_salary.value_at(date(2024, 3, 1)) == Decimal("1549.71")

    def test_legno_lapidei_artigianato_confartigianato_level_d_salary_jan2026(
        self,
    ) -> None:
        """Level D base salary at Jan 2026 tranche = 1639.71 EUR."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        lv = ccnl.level_by_code("D")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1639.71")

    def test_legno_lapidei_artigianato_confartigianato_level_ordering(self) -> None:
        """Level AS has highest order; level F has lowest order."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "F"
        assert by_order[-1].code == "AS"

    def test_legno_lapidei_artigianato_confartigianato_additional_months(
        self,
    ) -> None:
        """Additional months: 13 (tredicesima only, no quattordicesima)."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_legno_lapidei_artigianato_confartigianato_hourly_divisor(
        self,
    ) -> None:
        """Hourly divisor: 174 (per contract clause, 40h/week)."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(174)

    def test_legno_lapidei_artigianato_confartigianato_no_fixed_allowances(
        self,
    ) -> None:
        """All levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_legno_lapidei_artigianato_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_legno_lapidei_artigianato_confartigianato_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_legno_lapidei_artigianato_confartigianato_apprenticeship_tracks(
        self,
    ) -> None:
        """Three percentage tracks per CCNL: gruppi 1, 2, 3."""
        ccnl = load_ccnl("legno-lapidei-artigianato-confartigianato.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        g1 = by_name["gruppo_1_legno"]
        assert set(g1.destination_levels) == {"AS", "A", "B"}
        assert g1.periods[0].percentage == Decimal("0.70")  # type: ignore[union-attr]
        assert g1.periods[-1].percentage == Decimal("1.00")  # type: ignore[union-attr]
        assert g1.periods[-1].months_until is None
        g2 = by_name["gruppo_2_legno"]
        assert set(g2.destination_levels) == {"CS", "C", "D"}
        g3 = by_name["gruppo_3_legno"]
        assert set(g3.destination_levels) == {"E"}


# ---------------------------------------------------------------------------
# CCNL Area Comunicazione — Artigianato (G016)
# ---------------------------------------------------------------------------


class TestLoadComunicazioneArtigianatoConfartigianato:
    """Tests for CCNL Area Comunicazione Artigianato (CNEL G016)."""

    def test_comunicazione_artigianato_confartigianato_loads(self) -> None:
        """Contract loads with correct id and CNEL code G016."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        assert ccnl.meta.ccnl_id == "comunicazione-artigianato-confartigianato"
        assert ccnl.meta.cnel_code == "G016"

    def test_comunicazione_artigianato_confartigianato_has_8_levels(self) -> None:
        """Contract has exactly 8 levels with the correct codes."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "1A",
            "1B",
            "2",
            "3",
            "4",
            "5bis",
            "5",
            "6",
        }

    def test_comunicazione_artigianato_confartigianato_level4_salary_dec2024(
        self,
    ) -> None:
        """Level 4 base salary at Dec 2024 tranche is 1718.56 EUR."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        lv = next(lvl for lvl in ccnl.levels if lvl.code == "4")
        val = lv.base_salary.value_at(date(2024, 12, 1))
        assert val == Decimal("1718.56")

    def test_comunicazione_artigianato_confartigianato_level4_salary_mar2026(
        self,
    ) -> None:
        """Level 4 base salary at Mar 2026 tranche is 1808.56 EUR."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        lv = next(lvl for lvl in ccnl.levels if lvl.code == "4")
        val = lv.base_salary.value_at(date(2026, 3, 1))
        assert val == Decimal("1808.56")

    def test_comunicazione_artigianato_confartigianato_level_ordering(self) -> None:
        """Level 1A has highest order, level 6 has lowest order."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        assert by_code["1A"].order > by_code["1B"].order
        assert by_code["6"].order == 1
        assert by_code["1A"].order == 8

    def test_comunicazione_artigianato_confartigianato_additional_months(
        self,
    ) -> None:
        """Contract has 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_comunicazione_artigianato_confartigianato_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(173)

    def test_comunicazione_artigianato_confartigianato_allowances_structure(
        self,
    ) -> None:
        """Level 1A has 1 function allowance; all other levels have none."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        for lv in ccnl.levels:
            if lv.code == "1A":
                assert len(lv.fixed_allowances) == 1
                assert lv.fixed_allowances[0].code == "IND_FUN"
            else:
                assert lv.fixed_allowances == ()

    def test_comunicazione_artigianato_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_comunicazione_artigianato_confartigianato_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_comunicazione_artigianato_confartigianato_apprenticeship_tracks(
        self,
    ) -> None:
        """Two percentage tracks: operai_tecnici (5y) and amministrativi (3y)."""
        ccnl = load_ccnl("comunicazione-artigianato-confartigianato.json")
        assert len(ccnl.apprenticeship) == 2
        by_name = {t.name: t for t in ccnl.apprenticeship}
        ot = by_name["operai_tecnici"]
        assert isinstance(ot, ApprenticeshipPercentage)
        assert ot.periods[0].percentage == Decimal("0.70")
        assert ot.periods[-1].percentage == Decimal("1.00")
        assert ot.periods[-1].months_until is None
        adm = by_name["amministrativi"]
        assert isinstance(adm, ApprenticeshipPercentage)
        assert adm.periods[0].percentage == Decimal("0.70")
        assert adm.periods[-1].percentage == Decimal("0.90")


class TestLoadCeramicaIndustriaConfindustria:
    """Tests for CCNL Ceramica Industria (Confindustria-Assopiastrelle, B122)."""

    def test_ceramica_industria_confindustria_loads(self) -> None:
        """Contract loads with correct id and CNEL code B122."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        assert ccnl.meta.ccnl_id == "ceramica-industria-confindustria"
        assert ccnl.meta.cnel_code == "B122"

    def test_ceramica_industria_confindustria_has_12_levels(self) -> None:
        """Contract has 12 levels: A B1 B2 C1 C2 C3 D1 D2 D3 E1 E2 F."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        assert len(ccnl.levels) == 12
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "A",
            "B1",
            "B2",
            "C1",
            "C2",
            "C3",
            "D1",
            "D2",
            "D3",
            "E1",
            "E2",
            "F",
        }

    def test_ceramica_industria_confindustria_level_a_salary_sep2024(
        self,
    ) -> None:
        """Level A base salary at Sep 2024 tranche is 2600.08 EUR/month."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        val = by_code["A"].base_salary.value_at(date(2024, 9, 1))
        assert val == Decimal("2600.08")

    def test_ceramica_industria_confindustria_level_a_salary_jul2026(
        self,
    ) -> None:
        """Level A base salary at Jul 2026 tranche is 2716.41 EUR/month."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        val = by_code["A"].base_salary.value_at(date(2026, 7, 1))
        assert val == Decimal("2716.41")

    def test_ceramica_industria_confindustria_level_ordering(self) -> None:
        """Level A has highest order; level F has order 1 (lowest)."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        assert by_code["A"].order == 12
        assert by_code["F"].order == 1

    def test_ceramica_industria_confindustria_additional_months(self) -> None:
        """Contract has 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 7, 1))
        assert val == Decimal(13)

    def test_ceramica_industria_confindustria_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 7, 1))
        assert val == Decimal(173)

    def test_ceramica_industria_confindustria_ipo_allowances(self) -> None:
        """B1 C1 C2 D1 D2 E1 have IPO; A B2 C3 D3 E2 F have none."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        levels_with_ipo = {"B1", "C1", "C2", "D1", "D2", "E1"}
        for code, lv in by_code.items():
            if code in levels_with_ipo:
                assert len(lv.fixed_allowances) == 1
                assert lv.fixed_allowances[0].code == "IPO"
            else:
                assert lv.fixed_allowances == ()

    def test_ceramica_industria_confindustria_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_ceramica_industria_confindustria_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_ceramica_industria_confindustria_apprenticeship_track(
        self,
    ) -> None:
        """Single percentage track at 95% covering all 12 levels."""
        ccnl = load_ccnl("ceramica-industria-confindustria.json")
        assert len(ccnl.apprenticeship) == 1
        track = ccnl.apprenticeship[0]
        assert isinstance(track, ApprenticeshipPercentage)
        assert len(track.destination_levels) == 12
        assert track.periods[0].percentage == Decimal("0.95")
        assert track.periods[0].months_until is None


class TestLoadOrafiArgentieriIndustriaFederorafi:
    """Tests for CCNL Orafi e Argentieri Industria (Federorafi, C021)."""

    def test_orafi_argentieri_industria_federorafi_loads(self) -> None:
        """Contract loads with correct id and CNEL code C021."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        assert ccnl.meta.ccnl_id == "orafi-argentieri-industria-federorafi"
        assert ccnl.meta.cnel_code == "C021"

    def test_orafi_argentieri_industria_federorafi_has_8_levels(self) -> None:
        """Contract has 8 levels: 2 3 4 5 5S 6 7 7Q."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"2", "3", "4", "5", "5S", "6", "7", "7Q"}

    def test_orafi_argentieri_industria_federorafi_level5_salary_jun2022(
        self,
    ) -> None:
        """Level 5 base salary at Jun 2022 tranche is 1670.37 EUR/month."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        val = by_code["5"].base_salary.value_at(date(2022, 6, 1))
        assert val == Decimal("1670.37")

    def test_orafi_argentieri_industria_federorafi_level5_salary_dec2024(
        self,
    ) -> None:
        """Level 5 base salary at Dec 2024 tranche is 1744.37 EUR/month."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        val = by_code["5"].base_salary.value_at(date(2024, 12, 1))
        assert val == Decimal("1744.37")

    def test_orafi_argentieri_industria_federorafi_level_ordering(
        self,
    ) -> None:
        """Level 7Q has highest order (8); level 2 has order 1 (lowest)."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        assert by_code["7Q"].order == 8
        assert by_code["2"].order == 1

    def test_orafi_argentieri_industria_federorafi_additional_months(
        self,
    ) -> None:
        """Contract has 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 6, 1))
        assert val == Decimal(13)

    def test_orafi_argentieri_industria_federorafi_hourly_divisor(
        self,
    ) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1))
        assert val == Decimal(173)

    def test_orafi_argentieri_industria_federorafi_no_fixed_allowances_l5(
        self,
    ) -> None:
        """Levels 2-6 have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        by_code = {lv.code: lv for lv in ccnl.levels}
        for code in ("2", "3", "4", "5", "5S", "6"):
            assert by_code[code].fixed_allowances == ()

    def test_orafi_argentieri_industria_federorafi_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_orafi_argentieri_industria_federorafi_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_orafi_argentieri_industria_federorafi_apprenticeship_track(
        self,
    ) -> None:
        """Single percentage track: 85%/90%/95% over 36 months, all 8 levels."""
        ccnl = load_ccnl("orafi-argentieri-industria-federorafi.json")
        assert len(ccnl.apprenticeship) == 1
        track = ccnl.apprenticeship[0]
        assert isinstance(track, ApprenticeshipPercentage)
        assert len(track.destination_levels) == 8
        assert track.periods[0].percentage == Decimal("0.85")
        assert track.periods[1].percentage == Decimal("0.90")
        assert track.periods[2].percentage == Decimal("0.95")
        assert track.periods[2].months_until is None
