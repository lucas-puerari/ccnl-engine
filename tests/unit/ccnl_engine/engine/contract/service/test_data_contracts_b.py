"""CCNL contract data tests (B): Energia through overtime invariants."""

import importlib.resources
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.contract.domain.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipUnderClassification,
    UnderClassificationPeriod,
)
from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.payroll.service.seniority import seniority_maximum

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


class TestLoadEnergiaPetrolioConfindustria:
    """CCNL Energia e Petrolio (Confindustria Energia) — B254."""

    def test_energia_petrolio_confindustria_loads(self) -> None:
        """Contract loads with correct id and CNEL code B254."""
        ccnl = load_ccnl("energia-petrolio-confindustria.json")
        assert ccnl.meta.ccnl_id == "energia-petrolio-confindustria"
        assert ccnl.meta.cnel_code == "B254"

    def test_energia_petrolio_confindustria_has_23_levels(self) -> None:
        """Contract has 23 levels across 6 groups.

        Groups: 6-0, 5-0..5-4, 4-1..4-4, 3-1..3-4, 2-1..2-4, 1-1..1-5.
        """
        ccnl = load_ccnl("energia-petrolio-confindustria.json")
        assert len(ccnl.levels) == 23
        expected = {
            "6-0",
            "5-0",
            "5-1",
            "5-2",
            "5-3",
            "5-4",
            "4-1",
            "4-2",
            "4-3",
            "4-4",
            "3-1",
            "3-2",
            "3-3",
            "3-4",
            "2-1",
            "2-2",
            "2-3",
            "2-4",
            "1-1",
            "1-2",
            "1-3",
            "1-4",
            "1-5",
        }
        assert {lv.code for lv in ccnl.levels} == expected

    def test_energia_petrolio_confindustria_level_4_2_salary_2025(self) -> None:
        """Group 4/2 paga_base at 2025-07-01 first modelled tranche."""
        ccnl = load_ccnl("energia-petrolio-confindustria.json")
        lv = ccnl.level_by_code("4-2")
        assert lv.base_salary.value_at(date(2025, 7, 1)) == Decimal("2546.61")

    def test_energia_petrolio_confindustria_level_4_2_salary_2026(self) -> None:
        """Group 4/2 paga_base at 2026-07-01 fourth tranche."""
        ccnl = load_ccnl("energia-petrolio-confindustria.json")
        lv = ccnl.level_by_code("4-2")
        assert lv.base_salary.value_at(date(2026, 7, 1)) == Decimal("2651.61")

    def test_energia_petrolio_confindustria_level_ordering(self) -> None:
        """6-0 is the lowest order; 1-5 is the highest order."""
        ccnl = load_ccnl("energia-petrolio-confindustria.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6-0"
        assert by_order[-1].code == "1-5"

    def test_energia_petrolio_confindustria_additional_months(self) -> None:
        """Contract has 14 mensilità (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("energia-petrolio-confindustria.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 7, 1))
        assert val == Decimal(14)

    def test_energia_petrolio_confindustria_hourly_divisor(self) -> None:
        """Hourly divisor is 174.5 h/month (CCNL, two independent sources)."""
        ccnl = load_ccnl("energia-petrolio-confindustria.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 7, 1))
        assert val == Decimal("174.5")

    def test_energia_petrolio_confindustria_fixed_allowances_present(self) -> None:
        """All levels have at least one fixed allowance (EDR_IPCA)."""
        ccnl = load_ccnl("energia-petrolio-confindustria.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "EDR_IPCA" in codes, lv.code

    def test_energia_petrolio_confindustria_tax_sector(self) -> None:
        """Contract uses INDUSTRIA tax sector."""
        ccnl = load_ccnl("energia-petrolio-confindustria.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_energia_petrolio_confindustria_seniority_cadence(self) -> None:
        """Seniority abolished 2016: maximum_count=0, cadence=24 months."""
        ccnl = load_ccnl("energia-petrolio-confindustria.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 0


class TestLoadDistribuzioneCooperativaAncc:
    """Unit tests for CCNL Distribuzione Cooperativa (ANCC-Coop, H016)."""

    def test_distribuzione_cooperativa_ancc_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("distribuzione-cooperativa-ancc.json")
        assert ccnl.meta.ccnl_id == "distribuzione-cooperativa-ancc"
        assert ccnl.meta.cnel_code == "H016"

    def test_distribuzione_cooperativa_ancc_has_9_levels(self) -> None:
        """Contract has exactly 9 levels: Q, 1, 2, 3S, 3, 4S, 4, 5, 6."""
        ccnl = load_ccnl("distribuzione-cooperativa-ancc.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3S", "3", "4S", "4", "5", "6"}

    def test_distribuzione_cooperativa_ancc_level3_salary_2025(self) -> None:
        """L3 minimo tabellare at 2025-05-01 first modelled tranche."""
        ccnl = load_ccnl("distribuzione-cooperativa-ancc.json")
        lv = ccnl.level_by_code("3")
        assert lv.base_salary.value_at(date(2025, 5, 1)) == Decimal("1393.34")

    def test_distribuzione_cooperativa_ancc_level3_salary_2025_dec(self) -> None:
        """L3 minimo tabellare at 2025-12-01 confirmed fourth tranche."""
        ccnl = load_ccnl("distribuzione-cooperativa-ancc.json")
        lv = ccnl.level_by_code("3")
        assert lv.base_salary.value_at(date(2025, 12, 1)) == Decimal("1433.93")

    def test_distribuzione_cooperativa_ancc_level_ordering(self) -> None:
        """Level 6 has lowest order (1); Q has highest order (9)."""
        ccnl = load_ccnl("distribuzione-cooperativa-ancc.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "Q"

    def test_distribuzione_cooperativa_ancc_additional_months(self) -> None:
        """Contract has 14 mensilità (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("distribuzione-cooperativa-ancc.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_distribuzione_cooperativa_ancc_hourly_divisor(self) -> None:
        """Hourly divisor is 165 h/month (38h/week, ilccnl.it)."""
        ccnl = load_ccnl("distribuzione-cooperativa-ancc.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(165)

    def test_distribuzione_cooperativa_ancc_fixed_allowances_contingenza(self) -> None:
        """All levels carry CONTINGENZA and TERZO_ELEMENTO allowances."""
        ccnl = load_ccnl("distribuzione-cooperativa-ancc.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "CONTINGENZA" in codes, lv.code
            assert "TERZO_ELEMENTO" in codes, lv.code

    def test_distribuzione_cooperativa_ancc_tax_sector(self) -> None:
        """Contract uses TERZIARIO tax sector."""
        ccnl = load_ccnl("distribuzione-cooperativa-ancc.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_distribuzione_cooperativa_ancc_seniority_cadence(self) -> None:
        """Seniority: triennial cadence (36 months), maximum 10 scatti."""
        ccnl = load_ccnl("distribuzione-cooperativa-ancc.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadLavanderiIndustrialiAssosistema:
    """Unit tests for CCNL Lavanderie Industriali (D0L1) — turismo comparto."""

    def test_lavanderie_industriali_assosistema_loads(self) -> None:
        """Contract loads with correct id and CNEL code D0L1."""
        ccnl = load_ccnl("lavanderie-industriali-assosistema.json")
        assert ccnl.meta.ccnl_id == "lavanderie-industriali-assosistema"
        assert ccnl.meta.cnel_code == "D0L1"

    def test_lavanderie_industriali_assosistema_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: A1..A3, B1..B3, C1..C3, D2."""
        ccnl = load_ccnl("lavanderie-industriali-assosistema.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D2"}

    def test_lavanderie_industriali_assosistema_level_b2_salary_may2026(self) -> None:
        """B2 minimo tabellare at 2026-05-01 source-confirmed tranche."""
        ccnl = load_ccnl("lavanderie-industriali-assosistema.json")
        lv = ccnl.level_by_code("B2")
        assert lv.base_salary.value_at(date(2026, 5, 1)) == Decimal("1991.35")

    def test_lavanderie_industriali_assosistema_level_b2_salary_dec2026(self) -> None:
        """B2 minimo tabellare at 2026-12-01 derived second tranche."""
        ccnl = load_ccnl("lavanderie-industriali-assosistema.json")
        lv = ccnl.level_by_code("B2")
        assert lv.base_salary.value_at(date(2026, 12, 1)) == Decimal("2012.94")

    def test_lavanderie_industriali_assosistema_level_ordering(self) -> None:
        """A1 has lowest order (1); D2 has highest order (10)."""
        ccnl = load_ccnl("lavanderie-industriali-assosistema.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "A1"
        assert by_order[-1].code == "D2"

    def test_lavanderie_industriali_assosistema_additional_months(self) -> None:
        """Contract has 13 mensilità (tredicesima only, no quattordicesima)."""
        ccnl = load_ccnl("lavanderie-industriali-assosistema.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 6, 1))
        assert val == Decimal(13)

    def test_lavanderie_industriali_assosistema_hourly_divisor(self) -> None:
        """Hourly divisor is 173 h/month (40h/week standard)."""
        ccnl = load_ccnl("lavanderie-industriali-assosistema.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1))
        assert val == Decimal(173)

    def test_lavanderie_industriali_assosistema_incentivo_di_modulo(self) -> None:
        """D2 has INCENTIVO_DI_MODULO and INDENNITA_FUNZIONE; A1 has none."""
        ccnl = load_ccnl("lavanderie-industriali-assosistema.json")
        a1 = ccnl.level_by_code("A1")
        assert a1.fixed_allowances == ()
        d2 = ccnl.level_by_code("D2")
        d2_codes = {a.code for a in d2.fixed_allowances}
        assert "INCENTIVO_DI_MODULO" in d2_codes
        assert "INDENNITA_FUNZIONE" in d2_codes

    def test_lavanderie_industriali_assosistema_tax_sector(self) -> None:
        """Contract uses INDUSTRIA tax sector (Assosistema Confindustria)."""
        ccnl = load_ccnl("lavanderie-industriali-assosistema.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_lavanderie_industriali_assosistema_seniority_cadence(self) -> None:
        """Seniority: biennial cadence (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("lavanderie-industriali-assosistema.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadCedAssoced:
    """Unit tests for CCNL CED, ICT, Professioni Digitali e STP (H601)."""

    def test_ced_assoced_loads(self) -> None:
        """Contract loads with correct id and CNEL code H601."""
        ccnl = load_ccnl("ced-assoced.json")
        assert ccnl.meta.ccnl_id == "ced-assoced"
        assert ccnl.meta.cnel_code == "H601"

    def test_ced_assoced_has_9_levels(self) -> None:
        """Contract has 9 levels: 6, 5, 4, 3, 3S, 2, 1, Q, QDIR."""
        ccnl = load_ccnl("ced-assoced.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"6", "5", "4", "3", "3S", "2", "1", "Q", "QDIR"}

    def test_ced_assoced_level_3_salary_sep2025(self) -> None:
        """L3 paga base conglobata at 2025-09-01 first tranche."""
        ccnl = load_ccnl("ced-assoced.json")
        lv = ccnl.level_by_code("3")
        assert lv.base_salary.value_at(date(2025, 9, 1)) == Decimal("1861.71")

    def test_ced_assoced_level_3_salary_jun2026(self) -> None:
        """L3 paga base conglobata at 2026-06-01 second tranche."""
        ccnl = load_ccnl("ced-assoced.json")
        lv = ccnl.level_by_code("3")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("1907.12")

    def test_ced_assoced_level_ordering(self) -> None:
        """Level 6 has lowest order (1); QDIR has highest order (9)."""
        ccnl = load_ccnl("ced-assoced.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "QDIR"

    def test_ced_assoced_additional_months(self) -> None:
        """Contract has 14 mensilita (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("ced-assoced.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 6, 1))
        assert val == Decimal(14)

    def test_ced_assoced_hourly_divisor(self) -> None:
        """Hourly divisor is 173 h/month (Art. 171)."""
        ccnl = load_ccnl("ced-assoced.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1))
        assert val == Decimal(173)

    def test_ced_assoced_indennita_funzione(self) -> None:
        """Q and QDIR have INDENNITA_FUNZIONE; L3 has none (conglobated)."""
        ccnl = load_ccnl("ced-assoced.json")
        lv3 = ccnl.level_by_code("3")
        assert lv3.fixed_allowances == ()
        q_codes = {a.code for a in ccnl.level_by_code("Q").fixed_allowances}
        qdir_codes = {a.code for a in ccnl.level_by_code("QDIR").fixed_allowances}
        assert "INDENNITA_FUNZIONE" in q_codes
        assert "INDENNITA_FUNZIONE" in qdir_codes

    def test_ced_assoced_tax_sector(self) -> None:
        """Contract uses TERZIARIO tax sector (Confterziario/UGL)."""
        ccnl = load_ccnl("ced-assoced.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_ced_assoced_seniority_cadence(self) -> None:
        """Seniority abolished 2019 for new hires: biennial, maximum_count=0."""
        ccnl = load_ccnl("ced-assoced.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 0


class TestLoadContoterzismoCaiagromec:
    """Tests for CCNL Attivita Agromeccaniche A051 (contoterzismo-caiagromec)."""

    def test_contoterzismo_caiagromec_loads(self) -> None:
        """Contract loads with correct id and CNEL code A051."""
        ccnl = load_ccnl("contoterzismo-caiagromec.json")
        assert ccnl.meta.ccnl_id == "contoterzismo-caiagromec"
        assert ccnl.meta.cnel_code == "A051"

    def test_contoterzismo_caiagromec_has_6_levels(self) -> None:
        """Contract has 6 levels: 1, 2, 3, 4, 5, 6."""
        ccnl = load_ccnl("contoterzismo-caiagromec.json")
        assert len(ccnl.levels) == 6
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6"}

    def test_contoterzismo_caiagromec_level3_salary_jun2024(self) -> None:
        """L3 paga base conglobata at 2024-06-01 first tranche is 1914.03."""
        ccnl = load_ccnl("contoterzismo-caiagromec.json")
        lv = ccnl.level_by_code("3")
        assert lv.base_salary.value_at(date(2024, 6, 1)) == Decimal("1914.03")

    def test_contoterzismo_caiagromec_level3_salary_jun2026(self) -> None:
        """L3 paga base conglobata at 2026-06-01 third tranche is 2014.03."""
        ccnl = load_ccnl("contoterzismo-caiagromec.json")
        lv = ccnl.level_by_code("3")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("2014.03")

    def test_contoterzismo_caiagromec_level_ordering(self) -> None:
        """Level 6 has lowest order (1); level 1 has highest order (6)."""
        ccnl = load_ccnl("contoterzismo-caiagromec.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "1"

    def test_contoterzismo_caiagromec_additional_months(self) -> None:
        """Contract has 14 mensilita (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("contoterzismo-caiagromec.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 6, 1))
        assert val == Decimal(14)

    def test_contoterzismo_caiagromec_hourly_divisor(self) -> None:
        """Hourly divisor is 169 h/month (confirmed lavoro-economia.it)."""
        ccnl = load_ccnl("contoterzismo-caiagromec.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1))
        assert val == Decimal(169)

    def test_contoterzismo_caiagromec_premi_continuita(self) -> None:
        """All levels carry 3 premi di continuita with service thresholds."""
        ccnl = load_ccnl("contoterzismo-caiagromec.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert codes == {
                "PREMIO_CONTINUITA_5YR",
                "PREMIO_CONTINUITA_10YR",
                "PREMIO_CONTINUITA_15YR",
            }
            thresholds = {
                a.code: a.service_months_threshold for a in lv.fixed_allowances
            }
            assert thresholds["PREMIO_CONTINUITA_5YR"] == 60
            assert thresholds["PREMIO_CONTINUITA_10YR"] == 120
            assert thresholds["PREMIO_CONTINUITA_15YR"] == 180

    def test_contoterzismo_caiagromec_tax_sector(self) -> None:
        """Contract uses AGRICOLTURA tax sector."""
        ccnl = load_ccnl("contoterzismo-caiagromec.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_contoterzismo_caiagromec_seniority_cadence(self) -> None:
        """No periodic scatti: maximum_count=0 (only milestone premi exist)."""
        ccnl = load_ccnl("contoterzismo-caiagromec.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 0


class TestLoadConsorziDiBonificaSnebi:
    """Tests for CCNL Consorzi di Bonifica (SNEBI) — CNEL A131."""

    def test_consorzi_di_bonifica_snebi_loads(self) -> None:
        """Contract loads with correct id and CNEL code A131."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        assert ccnl.meta.ccnl_id == "consorzi-di-bonifica-snebi"
        assert ccnl.meta.cnel_code == "A131"

    def test_consorzi_di_bonifica_snebi_has_25_levels(self) -> None:
        """Contract has 25 levels including 4 B-sub-levels."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 25
        assert {
            "D100",
            "C127",
            "B128",
            "B128_ex52",
            "B132",
            "B132_ex51",
            "AQ162",
            "AQ187",
        }.issubset(codes)

    def test_consorzi_di_bonifica_snebi_level_c127_salary_jul2025(self) -> None:
        """C127 post-2000 Jul 2025 salary is 1906.71 (redigo.info)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        lv = ccnl.level_by_code("C127")
        assert lv.base_salary.value_at(date(2025, 7, 1)) == Decimal("1906.71")

    def test_consorzi_di_bonifica_snebi_level_c127_salary_jan2026(self) -> None:
        """C127 post-2000 Jan 2026 salary is 1948.38 (redigo.info)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        lv = ccnl.level_by_code("C127")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1948.38")

    def test_consorzi_di_bonifica_snebi_level_ordering(self) -> None:
        """D100 has lowest order (1); AQ187 has highest order (25)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "D100"
        assert by_order[-1].code == "AQ187"

    def test_consorzi_di_bonifica_snebi_additional_months(self) -> None:
        """Contract has 14 mensilita (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_consorzi_di_bonifica_snebi_hourly_divisor(self) -> None:
        """Hourly divisor 164.67 h/month (38h/week, ilccnl.it source)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal("164.67")

    def test_consorzi_di_bonifica_snebi_no_fixed_allowances(self) -> None:
        """All levels have no fixed allowances (contingenza frozen at 0)."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_consorzi_di_bonifica_snebi_tax_sector(self) -> None:
        """Contract uses AGRICOLTURA tax sector."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_consorzi_di_bonifica_snebi_seniority_tiers(self) -> None:
        """Ten scatti in three tiers: 6 biennial, 1 dodecennial, 3 quadrennial."""
        ccnl = load_ccnl("consorzi-di-bonifica-snebi.json")
        si = ccnl.parameters.seniority_increments
        assert len(si.tiers) == 3
        assert si.tiers[0].cadence_months == 24
        assert si.tiers[0].maximum_count == 6
        assert si.tiers[1].cadence_months == 144
        assert si.tiers[1].maximum_count == 1
        assert si.tiers[2].cadence_months == 48
        assert si.tiers[2].maximum_count == 3
        assert seniority_maximum(si, "C127") == 10


class TestLoadConsorziAgrariAssocap:
    """Tests for CCNL Consorzi Agrari (ASSOCAP) A141."""

    def test_consorzi_agrari_assocap_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        assert ccnl.meta.ccnl_id == "consorzi-agrari-assocap"
        assert ccnl.meta.cnel_code == "A141"

    def test_consorzi_agrari_assocap_has_9_levels(self) -> None:
        """Contract has 9 levels: Q, 1, 2, 3S, 3, 4S, 4, 5, 6."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 9
        assert codes == {
            "Q",
            "1",
            "2",
            "3S",
            "3",
            "4S",
            "4",
            "5",
            "6",
        }

    def test_consorzi_agrari_assocap_level3_salary_2025(self) -> None:
        """Level 3 paga base Jan 2025: 1529.42 (Wolters Kluwer)."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1529.42")

    def test_consorzi_agrari_assocap_level3_salary_2026(self) -> None:
        """Level 3 paga base Jan 2026: 1574.42 (kitech)."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1574.42")

    def test_consorzi_agrari_assocap_level_ordering(self) -> None:
        """Highest order level is Q; lowest is 6."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "6"
        assert sorted_levels[-1].code == "Q"

    def test_consorzi_agrari_assocap_additional_months(self) -> None:
        """Contract has 14 mensilita (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_consorzi_agrari_assocap_hourly_divisor(self) -> None:
        """Hourly divisor 169 h/month (ilccnl.it source)."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(169)

    def test_consorzi_agrari_assocap_split_model_contingenza(self) -> None:
        """Level 3 has CONTINGENZA fixed allowance of 530.19 EUR/month."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        cont = next(a for a in lv.fixed_allowances if a.code == "CONTINGENZA")
        assert cont.monthly.value_at(date(2026, 1, 1)) == Decimal("530.19")

    def test_consorzi_agrari_assocap_tax_sector(self) -> None:
        """Contract uses AGRICOLTURA tax sector."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_consorzi_agrari_assocap_seniority_cadence(self) -> None:
        """Five biennial scatti per Art. 34 CCNL (FLAI-CGIL PDF)."""
        ccnl = load_ccnl("consorzi-agrari-assocap.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadOrganizzazioniAllevatoriAia:
    """Tests for CCNL Organizzazioni Allevatori A221."""

    def test_organizzazioni_allevatori_aia_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        assert ccnl.meta.ccnl_id == "organizzazioni-allevatori-aia"
        assert ccnl.meta.cnel_code == "A221"

    def test_organizzazioni_allevatori_aia_has_13_levels(self) -> None:
        """Contract has 13 levels: 1/2 through 3/2."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 13
        assert codes == {
            "1/2",
            "1/3",
            "1/4",
            "1/5",
            "2/1",
            "2/2",
            "2/3",
            "2/4A",
            "2/4B",
            "2/5",
            "2/6",
            "3/1",
            "3/2",
        }

    def test_organizzazioni_allevatori_aia_level23_salary_sep2025(self) -> None:
        """Level 2/3 minimo Sep 2025: 1895.67 (Wolters Kluwer 2026 ed.)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "2/3")
        assert lv.base_salary.value_at(date(2025, 9, 1)) == Decimal("1895.67")

    def test_organizzazioni_allevatori_aia_level12_salary_sep2025(self) -> None:
        """Level 1/2 minimo Sep 2025: 2392.51 (Wolters Kluwer 2026 ed.)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1/2")
        assert lv.base_salary.value_at(date(2025, 9, 1)) == Decimal("2392.51")

    def test_organizzazioni_allevatori_aia_level_ordering(self) -> None:
        """Highest order level is 1/2; lowest is 3/2."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "3/2"
        assert sorted_levels[-1].code == "1/2"

    def test_organizzazioni_allevatori_aia_additional_months(self) -> None:
        """Contract has 14 mensilita (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_organizzazioni_allevatori_aia_hourly_divisor(self) -> None:
        """Hourly divisor 164.67 h/month (38h/week per Art. 11 CCNL)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal("164.67")

    def test_organizzazioni_allevatori_aia_no_fixed_allowances(self) -> None:
        """All 13 levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_organizzazioni_allevatori_aia_tax_sector(self) -> None:
        """Contract uses AGRICOLTURA tax sector."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_organizzazioni_allevatori_aia_seniority_cadence(self) -> None:
        """Ten biennial scatti per Art. 18 CCNL (FLAI + Confederdia)."""
        ccnl = load_ccnl("organizzazioni-allevatori-aia.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 10


class TestLoadOrtofrutticoliAgrumari:
    """Tests for CCNL Ortofrutticoli ed Agrumari Import-Export H341."""

    def test_ortofrutticoli_agrumari_loads(self) -> None:
        """Contract loads with correct id and CNEL code H341."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        assert ccnl.meta.ccnl_id == "ortofrutticoli-agrumari"
        assert ccnl.meta.cnel_code == "H341"

    def test_ortofrutticoli_agrumari_has_9_levels(self) -> None:
        """Contract has exactly 9 levels: Q, 1-5, 6S, 6, 7."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3", "4", "5", "6S", "6", "7"}

    def test_ortofrutticoli_agrumari_level6_salary_tranche1(self) -> None:
        """Level 6 at 2024-09-01 is 1559.53 EUR (confirmed primary source)."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        lv = ccnl.level_by_code("6")
        assert lv.base_salary.value_at(date(2024, 9, 1)) == Decimal("1559.53")

    def test_ortofrutticoli_agrumari_level_q_salary_tranche3(self) -> None:
        """Level Q at 2026-06-01 is 2396.59 EUR (confirmed from kitech.it)."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        lv = ccnl.level_by_code("Q")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("2396.59")

    def test_ortofrutticoli_agrumari_level_ordering(self) -> None:
        """Q is highest-order level; 7 is lowest-order level."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "7"
        assert by_order[-1].code == "Q"

    def test_ortofrutticoli_agrumari_additional_months(self) -> None:
        """Additional months is 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_ortofrutticoli_agrumari_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week, lavoro-economia.it quote)."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_ortofrutticoli_agrumari_level_q_ind_fun(self) -> None:
        """Level Q has IND_FUN allowance of 154.94 EUR/month."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        lv = ccnl.level_by_code("Q")
        codes = {fa.code for fa in lv.fixed_allowances}
        assert "IND_FUN" in codes
        ind = next(fa for fa in lv.fixed_allowances if fa.code == "IND_FUN")
        assert ind.monthly.value_at(date(2026, 6, 1)) == Decimal("154.94")

    def test_ortofrutticoli_agrumari_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_ortofrutticoli_agrumari_seniority_cadence(self) -> None:
        """Seniority: 36-month cadence (triennale), 13 increments maximum."""
        ccnl = load_ccnl("ortofrutticoli-agrumari.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 13


class TestLoadAlimentariPmiUnionalimentari:
    """Tests for CCNL PMI Alimentare E018 (Unionalimentari-Confapi)."""

    def test_alimentari_pmi_unionalimentari_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        assert ccnl.meta.ccnl_id == "alimentari-pmi-unionalimentari"
        assert ccnl.meta.cnel_code == "E018"

    def test_alimentari_pmi_unionalimentari_has_9_levels(self) -> None:
        """Settore alimentare has exactly 9 levels."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "1", "2", "3", "4", "5", "6", "7", "8"}

    def test_alimentari_pmi_unionalimentari_level4_salary_jun2025(self) -> None:
        """Level 4 paga base Jun 2025: 1672.78 (Unionalimentari circular)."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2025, 6, 1)) == Decimal("1672.78")

    def test_alimentari_pmi_unionalimentari_level4_salary_jan2026(self) -> None:
        """Level 4 paga base Jan 2026: 1746.87 (Unionalimentari circular)."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1746.87")

    def test_alimentari_pmi_unionalimentari_level_ordering(self) -> None:
        """Highest order level is Q; lowest is 8."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        sorted_levels = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_levels[0].code == "8"
        assert sorted_levels[-1].code == "Q"

    def test_alimentari_pmi_unionalimentari_additional_months(self) -> None:
        """Contract has 14 mensilita (Art. 4.1 CCNL text)."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_alimentari_pmi_unionalimentari_hourly_divisor(self) -> None:
        """Hourly divisor 173 h/month (Art. 4.3 CCNL text)."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        val = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert val == Decimal(173)

    def test_alimentari_pmi_unionalimentari_split_allowances(self) -> None:
        """All 9 levels carry CONTINGENZA and EDR allowances (split model)."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert codes == {"CONTINGENZA", "EDR"}

    def test_alimentari_pmi_unionalimentari_tax_sector(self) -> None:
        """Contract uses INDUSTRIA tax sector."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_alimentari_pmi_unionalimentari_seniority_cadence(self) -> None:
        """Five biennial scatti per Art. 5.5 CCNL text."""
        ccnl = load_ccnl("alimentari-pmi-unionalimentari.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


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


class TestLoadRecapitoCorrispondenzaFise:
    """Tests for CCNL Recapito Corrispondenza FISE-ARE (K711)."""

    def test_recapito_corrispondenza_fise_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert ccnl.meta.ccnl_id == "recapito-corrispondenza-fise"
        assert ccnl.meta.cnel_code == "K711"

    def test_recapito_corrispondenza_fise_has_8_levels(self) -> None:
        """Contract has exactly 8 levels with codes 1,2,3S,3,4,5S,5,6."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3S", "3", "4", "5S", "5", "6"}

    def test_recapito_corrispondenza_fise_level3_salary_feb2024(self) -> None:
        """Level 3 base salary at 2024-02-01: 1567.29 EUR (1st tranche)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 2, 1)) == Decimal("1567.29")

    def test_recapito_corrispondenza_fise_level3_salary_jun2026(self) -> None:
        """Level 3 base salary at 2026-06-01: 1687.29 EUR (4th tranche)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("1687.29")

    def test_recapito_corrispondenza_fise_level_ordering(self) -> None:
        """Level 1 is highest; level 6 is lowest."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "6"
        assert ordered[-1].code == "1"

    def test_recapito_corrispondenza_fise_additional_months(self) -> None:
        """14 mensilita: tredicesima + quattordicesima."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_recapito_corrispondenza_fise_hourly_divisor(self) -> None:
        """Hourly divisor 173 (confirmed from ilccnl.it cross-check)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 173

    def test_recapito_corrispondenza_fise_edr_allowance(self) -> None:
        """All 8 levels have EDR=10.33 as fixed_allowance (split model)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "EDR"

    def test_recapito_corrispondenza_fise_tax_sector(self) -> None:
        """tax_sector == TERZIARIO."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_recapito_corrispondenza_fise_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), max 8 scatti."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 8


class TestLoadServiziPostaliAppaltoFise:
    """Tests for CCNL Servizi Postali in Appalto (FISE-ARE, K721)."""

    def test_servizi_postali_appalto_fise_loads(self) -> None:
        """Contract loads with correct id and CNEL code K721."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert ccnl.meta.ccnl_id == "servizi-postali-appalto-fise"
        assert ccnl.meta.cnel_code == "K721"

    def test_servizi_postali_appalto_fise_has_7_levels(self) -> None:
        """7 levels: 1, 2, 3S, 3, 4S, 4, 5."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3S", "3", "4S", "4", "5"}

    def test_servizi_postali_appalto_fise_level3_salary_jan2024(self) -> None:
        """Level 3 base salary at 2024-01-01: 1448.09 EUR (1st tranche)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1448.09")

    def test_servizi_postali_appalto_fise_level3_salary_dec2025(self) -> None:
        """Level 3 base salary at 2025-12-01: 1509.09 EUR (3rd tranche)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2025, 12, 1)) == Decimal("1509.09")

    def test_servizi_postali_appalto_fise_level_ordering(self) -> None:
        """Level 1 is highest (order=7); level 5 is lowest (order=1)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "5"
        assert ordered[-1].code == "1"

    def test_servizi_postali_appalto_fise_additional_months(self) -> None:
        """14 mensilita: tredicesima (Art. 37) + quattordicesima (Art. 38)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_servizi_postali_appalto_fise_hourly_divisor(self) -> None:
        """Hourly divisor 173 (Art. 33 explicit)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 173

    def test_servizi_postali_appalto_fise_fixed_allowances(self) -> None:
        """All 7 levels have IND-INT and EDR as fixed allowances (split model)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert codes == {"IND-INT", "EDR"}

    def test_servizi_postali_appalto_fise_tax_sector(self) -> None:
        """tax_sector == TERZIARIO."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_servizi_postali_appalto_fise_seniority_cadence(self) -> None:
        """Seniority: biennale (24 mo), max=10, first at 48 mo (impiegati)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 10
        assert si.first_cadence_months == 48

    def test_servizi_postali_appalto_fise_operaio_seniority_max_1(self) -> None:
        """Operaio maximum_count=1 (Art. 35A single premio)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        si = ccnl.parameters.seniority_increments
        assert si.maximum_count_by_category.get("operaio") == 1

    def test_servizi_postali_appalto_fise_seniority_category_amounts(
        self,
    ) -> None:
        """Operaio and impiegato have different seniority amounts at L2."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        si = ccnl.parameters.seniority_increments
        op = si.amount_by_level_by_category["operaio"]["2"]
        imp = si.amount_by_level_by_category["impiegato"]["2"]
        assert op.value_at(date(2026, 1, 1)) == Decimal("56.66")
        assert imp.value_at(date(2026, 1, 1)) == Decimal("62.62")


class TestLoadPortieriFabbricatiConfedilizia:
    """Tests for CCNL Dipendenti da Proprietari di Fabbricati (H401)."""

    def test_portieri_fabbricati_confedilizia_loads(self) -> None:
        """Contract loads with correct id and CNEL code H401."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert ccnl.meta.ccnl_id == "portieri-fabbricati-confedilizia"
        assert ccnl.meta.cnel_code == "H401"

    def test_portieri_fabbricati_confedilizia_has_11_levels(self) -> None:
        """11 levels: B1-B5, C3, C4, D1-D4 (A and C1/C2 excluded)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "B1",
            "B2",
            "B3",
            "B4",
            "B5",
            "C3",
            "C4",
            "D1",
            "D2",
            "D3",
            "D4",
        }

    def test_portieri_fabbricati_confedilizia_level_b1_salary_2026(
        self,
    ) -> None:
        """B1 base salary at 2026-01-01: 1519.10 EUR (1st tranche)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B1")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1519.10")

    def test_portieri_fabbricati_confedilizia_level_c3_salary_2028(
        self,
    ) -> None:
        """C3 base salary at 2028-01-01: 1868.50 EUR (3rd tranche)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C3")
        assert lv.base_salary.value_at(date(2028, 1, 1)) == Decimal("1868.50")

    def test_portieri_fabbricati_confedilizia_level_ordering(self) -> None:
        """C3 is highest (order=11); B5 is lowest (order=1)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "B5"
        assert ordered[-1].code == "C3"

    def test_portieri_fabbricati_confedilizia_additional_months(self) -> None:
        """13 mensilita: tredicesima only (Art. 130 Gratifica natalizia)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 6, 1))
        assert val == Decimal(13)

    def test_portieri_fabbricati_confedilizia_hourly_divisor(self) -> None:
        """Hourly divisor 173 (40 h/week, Art. 60/62/69 CCNL)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1)) == 173

    def test_portieri_fabbricati_confedilizia_no_fixed_allowances(
        self,
    ) -> None:
        """All 11 levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_portieri_fabbricati_confedilizia_tax_sector(self) -> None:
        """tax_sector == TERZIARIO."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_portieri_fabbricati_confedilizia_seniority_cadence(self) -> None:
        """Seniority: triennale (36 mo), max=12 scatti."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 12


class TestLoadMetalmeccanicaCooperative:
    """Tests for CCNL Metalmeccanica - Cooperative (C016)."""

    def test_metalmeccanica_cooperative_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        assert ccnl.meta.ccnl_id == "metalmeccanica-cooperative"
        assert ccnl.meta.cnel_code == "C016"

    def test_metalmeccanica_cooperative_has_9_levels(self) -> None:
        """Contract has exactly 9 levels with correct codes."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"D1", "D2", "C1", "C2", "C3", "B1", "B2", "B3", "A1"}

    def test_metalmeccanica_cooperative_level_d1_salary_2025(self) -> None:
        """D1 base salary at first tranche (2025-06-01)."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        d1 = next(lv for lv in ccnl.levels if lv.code == "D1")
        assert d1.base_salary.value_at(date(2025, 6, 1)) == Decimal("1754.06")

    def test_metalmeccanica_cooperative_level_a1_salary_2026(self) -> None:
        """A1 base salary at second tranche (2026-06-01)."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        a1 = next(lv for lv in ccnl.levels if lv.code == "A1")
        assert a1.base_salary.value_at(date(2026, 6, 1)) == Decimal("3054.52")

    def test_metalmeccanica_cooperative_level_ordering(self) -> None:
        """A1 is the highest-order level; D1 is the lowest."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "D1"
        assert by_order[-1].code == "A1"

    def test_metalmeccanica_cooperative_additional_months(self) -> None:
        """Contract provides 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 6, 1)) == Decimal(
            13
        )

    def test_metalmeccanica_cooperative_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week, metalmeccanici standard)."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1)) == Decimal(173)

    def test_metalmeccanica_cooperative_fixed_allowances(self) -> None:
        """A1 and B3 have IND_FUN allowances; all others have none."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        a1 = next(lv for lv in ccnl.levels if lv.code == "A1")
        b3 = next(lv for lv in ccnl.levels if lv.code == "B3")
        c2 = next(lv for lv in ccnl.levels if lv.code == "C2")
        assert len(a1.fixed_allowances) == 1
        assert a1.fixed_allowances[0].code == "IND_FUN"
        assert a1.fixed_allowances[0].monthly.value_at(date(2026, 6, 1)) == Decimal(
            "180.00"
        )
        assert len(b3.fixed_allowances) == 1
        assert b3.fixed_allowances[0].monthly.value_at(date(2026, 6, 1)) == Decimal(
            "120.00"
        )
        assert c2.fixed_allowances == ()

    def test_metalmeccanica_cooperative_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_metalmeccanica_cooperative_seniority_cadence(self) -> None:
        """Seniority increments: biennali (24 months), max 5."""
        ccnl = load_ccnl("metalmeccanica-cooperative.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadScuolePrivatelaicheAninsei:
    """Tests for CCNL Scuole Private Laiche ANINSEI (T231)."""

    def test_scuole_private_laiche_aninsei_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        assert ccnl.meta.ccnl_id == "scuole-private-laiche-aninsei"
        assert ccnl.meta.cnel_code == "T231"

    def test_scuole_private_laiche_aninsei_has_9_levels(self) -> None:
        """Contract has exactly 9 levels with the expected codes."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"I", "II", "III", "IV", "V", "VI", "VII", "VIII_A", "VIII_B"}

    def test_scuole_private_laiche_aninsei_level4_salary_2024(self) -> None:
        """Level IV base salary at first tranche (2024-06-15) = 1397.56 EUR."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        lv = next(x for x in ccnl.levels if x.code == "IV")
        assert lv.base_salary.value_at(date(2024, 6, 15)) == Decimal("1397.56")

    def test_scuole_private_laiche_aninsei_level4_salary_2026(self) -> None:
        """Level IV base salary at third tranche (2026-01-01) = 1491.38 EUR."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        lv = next(x for x in ccnl.levels if x.code == "IV")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1491.38")

    def test_scuole_private_laiche_aninsei_level_ordering(self) -> None:
        """Lowest order is I (1), highest order is VIII_B (9)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "I"
        assert by_order[-1].code == "VIII_B"

    def test_scuole_private_laiche_aninsei_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_scuole_private_laiche_aninsei_hourly_divisor(self) -> None:
        """Hourly divisor = 165 (38h/week, Art. 27)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_scuole_private_laiche_aninsei_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_scuole_private_laiche_aninsei_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_scuole_private_laiche_aninsei_seniority_cadence(self) -> None:
        """Seniority frozen: maximum_count=0 (milestone-based, Art. 24)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadIstituzioniServiziSocioAssistenzialiAnaste:
    """Tests for CCNL Istituzioni e Servizi Socio-Assistenziali ANASTE (T131)."""

    def test_anaste_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        assert ccnl.meta.ccnl_id == "istituzioni-servizi-socio-assistenziali-anaste"
        assert ccnl.meta.cnel_code == "T131"

    def test_anaste_has_12_levels(self) -> None:
        """Contract has exactly 12 levels with the expected codes."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        assert len(ccnl.levels) == 12
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "10", "9", "8", "7", "6", "5", "4", "3S", "3", "2", "1"}

    def test_anaste_level6_salary_pre2025(self) -> None:
        """Level 6 base salary before 2025-08-01 = 1604.06 EUR (Art. 69)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        lv = next(x for x in ccnl.levels if x.code == "6")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1604.06")

    def test_anaste_level6_salary_2025(self) -> None:
        """Level 6 base salary from 2025-08-01 = 1696.37 EUR (CCNL rinnovo)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        lv = next(x for x in ccnl.levels if x.code == "6")
        assert lv.base_salary.value_at(date(2025, 8, 1)) == Decimal("1696.37")

    def test_anaste_level_ordering(self) -> None:
        """Lowest order is level 1 (order=1), highest is Q (order=12)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_anaste_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only, Art. 74)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        assert ccnl.parameters.additional_months.value_at(date(2025, 8, 1)) == Decimal(
            13
        )

    def test_anaste_hourly_divisor(self) -> None:
        """Hourly divisor = 164 (38h/week, Art. 72)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2025, 8, 1)) == Decimal(164)

    def test_anaste_level_q_fixed_allowance(self) -> None:
        """Level Q has indennita di funzione 77.47 EUR/month (Art. 70)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        lv_q = next(x for x in ccnl.levels if x.code == "Q")
        assert len(lv_q.fixed_allowances) == 1
        fa = lv_q.fixed_allowances[0]
        assert fa.code == "INDENNITA_FUNZIONE"
        assert fa.monthly.value_at(date(2025, 8, 1)) == Decimal("77.47")

    def test_anaste_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_anaste_seniority_cadence(self) -> None:
        """Seniority: cadence 36 months, max 10 scatti (Art. 73)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadScuoleMaternieFism:
    """Tests for CCNL Scuole Materne FISM (T271)."""

    def test_fism_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        assert ccnl.meta.ccnl_id == "scuole-materne-fism"
        assert ccnl.meta.cnel_code == "T271"

    def test_fism_has_8_levels(self) -> None:
        """Contract has exactly 8 levels with codes I through VIII."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"I", "II", "III", "IV", "V", "VI", "VII", "VIII"}

    def test_fism_level5_salary_2023(self) -> None:
        """Level V base salary at first tranche (2023-09-01) = 1564.87 EUR."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        lv = next(x for x in ccnl.levels if x.code == "V")
        assert lv.base_salary.value_at(date(2023, 9, 1)) == Decimal("1564.87")

    def test_fism_level5_salary_2026(self) -> None:
        """Level V base salary from 2026-09-01 (accord tranche) = 1679.76 EUR."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        lv = next(x for x in ccnl.levels if x.code == "V")
        assert lv.base_salary.value_at(date(2026, 9, 1)) == Decimal("1679.76")

    def test_fism_level_ordering(self) -> None:
        """Lowest order is I (1), highest order is VIII (8)."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "I"
        assert by_order[-1].code == "VIII"

    def test_fism_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only, Art. 49)."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            13
        )

    def test_fism_hourly_divisor(self) -> None:
        """Hourly divisor = 160 (37h/week, Art. 51)."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == Decimal(160)

    def test_fism_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_fism_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_fism_seniority_frozen(self) -> None:
        """Seniority frozen: maximum_count=0 (historic scatti frozen, Arts. 44-46)."""
        ccnl = load_ccnl("scuole-materne-fism.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadOcchialiOcchialeriaIndustria:
    """Tests for D271 CCNL Occhiali e Occhialeria — Industria (ANFAO)."""

    def test_occhiali_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        assert ccnl.meta.ccnl_id == "occhiali-occhialeria-industria"
        assert ccnl.meta.cnel_code == "D271"

    def test_occhiali_has_10_levels(self) -> None:
        """Contract has exactly 10 levels with correct codes."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "3S", "4", "4S", "5", "5S", "6", "Q"}

    def test_occhiali_level4_salary_2023(self) -> None:
        """Level 4 tabular minimum at 01/05/2023 first tranche = 1887.96."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2023, 5, 1)) == Decimal("1887.96")

    def test_occhiali_level4_salary_2026(self) -> None:
        """Level 4 tabular minimum at 01/03/2026 renewal tranche = 2042.96."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2026, 3, 1)) == Decimal("2042.96")

    def test_occhiali_level_ordering(self) -> None:
        """Q is highest order (10); level 1 is lowest order (1)."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_occhiali_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only)."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 3, 1)) == Decimal(
            13
        )

    def test_occhiali_hourly_divisor(self) -> None:
        """Hourly divisor = 173 (standard 40h/week)."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 3, 1)) == Decimal(173)

    def test_occhiali_level_q_fixed_allowance(self) -> None:
        """Level Q carries INDENNITA_FUNZIONE allowance of 82.63 EUR/month."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "Q")
        assert len(lv.fixed_allowances) == 1
        fa = lv.fixed_allowances[0]
        assert fa.code == "INDENNITA_FUNZIONE"
        assert fa.monthly.value_at(date(2026, 3, 1)) == Decimal("82.63")

    def test_occhiali_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_occhiali_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence, max 5 scatti biennali."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_occhiali_non_q_no_fixed_allowances(self) -> None:
        """Conglobated model: all non-Q levels have no fixed allowances."""
        ccnl = load_ccnl("occhiali-occhialeria-industria.json")
        for lv in ccnl.levels:
            if lv.code != "Q":
                assert lv.fixed_allowances == ()


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


class TestLoadAlimentaristiCooperativeE016:
    """Tests for CCNL Alimentaristi Cooperative (E016)."""

    def test_e016_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        assert ccnl.meta.ccnl_id == "alimentaristi-cooperative-e016"
        assert ccnl.meta.cnel_code == "E016"

    def test_e016_has_8_levels(self) -> None:
        """Contract has exactly 8 levels."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 8
        assert codes == {"6", "5", "4", "3", "3A", "2", "1", "1A"}

    def test_e016_level_3_base_salary_2025(self) -> None:
        """Level 3 paga base at 2025-01-01 is 1509.22 EUR."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("1509.22")

    def test_e016_level_3_base_salary_2026(self) -> None:
        """Level 3 paga base at 2026-01-01 is 1566.16 EUR."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1566.16")

    def test_e016_level_ordering(self) -> None:
        """Level 6 is lowest order (1), 1A is highest order (8)."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "6"
        assert levels_by_order[-1].code == "1A"

    def test_e016_additional_months(self) -> None:
        """Additional months is 14."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_e016_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_e016_level_3_contingenza(self) -> None:
        """Level 3 contingenza frozen at 522.32 EUR/month."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        cont = next(fa for fa in lv.fixed_allowances if fa.code == "CONTINGENZA")
        assert cont.monthly.value_at(date(2026, 1, 1)) == Decimal("522.32")
        assert cont.months_per_year == 14

    def test_e016_level_3_edr(self) -> None:
        """Level 3 EDR is 10.33 EUR at 13 months."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        edr = next(fa for fa in lv.fixed_allowances if fa.code == "EDR")
        assert edr.monthly.value_at(date(2026, 1, 1)) == Decimal("10.33")
        assert edr.months_per_year == 13

    def test_e016_level_3_iar(self) -> None:
        """Level 3 IAR is 85.41 EUR (first period) at 14 months."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        iar = next(fa for fa in lv.fixed_allowances if fa.code == "IAR")
        assert iar.monthly.value_at(date(2026, 1, 1)) == Decimal("85.41")
        assert iar.months_per_year == 14

    def test_e016_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_e016_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence, maximum 5 scatti."""
        ccnl = load_ccnl("alimentaristi-cooperative-e016.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadTurismoConfesercenti:
    """Tests for CCNL Turismo Confesercenti (H058)."""

    def test_h058_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        assert ccnl.meta.ccnl_id == "turismo-confesercenti"
        assert ccnl.meta.cnel_code == "H058"

    def test_h058_has_10_levels(self) -> None:
        """Contract has exactly 10 levels."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 10
        assert codes == {"7", "6", "6S", "5", "4", "3", "2", "1", "QB", "QA"}

    def test_h058_level_3_salary_2024(self) -> None:
        """Level 3 base salary at 2024-07-01 is 1717.55 EUR."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 7, 1)) == Decimal("1717.55")

    def test_h058_level_3_salary_2026(self) -> None:
        """Level 3 base salary at 2026-05-01 is 1797.04 EUR."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 5, 1)) == Decimal("1797.04")

    def test_h058_level_ordering(self) -> None:
        """Level 7 is lowest order (1), QA is highest order (10)."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "7"
        assert levels_by_order[-1].code == "QA"

    def test_h058_additional_months(self) -> None:
        """Additional months is 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 5, 1)) == Decimal(
            14
        )

    def test_h058_hourly_divisor(self) -> None:
        """Hourly divisor is 172."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 5, 1)) == Decimal(172)

    def test_h058_no_fixed_allowances(self) -> None:
        """Level 3 has no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.fixed_allowances == ()

    def test_h058_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_h058_seniority_cadence(self) -> None:
        """Seniority: 36-month cadence, maximum 6 scatti."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 6

    def test_h058_qa_salary_2026(self) -> None:
        """Level QA base salary at 2026-05-01 is 2416.82 EUR."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "QA")
        assert lv.base_salary.value_at(date(2026, 5, 1)) == Decimal("2416.82")

    def test_h058_level_7_final_tranche(self) -> None:
        """Level 7 base salary at 2027-11-01 is 1458.42 EUR."""
        ccnl = load_ccnl("turismo-confesercenti.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "7")
        assert lv.base_salary.value_at(date(2027, 11, 1)) == Decimal("1458.42")


class TestLoadRsaAiop:
    """Tests for CCNL RSA e Strutture Residenziali AIOP (T091)."""

    def test_t091_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("rsa-aiop.json")
        assert ccnl.meta.ccnl_id == "rsa-aiop"
        assert ccnl.meta.cnel_code == "T091"

    def test_t091_has_12_levels(self) -> None:
        """Contract has exactly 12 levels."""
        ccnl = load_ccnl("rsa-aiop.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 12
        assert codes == {
            "A",
            "B",
            "C",
            "D1",
            "D2",
            "D3",
            "E1",
            "E2",
            "E3",
            "F",
            "G",
            "H",
        }

    def test_t091_level_d2_salary_2012(self) -> None:
        """Level D2 base salary at 2012-04-01 is 1325.00 EUR."""
        ccnl = load_ccnl("rsa-aiop.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "D2")
        assert lv.base_salary.value_at(date(2012, 4, 1)) == Decimal("1325.00")

    def test_t091_level_d2_salary_2023(self) -> None:
        """Level D2 base salary at 2023-10-01 is 1463.33 EUR."""
        ccnl = load_ccnl("rsa-aiop.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "D2")
        assert lv.base_salary.value_at(date(2023, 10, 1)) == Decimal("1463.33")

    def test_t091_level_ordering(self) -> None:
        """Level A is lowest order (1), H is highest order (12)."""
        ccnl = load_ccnl("rsa-aiop.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "A"
        assert levels_by_order[-1].code == "H"

    def test_t091_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("rsa-aiop.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_t091_hourly_divisor(self) -> None:
        """Hourly divisor is 165."""
        ccnl = load_ccnl("rsa-aiop.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_t091_no_fixed_allowances(self) -> None:
        """Level D2 has no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("rsa-aiop.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "D2")
        assert lv.fixed_allowances == ()

    def test_t091_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("rsa-aiop.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_t091_seniority_cadence(self) -> None:
        """Seniority: 60-month cadence, maximum 1 scatto."""
        ccnl = load_ccnl("rsa-aiop.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 60
        assert si.maximum_count == 1

    def test_t091_seniority_a_level(self) -> None:
        """Level A seniority is 40.00 EUR."""
        ccnl = load_ccnl("rsa-aiop.json")
        si = ccnl.parameters.seniority_increments
        assert si.amount_by_level["A"].value_at(date(2026, 1, 1)) == Decimal("40.00")

    def test_t091_seniority_h_level_zero(self) -> None:
        """Level H (excluded from seniority) has 0.00 EUR scatto."""
        ccnl = load_ccnl("rsa-aiop.json")
        si = ccnl.parameters.seniority_increments
        assert si.amount_by_level["H"].value_at(date(2026, 1, 1)) == Decimal("0.00")


class TestLoadAutostradeTrafori:
    """Tests for CCNL Autostrade e Trafori Concessionari (I192)."""

    def test_i192_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("autostrade-trafori.json")
        assert ccnl.meta.ccnl_id == "autostrade-trafori"
        assert ccnl.meta.cnel_code == "I192"

    def test_i192_has_11_levels(self) -> None:
        """Contract has exactly 11 levels."""
        ccnl = load_ccnl("autostrade-trafori.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 11
        assert codes == {
            "D",
            "C1",
            "C",
            "C+",
            "B1",
            "B1+",
            "B",
            "B+",
            "A1",
            "A",
            "AQ",
        }

    def test_i192_level_b_salary_2023(self) -> None:
        """Level B base salary at 2023-01-01 is 2200.85 EUR."""
        ccnl = load_ccnl("autostrade-trafori.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B")
        assert lv.base_salary.value_at(date(2023, 1, 1)) == Decimal("2200.85")

    def test_i192_level_b_salary_2026(self) -> None:
        """Level B base salary at 2026-08-01 is 2469.60 EUR."""
        ccnl = load_ccnl("autostrade-trafori.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B")
        assert lv.base_salary.value_at(date(2026, 8, 1)) == Decimal("2469.60")

    def test_i192_level_ordering(self) -> None:
        """Level D is lowest order (1), AQ is highest order (11)."""
        ccnl = load_ccnl("autostrade-trafori.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "D"
        assert levels_by_order[-1].code == "AQ"

    def test_i192_additional_months(self) -> None:
        """Additional months is 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("autostrade-trafori.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 8, 1)) == Decimal(
            14
        )

    def test_i192_hourly_divisor(self) -> None:
        """Hourly divisor is 167."""
        ccnl = load_ccnl("autostrade-trafori.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 8, 1)) == Decimal(167)

    def test_i192_fixed_allowances_present(self) -> None:
        """Level B has CONTINGENZA, EDR_1991, EDR_1997, IDR_2021."""
        ccnl = load_ccnl("autostrade-trafori.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B")
        codes = {fa.code for fa in lv.fixed_allowances}
        assert codes == {"CONTINGENZA", "EDR_1991", "EDR_1997", "IDR_2021"}

    def test_i192_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("autostrade-trafori.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_i192_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence, maximum 9 scatti."""
        ccnl = load_ccnl("autostrade-trafori.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 9

    def test_i192_aq_has_ind_funzione(self) -> None:
        """AQ level has IND_FUNZIONE allowance (72.30 EUR/month)."""
        ccnl = load_ccnl("autostrade-trafori.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "AQ")
        ind_f = next(fa for fa in lv.fixed_allowances if fa.code == "IND_FUNZIONE")
        assert ind_f.monthly.value_at(date(2026, 8, 1)) == Decimal("72.30")

    def test_i192_edr1991_months_per_year(self) -> None:
        """EDR_1991 allowance is paid 13 months per year."""
        ccnl = load_ccnl("autostrade-trafori.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B")
        edr = next(fa for fa in lv.fixed_allowances if fa.code == "EDR_1991")
        assert edr.months_per_year == 13


class TestLoadCooperativeConsorziAgricoli:
    """Tests for CCNL Cooperative e Consorzi Agricoli (A016)."""

    def test_a016_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        assert ccnl.meta.ccnl_id == "cooperative-consorzi-agricoli"
        assert ccnl.meta.cnel_code == "A016"

    def test_a016_has_8_levels(self) -> None:
        """Contract has exactly 8 levels."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 8
        assert codes == {"np", "7", "6", "5", "4", "3", "2", "1"}

    def test_a016_level_3_salary_2024(self) -> None:
        """Level 3 base salary at 2024-04-01 is 1821.25 EUR."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 4, 1)) == Decimal("1821.25")

    def test_a016_level_3_salary_2026(self) -> None:
        """Level 3 base salary at 2026-05-01 is 1877.79 EUR."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 5, 1)) == Decimal("1877.79")

    def test_a016_level_ordering(self) -> None:
        """Level np is lowest order (1), level 1 is highest order (8)."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        levels_by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert levels_by_order[0].code == "np"
        assert levels_by_order[-1].code == "1"

    def test_a016_additional_months(self) -> None:
        """Additional months is 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 5, 1)) == Decimal(
            14
        )

    def test_a016_hourly_divisor(self) -> None:
        """Hourly divisor is 169."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 5, 1)) == Decimal(169)

    def test_a016_level_3_no_allowances(self) -> None:
        """Level 3 has no fixed allowances (operaio, no funzione)."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.fixed_allowances == ()

    def test_a016_tax_sector(self) -> None:
        """Tax sector is agricoltura."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_a016_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence, maximum 12 scatti."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 12

    def test_a016_level_1_has_ind_funzione(self) -> None:
        """Level 1 has IND_FUNZIONE_1 allowance (230.00 from Aug 2024)."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1")
        ind = next(fa for fa in lv.fixed_allowances if fa.code == "IND_FUNZIONE_1")
        assert ind.monthly.value_at(date(2024, 8, 1)) == Decimal("230.00")

    def test_a016_level_1_ind_funzione_old_value(self) -> None:
        """IND_FUNZIONE_1 before Aug 2024 is 180.00 EUR."""
        ccnl = load_ccnl("cooperative-consorzi-agricoli.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1")
        ind = next(fa for fa in lv.fixed_allowances if fa.code == "IND_FUNZIONE_1")
        assert ind.monthly.value_at(date(2024, 4, 1)) == Decimal("180.00")


class TestLoadAnas:
    """Unit tests for CCNL Gruppo ANAS (T511)."""

    def test_t511_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("anas.json")
        assert ccnl.meta.ccnl_id == "anas"
        assert ccnl.meta.cnel_code == "T511"

    def test_t511_has_7_levels(self) -> None:
        """Contract has exactly 7 levels: C1 C B2 B1 B A1 A."""
        ccnl = load_ccnl("anas.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"C1", "C", "B2", "B1", "B", "A1", "A"}

    def test_t511_level_b1_salary_tranche1(self) -> None:
        """Level B1 minimo tabellare at 01/03/2026 is 2074.84."""
        ccnl = load_ccnl("anas.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B1")
        assert lv.base_salary.value_at(date(2026, 3, 1)) == Decimal("2074.84")

    def test_t511_level_b1_salary_tranche2(self) -> None:
        """Level B1 minimo tabellare at 01/09/2026 is 2124.84."""
        ccnl = load_ccnl("anas.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B1")
        assert lv.base_salary.value_at(date(2026, 9, 1)) == Decimal("2124.84")

    def test_t511_level_ordering(self) -> None:
        """Level C1 is lowest (order 1), level A is highest (order 7)."""
        ccnl = load_ccnl("anas.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "C1"
        assert by_order[-1].code == "A"

    def test_t511_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("anas.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            13
        )

    def test_t511_hourly_divisor(self) -> None:
        """Hourly divisor is 156."""
        ccnl = load_ccnl("anas.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == Decimal(156)

    def test_t511_iis_allowance_present(self) -> None:
        """Every level has exactly one fixed allowance: IIS."""
        ccnl = load_ccnl("anas.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert codes == {"IIS"}

    def test_t511_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("anas.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_t511_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence, maximum 10 scatti."""
        ccnl = load_ccnl("anas.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 10

    def test_t511_level_a_iis_value(self) -> None:
        """Level A IIS monthly value is 553.45."""
        ccnl = load_ccnl("anas.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "A")
        iis = next(fa for fa in lv.fixed_allowances if fa.code == "IIS")
        assert iis.monthly.value_at(date(2026, 9, 1)) == Decimal("553.45")

    def test_t511_apprenticeship_percentage(self) -> None:
        """Apprenticeship first period is 70% (professionalizzante)."""
        ccnl = load_ccnl("anas.json")
        assert len(ccnl.apprenticeship) == 1
        appr = ccnl.apprenticeship[0]
        assert isinstance(appr, ApprenticeshipPercentage)
        assert appr.periods[0].percentage == Decimal("0.70")


class TestLoadVigilanzaPrivataFederdatGpg:
    """Unit tests for CCNL Vigilanza Privata FEDERDAT GPG (HV17)."""

    def test_hv17_gpg_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        assert ccnl.meta.ccnl_id == "vigilanza-privata-federdat-gpg"
        assert ccnl.meta.cnel_code == "HV17"

    def test_hv17_gpg_has_7_levels(self) -> None:
        """Contract has exactly 7 levels: VI V IV III II I Q."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"VI", "V", "IV", "III", "II", "I", "Q"}

    def test_hv17_gpg_level_iii_salary_tranche1(self) -> None:
        """Level III base salary at 01/06/2023 is 1483.31 EUR."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "III")
        assert lv.base_salary.value_at(date(2023, 6, 1)) == Decimal("1483.31")

    def test_hv17_gpg_level_iii_salary_tranche2(self) -> None:
        """Level III base salary at 01/04/2026 is 1651.31 EUR."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "III")
        assert lv.base_salary.value_at(date(2026, 4, 1)) == Decimal("1651.31")

    def test_hv17_gpg_level_ordering(self) -> None:
        """Level VI is lowest (order 1), Q is highest (order 7)."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "VI"
        assert by_order[-1].code == "Q"

    def test_hv17_gpg_additional_months(self) -> None:
        """Additional months is 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 4, 1)) == Decimal(
            14
        )

    def test_hv17_gpg_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 4, 1)) == Decimal(173)

    def test_hv17_gpg_no_fixed_allowances(self) -> None:
        """All GPG levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_hv17_gpg_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_hv17_gpg_seniority_cadence(self) -> None:
        """Seniority: 36-month cadence, max 10 scatti (raised by July 2026 rinnovo)."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10

    def test_hv17_gpg_level_q_salary_last_tranche(self) -> None:
        """Level Q base salary at 01/12/2026 is 2434.74 EUR."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "Q")
        assert lv.base_salary.value_at(date(2026, 12, 1)) == Decimal("2434.74")

    def test_hv17_gpg_apprenticeship_passthrough(self) -> None:
        """Apprenticeship is 100% passthrough (SIMPLIFICATION)."""
        ccnl = load_ccnl("vigilanza-privata-federdat-gpg.json")
        assert len(ccnl.apprenticeship) == 1
        appr = ccnl.apprenticeship[0]
        assert isinstance(appr, ApprenticeshipPercentage)
        assert appr.periods[0].percentage == Decimal("1.00")


class TestLoadVigilanzaPrivataFederdatSf:
    """Unit tests for CCNL Vigilanza Privata FEDERDAT SF (HV17)."""

    def test_hv17_sf_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        assert ccnl.meta.ccnl_id == "vigilanza-privata-federdat-sf"
        assert ccnl.meta.cnel_code == "HV17"

    def test_hv17_sf_has_5_levels(self) -> None:
        """Contract has exactly 5 levels: E D C B A."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        assert len(ccnl.levels) == 5
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"E", "D", "C", "B", "A"}

    def test_hv17_sf_level_c_salary_tranche1(self) -> None:
        """Level C base salary at 01/06/2023 is 1333.43 EUR."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C")
        assert lv.base_salary.value_at(date(2023, 6, 1)) == Decimal("1333.43")

    def test_hv17_sf_level_c_salary_last_tranche(self) -> None:
        """Level C base salary at 01/04/2026 is 1556.29 EUR."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C")
        assert lv.base_salary.value_at(date(2026, 4, 1)) == Decimal("1556.29")

    def test_hv17_sf_level_ordering(self) -> None:
        """Level E is lowest (order 1), A is highest (order 5)."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "E"
        assert by_order[-1].code == "A"

    def test_hv17_sf_additional_months_pre_2024(self) -> None:
        """Additional months before 01/01/2024 is 13."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        assert ccnl.parameters.additional_months.value_at(date(2023, 6, 1)) == Decimal(
            13
        )

    def test_hv17_sf_additional_months_post_2024(self) -> None:
        """Additional months from 01/01/2024 onwards is 14."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        assert ccnl.parameters.additional_months.value_at(date(2024, 1, 1)) == Decimal(
            14
        )

    def test_hv17_sf_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 4, 1)) == Decimal(173)

    def test_hv17_sf_no_fixed_allowances(self) -> None:
        """All SF levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_hv17_sf_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_hv17_sf_seniority_cadence(self) -> None:
        """Seniority: 36-month cadence, max 10 scatti (raised by July 2026 rinnovo)."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10

    def test_hv17_sf_level_a_salary_mid_tranche(self) -> None:
        """Level A base salary at 01/10/2024 is 1886.32 EUR."""
        ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "A")
        assert lv.base_salary.value_at(date(2024, 10, 1)) == Decimal("1886.32")


class TestLoadSistemazioniIdraulicoForestaliImpiegati:
    """Unit tests for CCNL Sistemazioni Idraulico-Forestali Impiegati (A181)."""

    def test_a181_impiegati_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-impiegati.json")
        assert ccnl.meta.ccnl_id == "sistemazioni-idraulico-forestali-impiegati"
        assert ccnl.meta.cnel_code == "A181"

    def test_a181_impiegati_has_7_levels(self) -> None:
        """Contract has exactly 7 impiegati levels: I1-I6 plus I6Q."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-impiegati.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"I1", "I2", "I3", "I4", "I5", "I6", "I6Q"}

    def test_a181_impiegati_level_i4_salary_tranche1(self) -> None:
        """Level I4 base salary at 01/01/2026 is 1617.94 EUR."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-impiegati.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "I4")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("1617.94")

    def test_a181_impiegati_level_i4_salary_tranche2(self) -> None:
        """Level I4 base salary at 01/01/2027 is 1657.43 EUR."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-impiegati.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "I4")
        assert lv.base_salary.value_at(date(2027, 6, 1)) == Decimal("1657.43")

    def test_a181_impiegati_level_ordering(self) -> None:
        """I1 is lowest (order 1), I6Q is highest (order 7)."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-impiegati.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "I1"
        assert by_order[-1].code == "I6Q"

    def test_a181_impiegati_additional_months(self) -> None:
        """Additional months is 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-impiegati.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_a181_impiegati_hourly_divisor(self) -> None:
        """Hourly divisor is 169 (Art. 52 CCNL)."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-impiegati.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(169)

    def test_a181_impiegati_i6q_has_ind_funzione(self) -> None:
        """I6Q (quadro) has IND_FUNZIONE fixed allowance of 120 EUR."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-impiegati.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "I6Q")
        codes = [a.code for a in lv.fixed_allowances]
        assert "IND_FUNZIONE" in codes
        fa = next(a for a in lv.fixed_allowances if a.code == "IND_FUNZIONE")
        assert fa.monthly.value_at(date(2026, 1, 1)) == Decimal("120.00")

    def test_a181_impiegati_tax_sector(self) -> None:
        """Tax sector is agricoltura."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-impiegati.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_a181_impiegati_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence (biennale), 12 scatti max."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-impiegati.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 12


class TestLoadSistemazioniIdraulicoForestaliOperai:
    """Unit tests for CCNL Sistemazioni Idraulico-Forestali Operai OTI (A181)."""

    def test_a181_operai_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-operai.json")
        assert ccnl.meta.ccnl_id == "sistemazioni-idraulico-forestali-operai"
        assert ccnl.meta.cnel_code == "A181"

    def test_a181_operai_has_5_levels(self) -> None:
        """Contract has exactly 5 operai levels: O1-O5."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-operai.json")
        assert len(ccnl.levels) == 5
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"O1", "O2", "O3", "O4", "O5"}

    def test_a181_operai_level_o3_salary_tranche1(self) -> None:
        """Level O3 base salary at 01/01/2026 is 1471.55 EUR."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-operai.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "O3")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("1471.55")

    def test_a181_operai_level_o3_salary_tranche2(self) -> None:
        """Level O3 base salary at 01/01/2027 is 1507.52 EUR."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-operai.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "O3")
        assert lv.base_salary.value_at(date(2027, 6, 1)) == Decimal("1507.52")

    def test_a181_operai_level_ordering(self) -> None:
        """O1 is lowest (order 1), O5 is highest (order 5)."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-operai.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "O1"
        assert by_order[-1].code == "O5"

    def test_a181_operai_additional_months(self) -> None:
        """Additional months is 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-operai.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_a181_operai_hourly_divisor(self) -> None:
        """Hourly divisor is 169 (Art. 52 CCNL)."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-operai.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(169)

    def test_a181_operai_no_fixed_allowances(self) -> None:
        """All operai levels have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-operai.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_a181_operai_tax_sector(self) -> None:
        """Tax sector is agricoltura."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-operai.json")
        assert ccnl.meta.tax_sector == TaxSector.AGRICOLTURA

    def test_a181_operai_seniority_no_scatti(self) -> None:
        """Operai seniority: 0 scatti (no CCNL-level increments; governed by CIRL)."""
        ccnl = load_ccnl("sistemazioni-idraulico-forestali-operai.json")
        si = ccnl.parameters.seniority_increments
        assert si.maximum_count == 0


class TestLoadImpiantiSportiviSport:
    """Unit tests for CCNL Impianti e Attività Sportive (H077)."""

    def test_impianti_sportivi_sport_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("impianti-sportivi-sport.json")
        assert ccnl.meta.ccnl_id == "impianti-sportivi-sport"
        assert ccnl.meta.cnel_code == "H077"

    def test_impianti_sportivi_sport_has_7_levels(self) -> None:
        """Contract has exactly 7 levels: VI, V, IV, III, II, I, Q."""
        ccnl = load_ccnl("impianti-sportivi-sport.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"VI", "V", "IV", "III", "II", "I", "Q"}

    def test_impianti_sportivi_sport_level_vi_salary_tranche1(self) -> None:
        """Level VI base salary at 01/01/2024 is 1247.94 EUR."""
        ccnl = load_ccnl("impianti-sportivi-sport.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "VI")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1247.94")

    def test_impianti_sportivi_sport_level_vi_salary_tranche4(self) -> None:
        """Level VI base salary at 01/07/2026 is 1336.82 EUR."""
        ccnl = load_ccnl("impianti-sportivi-sport.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "VI")
        assert lv.base_salary.value_at(date(2026, 7, 1)) == Decimal("1336.82")

    def test_impianti_sportivi_sport_level_ordering(self) -> None:
        """VI is lowest (order 1), Q is highest (order 7)."""
        ccnl = load_ccnl("impianti-sportivi-sport.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "VI"
        assert by_order[-1].code == "Q"

    def test_impianti_sportivi_sport_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only — Art. 125 CCNL)."""
        ccnl = load_ccnl("impianti-sportivi-sport.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 7, 1)) == Decimal(
            13
        )

    def test_impianti_sportivi_sport_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week — Art. 120 CCNL)."""
        ccnl = load_ccnl("impianti-sportivi-sport.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 7, 1)) == Decimal(173)

    def test_impianti_sportivi_sport_q_has_ind_funzione(self) -> None:
        """Q level has IND_FUNZIONE of 60.00 EUR/month (13 months); others empty."""
        ccnl = load_ccnl("impianti-sportivi-sport.json")
        q = next(lv for lv in ccnl.levels if lv.code == "Q")
        assert len(q.fixed_allowances) == 1
        fa = q.fixed_allowances[0]
        assert fa.code == "IND_FUNZIONE"
        assert fa.monthly.value_at(date(2026, 7, 1)) == Decimal("60.00")
        assert fa.months_per_year == 13
        for lv in ccnl.levels:
            if lv.code != "Q":
                assert lv.fixed_allowances == ()

    def test_impianti_sportivi_sport_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("impianti-sportivi-sport.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_impianti_sportivi_sport_seniority_no_new_scatti(self) -> None:
        """Seniority: maximum_count == 0 (no new scatti in 2024 CCNL)."""
        ccnl = load_ccnl("impianti-sportivi-sport.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 0


class TestLoadFormazioneProfessionale:
    """Unit tests for CCNL Formazione Professionale (T261)."""

    def test_formazione_professionale_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("formazione-professionale.json")
        assert ccnl.meta.ccnl_id == "formazione-professionale"
        assert ccnl.meta.cnel_code == "T261"

    def test_formazione_professionale_has_9_levels(self) -> None:
        """Contract has exactly 9 levels: I through IX."""
        ccnl = load_ccnl("formazione-professionale.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"}

    def test_formazione_professionale_level_v_salary_tranche1(self) -> None:
        """Level V base salary at 01/01/2024 (carry-over) is 1957.63 EUR."""
        ccnl = load_ccnl("formazione-professionale.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "V")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1957.63")

    def test_formazione_professionale_level_v_salary_tranche2(self) -> None:
        """Level V base salary at 01/06/2024 (first increase) is 2017.63 EUR."""
        ccnl = load_ccnl("formazione-professionale.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "V")
        assert lv.base_salary.value_at(date(2024, 6, 1)) == Decimal("2017.63")

    def test_formazione_professionale_level_ordering(self) -> None:
        """I is lowest (order 1), IX is highest (order 9)."""
        ccnl = load_ccnl("formazione-professionale.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "I"
        assert by_order[-1].code == "IX"

    def test_formazione_professionale_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only — Art. 27 CCNL)."""
        ccnl = load_ccnl("formazione-professionale.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_formazione_professionale_hourly_divisor(self) -> None:
        """Hourly divisor is 156 (36h/week — Art. 29 para 6 CCNL)."""
        ccnl = load_ccnl("formazione-professionale.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_formazione_professionale_no_fixed_allowances(self) -> None:
        """All levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("formazione-professionale.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_formazione_professionale_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("formazione-professionale.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_formazione_professionale_seniority_cadence(self) -> None:
        """Seniority: quadrennial cadence (48 months), 5 increments max."""
        ccnl = load_ccnl("formazione-professionale.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 48
        assert si.maximum_count == 5


class TestLoadConciaUnic:
    """Unit tests for CCNL Industria Conciaria (UNIC) — B101."""

    def test_concia_unic_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("concia-unic.json")
        assert ccnl.meta.ccnl_id == "concia-unic"
        assert ccnl.meta.cnel_code == "B101"

    def test_concia_unic_has_11_levels(self) -> None:
        """Contract has exactly 11 levels: A, B1, B2, C1, C2, D1, D2, E1, E2, E3, F1."""
        ccnl = load_ccnl("concia-unic.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "A",
            "B1",
            "B2",
            "C1",
            "C2",
            "D1",
            "D2",
            "E1",
            "E2",
            "E3",
            "F1",
        }

    def test_concia_unic_level_c1_salary_tranche1(self) -> None:
        """Level C1 minimo tabellare at 01/03/2024 is 2125.21 EUR (Allegato n. 1)."""
        ccnl = load_ccnl("concia-unic.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        assert lv.base_salary.value_at(date(2024, 3, 1)) == Decimal("2125.21")

    def test_concia_unic_level_c1_salary_tranche3(self) -> None:
        """Level C1 minimo tabellare at 01/01/2026 is 2234.82 EUR (Allegato n. 1)."""
        ccnl = load_ccnl("concia-unic.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C1")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("2234.82")

    def test_concia_unic_level_ordering(self) -> None:
        """F1 is lowest (order 1), A is highest (order 11)."""
        ccnl = load_ccnl("concia-unic.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "F1"
        assert by_order[-1].code == "A"

    def test_concia_unic_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only — CCNL art. 50)."""
        ccnl = load_ccnl("concia-unic.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_concia_unic_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week — Allegato n. 1)."""
        ccnl = load_ccnl("concia-unic.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_concia_unic_level_a_ind_funzione(self) -> None:
        """Level A has IND_FUNZIONE allowance of 25.82 EUR; B1 has EDR + IPO."""
        ccnl = load_ccnl("concia-unic.json")
        lv_a = next(lv for lv in ccnl.levels if lv.code == "A")
        codes_a = {fa.code for fa in lv_a.fixed_allowances}
        assert "IND_FUNZIONE" in codes_a
        ind = next(fa for fa in lv_a.fixed_allowances if fa.code == "IND_FUNZIONE")
        assert ind.monthly.value_at(date(2026, 1, 1)) == Decimal("25.82")
        lv_b1 = next(lv for lv in ccnl.levels if lv.code == "B1")
        codes_b1 = {fa.code for fa in lv_b1.fixed_allowances}
        assert codes_b1 == {"EDR", "IPO"}

    def test_concia_unic_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("concia-unic.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_concia_unic_seniority_cadence(self) -> None:
        """Seniority: biennial cadence (24 months), 5 increments maximum."""
        ccnl = load_ccnl("concia-unic.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_concia_unic_gross_totals_2026(self) -> None:
        """Level totals at 01/01/2026: C1=2356.47, B1=2726.38, A=2973.75."""
        ccnl = load_ccnl("concia-unic.json")
        d = date(2026, 1, 1)
        expected = {"C1": "2356.47", "B1": "2726.38", "A": "2973.75"}
        for code, want in expected.items():
            lv = next(x for x in ccnl.levels if x.code == code)
            total = lv.base_salary.value_at(d) + sum(
                (fa.monthly.value_at(d) for fa in lv.fixed_allowances),
                Decimal(0),
            )
            assert total == Decimal(want), f"{code}: {total} != {want}"

    def test_concia_unic_ipo_levels(self) -> None:
        """IPO on exactly B1/C1/D1/E1/E2; EDR on every level."""
        ccnl = load_ccnl("concia-unic.json")
        with_ipo = {
            lv.code
            for lv in ccnl.levels
            if any(fa.code == "IPO" for fa in lv.fixed_allowances)
        }
        assert with_ipo == {"B1", "C1", "D1", "E1", "E2"}
        for lv in ccnl.levels:
            assert any(fa.code == "EDR" for fa in lv.fixed_allowances), (
                f"{lv.code} missing EDR"
            )


class TestLoadPuliziaArtigianatoConfartigianato:
    """Unit tests for CCNL Pulizia Artigianato (Confartigianato) — K521."""

    def test_pulizia_artigianato_confartigianato_loads(self) -> None:
        """Contract loads with correct id and CNEL code K521."""
        ccnl = load_ccnl("pulizia-artigianato-confartigianato.json")
        assert ccnl.meta.ccnl_id == "pulizia-artigianato-confartigianato"
        assert ccnl.meta.cnel_code == "K521"

    def test_pulizia_artigianato_confartigianato_has_7_levels(self) -> None:
        """Contract has exactly 7 levels: 1, 2, 3S, 3, 4, 5, 6."""
        ccnl = load_ccnl("pulizia-artigianato-confartigianato.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3S", "3", "4", "5", "6"}

    def test_pulizia_artigianato_confartigianato_level1_salary_tranche1(
        self,
    ) -> None:
        """Level 1 tabellare at 2022-11-01 is 1534.64 EUR (PDF 2022)."""
        ccnl = load_ccnl("pulizia-artigianato-confartigianato.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1")
        assert lv.base_salary.value_at(date(2022, 11, 1)) == Decimal("1534.64")

    def test_pulizia_artigianato_confartigianato_level1_salary_tranche2(
        self,
    ) -> None:
        """Level 1 tabellare at 2026-07-01 is 1693.84 EUR (kitech verified)."""
        ccnl = load_ccnl("pulizia-artigianato-confartigianato.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1")
        assert lv.base_salary.value_at(date(2026, 7, 1)) == Decimal("1693.84")

    def test_pulizia_artigianato_confartigianato_level_ordering(self) -> None:
        """Level 6 is lowest (order 1), level 1 is highest (order 7)."""
        ccnl = load_ccnl("pulizia-artigianato-confartigianato.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "1"

    def test_pulizia_artigianato_confartigianato_additional_months(
        self,
    ) -> None:
        """Additional months is 13 (tredicesima only, PDF 2022)."""
        ccnl = load_ccnl("pulizia-artigianato-confartigianato.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 7, 1)) == Decimal(
            13
        )

    def test_pulizia_artigianato_confartigianato_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (PARAMETRI E COEFFICIENTI, PDF 2022)."""
        ccnl = load_ccnl("pulizia-artigianato-confartigianato.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 7, 1)) == Decimal(173)

    def test_pulizia_artigianato_confartigianato_level1_ind_fun(self) -> None:
        """Level 1 has IND_FUN allowance of 25.82 EUR; others have none."""
        ccnl = load_ccnl("pulizia-artigianato-confartigianato.json")
        lv1 = next(lv for lv in ccnl.levels if lv.code == "1")
        codes = {fa.code for fa in lv1.fixed_allowances}
        assert "IND_FUN" in codes
        ind = next(fa for fa in lv1.fixed_allowances if fa.code == "IND_FUN")
        assert ind.monthly.value_at(date(2026, 7, 1)) == Decimal("25.82")
        for lv in ccnl.levels:
            if lv.code != "1":
                assert lv.fixed_allowances == ()

    def test_pulizia_artigianato_confartigianato_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("pulizia-artigianato-confartigianato.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_pulizia_artigianato_confartigianato_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennial cadence (24 months), 5 increments maximum."""
        ccnl = load_ccnl("pulizia-artigianato-confartigianato.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadAziendeTermaliFederterme:
    """Unit tests for CCNL Aziende Termali Federterme (K461)."""

    def test_aziende_termali_federterme_loads(self) -> None:
        """Contract loads with correct id and CNEL code K461."""
        ccnl = load_ccnl("aziende-termali-federterme.json")
        assert ccnl.meta.ccnl_id == "aziende-termali-federterme"
        assert ccnl.meta.cnel_code == "K461"

    def test_aziende_termali_federterme_has_9_levels(self) -> None:
        """Contract has exactly 9 levels: 6, 5, 4, 4S, 3, 2, 1, 1SB, 1SA."""
        ccnl = load_ccnl("aziende-termali-federterme.json")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"6", "5", "4", "4S", "3", "2", "1", "1SB", "1SA"}

    def test_aziende_termali_federterme_level3_salary_tranche1(self) -> None:
        """Level 3 paga base at 2024-10-01 is 1078.64 EUR (PDF Art. 82)."""
        ccnl = load_ccnl("aziende-termali-federterme.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 10, 1)) == Decimal("1078.64")

    def test_aziende_termali_federterme_level3_salary_tranche2(self) -> None:
        """Level 3 paga base at 2026-06-01 is 1193.48 EUR (PDF Art. 82)."""
        ccnl = load_ccnl("aziende-termali-federterme.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("1193.48")

    def test_aziende_termali_federterme_level_ordering(self) -> None:
        """Level 6 is lowest (order 1), level 1SA is highest (order 9)."""
        ccnl = load_ccnl("aziende-termali-federterme.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "6"
        assert by_order[-1].code == "1SA"

    def test_aziende_termali_federterme_additional_months(self) -> None:
        """Additional months is 14 (tredicesima + quattordicesima, Art. 37)."""
        ccnl = load_ccnl("aziende-termali-federterme.json")
        assert ccnl.parameters.additional_months.value_at(date(2025, 1, 1)) == Decimal(
            14
        )

    def test_aziende_termali_federterme_hourly_divisor(self) -> None:
        """Hourly divisor is 173.33 (PDF Art. 35 + Art. 37)."""
        ccnl = load_ccnl("aziende-termali-federterme.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2025, 1, 1)) == Decimal(
            "173.33"
        )

    def test_aziende_termali_federterme_fixed_allowances_split(self) -> None:
        """Split model: every level has CONTINGENZA and EDR allowances."""
        ccnl = load_ccnl("aziende-termali-federterme.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONTINGENZA" in codes, f"{lv.code} missing CONTINGENZA"
            assert "EDR" in codes, f"{lv.code} missing EDR"

    def test_aziende_termali_federterme_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("aziende-termali-federterme.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_aziende_termali_federterme_seniority_cadence(self) -> None:
        """Seniority: biennial cadence (24 months), 5 increments maximum."""
        ccnl = load_ccnl("aziende-termali-federterme.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadAutoscuoleUnasca:
    """Unit tests for CCNL Autoscuole UNASCA/CONFARCA (IC91)."""

    def test_autoscuole_unasca_loads(self) -> None:
        """Contract loads with correct id and CNEL code IC91."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        assert ccnl.meta.ccnl_id == "autoscuole-unasca"
        assert ccnl.meta.cnel_code == "IC91"

    def test_autoscuole_unasca_has_6_levels(self) -> None:
        """Contract has exactly 6 levels: Q, 5, 4, 3, 2, 1."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        assert len(ccnl.levels) == 6
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "5", "4", "3", "2", "1"}

    def test_autoscuole_unasca_level3_salary_tranche1(self) -> None:
        """Level 3 paga base before 01/09/2021 is 931.48 EUR (verbale rettifica)."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2021, 6, 1)) == Decimal("931.48")

    def test_autoscuole_unasca_level5_salary_tranche3(self) -> None:
        """Level 5 paga base a regime (01/02/2022) is 1227.87 EUR."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "5")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1227.87")

    def test_autoscuole_unasca_level_ordering(self) -> None:
        """Level 1 is lowest (order 1), level Q is highest (order 6)."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_autoscuole_unasca_additional_months(self) -> None:
        """Additional months is 14 (Art. 18 tredicesima + Art. 19 quattordicesima)."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_autoscuole_unasca_hourly_divisor(self) -> None:
        """Hourly divisor is 170 (Art. 13 comma 3 CCNL)."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(170)

    def test_autoscuole_unasca_fixed_allowances_split(self) -> None:
        """Split model: every level has CONTINGENZA+EDR; Q adds IND_FUNZIONE_Q."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        for lv in ccnl.levels:
            codes = {fa.code for fa in lv.fixed_allowances}
            assert "CONTINGENZA" in codes, f"{lv.code} missing CONTINGENZA"
            assert "EDR" in codes, f"{lv.code} missing EDR"
        q = next(lv for lv in ccnl.levels if lv.code == "Q")
        assert any(fa.code == "IND_FUNZIONE_Q" for fa in q.fixed_allowances)

    def test_autoscuole_unasca_tax_sector(self) -> None:
        """Tax sector is terziario (IC35 autorimesse precedent)."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_autoscuole_unasca_seniority_cadence(self) -> None:
        """Seniority: biennial cadence (24 months), 5 increments maximum."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_autoscuole_unasca_apprenticeship_under_classification(self) -> None:
        """Apprenticeship is under_classification; Q is excluded (5 tracks)."""
        ccnl = load_ccnl("autoscuole-unasca.json")
        tracks = ccnl.apprenticeship
        assert tracks is not None
        assert len(tracks) == 5
        assert all(isinstance(t, ApprenticeshipUnderClassification) for t in tracks)


class TestLoadAgentiImmobilariFiaip:
    """Tests for CCNL Agenti Immobiliari Professionali FIAIP (H0B1)."""

    def test_agenti_immobiliari_fiaip_loads(self) -> None:
        """Loads agenti-immobiliari-fiaip and verifies id and CNEL code H0B1."""
        ccnl = load_ccnl("agenti-immobiliari-fiaip.json")
        assert ccnl.meta.ccnl_id == "agenti-immobiliari-fiaip"
        assert ccnl.meta.cnel_code == "H0B1"

    def test_agenti_immobiliari_fiaip_has_7_levels(self) -> None:
        """Has exactly 7 levels: Q, I, II, III, IV, V, VI."""
        ccnl = load_ccnl("agenti-immobiliari-fiaip.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "I", "II", "III", "IV", "V", "VI"}

    def test_agenti_immobiliari_fiaip_level_iii_salary_tranche1(self) -> None:
        """Level III conglobated salary at 01/05/2025 is 1925.95 EUR (Art. 163)."""
        ccnl = load_ccnl("agenti-immobiliari-fiaip.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "III")
        assert lv.base_salary.value_at(date(2025, 5, 1)) == Decimal("1925.95")

    def test_agenti_immobiliari_fiaip_level_iii_salary_tranche2(self) -> None:
        """Level III conglobated salary at 01/01/2026 is 1970.16 EUR (Art. 163)."""
        ccnl = load_ccnl("agenti-immobiliari-fiaip.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "III")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1970.16")

    def test_agenti_immobiliari_fiaip_level_ordering(self) -> None:
        """Level VI is lowest (order 1), level Q is highest (order 7)."""
        ccnl = load_ccnl("agenti-immobiliari-fiaip.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "VI"
        assert by_order[-1].code == "Q"

    def test_agenti_immobiliari_fiaip_additional_months(self) -> None:
        """Additional months is 14 (Art. 168 tredicesima + Art. 169 quattordicesima)."""
        ccnl = load_ccnl("agenti-immobiliari-fiaip.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_agenti_immobiliari_fiaip_hourly_divisor(self) -> None:
        """Hourly divisor is 168 (Art. 161 explicit text)."""
        ccnl = load_ccnl("agenti-immobiliari-fiaip.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(168)

    def test_agenti_immobiliari_fiaip_no_fixed_allowances(self) -> None:
        """Conglobated model: every level has fixed_allowances == [] (Art. 158)."""
        ccnl = load_ccnl("agenti-immobiliari-fiaip.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == (), f"{lv.code} has unexpected allowances"

    def test_agenti_immobiliari_fiaip_tax_sector(self) -> None:
        """Tax sector is terziario (FILCAMS/FISASCAT/UILTUCS signatories)."""
        ccnl = load_ccnl("agenti-immobiliari-fiaip.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_agenti_immobiliari_fiaip_seniority_cadence(self) -> None:
        """Seniority: triennial cadence (36 months), 10 increments (Art. 157)."""
        ccnl = load_ccnl("agenti-immobiliari-fiaip.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


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
        """Fonchim employer fund at 2.0% from 2026-01-01 (was 1.5% pre-renewal)."""
        ccnl = load_ccnl("vetro-meccanizzato-assovetro.json")
        funds = {f.code: f for f in ccnl.parameters.employer_funds}
        assert "FONCHIM" in funds
        assert funds["FONCHIM"].rate.value_at(date(2026, 1, 1)) == Decimal("0.0200")
        assert funds["FONCHIM"].rate.value_at(date(2025, 1, 1)) == Decimal("0.0150")


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

    def test_tessile_pmi_uniontessile_fondapi_fund(self) -> None:
        """FONDAPI rate 1.90% until Mar 2025, 2.00% from Mar 2025 (adapt.it)."""
        ccnl = load_ccnl("tessile-pmi-uniontessile.json")
        funds = {f.code: f for f in ccnl.parameters.employer_funds}
        assert "FONDAPI" in funds
        assert funds["FONDAPI"].rate.value_at(date(2024, 4, 1)) == Decimal("0.0190")
        assert funds["FONDAPI"].rate.value_at(date(2025, 3, 1)) == Decimal("0.0200")


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


class TestLoadEdiliziaPmiConfapiAniem:
    """Unit tests for edilizia-pmi-confapi-aniem.json (CNEL F018)."""

    def test_edilizia_pmi_confapi_aniem_loads(self) -> None:
        """Contract loads with correct id and CNEL code F018."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        assert ccnl.meta.ccnl_id == "edilizia-pmi-confapi-aniem"
        assert ccnl.meta.cnel_code == "F018"

    def test_edilizia_pmi_confapi_aniem_has_7_levels(self) -> None:
        """Seven levels: 1, 2, 3, 4, 5, 6, 7."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7"}

    def test_edilizia_pmi_confapi_aniem_level4_salary_2025(self) -> None:
        """Level 4 base salary at 01/04/2025 tranche: 1523.17 EUR."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2025, 4, 1)) == Decimal("1523.17")

    def test_edilizia_pmi_confapi_aniem_level4_salary_2027(self) -> None:
        """Level 4 base salary at 01/03/2027 tranche: 1628.17 EUR."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2027, 3, 1)) == Decimal("1628.17")

    def test_edilizia_pmi_confapi_aniem_level_ordering(self) -> None:
        """Level 1 has lowest order; level 7 has highest order."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "7"

    def test_edilizia_pmi_confapi_aniem_additional_months(self) -> None:
        """Tredicesima only: 13 additional months."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        assert ccnl.parameters.additional_months.value_at(date(2025, 4, 1)) == Decimal(
            13
        )

    def test_edilizia_pmi_confapi_aniem_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (Art. 25 CCNL, 40h/week)."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2025, 4, 1)) == Decimal(173)

    def test_edilizia_pmi_confapi_aniem_split_model_fixed_allowances(self) -> None:
        """All levels carry CONTINGENZA + EDR (split salary model)."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
            assert "EDR" in codes

    def test_edilizia_pmi_confapi_aniem_tax_sector(self) -> None:
        """Tax sector is edilizia."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        assert ccnl.meta.tax_sector == TaxSector.EDILIZIA

    def test_edilizia_pmi_confapi_aniem_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), max 5 increments (Art. 49)."""
        ccnl = load_ccnl("edilizia-pmi-confapi-aniem.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadEdiliziaCooperativeAncpl:
    """Unit tests for CCNL Edilizia Cooperative ANCPL (F016)."""

    def test_edilizia_cooperative_ancpl_loads(self) -> None:
        """Contract loads with correct id and CNEL code F016."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        assert ccnl.meta.ccnl_id == "edilizia-cooperative-ancpl"
        assert ccnl.meta.cnel_code == "F016"

    def test_edilizia_cooperative_ancpl_has_10_levels(self) -> None:
        """Contract has 10 levels including Q variants."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7", "7Q", "8", "8Q"}

    def test_edilizia_cooperative_ancpl_level4_salary_t1(self) -> None:
        """Level 4 paga base is 1485.49 EUR at T1 tranche (01/02/2025)."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        lv4 = next(lv for lv in ccnl.levels if lv.code == "4")
        period = next(
            p
            for p in lv4.base_salary.periods
            if p.valid_from.isoformat() == "2025-02-01"
        )
        assert period.value == Decimal("1485.49")

    def test_edilizia_cooperative_ancpl_level4_salary_t2(self) -> None:
        """Level 4 paga base is 1553.74 EUR at T2 tranche (01/03/2026)."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        lv4 = next(lv for lv in ccnl.levels if lv.code == "4")
        period = next(
            p
            for p in lv4.base_salary.periods
            if p.valid_from.isoformat() == "2026-03-01"
        )
        assert period.value == Decimal("1553.74")

    def test_edilizia_cooperative_ancpl_level4_salary_t3(self) -> None:
        """Level 4 paga base is 1621.99 EUR at T3 tranche (01/03/2027)."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        lv4 = next(lv for lv in ccnl.levels if lv.code == "4")
        period = next(
            p
            for p in lv4.base_salary.periods
            if p.valid_from.isoformat() == "2027-03-01"
        )
        assert period.value == Decimal("1621.99")

    def test_edilizia_cooperative_ancpl_level_ordering(self) -> None:
        """Level 1 is lowest, 8Q is highest."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        sorted_lvs = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_lvs[0].code == "1"
        assert sorted_lvs[-1].code == "8Q"

    def test_edilizia_cooperative_ancpl_additional_months(self) -> None:
        """Additional months is 13."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(13)

    def test_edilizia_cooperative_ancpl_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_edilizia_cooperative_ancpl_split_model_fixed_allowances(self) -> None:
        """All levels carry CONTINGENZA + EDR; Q levels also carry INDENNITA_FUNZIONE."""  # noqa: E501
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "CONTINGENZA" in codes
            assert "EDR" in codes
            if lv.code in {"7Q", "8Q"}:
                assert "INDENNITA_FUNZIONE" in codes
            else:
                assert "INDENNITA_FUNZIONE" not in codes

    def test_edilizia_cooperative_ancpl_tax_sector(self) -> None:
        """Tax sector is edilizia."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        assert ccnl.meta.tax_sector == TaxSector.EDILIZIA

    def test_edilizia_cooperative_ancpl_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), max 5 increments."""
        ccnl = load_ccnl("edilizia-cooperative-ancpl.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadMetalmeccanicoConfimiPmi:
    """Tests for CCNL Metalmeccanici Piccola Industria CONFIMI (C01A)."""

    def test_metalmeccanico_confimi_pmi_loads(self) -> None:
        """File loads; ccnl_id and CNEL code are correct."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        assert ccnl.meta.ccnl_id == "metalmeccanico-confimi-pmi"
        assert ccnl.meta.cnel_code == "C01A"

    def test_metalmeccanico_confimi_pmi_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: 2-7, 8, 8Q, 9, 9Q."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 10
        assert codes == {"2", "3", "4", "5", "6", "7", "8", "8Q", "9", "9Q"}

    def test_metalmeccanico_confimi_pmi_level5_salary_t1(self) -> None:
        """Level 5 base salary is 2251.35 EUR at T1 tranche (01/06/2026)."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        lv5 = next(lv for lv in ccnl.levels if lv.code == "5")
        period = next(
            p
            for p in lv5.base_salary.periods
            if p.valid_from.isoformat() == "2026-06-01"
        )
        assert period.value == Decimal("2251.35")

    def test_metalmeccanico_confimi_pmi_level5_salary_t2(self) -> None:
        """Level 5 base salary is 2306.35 EUR at T2 tranche (01/06/2027)."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        lv5 = next(lv for lv in ccnl.levels if lv.code == "5")
        period = next(
            p
            for p in lv5.base_salary.periods
            if p.valid_from.isoformat() == "2027-06-01"
        )
        assert period.value == Decimal("2306.35")

    def test_metalmeccanico_confimi_pmi_level_ordering(self) -> None:
        """Level 2 is lowest-order; 9Q is highest-order."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        sorted_lvs = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert sorted_lvs[0].code == "2"
        assert sorted_lvs[-1].code == "9Q"

    def test_metalmeccanico_confimi_pmi_additional_months(self) -> None:
        """Additional months is 13 (tredicesima only)."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 6, 1))
        assert val == Decimal(13)

    def test_metalmeccanico_confimi_pmi_hourly_divisor(self) -> None:
        """Hourly divisor is 173."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1)) == Decimal(173)

    def test_metalmeccanico_confimi_pmi_conglobated_levels_2_to_7(self) -> None:
        """Levels 2-7 have no fixed allowances (conglobated model)."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        for code in ("2", "3", "4", "5", "6", "7"):
            lv = next(lv for lv in ccnl.levels if lv.code == code)
            assert lv.fixed_allowances == ()

    def test_metalmeccanico_confimi_pmi_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_metalmeccanico_confimi_pmi_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), max 5 increments."""
        ccnl = load_ccnl("metalmeccanico-confimi-pmi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadNoleggioAutobusConducenteAnav:
    """Tests for CCNL Noleggio Autobus con Conducente ANAV (IC36)."""

    def test_noleggio_autobus_conducente_anav_loads(self) -> None:
        """CCNL id and CNEL code match."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        assert ccnl.meta.ccnl_id == "noleggio-autobus-conducente-anav"
        assert ccnl.meta.cnel_code == "IC36"

    def test_noleggio_autobus_conducente_anav_has_11_levels(self) -> None:
        """Eleven levels: C4-C1, B3-B1, A2-A1, Q2-Q1."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "C4",
            "C3",
            "C2",
            "C1",
            "B3",
            "B2",
            "B1",
            "A2",
            "A1",
            "Q2",
            "Q1",
        }

    def test_noleggio_autobus_conducente_anav_level_c2_salary_t1(self) -> None:
        """C2 base_salary at 2025-07-01 tranche = 1126.97."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C2")
        assert lv.base_salary.value_at(date(2025, 7, 1)) == Decimal("1126.97")

    def test_noleggio_autobus_conducente_anav_level_c2_salary_t2(self) -> None:
        """C2 base_salary at 2026-08-01 tranche = 1226.97."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C2")
        assert lv.base_salary.value_at(date(2026, 8, 1)) == Decimal("1226.97")

    def test_noleggio_autobus_conducente_anav_level_ordering(self) -> None:
        """Q1 is highest order; C4 is lowest order."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "C4"
        assert ordered[-1].code == "Q1"

    def test_noleggio_autobus_conducente_anav_additional_months(self) -> None:
        """Fourteen mensilita (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            14
        )

    def test_noleggio_autobus_conducente_anav_hourly_divisor(self) -> None:
        """Hourly divisor = 173."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == 173

    def test_noleggio_autobus_conducente_anav_split_model_c2(self) -> None:
        """C2 has CONTINGENZA, EDR, EDR_RINNOVO as fixed allowances."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C2")
        codes = {a.code for a in lv.fixed_allowances}
        assert codes == {"CONTINGENZA", "EDR", "EDR_RINNOVO"}

    def test_noleggio_autobus_conducente_anav_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_noleggio_autobus_conducente_anav_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), max 9 increments."""
        ccnl = load_ccnl("noleggio-autobus-conducente-anav.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 9


class TestLoadMaterialiCostruzioneLapideiConfapi:
    """Tests for CCNL Materiali da Costruzione PMI Lapidei CONFAPI ANIEM (F020)."""

    def test_materiali_costruzione_lapidei_confapi_loads(self) -> None:
        """CCNL id and CNEL code match."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        assert ccnl.meta.ccnl_id == "materiali-costruzione-lapidei-confapi"
        assert ccnl.meta.cnel_code == "F020"

    def test_materiali_costruzione_lapidei_confapi_has_8_levels(self) -> None:
        """Eight levels: 1 (highest) through 8 (lowest)."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7", "8"}

    def test_materiali_costruzione_lapidei_confapi_level1_salary_2022(self) -> None:
        """Level 1 base_salary at 2022-01-01 tranche = 2605.54."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1")
        assert lv.base_salary.value_at(date(2022, 1, 1)) == Decimal("2605.54")

    def test_materiali_costruzione_lapidei_confapi_level1_salary_2025(self) -> None:
        """Level 1 base_salary at 2025-01-01 tranche = 2795.46."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "1")
        assert lv.base_salary.value_at(date(2025, 1, 1)) == Decimal("2795.46")

    def test_materiali_costruzione_lapidei_confapi_level_ordering(self) -> None:
        """Level 1 is highest order; level 8 is lowest order."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "8"
        assert ordered[-1].code == "1"

    def test_materiali_costruzione_lapidei_confapi_additional_months(self) -> None:
        """Thirteen mensilita (tredicesima only)."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        assert ccnl.parameters.additional_months.value_at(date(2025, 1, 1)) == Decimal(
            13
        )

    def test_materiali_costruzione_lapidei_confapi_hourly_divisor(self) -> None:
        """Hourly divisor = 174 (Art. 24 Disciplina Lapidei)."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2025, 1, 1)) == 174

    def test_materiali_costruzione_lapidei_confapi_split_model_edr(self) -> None:
        """All levels have EDR as fixed allowance (split model)."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert "EDR" in codes

    def test_materiali_costruzione_lapidei_confapi_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_materiali_costruzione_lapidei_confapi_seniority_cadence(self) -> None:
        """Seniority: biennial (24 months), max 5 increments."""
        ccnl = load_ccnl("materiali-costruzione-lapidei-confapi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestOvertimeBandInvariants:
    """Parametric invariants over all 125 bundled CCNL JSON files.

    Every CCNL must satisfy the no-ambiguous-collision invariant: two or more
    bands for the same WorkKind without a threshold or conditional predicate
    cannot be applied deterministically.

    This test validates that the bundle validator in TimeSupplements is in sync
    with the actual data — i.e. no file triggers the validator at load time.
    """

    @pytest.mark.parametrize("entry", _JSON_FILES, ids=lambda e: e.name)
    def test_no_ambiguous_band_collisions(self, entry: object) -> None:
        """Loading every CCNL file must not raise DataIntegrityError or ValueError.

        The TimeSupplements.no_ambiguous_collisions validator rejects ambiguous
        band layouts.  Passing here proves all 125 files are collision-free.
        """
        ccnl = load_ccnl(getattr(entry, "name", str(entry)))
        wr = ccnl.work_rules
        if wr is None or wr.time_supplements is None:
            return
        # Validator already ran during load_ccnl; reaching here means it passed.
        assert wr.time_supplements is not None
