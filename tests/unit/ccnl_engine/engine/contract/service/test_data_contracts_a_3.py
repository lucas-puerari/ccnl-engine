"""CCNL contract data tests (A): Metalmeccanico through Assicurazioni."""

import importlib.resources
from datetime import date
from decimal import Decimal

from ccnl_engine.engine.contract.domain.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.payroll.domain.employment import Apprentice
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
)
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual as compute

# ---------------------------------------------------------------------------
# Parametrised: every JSON in ccnl_engine.knowledge.ccnl.data must validate
# ---------------------------------------------------------------------------

# Use importlib.resources so the path is correct for both editable installs
# (plain .json) and installed wheels (.json.gz), and does not depend on the
# number of parent directories from this test file.
_DATA_PKG = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
_JSON_FILES = sorted(
    (entry for entry in _DATA_PKG.iterdir() if entry.name.endswith(".json")),
    key=lambda e: e.name,
)


class TestLoadEdiliziaArtigianatoCna:
    """CCNL Edilizia Artigianato (CNA/Confartigianato/Casartigiani, F015)."""

    def test_edilizia_artigianato_cna_loads(self) -> None:
        """Contract loads and reports correct id and CNEL code."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert ccnl.meta.ccnl_id == "edilizia-artigianato-cna"
        assert ccnl.meta.cnel_code == "F015"

    def test_edilizia_artigianato_cna_has_8_levels(self) -> None:
        """Contract has exactly 8 levels: 1-7 plus 7Q."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7", "7Q"}

    def test_edilizia_artigianato_cna_level4_salary_tranche1(self) -> None:
        """Level 4 paga base at May 2025 tranche: EUR 1485.23."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4")
        assert lv.base_salary.periods[0].value == Decimal("1485.23")

    def test_edilizia_artigianato_cna_level4_salary_tranche2(self) -> None:
        """Level 4 paga base at Jan 2026 tranche: EUR 1533.88."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4")
        assert lv.base_salary.periods[1].value == Decimal("1533.88")

    def test_edilizia_artigianato_cna_level_ordering(self) -> None:
        """Level 7Q has higher order than level 1 (highest vs lowest)."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "7Q"

    def test_edilizia_artigianato_cna_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_edilizia_artigianato_cna_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (edilizia 40h/week standard)."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_edilizia_artigianato_cna_fixed_allowances_split(self) -> None:
        """All levels carry CONTINGENZA and EDR allowances (split salary model)."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
            assert "EDR" in codes

    def test_edilizia_artigianato_cna_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_edilizia_artigianato_cna_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_edilizia_artigianato_cna_apprenticeship_percentage(self) -> None:
        """Apprenticeship: Gruppo 4 track; 7 periods (6 semestri + open 100%).

        Gruppo 4 track has 6 increasing-percentage semesters then an open-ended
        destination period at 100%.  Two tracks exist: standard_gruppo_4 (dest 4)
        and standard_gruppi_1_3 (dest 3, 4, 5).
        """
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipPercentage)
        assert ccnl.apprenticeship[0].destination_levels == ("4",)
        assert len(ccnl.apprenticeship[0].periods) == 7
        assert ccnl.apprenticeship[0].periods[0].percentage == Decimal("0.74")
        assert ccnl.apprenticeship[0].periods[-1].percentage == Decimal("1.00")

    def test_edilizia_artigianato_cna_specialistico_tracks(self) -> None:
        """Apprenticeship specialistico tracks (Allegato D, verbale 05/09/2023, Art.9).

        Track 1Sp (54m, livelli 4-5): 78/80/86/91/96/96/100%.
        Track 2Sp (45m, livelli 3-4): 78/80/86/91/96/100% (last period 3m, SIMPLIF.).
        Track 3Sp (42m, livello 3):   78/80/86/91/100%.
        """
        ccnl = load_ccnl("edilizia-artigianato-cna.json")
        assert len(ccnl.apprenticeship) == 5  # 2 standard + 3 specialistico
        by_name = {t.name: t for t in ccnl.apprenticeship}

        sp1 = by_name["specialistico_1sp"]
        assert set(sp1.destination_levels) == {"4", "5"}
        assert isinstance(sp1, ApprenticeshipPercentage)
        assert len(sp1.periods) == 7  # 6 active + open 100%
        assert sp1.periods[0].percentage == Decimal("0.78")
        assert sp1.periods[4].percentage == Decimal("0.96")
        assert sp1.periods[5].months_until == 54
        assert sp1.periods[-1].months_until is None

        sp2 = by_name["specialistico_2sp"]
        assert set(sp2.destination_levels) == {"3", "4"}
        assert isinstance(sp2, ApprenticeshipPercentage)
        assert sp2.periods[-2].months_until == 45  # last active period ends at 45m

        sp3 = by_name["specialistico_3sp"]
        assert sp3.destination_levels == ("3",)
        assert isinstance(sp3, ApprenticeshipPercentage)
        assert len(sp3.periods) == 5  # 4 active + open 100%
        assert sp3.periods[3].percentage == Decimal("0.91")
        assert sp3.periods[3].months_until == 42


