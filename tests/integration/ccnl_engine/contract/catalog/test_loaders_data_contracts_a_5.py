"""Bundled CCNL data files load with their expected values.

Covers Funzioni Locali Aran, Sanita Aran, Dirigenza Sanitaria Medico
Veterinaria Aran, Dirigenza Sanitaria Area Sanita Aran, Dirigenza Funzioni
Locali Aran, Dirigenza Funzioni Centrali Aran.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.identity.facade import TaxSector


class TestLoadFunzioniLocaliAran:
    """Tests for CCNL Comparto Funzioni Locali 2022-2024 (ARAN)."""

    def test_funzioni_locali_aran_loads(self) -> None:
        """Contract loads with correct id and CNEL code S105."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        assert ccnl.meta.ccnl_id == "funzioni-locali-aran"
        assert ccnl.meta.cnel_code == "S105"

    def test_funzioni_locali_aran_has_4_levels(self) -> None:
        """Contract has exactly 4 areas (Operatori, Oper.Esp., Istruttori, Funz.EQ)."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        assert len(ccnl.levels) == 4
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "OPERATORI",
            "OPERATORI_ESPERTI",
            "ISTRUTTORI",
            "FUNZIONARI_EQ",
        }

    def test_funzioni_locali_aran_istruttori_salary_tranche1(self) -> None:
        """ISTRUTTORI first tranche (2022-11-16): 1782.74 EUR/month."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        lv = ccnl.level_by_code("ISTRUTTORI")
        assert lv.base_salary.value_at(date(2022, 11, 16)) == Decimal("1782.74")

    def test_funzioni_locali_aran_istruttori_salary_tranche2(self) -> None:
        """ISTRUTTORI second tranche (1/1/2024): 1915.55 EUR/month."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        lv = ccnl.level_by_code("ISTRUTTORI")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1915.55")

    def test_funzioni_locali_aran_level_ordering(self) -> None:
        """FUNZIONARI_EQ is highest-order; OPERATORI is lowest-order."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["FUNZIONARI_EQ"] == max(orders.values())
        assert orders["OPERATORI"] == min(orders.values())

    def test_funzioni_locali_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_funzioni_locali_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 156 (Art. 74 CCNL 16.11.2022, 36h/week)."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_funzioni_locali_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_funzioni_locali_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_funzioni_locali_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (differenziali non automatici, Art. 14)."""
        ccnl = load_ccnl("funzioni-locali-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadSanitaAran:
    """Tests for CCNL Comparto Sanità 2022-2024 (sanita-aran, CNEL S205)."""

    def test_sanita_aran_loads(self) -> None:
        """File loads successfully and has correct id and CNEL code."""
        ccnl = load_ccnl("sanita-aran.json")
        assert ccnl.meta.ccnl_id == "sanita-aran"
        assert ccnl.meta.cnel_code == "S205"

    def test_sanita_aran_has_5_levels(self) -> None:
        """Contract has exactly 5 areas."""
        ccnl = load_ccnl("sanita-aran.json")
        assert len(ccnl.levels) == 5
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "SUPPORTO",
            "OPERATORI",
            "ASSISTENTI",
            "PROFESSIONISTI",
            "ELEVATA_QUALIFICAZIONE",
        }

    def test_sanita_aran_professionisti_salary_tranche1(self) -> None:
        """PROFESSIONISTI first tranche (2022-11-02): 1941.58 EUR/month."""
        ccnl = load_ccnl("sanita-aran.json")
        lv = ccnl.level_by_code("PROFESSIONISTI")
        assert lv.base_salary.value_at(date(2022, 11, 2)) == Decimal("1941.58")

    def test_sanita_aran_professionisti_salary_tranche2(self) -> None:
        """PROFESSIONISTI second tranche (1/1/2024): 2076.58 EUR/month."""
        ccnl = load_ccnl("sanita-aran.json")
        lv = ccnl.level_by_code("PROFESSIONISTI")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("2076.58")

    def test_sanita_aran_level_ordering(self) -> None:
        """ELEVATA_QUALIFICAZIONE is highest-order; SUPPORTO is lowest-order."""
        ccnl = load_ccnl("sanita-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["ELEVATA_QUALIFICAZIONE"] == max(orders.values())
        assert orders["SUPPORTO"] == min(orders.values())

    def test_sanita_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only, Art. 57)."""
        ccnl = load_ccnl("sanita-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_sanita_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 156 (Art. 26 CCNL, 36h/week)."""
        ccnl = load_ccnl("sanita-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_sanita_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("sanita-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_sanita_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("sanita-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_sanita_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (DEP non automatici, Art. 60)."""
        ccnl = load_ccnl("sanita-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadDirigenzaSanitariaMedicoVeterinariaAran:
    """Tests for CCNL Area Sanità 2022-2024 — Dirigenti Medici e Vet (S225)."""

    def test_dirigenza_sanitaria_medico_veterinaria_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        assert ccnl.meta.ccnl_id == "dirigenza-sanitaria-medico-veterinaria-aran"
        assert ccnl.meta.cnel_code == "S225"

    def test_dirigenza_sanitaria_medico_veterinaria_aran_has_1_level(
        self,
    ) -> None:
        """Contract has exactly 1 level (DIRIGENTE)."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        assert len(ccnl.levels) == 1
        assert {lv.code for lv in ccnl.levels} == {"DIRIGENTE"}

    def test_dirigenza_sanitaria_medico_veterinaria_aran_salary_tranche1(
        self,
    ) -> None:
        """DIRIGENTE first tranche (2019-12-19): 3616.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2019, 12, 19)) == Decimal("3616.60")

    def test_dirigenza_sanitaria_medico_veterinaria_aran_salary_tranche2(
        self,
    ) -> None:
        """DIRIGENTE second tranche (1/1/2024): 3846.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("3846.60")

    def test_dirigenza_sanitaria_medico_veterinaria_aran_level_ordering(
        self,
    ) -> None:
        """DIRIGENTE is both highest-order and lowest-order (single level)."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["DIRIGENTE"] == max(orders.values())
        assert orders["DIRIGENTE"] == min(orders.values())

    def test_dirigenza_sanitaria_medico_veterinaria_aran_additional_months(
        self,
    ) -> None:
        """Additional months: 13 (Art. 11 — 'per 13 mensilità')."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_dirigenza_sanitaria_medico_veterinaria_aran_hourly_divisor(
        self,
    ) -> None:
        """Hourly divisor: 165 (38h/week approximation, SIMPLIFICATION)."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_dirigenza_sanitaria_medico_veterinaria_aran_specificita_allowance(
        self,
    ) -> None:
        """DIRIGENTE has one fixed allowance: SPECIFICITA_MEDICO_VETERINARIA."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert len(lv.fixed_allowances) == 1
        assert lv.fixed_allowances[0].code == "SPECIFICITA_MEDICO_VETERINARIA"
        assert lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "728.15"
        )

    def test_dirigenza_sanitaria_medico_veterinaria_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_dirigenza_sanitaria_medico_veterinaria_aran_seniority_cadence(
        self,
    ) -> None:
        """Seniority: maximum_count=0 (no automatic scatti per dirigenza)."""
        ccnl = load_ccnl("dirigenza-sanitaria-medico-veterinaria-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadDirigenzaSanitariaAreaSanitaAran:
    """Tests for CCNL Area Sanità 2022-2024 — Dirigenti Sanitari (S225)."""

    def test_dirigenza_sanitaria_area_sanita_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        assert ccnl.meta.ccnl_id == "dirigenza-sanitaria-area-sanita-aran"
        assert ccnl.meta.cnel_code == "S225"

    def test_dirigenza_sanitaria_area_sanita_aran_has_1_level(self) -> None:
        """Contract has exactly 1 level (DIRIGENTE)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        assert len(ccnl.levels) == 1
        assert {lv.code for lv in ccnl.levels} == {"DIRIGENTE"}

    def test_dirigenza_sanitaria_area_sanita_aran_salary_tranche1(self) -> None:
        """DIRIGENTE first tranche (2019-12-19): 3616.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2019, 12, 19)) == Decimal("3616.60")

    def test_dirigenza_sanitaria_area_sanita_aran_salary_tranche2(self) -> None:
        """DIRIGENTE second tranche (1/1/2024): 3846.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("3846.60")

    def test_dirigenza_sanitaria_area_sanita_aran_level_ordering(self) -> None:
        """DIRIGENTE is both highest-order and lowest-order (single level)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["DIRIGENTE"] == max(orders.values())
        assert orders["DIRIGENTE"] == min(orders.values())

    def test_dirigenza_sanitaria_area_sanita_aran_additional_months(
        self,
    ) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_dirigenza_sanitaria_area_sanita_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 165 (38h/week, SIMPLIFICATION)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_dirigenza_sanitaria_area_sanita_aran_specificita_allowance(
        self,
    ) -> None:
        """DIRIGENTE has one fixed allowance: SPECIFICITA_SANITARIA (124.19)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert len(lv.fixed_allowances) == 1
        assert lv.fixed_allowances[0].code == "SPECIFICITA_SANITARIA"
        assert lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "124.19"
        )

    def test_dirigenza_sanitaria_area_sanita_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_dirigenza_sanitaria_area_sanita_aran_seniority_cadence(
        self,
    ) -> None:
        """Seniority: maximum_count=0 (no automatic scatti per dirigenza)."""
        ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadDirigenzaFunzioniLocaliAran:
    """Tests for CCNL Area Dirigenza Funzioni Locali 2022-2024 (S125)."""

    def test_dirigenza_funzioni_locali_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        assert ccnl.meta.ccnl_id == "dirigenza-funzioni-locali-aran"
        assert ccnl.meta.cnel_code == "S125"

    def test_dirigenza_funzioni_locali_aran_has_1_level(self) -> None:
        """Contract has exactly 1 level (DIRIGENTE)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        assert len(ccnl.levels) == 1
        assert {lv.code for lv in ccnl.levels} == {"DIRIGENTE"}

    def test_dirigenza_funzioni_locali_aran_salary_tranche1(self) -> None:
        """DIRIGENTE first tranche (2020-12-17): 3616.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2020, 12, 17)) == Decimal("3616.60")

    def test_dirigenza_funzioni_locali_aran_salary_tranche2(self) -> None:
        """DIRIGENTE second tranche (1/1/2024): 3846.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        lv = ccnl.level_by_code("DIRIGENTE")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("3846.60")

    def test_dirigenza_funzioni_locali_aran_level_ordering(self) -> None:
        """DIRIGENTE is both highest-order and lowest-order (single level)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["DIRIGENTE"] == max(orders.values())
        assert orders["DIRIGENTE"] == min(orders.values())

    def test_dirigenza_funzioni_locali_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_dirigenza_funzioni_locali_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 165 (38h/week, SIMPLIFICATION)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_dirigenza_funzioni_locali_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: no fixed allowances (posizione variabile)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_dirigenza_funzioni_locali_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_dirigenza_funzioni_locali_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (no automatic scatti per dirigenza)."""
        ccnl = load_ccnl("dirigenza-funzioni-locali-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadDirigenzaFunzioniCentraliAran:
    """Tests for CCNL Area Dirigenza Funzioni Centrali 2022-2024 (S025)."""

    def test_dirigenza_funzioni_centrali_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        assert ccnl.meta.ccnl_id == "dirigenza-funzioni-centrali-aran"
        assert ccnl.meta.cnel_code == "S025"

    def test_dirigenza_funzioni_centrali_aran_has_2_levels(self) -> None:
        """Contract has exactly 2 levels: PRIMA_FASCIA and SECONDA_FASCIA."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        assert len(ccnl.levels) == 2
        assert {lv.code for lv in ccnl.levels} == {
            "PRIMA_FASCIA",
            "SECONDA_FASCIA",
        }

    def test_dirigenza_funzioni_centrali_aran_salary_tranche1(self) -> None:
        """SECONDA_FASCIA first tranche (2023-11-16): 3616.60 EUR/month."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        lv = ccnl.level_by_code("SECONDA_FASCIA")
        assert lv.base_salary.value_at(date(2023, 11, 16)) == Decimal("3616.60")

    def test_dirigenza_funzioni_centrali_aran_salary_tranche2(self) -> None:
        """PRIMA_FASCIA second tranche (1/1/2024): 4908.30 EUR/month."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        lv = ccnl.level_by_code("PRIMA_FASCIA")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("4908.30")

    def test_dirigenza_funzioni_centrali_aran_level_ordering(self) -> None:
        """PRIMA_FASCIA has highest order; SECONDA_FASCIA has lowest."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "PRIMA_FASCIA"
        assert min(orders, key=lambda k: orders[k]) == "SECONDA_FASCIA"

    def test_dirigenza_funzioni_centrali_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_dirigenza_funzioni_centrali_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 165 (38h/week, SIMPLIFICATION)."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_dirigenza_funzioni_centrali_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: no fixed allowances (posizione variabile)."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_dirigenza_funzioni_centrali_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_dirigenza_funzioni_centrali_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (no automatic scatti)."""
        ccnl = load_ccnl("dirigenza-funzioni-centrali-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0
