"""Bundled CCNL data files load with their expected values.

Covers Energia Petrolio Confindustria, Distribuzione Cooperativa Ancc,
Lavanderi Industriali Assosistema, Ced Assoced, Contoterzismo Caiagromec.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.identity.facade import TaxSector


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