class TestLoadGasAcquaUtilitalia:
    """Tests for CCNL Gas e Acqua — Utilitalia/Proxigas/Anfida (K321)."""

    def test_gas_acqua_utilitalia_loads(self) -> None:
        """Contract loads with id='gas-acqua-utilitalia' and CNEL K321."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert ccnl.meta.ccnl_id == "gas-acqua-utilitalia"
        assert ccnl.meta.cnel_code == "K321"

    def test_gas_acqua_utilitalia_has_9_levels(self) -> None:
        """Contract has exactly 9 levels: 1-8 plus Q."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7", "8", "Q"}

    def test_gas_acqua_utilitalia_level4_salary_tranche1(self) -> None:
        """Level 4 minimo at Oct 2022 tranche: EUR 2056.35."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4")
        assert lv.base_salary.periods[0].value == Decimal("2056.35")

    def test_gas_acqua_utilitalia_level4_salary_tranche2(self) -> None:
        """Level 4 minimo at Sep 2024 tranche: EUR 2204.68."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4")
        assert lv.base_salary.value_at(date(2024, 9, 1)) == Decimal("2204.68")

    def test_gas_acqua_utilitalia_jul2025_tranche(self) -> None:
        """Level 1 at Jul 2025 tranche (parametric, 90:60 ratio)."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "1")
        assert lv.base_salary.value_at(date(2025, 7, 1)) == Decimal("1740.34")

    def test_gas_acqua_utilitalia_q_ind_fun_months_per_year(self) -> None:
        """Q indennita di funzione is paid 12 months per year (Art. 2.1)."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        lv_q = next(lx for lx in ccnl.levels if lx.code == "Q")
        ind_fun = next(fa for fa in lv_q.fixed_allowances if fa.code == "IND_FUN")
        assert ind_fun.months_per_year == 12

    def test_gas_acqua_utilitalia_apprenticeship_tracks(self) -> None:
        """Three per-duration tracks: professionalizzante_24/30/36."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert len(ccnl.apprenticeship) == 3
        names = {t.name for t in ccnl.apprenticeship}
        assert names == {
            "professionalizzante_24",
            "professionalizzante_30",
            "professionalizzante_36",
        }
        t24 = ccnl.apprenticeship_track_named("professionalizzante_24")
        assert set(t24.destination_levels) == {"7", "8"}
        t36 = ccnl.apprenticeship_track_named("professionalizzante_36")
        assert t36.destination_levels == ("3",)

    def test_gas_acqua_utilitalia_level_ordering(self) -> None:
        """Level Q has highest order; level 1 has lowest order."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_gas_acqua_utilitalia_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(14)

    def test_gas_acqua_utilitalia_hourly_divisor(self) -> None:
        """Hourly divisor: 167 (38h 30min contractual week, CCNL §4.3)."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(167)

    def test_gas_acqua_utilitalia_edr_allowance(self) -> None:
        """All levels carry EDR 10.33 fixed allowance (separate from minimo)."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        for lv in ccnl.levels:
            edr = next((fa for fa in lv.fixed_allowances if fa.code == "EDR"), None)
            assert edr is not None
            assert edr.monthly.periods[0].value == Decimal("10.33")

    def test_gas_acqua_utilitalia_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_gas_acqua_utilitalia_seniority_cadence(self) -> None:
        """Seniority abolished 2015: cadence 24 months, maximum_count 0."""
        ccnl = load_ccnl("gas-acqua-utilitalia.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 0


class TestLoadUnebaUneba:
    """CCNL Istituzioni Socio-Assistenziali UNEBA (T141) data-layer tests."""

    def test_uneba_uneba_loads(self) -> None:
        """Loads with id='uneba-uneba' and CNEL code T141."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert ccnl.meta.ccnl_id == "uneba-uneba"
        assert ccnl.meta.cnel_code == "T141"

    def test_uneba_uneba_has_11_levels(self) -> None:
        """Contract has exactly 11 levels: Q, 1, 2, 3S, 3, 4S, 4, 5S, 5, 6S, 6."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3S", "3", "4S", "4", "5S", "5", "6S", "6"}

    def test_uneba_uneba_level_4s_salary_tranche1(self) -> None:
        """Level 4S (OSS) minimo at Oct 2024 tranche: EUR 1467.86."""
        ccnl = load_ccnl("uneba-uneba.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4S")
        assert lv.base_salary.periods[0].value == Decimal("1467.86")

    def test_uneba_uneba_level_4s_salary_tranche2(self) -> None:
        """Level 4S (OSS) minimo at Jul 2025 tranche: EUR 1517.86."""
        ccnl = load_ccnl("uneba-uneba.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "4S")
        assert lv.base_salary.periods[1].value == Decimal("1517.86")

    def test_uneba_uneba_level_ordering(self) -> None:
        """Level Q has highest order; level 6 has lowest order."""
        ccnl = load_ccnl("uneba-uneba.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "Q"

    def test_uneba_uneba_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima, Art. 46)."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(14)

    def test_uneba_uneba_hourly_divisor(self) -> None:
        """Hourly divisor: 164 (38-hour week, Art. 50)."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(164)

    def test_uneba_uneba_level_q_ind_fun_allowance(self) -> None:
        """Level Q carries IND_FUN allowance EUR 100.00/month (Art. 43)."""
        ccnl = load_ccnl("uneba-uneba.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "Q")
        ind_fun = next(fa for fa in lv.fixed_allowances if fa.code == "IND_FUN")
        assert ind_fun.monthly.periods[0].value == Decimal("100.00")

    def test_uneba_uneba_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("uneba-uneba.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_uneba_uneba_seniority_cadence(self) -> None:
        """Seniority: triennial (36 months), maximum 10 scatti (Art. 48)."""
        ccnl = load_ccnl("uneba-uneba.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadAcconciaturaesteticaConfartigianato:
    """Unit tests for CCNL Acconciatura ed Estetica Confartigianato (H515)."""

    def test_acconciatura_estetica_confartigianato_loads(self) -> None:
        """Loads with id='acconciatura-estetica-confartigianato', code H515."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert ccnl.meta.ccnl_id == "acconciatura-estetica-confartigianato"
        assert ccnl.meta.cnel_code == "H515"

    def test_acconciatura_estetica_confartigianato_has_4_levels(self) -> None:
        """Contract has exactly 4 levels: 1, 2, 3, 4."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert len(ccnl.levels) == 4
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4"}

    def test_acconciatura_estetica_confartigianato_level3_salary_tranche1(self) -> None:
        """Level 3 minimo at May 2024 tranche: EUR 1379.00."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "3")
        assert lv.base_salary.value_at(date(2024, 5, 1)) == Decimal("1379.00")

    def test_acconciatura_estetica_confartigianato_level3_salary_tranche2(self) -> None:
        """Level 3 minimo at Jan 2025 tranche: EUR 1429.00."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "3")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1429.00")

    def test_acconciatura_estetica_confartigianato_level_ordering(self) -> None:
        """Level 1 has highest order; level 4 has lowest order."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "4"
        assert by_order[-1].code == "1"

    def test_acconciatura_estetica_confartigianato_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only, Art. 40)."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_acconciatura_estetica_confartigianato_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (40-hour week, Art. 12)."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_acconciatura_estetica_confartigianato_no_fixed_allowances(self) -> None:
        """All levels have no unconditional allowances (conglobated salary model).

        Levels 1 and 2 carry the role-scoped Responsabile Tecnico allowance
        (role='responsabile_tecnico'), which is excluded from this check.
        """
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        for lv in ccnl.levels:
            unconditional = [a for a in lv.fixed_allowances if a.role is None]
            assert unconditional == [], f"level {lv.code} has unconditional allowances"

    def test_acconciatura_estetica_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_acconciatura_estetica_confartigianato_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_acconciatura_estetica_confartigianato_gruppo3_apprenticeship(
        self,
    ) -> None:
        """Gruppo 3 track: dest=['2'], 6 semestri, 70/70/70/78/85/85."""
        ccnl = load_ccnl("acconciatura-estetica-confartigianato.json")
        track = next(t for t in ccnl.apprenticeship if t.name == "gruppo_3")
        assert track.destination_levels == ("2",)
        assert len(track.periods) == 6
        pcts = [p.percentage for p in track.periods]  # type: ignore[union-attr]
        assert pcts == [
            Decimal("0.70"),
            Decimal("0.70"),
            Decimal("0.70"),
            Decimal("0.78"),
            Decimal("0.85"),
            Decimal("0.85"),
        ]
        assert track.periods[-1].months_until is None


