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


class TestLoadTessileSmi:
    """Tests for CCNL Tessile Abbigliamento Moda SMI (D014)."""

    def test_tessile_smi_loads(self) -> None:
        """Contract id == 'tessile-smi', CNEL code == 'D014'."""
        ccnl = load_ccnl("tessile-smi.json")
        assert ccnl.meta.ccnl_id == "tessile-smi"
        assert ccnl.meta.cnel_code == "D014"

    def test_tessile_smi_has_10_levels(self) -> None:
        """10 livelli: 1, 2, 2S, 3, 3S, 4, 5, 6, 7, 8."""
        ccnl = load_ccnl("tessile-smi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 10
        assert codes == {"1", "2", "2S", "3", "3S", "4", "5", "6", "7", "8"}

    def test_tessile_smi_level4_salary_tranche1(self) -> None:
        """Level 4 Nov 2024 ERN (pre-Dec 2024): 1786.95 EUR (lexplain.it)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        val = level.base_salary.value_at(date(2024, 11, 15))
        assert val == Decimal("1786.95")

    def test_tessile_smi_level4_salary_tranche_dec2024(self) -> None:
        """Level 4 Dec 2024 ERN: 1881.95 EUR (+95 tranche, proportionally derived)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        val = level.base_salary.value_at(date(2025, 6, 1))
        assert val == Decimal("1881.95")

    def test_tessile_smi_level4_salary_tranche_jan2026(self) -> None:
        """Level 4 Jan 2026 ERN: 1938.95 EUR (kitech.it)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "4")
        val = level.base_salary.value_at(date(2026, 1, 1))
        assert val == Decimal("1938.95")

    def test_tessile_smi_level1_salary_dec2024(self) -> None:
        """Level 1 Dec 2024 ERN: 1401.94 EUR (proportionally derived from +95 at L4)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "1")
        val = level.base_salary.value_at(date(2025, 1, 1))
        assert val == Decimal("1401.94")

    def test_tessile_smi_level8_salary_dec2024(self) -> None:
        """Level 8 Dec 2024 ERN: 2385.33 EUR (proportionally derived, +120.65)."""
        ccnl = load_ccnl("tessile-smi.json")
        level = next(lv for lv in ccnl.levels if lv.code == "8")
        val = level.base_salary.value_at(date(2025, 1, 1))
        assert val == Decimal("2385.33")

    def test_tessile_smi_level_ordering(self) -> None:
        """Level 1 must be lowest (order 1), level 8 must be highest."""
        ccnl = load_ccnl("tessile-smi.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "8"

    def test_tessile_smi_additional_months(self) -> None:
        """13 additional months (tredicesima only)."""
        ccnl = load_ccnl("tessile-smi.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 1, 1)) == Decimal(13)

    def test_tessile_smi_hourly_divisor(self) -> None:
        """Hourly divisor must be 173 (40h/week standard)."""
        ccnl = load_ccnl("tessile-smi.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_tessile_smi_level8_has_fixed_allowance(self) -> None:
        """Level 8 has exactly one fixed allowance: Indennita funzione 51.65."""
        ccnl = load_ccnl("tessile-smi.json")
        level8 = next(lv for lv in ccnl.levels if lv.code == "8")
        assert len(level8.fixed_allowances) == 1
        fa = level8.fixed_allowances[0]
        assert fa.code == "IND_FUN"
        assert fa.monthly.value_at(date(2026, 1, 1)) == Decimal("51.65")

    def test_tessile_smi_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("tessile-smi.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_tessile_smi_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 4 scatti."""
        ccnl = load_ccnl("tessile-smi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 4

    def test_tessile_smi_apprenticeship_tracks(self) -> None:
        """7 UC apprenticeship tracks; prof_L6_L8 covers levels 6, 7, 8."""
        ccnl = load_ccnl("tessile-smi.json")
        assert len(ccnl.apprenticeship) == 7
        by_name = {t.name: t for t in ccnl.apprenticeship}
        assert set(by_name["prof_L6_L8"].destination_levels) == {"6", "7", "8"}
        # prof_L6_L8: 0-15m 2 below, 15-30m 1 below, 30m+ at destination
        t = by_name["prof_L6_L8"]
        assert t.periods[0].months_until == 15
        assert t.periods[0].levels_below == 2  # type: ignore[union-attr]
        assert t.periods[1].months_until == 30
        assert t.periods[1].levels_below == 1  # type: ignore[union-attr]
        assert t.periods[2].months_until is None
        assert t.periods[2].levels_below == 0  # type: ignore[union-attr]
        # prof_L2: 0-12m 1 below, 12m+ at destination
        t2 = by_name["prof_L2"]
        assert t2.destination_levels == ("2",)
        assert t2.periods[0].levels_below == 1  # type: ignore[union-attr]
        assert t2.periods[1].months_until is None

    def test_tessile_smi_level4_salary_jan2027(self) -> None:
        """Level 4 base salary from Jan 2027: EUR 1986.95."""
        ccnl = load_ccnl("tessile-smi.json")
        lv4 = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv4.base_salary.value_at(date(2027, 1, 1)) == Decimal("1986.95")


class TestLoadAlimentariFederalimentare:
    """Tests for CCNL Alimentari Industria — Federalimentare (E012)."""

    def test_alimentari_federalimentare_loads(self) -> None:
        """CCNL id == 'alimentari-federalimentare', cnel_code == 'E012'."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert ccnl.meta.ccnl_id == "alimentari-federalimentare"
        assert ccnl.meta.cnel_code == "E012"

    def test_alimentari_federalimentare_has_8_levels(self) -> None:
        """8 levels: 6, 5, 4, 3, 3A, 2, 1, 1S."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "1S",
            "1",
            "2",
            "3A",
            "3",
            "4",
            "5",
            "6",
        }

    def test_alimentari_federalimentare_level3_salary_tranche1(self) -> None:
        """Level 3 TEM at tranche 1 (2023-12-01): 1419.08 EUR."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        level = next(lv for lv in ccnl.levels if lv.code == "3")
        assert level.base_salary.value_at(date(2023, 12, 1)) == Decimal("1419.08")

    def test_alimentari_federalimentare_level3_salary_tranche4(self) -> None:
        """Level 3 TEM at tranche 4 (2026-01-01): 1566.16 EUR."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        level = next(lv for lv in ccnl.levels if lv.code == "3")
        assert level.base_salary.value_at(date(2026, 1, 1)) == Decimal("1566.16")

    def test_alimentari_federalimentare_level_ordering(self) -> None:
        """Level 6 (order 1) is lowest; level 1S (order 8) is highest."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "1S"

    def test_alimentari_federalimentare_additional_months(self) -> None:
        """14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 1, 1)) == Decimal(14)

    def test_alimentari_federalimentare_hourly_divisor(self) -> None:
        """Hourly divisor must be 173 (40h/week standard industria)."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_alimentari_federalimentare_split_allowances(self) -> None:
        """Split model: every level has CONT, EDR, IAR allowances.

        Level 1S (quadro) additionally carries ind_funzione_quadro; the base
        three components must be present on all levels.
        """
        ccnl = load_ccnl("alimentari-federalimentare.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert {"CONTINGENZA", "EDR", "IAR"}.issubset(codes), (
                f"level {lv.code} missing base allowances: {codes}"
            )

    def test_alimentari_federalimentare_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_alimentari_federalimentare_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("alimentari-federalimentare.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_alimentari_federalimentare_apprenticeship_type(self) -> None:
        """Apprenticeship: two UC tracks (36-month covering 1-4/3A; 24-month for 5).

        The 36-month track covers all levels where the full 3-period table
        applies: destinations 4, 3, 3A, 2, 1.
        """
        ccnl = load_ccnl("alimentari-federalimentare.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipUnderClassification)
        assert ccnl.apprenticeship[0].destination_levels == ("4", "3", "3A", "2", "1")

    def test_alimentari_federalimentare_apprentice_under_classification(self) -> None:
        """Apprentice 5 months elapsed → under level 4 (period 0-9 months)."""
        result = compute(
            AnnualEstimateInput(
                employee=Employee(level_code="3A"),
                employment=Employment(
                    ccnl="alimentari-federalimentare.json",
                    contract=Apprentice(months_elapsed=5),
                    employer=Employer(num_employees=50),
                    as_of=date(2026, 1, 1),
                ),
            )
        ).result
        assert result.earnings.apprenticeship_under_level_code == "4"
        assert result.earnings.apprenticeship_pct is None


class TestLoadDmoFederdistribuzione:
    """Tests for CCNL DMO Federdistribuzione (H008) data file."""

    def test_dmo_federdistribuzione_loads(self) -> None:
        """Loads dmo-federdistribuzione and verifies id and CNEL code H008."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        assert ccnl.meta.ccnl_id == "dmo-federdistribuzione"
        assert ccnl.meta.cnel_code == "H008"

    def test_dmo_federdistribuzione_has_8_levels(self) -> None:
        """Eight levels: VII, VI, V, IV, III, II, I, Q."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 8
        assert codes == {
            "VII",
            "VI",
            "V",
            "IV",
            "III",
            "II",
            "I",
            "Q",
        }

    def test_dmo_federdistribuzione_level_iv_salary_tranche1(self) -> None:
        """Level IV paga base at tranche 1 (2023-04-01): 1122.46 EUR."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        level = next(lv for lv in ccnl.levels if lv.code == "IV")
        assert level.base_salary.value_at(date(2023, 4, 1)) == Decimal("1122.46")

    def test_dmo_federdistribuzione_level_iv_salary_tranche2(self) -> None:
        """Level IV paga base at tranche 2 (2024-04-01): 1192.46 EUR."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        level = next(lv for lv in ccnl.levels if lv.code == "IV")
        assert level.base_salary.value_at(date(2024, 4, 1)) == Decimal("1192.46")

    def test_dmo_federdistribuzione_level_ordering(self) -> None:
        """VII must be lowest (order 1), Q must be highest."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "VII"
        assert by_order[-1].code == "Q"

    def test_dmo_federdistribuzione_additional_months(self) -> None:
        """14 additional months (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2026, 1, 1)) == Decimal(14)

    def test_dmo_federdistribuzione_hourly_divisor(self) -> None:
        """Hourly divisor must be 168 (40h/week, Art. 194)."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(168)

    def test_dmo_federdistribuzione_fixed_allowances_split(self) -> None:
        """Split model: all levels have contingenza and terzo_elemento_nazionale."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONTINGENZA" in codes, f"level {lv.code} missing CONTINGENZA"
            assert "TERZO_ELEMENTO_NAZIONALE" in codes, (
                f"level {lv.code} missing TERZO_ELEMENTO_NAZIONALE"
            )

    def test_dmo_federdistribuzione_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_dmo_federdistribuzione_seniority_cadence(self) -> None:
        """Seniority: triennale cadence (36 months), maximum 10 scatti."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10

    def test_dmo_federdistribuzione_apprenticeship_tracks(self) -> None:
        """Two UC tracks: standard_II_V (dest II-V, 18/18m) and standard_VI (12/12m)."""
        ccnl = load_ccnl("dmo-federdistribuzione.json")
        assert len(ccnl.apprenticeship) == 2
        by_name = {t.name: t for t in ccnl.apprenticeship}
        t_ii_v = by_name["standard_II_V"]
        assert set(t_ii_v.destination_levels) == {"II", "III", "IV", "V"}
        assert t_ii_v.periods[0].levels_below == 2  # type: ignore[union-attr]
        assert t_ii_v.periods[0].months_until == 18
        assert t_ii_v.periods[1].levels_below == 1  # type: ignore[union-attr]
        assert t_ii_v.periods[1].months_until is None
        t_vi = by_name["standard_VI"]
        assert t_vi.destination_levels == ("VI",)
        assert t_vi.periods[0].levels_below == 1  # type: ignore[union-attr]
        assert t_vi.periods[0].months_until == 12
        assert t_vi.periods[1].levels_below == 0  # type: ignore[union-attr]
        assert t_vi.periods[1].months_until is None


class TestLoadMetalmeccanicoArtigianato:
    """Tests for CCNL Metalmeccanica Artigianato (Confartigianato/CNA, C030)."""

    def test_metalmeccanico_artigianato_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        assert ccnl.meta.ccnl_id == "metalmeccanico-artigianato"
        assert ccnl.meta.cnel_code == "C030"

    def test_metalmeccanico_artigianato_has_8_levels(self) -> None:
        """Contract has exactly 8 levels with expected codes."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1Q", "1", "2", "2bis", "3", "4", "5", "6"}

    def test_metalmeccanico_artigianato_level4_salary_first_tranche(self) -> None:
        """Level 4° salary at first tranche date (2022-01-01)."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        val = lv.base_salary.value_at(date(2022, 1, 1))
        assert val == Decimal("1416.41")

    def test_metalmeccanico_artigianato_level4_salary_2026(self) -> None:
        """Level 4° salary at March 2026 tranche (kitech-confirmed)."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        val = lv.base_salary.value_at(date(2026, 3, 1))
        assert val == Decimal("1656.98")

    def test_metalmeccanico_artigianato_level_ordering(self) -> None:
        """1Q has highest order; 6 has lowest order."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "1Q"

    def test_metalmeccanico_artigianato_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_metalmeccanico_artigianato_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (Art. 28 CCNL 17.12.2021)."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_metalmeccanico_artigianato_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have empty fixed_allowances."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_metalmeccanico_artigianato_tax_sector(self) -> None:
        """CCNL must declare tax_sector ARTIGIANATO."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.ARTIGIANATO

    def test_metalmeccanico_artigianato_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_metalmeccanico_artigianato_apprenticeship_impiegati(self) -> None:
        """Impiegati track: dest=[2,1], 3 years, 70/77/87/100%."""
        ccnl = load_ccnl("metalmeccanico-artigianato.json")
        by_name = {t.name: t for t in ccnl.apprenticeship}
        assert "impiegati" in by_name
        t = by_name["impiegati"]
        assert set(t.destination_levels) == {"2", "1"}
        pcts = [p.percentage for p in t.periods]  # type: ignore[union-attr]
        assert pcts == [
            Decimal("0.70"),
            Decimal("0.77"),
            Decimal("0.87"),
            Decimal("1.00"),
        ]
        assert t.periods[-1].months_until is None


class TestLoadGommaPlasticaFederazioneGommaPlastica:
    """Tests for CCNL Gomma e Plastica Industria (Federazione Gomma Plastica, B371)."""

    def test_gomma_plastica_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        assert ccnl.meta.ccnl_id == "gomma-plastica-federazione-gomma-plastica"
        assert ccnl.meta.cnel_code == "B371"

    def test_gomma_plastica_has_10_levels(self) -> None:
        """Contract has exactly 10 levels with expected codes."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "A", "B", "C", "D", "E", "F", "G", "H", "I"}

    def test_gomma_plastica_level_f_salary_first_tranche(self) -> None:
        """Level F salary at first tranche date 2023-01-01 (lexplain.it)."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "F")
        val = lv.base_salary.value_at(date(2023, 1, 1))
        assert val == Decimal("1869.12")

    def test_gomma_plastica_level_f_salary_2026(self) -> None:
        """Level F salary at 2026-01-01 tranche (kitech.it confirmed)."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "F")
        val = lv.base_salary.value_at(date(2026, 1, 1))
        assert val == Decimal("2021.12")

    def test_gomma_plastica_level_ordering(self) -> None:
        """I has lowest order (1); Q has highest order (10)."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "I"
        assert by_order[-1].code == "Q"

    def test_gomma_plastica_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_gomma_plastica_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week standard)."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_gomma_plastica_q_has_funzione_allowance(self) -> None:
        """Level Q has exactly one fixed allowance of 50 EUR/month."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        q = next(lv for lv in ccnl.levels if lv.code == "Q")
        assert len(q.fixed_allowances) == 1
        val = q.fixed_allowances[0].monthly.value_at(date(2026, 1, 1))
        assert val == Decimal("50.00")

    def test_gomma_plastica_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_gomma_plastica_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_gomma_plastica_seniority_amounts_pre_2026(self) -> None:
        """Seniority amounts are the same before and after the 2026 rinnovo.

        The December 2025 rinnovo left Art.23 (scatti) untouched, so the amounts
        at 01.01.2023 equal those at 01.01.2026. Level F amount confirmed 13.94 EUR.
        """
        ccnl = load_ccnl("gomma-plastica-federazione-gomma-plastica.json")
        si = ccnl.parameters.seniority_increments
        assert si.amount_by_level is not None
        f_amount_2023 = si.amount_by_level["F"].value_at(date(2023, 1, 1))
        f_amount_2026 = si.amount_by_level["F"].value_at(date(2026, 1, 1))
        assert f_amount_2023 == f_amount_2026
        assert f_amount_2023 == Decimal("13.94")


class TestLoadGraficaEditoriaAieg:
    """Tests for CCNL Grafica e Editoria Industria (AIEG-Acigraf, G011)."""

    def test_grafica_editoria_aieg_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert ccnl.meta.ccnl_id == "grafica-editoria-aieg"
        assert ccnl.meta.cnel_code == "G011"

    def test_grafica_editoria_aieg_has_12_levels(self) -> None:
        """Grafici sector has exactly 12 levels with expected codes."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert len(ccnl.levels) == 12
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "Q",
            "AS",
            "A",
            "B1S",
            "B1",
            "B2",
            "B3",
            "C1",
            "C2",
            "D1",
            "D2",
            "E",
        }

    def test_grafica_editoria_aieg_level_c1_salary_first_tranche(self) -> None:
        """Level C1 salary at first tranche date 2024-03-01 (lexplain.it)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        val = lv.base_salary.value_at(date(2024, 3, 1))
        assert val == Decimal("1852.88")

    def test_grafica_editoria_aieg_level_c1_salary_jul2026(self) -> None:
        """Level C1 salary at July 2026 tranche (kitech.it confirmed)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        val = lv.base_salary.value_at(date(2026, 7, 1))
        assert val == Decimal("2002.49")

    def test_grafica_editoria_aieg_level_ordering(self) -> None:
        """E has lowest order (1); Q has highest order (12)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "E"
        assert by_order[-1].code == "Q"

    def test_grafica_editoria_aieg_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 7, 1))
        assert val == Decimal(13)

    def test_grafica_editoria_aieg_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week standard assumption)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_grafica_editoria_aieg_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (total modelled as base_salary)."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_grafica_editoria_aieg_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_grafica_editoria_aieg_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_grafica_editoria_aieg_apprenticeship_tracks(self) -> None:
        """Two apprenticeship tracks per CCNL 19/01/2021 Art.26e (pag.42).

        Triennale (36m, gruppi C/B/A/Q): 6 semestri 70/75/80/85/90/95/100%.
        Biennale (24m, gruppo D): 6 quadrimestri (4m) 70/75/80/85/90/95/100%.
        Level E is not eligible (not cited in CCNL apprenticeship provisions).
        """
        ccnl = load_ccnl("grafica-editoria-aieg.json")
        assert len(ccnl.apprenticeship) == 2
        by_name = {t.name: t for t in ccnl.apprenticeship}

        tri = by_name["triennale"]
        assert isinstance(tri, ApprenticeshipPercentage)
        assert set(tri.destination_levels) == {
            "C2",
            "C1",
            "B3",
            "B2",
            "B1",
            "B1S",
            "A",
            "AS",
            "Q",
        }
        assert len(tri.periods) == 7  # 6 semestri + open 100%
        assert tri.periods[0].months_until == 6
        assert tri.periods[0].percentage == Decimal("0.70")
        assert tri.periods[5].months_until == 36
        assert tri.periods[5].percentage == Decimal("0.95")
        assert tri.periods[-1].months_until is None

        bi = by_name["biennale"]
        assert isinstance(bi, ApprenticeshipPercentage)
        assert set(bi.destination_levels) == {"D2", "D1"}
        assert len(bi.periods) == 7  # 6 quadrimestri (4m) + open 100%
        assert bi.periods[0].months_until == 4
        assert bi.periods[0].percentage == Decimal("0.70")
        assert bi.periods[5].months_until == 24
        assert bi.periods[5].percentage == Decimal("0.95")
        assert bi.periods[-1].months_until is None


