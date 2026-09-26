"""CCNL contract data tests (B): Energia through ServiziAmministrativi."""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.payroll.service.seniority import seniority_maximum


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