class TestLoadPanificazioneArtigianatoConfartigianato:
    """Tests for CCNL Panificazione Artigianato (E015)."""

    def test_panificazione_artigianato_confartigianato_loads(self) -> None:
        """Loads with id='panificazione-artigianato-confartigianato', code E015."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert ccnl.meta.ccnl_id == "panificazione-artigianato-confartigianato"
        assert ccnl.meta.cnel_code == "E015"

    def test_panificazione_artigianato_confartigianato_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: B4 A4 B3 B3S A3 B2 A2 A1 B1 A1S."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"B4", "A4", "B3", "B3S", "A3", "B2", "A2", "A1", "B1", "A1S"}

    def test_panificazione_artigianato_confartigianato_level_a2_salary_tranche1(
        self,
    ) -> None:
        """Level A2 TOTALE at Apr 2024 tranche: EUR 1788.61."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "A2")
        assert lv.base_salary.periods[0].value == Decimal("1788.61")

    def test_panificazione_artigianato_confartigianato_level_a2_salary_tranche2(
        self,
    ) -> None:
        """Level A2 TOTALE at Jan 2025 tranche: EUR 1828.61."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "A2")
        assert lv.base_salary.periods[1].value == Decimal("1828.61")

    def test_panificazione_artigianato_confartigianato_level_ordering(self) -> None:
        """Level A1S has highest order; level B4 has lowest order."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "B4"
        assert by_order[-1].code == "A1S"

    def test_panificazione_artigianato_confartigianato_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only; Art. 33 ter replaced 14th)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_panificazione_artigianato_confartigianato_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (40-hour work week)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_panificazione_artigianato_confartigianato_no_fixed_allowances(
        self,
    ) -> None:
        """All levels have empty fixed_allowances (unified TOTALE model)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_panificazione_artigianato_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_panificazione_artigianato_confartigianato_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti (Art. 34-bis)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_panificazione_artigianato_confartigianato_apprenticeship_tracks(
        self,
    ) -> None:
        """7 tracks total: gruppo_1 (existing) + 6 new (A2, A3, B1, B2, B3S, B3)."""
        ccnl = load_ccnl("panificazione-artigianato-confartigianato.json")
        assert len(ccnl.apprenticeship) == 7
        by_name = {t.name: t for t in ccnl.apprenticeship}
        # Existing gruppo 1 unchanged
        assert by_name["gruppo_1_panificatori"].destination_levels == ("A1",)
        # Gruppo A2: 54m, 6 periods
        t_a2 = by_name["gruppo_a2_panificatori"]
        assert t_a2.destination_levels == ("A2",)
        assert len(t_a2.periods) == 6
        assert t_a2.periods[0].percentage == Decimal("0.70")  # type: ignore[union-attr]
        assert t_a2.periods[-1].months_until is None
        # Gruppo B1: 36m, 4 periods (70/75/84/100)
        t_b1 = by_name["gruppo_b1_addetti"]
        assert t_b1.destination_levels == ("B1",)
        pcts_b1 = [p.percentage for p in t_b1.periods]  # type: ignore[union-attr]
        assert pcts_b1[2] == Decimal("0.84")


class TestLoadAutoferrotranvieriInternavigatori:
    """Tests for CCNL Autoferrotranvieri e Internavigatori (I022)."""

    def test_autoferrotranvieri_internavigatori_loads(self) -> None:
        """Contract id is autoferrotranvieri-internavigatori, CNEL code I022."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert ccnl.meta.ccnl_id == "autoferrotranvieri-internavigatori"
        assert ccnl.meta.cnel_code == "I022"

    def test_autoferrotranvieri_internavigatori_has_33_levels(self) -> None:
        """Contract has exactly 33 levels (parametri 100 to 250)."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert len(ccnl.levels) == 33
        codes = {lv.code for lv in ccnl.levels}
        assert "100" in codes
        assert "175" in codes
        assert "250" in codes

    def test_autoferrotranvieri_internavigatori_level175_salary_tranche1(
        self,
    ) -> None:
        """Par.175 TOTALE at Dec 2024 (period 1): EUR 1805.57."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "175")
        assert lv.base_salary.periods[0].value == Decimal("1805.57")

    def test_autoferrotranvieri_internavigatori_level175_salary_tranche2(
        self,
    ) -> None:
        """Par.175 TOTALE at Mar 2025 (+60 EUR tabellare): EUR 1865.57."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "175")
        assert lv.base_salary.periods[1].value == Decimal("1865.57")

    def test_autoferrotranvieri_internavigatori_level_ordering(self) -> None:
        """Par.100 has lowest order; par.250 has highest order."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "100"
        assert by_order[-1].code == "250"

    def test_autoferrotranvieri_internavigatori_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(14)

    def test_autoferrotranvieri_internavigatori_hourly_divisor(self) -> None:
        """Hourly divisor: 195 (CCNL Art. 15 formula, 39h/week / 6 days)."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(195)

    def test_autoferrotranvieri_internavigatori_edr_allowance(self) -> None:
        """Each level has one fixed_allowance (edr_2024); par.175 = 40.00."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "EDR_2024"
        lv175 = next(lx for lx in ccnl.levels if lx.code == "175")
        edr = lv175.fixed_allowances[0].monthly
        active = next(
            p
            for p in edr.periods
            if p.valid_until is not None and p.valid_from.year == 2025
        )
        assert active.value == Decimal("40.00")

    def test_autoferrotranvieri_internavigatori_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_autoferrotranvieri_internavigatori_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 6 scatti."""
        ccnl = load_ccnl("autoferrotranvieri-internavigatori.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 6


class TestLoadBccCreditoCooperativo:
    """Tests for CCNL BCC Credito Cooperativo (J271)."""

    def test_bcc_credito_cooperativo_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert ccnl.meta.ccnl_id == "bcc-credito-cooperativo"
        assert ccnl.meta.cnel_code == "J271"

    def test_bcc_credito_cooperativo_has_11_levels(self) -> None:
        """Contract has exactly 11 levels across QD and Aree Professionali."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 11
        assert codes == {
            "QD4",
            "QD3",
            "QD2",
            "QD1",
            "3AP4",
            "3AP3",
            "3AP2",
            "3AP1",
            "2AP2",
            "2AP1",
            "1AP",
        }

    def test_bcc_credito_cooperativo_level_3ap4_salary_tranche1(self) -> None:
        """3AP4 base salary at first tranche (2024-09-01): 3206.90."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "3AP4")
        p = next(x for x in lv.base_salary.periods if x.valid_from == date(2024, 9, 1))
        assert p.value == Decimal("3206.90")

    def test_bcc_credito_cooperativo_level_3ap4_salary_tranche3(self) -> None:
        """3AP4 base salary at third tranche (2026-01-01): 3341.90."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "3AP4")
        p = next(x for x in lv.base_salary.periods if x.valid_from == date(2026, 1, 1))
        assert p.value == Decimal("3341.90")

    def test_bcc_credito_cooperativo_level_ordering(self) -> None:
        """QD4 is highest-order level; 1AP is lowest-order level."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "1AP"
        assert by_order[-1].code == "QD4"

    def test_bcc_credito_cooperativo_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only per Art. 46)."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_bcc_credito_cooperativo_hourly_divisor(self) -> None:
        """Hourly divisor: 160 (Art. 114 formula, arrotondamento a 5)."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(160)

    def test_bcc_credito_cooperativo_no_fixed_allowances(self) -> None:
        """All levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_bcc_credito_cooperativo_tax_sector(self) -> None:
        """Contract declares CREDITO tax sector."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert ccnl.meta.tax_sector == TaxSector.CREDITO

    def test_bcc_credito_cooperativo_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months); global max 8 (AP area), QD* max 12."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 8
        for code in ("QD1", "QD2", "QD3", "QD4"):
            assert si.maximum_count_by_level[code] == 12

    def test_bcc_credito_cooperativo_apprenticeship_type(self) -> None:
        """Apprenticeship: under_classification track covers all 4 Terza Area levels."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert ccnl.apprenticeship
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipUnderClassification)
        assert ccnl.apprenticeship[0].destination_levels == (
            "3AP1",
            "3AP2",
            "3AP3",
            "3AP4",
        )

    def test_bcc_credito_cooperativo_apprenticeship_periods(self) -> None:
        """Months 0-18 at 2AP-2° pay level, months 18+ at destination 3AP1."""
        ccnl = load_ccnl("bcc-credito-cooperativo.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipUnderClassification)
        periods = ccnl.apprenticeship[0].periods
        assert len(periods) == 2
        assert periods[0].months_from == 0
        assert periods[0].months_until == 18
        assert periods[0].levels_below == 1
        assert periods[1].months_from == 18
        assert periods[1].months_until is None
        assert periods[1].levels_below == 0

    def test_bcc_credito_cooperativo_apprentice_compute(self) -> None:
        """Apprentice 12 months elapsed → salary at 2AP2 level."""
        result = compute(
            AnnualEstimateInput(
                employee=Employee(level_code="3AP1"),
                employment=Employment(
                    ccnl="bcc-credito-cooperativo.json",
                    contract=Apprentice(months_elapsed=12),
                    employer=Employer(num_employees=50),
                    as_of=date(2026, 6, 1),
                ),
            )
        ).result
        # At 12 months, pay level is 2AP2 (under-classification)
        assert result.earnings.apprenticeship_under_level_code == "2AP2"
        assert result.earnings.gross_monthly > 0


class TestLoadElettricoElettricita:
    """Tests for CCNL Elettrico Elettricita Futura (K051)."""

    def test_elettrico_elettricita_futura_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        assert ccnl.meta.ccnl_id == "elettrico-elettricita-futura"
        assert ccnl.meta.cnel_code == "K051"

    def test_elettrico_elettricita_futura_has_14_levels(self) -> None:
        """Contract has exactly 14 levels from C1 to QS."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 14
        assert codes == {
            "QS",
            "Q",
            "ASS",
            "AS",
            "A1S",
            "A1",
            "BSS",
            "BS",
            "B1S",
            "B1",
            "B2S",
            "B2",
            "CS",
            "C1",
        }

    def test_elettrico_elettricita_futura_level_a1_salary_tranche1(self) -> None:
        """A1 base salary at first tranche (2025-04-01): 2788.67."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "A1")
        p = next(x for x in lv.base_salary.periods if x.valid_from == date(2025, 4, 1))
        assert p.value == Decimal("2788.67")

    def test_elettrico_elettricita_futura_level_a1_salary_tranche2(self) -> None:
        """A1 base salary at second tranche (2026-04-01): 2851.16."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        lv = next(lx for lx in ccnl.levels if lx.code == "A1")
        p = next(x for x in lv.base_salary.periods if x.valid_from == date(2026, 4, 1))
        assert p.value == Decimal("2851.16")

    def test_elettrico_elettricita_futura_level_ordering(self) -> None:
        """QS is highest-order level; C1 is lowest-order level."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        by_order = sorted(ccnl.levels, key=lambda lx: lx.order)
        assert by_order[0].code == "C1"
        assert by_order[-1].code == "QS"

    def test_elettrico_elettricita_futura_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(14)

    def test_elettrico_elettricita_futura_hourly_divisor(self) -> None:
        """Hourly divisor: 173.33 (40h/week, 40 x 52 / 12 rounded to 2 dp)."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal("173.33")

    def test_elettrico_elettricita_futura_edr_allowance(self) -> None:
        """Each level has one fixed_allowance (EDR) at 10.33 EUR/month."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "EDR"
            assert lv.fixed_allowances[0].monthly.periods[0].value == Decimal("10.33")

    def test_elettrico_elettricita_futura_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_elettrico_elettricita_futura_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadCalzaturieroAssocalzaturifici:
    """Tests for CCNL Calzaturiero Industria (D121)."""

    def test_calzaturiero_assocalzaturifici_loads(self) -> None:
        """CCNL loads with correct id and CNEL code D121."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert ccnl.meta.ccnl_id == "calzaturiero-assocalzaturifici"
        assert ccnl.meta.cnel_code == "D121"

    def test_calzaturiero_assocalzaturifici_has_10_levels(self) -> None:
        """Contract has exactly 10 classification levels."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "2S", "3", "3S", "4", "5", "6", "7", "8"}

    def test_calzaturiero_assocalzaturifici_level4_salary_aug2024(self) -> None:
        """Level 4 base salary at Aug 2024 tranche: 1879.50 EUR."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.periods[0].value == Decimal("1879.50")
        assert str(lv.base_salary.periods[0].valid_from) == "2024-08-01"

    def test_calzaturiero_assocalzaturifici_level4_salary_aug2026(self) -> None:
        """Level 4 base salary at Aug 2026 tranche: 1980.50 EUR."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.periods[-1].value == Decimal("1980.50")
        assert lv.base_salary.periods[-1].valid_until is None

    def test_calzaturiero_assocalzaturifici_level_ordering(self) -> None:
        """Level 8 has the highest order; level 1 has the lowest."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "8"

    def test_calzaturiero_assocalzaturifici_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_calzaturiero_assocalzaturifici_hourly_divisor(self) -> None:
        """Hourly divisor: 169 (kitech.it, daily divisor 26)."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(169)

    def test_calzaturiero_assocalzaturifici_no_fixed_allowances(self) -> None:
        """All levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_calzaturiero_assocalzaturifici_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_calzaturiero_assocalzaturifici_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), maximum 5 scatti."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 5

    def test_calzaturiero_assocalzaturifici_apprenticeship_tracks(self) -> None:
        """Three percentage tracks: L6-8, L3-5, L2 groups at 80/90/100%."""
        ccnl = load_ccnl("calzaturiero-assocalzaturifici.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        assert set(by_name["prof_L6_L8"].destination_levels) == {"6", "7", "8"}
        assert set(by_name["prof_L3_L5"].destination_levels) == {"3", "3S", "4", "5"}
        assert set(by_name["prof_L2"].destination_levels) == {"2", "2S"}
        # All tracks: 80/90/100% over three periods
        for track in ccnl.apprenticeship:
            pcts = [p.percentage for p in track.periods]  # type: ignore[union-attr]
            assert pcts[0] == Decimal("0.80")
            assert pcts[1] == Decimal("0.90")
            assert pcts[2] == Decimal("1.00")
            assert track.periods[-1].months_until is None
        # Period split for L6-8: 10/10/open
        t68 = by_name["prof_L6_L8"]
        assert t68.periods[0].months_until == 10
        assert t68.periods[1].months_until == 20

    def test_elettrico_elettricita_futura_apprenticeship_tracks(self) -> None:
        """Three percentage tracks per Art. 15: C (36m), B (36m), A+BSS (24m)."""
        ccnl = load_ccnl("elettrico-elettricita-futura.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        # Gruppo C: dest=CS, 36m, 86/90/96/100%
        c = by_name["gruppo_c"]
        assert set(c.destination_levels) == {"CS"}
        pcts_c = [p.percentage for p in c.periods]  # type: ignore[union-attr]
        exp_36 = [Decimal("0.86"), Decimal("0.90"), Decimal("0.96"), Decimal("1.00")]
        assert pcts_c == exp_36
        assert c.periods[-1].months_until is None
        assert c.periods[0].months_until == 12
        # Gruppo B: dest=B1, 36m, 86/90/96/100%
        b = by_name["gruppo_b"]
        assert set(b.destination_levels) == {"B1"}
        pcts_b = [p.percentage for p in b.periods]  # type: ignore[union-attr]
        assert pcts_b == exp_36
        # Gruppo A+BSS: dest=A1+BSS, 24m, 86/96/100%
        a = by_name["gruppo_a_bss"]
        assert set(a.destination_levels) == {"A1", "BSS"}
        pcts_a = [p.percentage for p in a.periods]  # type: ignore[union-attr]
        assert pcts_a == [Decimal("0.86"), Decimal("0.96"), Decimal("1.00")]
        assert a.periods[-1].months_until is None
        assert a.periods[0].months_until == 12
        assert a.periods[1].months_until == 24


class TestLoadTessileModaArtigianatoConfartigianato:
    """Tests for CCNL Tessile-Moda Artigianato Confartigianato (V751)."""

    def test_tessile_moda_artigianato_confartigianato_loads(self) -> None:
        """Contract loads with correct id and CNEL code V751."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert ccnl.meta.ccnl_id == "tessile-moda-artigianato-confartigianato"
        assert ccnl.meta.cnel_code == "V751"

    def test_tessile_moda_artigianato_confartigianato_has_7_levels(self) -> None:
        """Contract has exactly 7 levels: 1, 2, 3, 4, 5, 6, 6S."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert len(ccnl.levels) == 7
        assert {lv.code for lv in ccnl.levels} == {"1", "2", "3", "4", "5", "6", "6S"}

    def test_tessile_moda_artigianato_confartigianato_level4_salary_jul2024(
        self,
    ) -> None:
        """Level 4 base salary at Jul 2024 tranche is 1524.87 EUR."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2024, 7, 1)) == Decimal("1524.87")

    def test_tessile_moda_artigianato_confartigianato_level4_salary_jan2025(
        self,
    ) -> None:
        """Level 4 base salary at Jan 2025 tranche is 1566.69 EUR."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1566.69")

    def test_tessile_moda_artigianato_confartigianato_level_ordering(self) -> None:
        """Level 6S has the highest order; level 1 has the lowest."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "6S"

    def test_tessile_moda_artigianato_confartigianato_additional_months(
        self,
    ) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert ccnl.parameters.additional_months.periods[0].value == Decimal(13)

    def test_tessile_moda_artigianato_confartigianato_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (40h/week, Art. 9)."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_tessile_moda_artigianato_confartigianato_no_fixed_allowances(
        self,
    ) -> None:
        """All levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_tessile_moda_artigianato_confartigianato_tax_sector(self) -> None:
        """Contract declares ARTIGIANATO tax sector."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_tessile_moda_artigianato_confartigianato_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennale (24 months), maximum 4 scatti."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 4

    def test_tessile_moda_artigianato_confartigianato_apprenticeship_tracks(
        self,
    ) -> None:
        """Three percentage tracks per Art. 68: gruppi 1, 2, 3."""
        ccnl = load_ccnl("tessile-moda-artigianato-confartigianato.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        g1 = by_name["gruppo_1_abb"]
        assert set(g1.destination_levels) == {"4", "5", "6", "6S"}
        assert g1.periods[0].percentage == Decimal("0.70")  # type: ignore[union-attr]
        assert g1.periods[-1].percentage == Decimal("1.00")  # type: ignore[union-attr]
        assert g1.periods[-1].months_until is None
        g2 = by_name["gruppo_2_abb"]
        assert set(g2.destination_levels) == {"3"}
        g3 = by_name["gruppo_3_abb"]
        assert set(g3.destination_levels) == {"2"}