class TestLoadCartaCartoneAssocarta:
    """Tests for CCNL Carta e Cartone Industria (Assocarta, CNEL G022)."""

    def test_carta_cartone_assocarta_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        assert ccnl.meta.ccnl_id == "carta-cartone-assocarta"
        assert ccnl.meta.cnel_code == "G022"

    def test_carta_cartone_assocarta_has_13_levels(self) -> None:
        """Contract has exactly 13 levels with correct codes."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 13
        assert codes == {
            "Q",
            "AS",
            "A",
            "B1",
            "B2S",
            "B2",
            "C1S",
            "C1",
            "C2",
            "C3",
            "D1",
            "D2",
            "E",
        }

    def test_carta_cartone_assocarta_level_c1_salary_2024(self) -> None:
        """Level C1 total at 2024-07-01 equals 1855.11 EUR."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        val = lv.base_salary.value_at(date(2024, 7, 1))
        assert val == Decimal("1855.11")

    def test_carta_cartone_assocarta_level_c1_salary_2026(self) -> None:
        """Level C1 conglobated total at 2026-04-01 equals 1960.11 EUR."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        val = lv.base_salary.value_at(date(2026, 4, 1))
        assert val == Decimal("1960.11")

    def test_carta_cartone_assocarta_level_ordering(self) -> None:
        """Q is the highest-order level; E is the lowest-order level."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "E"
        assert by_order[-1].code == "Q"

    def test_carta_cartone_assocarta_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 4, 1))
        assert val == Decimal(13)

    def test_carta_cartone_assocarta_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week convention)."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_carta_cartone_assocarta_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_carta_cartone_assocarta_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_carta_cartone_assocarta_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("carta-cartone-assocarta.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadTelecomunicazioniAsstel:
    """Tests for CCNL Telecomunicazioni — Asstel (K411)."""

    def test_telecomunicazioni_asstel_loads(self) -> None:
        """Contract id == 'telecomunicazioni-asstel', cnel_code == 'K411'."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        assert ccnl.meta.ccnl_id == "telecomunicazioni-asstel"
        assert ccnl.meta.cnel_code == "K411"

    def test_telecomunicazioni_asstel_has_9_levels(self) -> None:
        """9 livelli: A1, A2, B1, B2, C1, C2, C3, C4, D1."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 9
        assert codes == {"A1", "A2", "B1", "B2", "C1", "C2", "C3", "C4", "D1"}

    def test_telecomunicazioni_asstel_levelc1_salary_tranche1(self) -> None:
        """C1 TEM at Tranche 1 (2026-01-01): 1988.73 EUR."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        level = next(lv for lv in ccnl.levels if lv.code == "C1")
        assert level.base_salary.value_at(date(2026, 1, 1)) == Decimal("1988.73")

    def test_telecomunicazioni_asstel_levelc1_salary_tranche2(self) -> None:
        """C1 TEM at Tranche 2 (2026-12-01): 2038.73 EUR."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        level = next(lv for lv in ccnl.levels if lv.code == "C1")
        assert level.base_salary.value_at(date(2026, 12, 1)) == Decimal("2038.73")

    def test_telecomunicazioni_asstel_level_ordering(self) -> None:
        """A1 is the lowest-order level; D1 is the highest-order level."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "A1"
        assert by_order[-1].code == "D1"

    def test_telecomunicazioni_asstel_additional_months(self) -> None:
        """13 additional months (tredicesima only, Art. 42 CCNL TLC)."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_telecomunicazioni_asstel_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week, Art. 40 CCNL TLC)."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_telecomunicazioni_asstel_c4_d1_fixed_allowances(self) -> None:
        """C4 has ERS=59.39; D1 has IND_FUN=98.13; others have none."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        c4 = next(lv for lv in ccnl.levels if lv.code == "C4")
        d1 = next(lv for lv in ccnl.levels if lv.code == "D1")
        assert len(c4.fixed_allowances) == 1
        assert c4.fixed_allowances[0].code == "ERS"
        assert c4.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "59.39"
        )
        assert len(d1.fixed_allowances) == 1
        assert d1.fixed_allowances[0].code == "IND_FUN"
        assert d1.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "98.13"
        )
        for lv in ccnl.levels:
            if lv.code not in {"C4", "D1"}:
                assert lv.fixed_allowances == ()

    def test_telecomunicazioni_asstel_tax_sector(self) -> None:
        """CCNL must declare tax_sector INDUSTRIA (Asstel/Confindustria)."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_telecomunicazioni_asstel_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 7 scatti."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 7

    def test_telecomunicazioni_asstel_apprenticeship_under_classification(
        self,
    ) -> None:
        """Apprenticeship: under_classification covering levels B1, B2, C1, C2, C3."""
        ccnl = load_ccnl("telecomunicazioni-asstel.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipUnderClassification)
        expected = ("B1", "B2", "C1", "C2", "C3")
        assert ccnl.apprenticeship[0].destination_levels == expected


class TestLoadVigilanzaPrivataAssiv:
    """Unit tests for CCNL Vigilanza Privata ASSIV (HV40, GPG section)."""

    def test_vigilanza_privata_assiv_loads(self) -> None:
        """Contract loads with correct id and CNEL code HV40."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert ccnl.meta.ccnl_id == "vigilanza-privata-assiv"
        assert ccnl.meta.cnel_code == "HV40"

    def test_vigilanza_privata_assiv_has_7_levels(self) -> None:
        """GPG section has exactly 7 levels: Q, 1, 2, 3, 4, 5, 6."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3", "4", "5", "6"}

    def test_vigilanza_privata_assiv_level4_salary_tranche1(self) -> None:
        """4th level salary at 01/06/2023 (1st tranche) = 1328.88 EUR."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2023, 6, 1)) == Decimal("1328.88")

    def test_vigilanza_privata_assiv_level4_salary_tranche5(self) -> None:
        """4th level salary at 01/04/2026 (5th tranche) = 1468.88 EUR."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2026, 4, 1)) == Decimal("1468.88")

    def test_vigilanza_privata_assiv_level_ordering(self) -> None:
        """Level 6 is the lowest-order level; Q is the highest-order level."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "Q"

    def test_vigilanza_privata_assiv_additional_months(self) -> None:
        """14 additional months (tredicesima + quattordicesima, Art. 117)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        val = ccnl.parameters.additional_months.value_at(date(2023, 6, 1))
        assert val == Decimal(14)

    def test_vigilanza_privata_assiv_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week, Art. 115 base CCNL 2013)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_vigilanza_privata_assiv_no_fixed_allowances(self) -> None:
        """All GPG levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_vigilanza_privata_assiv_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector (non-Confindustria)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_vigilanza_privata_assiv_seniority_cadence(self) -> None:
        """Seniority: triennale cadence (36 months), maximum 6 scatti."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 6

    def test_vigilanza_privata_assiv_apprenticeship_percentage(self) -> None:
        """Apprenticeship: percentage type, destination levels 6-1 (all GPG)."""
        ccnl = load_ccnl("vigilanza-privata-assiv.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipPercentage)
        expected = ("6", "5", "4", "3", "2", "1")
        assert ccnl.apprenticeship[0].destination_levels == expected
        assert ccnl.apprenticeship[0].periods[0].percentage == Decimal("1.00")


class TestLoadLegnoArredamentoFederlegno:
    """CCNL Legno e Arredamento Industria (Federlegno-Arredo, CNEL F051)."""

    def test_legno_arredamento_federlegno_loads(self) -> None:
        """Contract loads with id='legno-arredamento-federlegno', code F051."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert ccnl.meta.ccnl_id == "legno-arredamento-federlegno"
        assert ccnl.meta.cnel_code == "F051"

    def test_legno_arredamento_federlegno_has_16_levels(self) -> None:
        """16 level codes across 12 salary bands (AE, AS, AC, AD areas)."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert len(ccnl.levels) == 16
        codes = {lv.code for lv in ccnl.levels}
        expected = {
            "AE1",
            "AE2",
            "AE3",
            "AE4",
            "AS1",
            "AS2",
            "AS3",
            "AS4",
            "AC1",
            "AC2",
            "AC3",
            "AC4",
            "AC5",
            "AD1",
            "AD2",
            "AD3",
        }
        assert codes == expected

    def test_legno_arredamento_federlegno_level_ac4_salary_tranche1(self) -> None:
        """AC4 paga base at 2023-07-01 (1st tranche) = 1888.07 EUR."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "AC4")
        assert lv.base_salary.value_at(date(2023, 7, 1)) == Decimal("1888.07")

    def test_legno_arredamento_federlegno_level_ac4_salary_tranche3(self) -> None:
        """AC4 paga base at 2025-01-01 (3rd tranche) = 2061.83 EUR."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "AC4")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("2061.83")

    def test_legno_arredamento_federlegno_level_ordering(self) -> None:
        """AE1 is lowest-order level; AD3 is highest-order level."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "AE1"
        assert by_order[-1].code == "AD3"

    def test_legno_arredamento_federlegno_additional_months(self) -> None:
        """13 mensilita (tredicesima only, CNEL F051 PDF)."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        val = ccnl.parameters.additional_months.value_at(date(2025, 1, 1))
        assert val == Decimal(13)

    def test_legno_arredamento_federlegno_hourly_divisor(self) -> None:
        """Hourly divisor 174 (40h/week: 40 x 52 / 12 ≈ 173.33 → 174)."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(174)

    def test_legno_arredamento_federlegno_fixed_allowances_split(self) -> None:
        """All levels carry CONTINGENZA and EDR allowances (split salary model)."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
            assert "EDR" in codes

    def test_legno_arredamento_federlegno_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_legno_arredamento_federlegno_seniority_cadence(self) -> None:
        """Seniority: biennale cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_legno_arredamento_federlegno_apprenticeship_under(self) -> None:
        """Apprenticeship: 6 under_classification tracks covering all areas.

        Track 0 (professionalizzante_1) covers AE3 and AE4 (Esecutivo area).
        Track 3 (professionalizzante_4) covers AS3 and AC3.
        """
        ccnl = load_ccnl("legno-arredamento-federlegno.json")
        assert len(ccnl.apprenticeship) == 6
        assert all(
            isinstance(t, ApprenticeshipUnderClassification)
            for t in ccnl.apprenticeship
        )
        assert ccnl.apprenticeship[0].destination_levels == ("AE3", "AE4")
        # Track 3 covers the Specializzato area including AS3
        assert "AS3" in ccnl.apprenticeship[3].destination_levels
