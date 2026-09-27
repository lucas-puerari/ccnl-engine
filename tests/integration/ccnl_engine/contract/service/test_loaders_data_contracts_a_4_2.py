"""Bundled CCNL data files load with their expected values.

Covers Pelli Cuoio Industria Assopellettieri, Pubblici Esercizi Ristorazione
Fipe Angem, Agenzie Di Viaggio Fiavet, Terziario Confesercenti, Turismo
Federalberghi, Funzioni Centrali Aran.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.apprenticeship import (
    ApprenticeshipUnderClassification,
)
from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl


class TestLoadPelliCuoioIndustriaAssopellettieri:
    """Tests for CCNL Pelli e Cuoio Industria — Assopellettieri (D111)."""

    def test_pelli_cuoio_industria_assopellettieri_loads(self) -> None:
        """Contract loads with correct id and CNEL code D111."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert ccnl.meta.ccnl_id == "pelli-cuoio-industria-assopellettieri"
        assert ccnl.meta.cnel_code == "D111"

    def test_pelli_cuoio_industria_assopellettieri_has_7_levels(self) -> None:
        """Contract has exactly 7 levels: 1, 2, 3, 4, 4S, 5, 6."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "4S", "5", "6"}

    def test_pelli_cuoio_industria_assopellettieri_level4_salary_tranche1(
        self,
    ) -> None:
        """Level 4 first tranche (Apr 2023): 1810.42 EUR/month."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2023, 6, 1)) == Decimal("1810.42")

    def test_pelli_cuoio_industria_assopellettieri_level4_salary_tranche2(
        self,
    ) -> None:
        """Level 4 second tranche (Dec 2023): 1873.70 EUR/month."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1873.70")

    def test_pelli_cuoio_industria_assopellettieri_level_ordering(self) -> None:
        """Level 6 is highest order; level 1 is lowest order."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["6"] == max(orders.values())
        assert orders["1"] == min(orders.values())

    def test_pelli_cuoio_industria_assopellettieri_additional_months(
        self,
    ) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_pelli_cuoio_industria_assopellettieri_hourly_divisor(self) -> None:
        """Hourly divisor: 173 (Art. 35 CCNL CNEL PDF)."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(173)

    def test_pelli_cuoio_industria_assopellettieri_no_fixed_allowances(
        self,
    ) -> None:
        """Conglobated model: all levels have empty fixed_allowances."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_pelli_cuoio_industria_assopellettieri_tax_sector(self) -> None:
        """Contract declares INDUSTRIA tax sector."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_pelli_cuoio_industria_assopellettieri_seniority_cadence(
        self,
    ) -> None:
        """Seniority: biennale (24 months), maximum 4 scatti."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 4

    def test_pelli_cuoio_industria_assopellettieri_apprenticeship_tracks(
        self,
    ) -> None:
        """6 under_classification tracks, one per destination level."""
        ccnl = load_ccnl("pelli-cuoio-industria-assopellettieri.json")
        assert len(ccnl.apprenticeship) == 6
        for track in ccnl.apprenticeship:
            assert isinstance(track, ApprenticeshipUnderClassification)
        dest_levels = {t.name: t.destination_levels for t in ccnl.apprenticeship}
        assert dest_levels["dest_6"] == ("6",)
        assert dest_levels["dest_2"] == ("2",)


class TestLoadPubbliciEserciziRistorazioneFipeAngem:
    """CCNL Pubblici Esercizi, Ristorazione Collettiva e Turismo (FIPE/ANGEM, H05Y)."""

    def test_pubblici_esercizi_fipe_angem_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        assert ccnl.meta.ccnl_id == "pubblici-esercizi-fipe-angem"
        assert ccnl.meta.cnel_code == "H05Y"

    def test_pubblici_esercizi_fipe_angem_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: 1, 2, 3, 4, 5, 6, 6s, 7, Qa, Qb."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "6s", "7", "Qa", "Qb"}

    def test_pubblici_esercizi_fipe_angem_level4_salary_tranche1(self) -> None:
        """Level 4 first tranche (Jun 2024): 1612.69 EUR/month."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2024, 6, 1)) == Decimal("1612.69")

    def test_pubblici_esercizi_fipe_angem_level4_salary_tranche2(self) -> None:
        """Level 4 second tranche (Jun 2026): 1692.69 EUR/month."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("1692.69")

    def test_pubblici_esercizi_fipe_angem_level_ordering(self) -> None:
        """Qa is highest-order level; 7 is lowest-order level."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["Qa"] == max(orders.values())
        assert orders["7"] == min(orders.values())

    def test_pubblici_esercizi_fipe_angem_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_pubblici_esercizi_fipe_angem_hourly_divisor(self) -> None:
        """Hourly divisor: 172 (Art. 160 CCNL FIPE/ANGEM 2024)."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(172)

    def test_pubblici_esercizi_fipe_angem_quadri_fixed_allowances(self) -> None:
        """Qa has IDF_A=75, Qb has IDF_B=70; all other levels have no allowances."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        qa = ccnl.level_by_code("Qa")
        qb = ccnl.level_by_code("Qb")
        assert len(qa.fixed_allowances) == 1
        assert qa.fixed_allowances[0].code == "IND_FUN"
        assert qa.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "75.00"
        )
        assert len(qb.fixed_allowances) == 1
        assert qb.fixed_allowances[0].code == "IND_FUN"
        assert qb.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
            "70.00"
        )
        for lv in ccnl.levels:
            if lv.code not in {"Qa", "Qb"}:
                assert lv.fixed_allowances == ()

    def test_pubblici_esercizi_fipe_angem_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_pubblici_esercizi_fipe_angem_seniority_cadence(self) -> None:
        """Seniority: quadriennale (48 months), maximum 6 scatti."""
        ccnl = load_ccnl("pubblici-esercizi-fipe-angem.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 48
        assert si.maximum_count == 6


class TestLoadAgenzieDiViaggioFiavet:
    """CCNL Agenzie di Viaggio e Turismo — Fiavet/Confcommercio (H052)."""

    def test_agenzie_viaggio_fiavet_loads(self) -> None:
        """Contract loads with id and CNEL code H052."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        assert ccnl.meta.ccnl_id == "agenzie-viaggio-fiavet"
        assert ccnl.meta.cnel_code == "H052"

    def test_agenzie_viaggio_fiavet_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: QA QB 1 2 3 4 5 6S 6 7."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"QA", "QB", "1", "2", "3", "4", "5", "6S", "6", "7"}

    def test_agenzie_viaggio_fiavet_level4_salary_tranche1(self) -> None:
        """Level 4 first tranche (Jun 2024): 1550.69 EUR/month."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2024, 6, 1)) == Decimal("1550.69")

    def test_agenzie_viaggio_fiavet_level4_salary_tranche2(self) -> None:
        """Level 4 second tranche (Sep 2026): 1680.69 EUR/month."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2026, 9, 1)) == Decimal("1680.69")

    def test_agenzie_viaggio_fiavet_level_ordering(self) -> None:
        """QA is highest-order level; 7 is lowest-order level."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["QA"] == max(orders.values())
        assert orders["7"] == min(orders.values())

    def test_agenzie_viaggio_fiavet_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_agenzie_viaggio_fiavet_hourly_divisor(self) -> None:
        """Hourly divisor: 172 (Art. 146 CCNL Fiavet 2019)."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(172)

    def test_agenzie_viaggio_fiavet_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_agenzie_viaggio_fiavet_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_agenzie_viaggio_fiavet_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), maximum 6 scatti."""
        ccnl = load_ccnl("agenzie-viaggio-fiavet.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 6


class TestLoadTerziarioConfesercenti:
    """Tests for CCNL Terziario Distribuzione e Servizi — Confesercenti (H012)."""

    def test_terziario_confesercenti_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        assert ccnl.meta.ccnl_id == "terziario-confesercenti"
        assert ccnl.meta.cnel_code == "H012"

    def test_terziario_confesercenti_has_8_levels(self) -> None:
        """Contract has exactly 8 levels: Q, I, II, III, IV, V, VI, VII."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 8
        assert codes == {"Q", "I", "II", "III", "IV", "V", "VI", "VII"}

    def test_terziario_confesercenti_level4_salary_tranche1(self) -> None:
        """Level IV first tranche (Apr 2023): 1646.68 EUR/month."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        lv = ccnl.level_by_code("IV")
        assert lv.base_salary.value_at(date(2023, 4, 1)) == Decimal("1646.68")

    def test_terziario_confesercenti_level4_salary_tranche5(self) -> None:
        """Level IV fifth tranche (Nov 2026): 1816.68 EUR/month."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        lv = ccnl.level_by_code("IV")
        assert lv.base_salary.value_at(date(2026, 11, 1)) == Decimal("1816.68")

    def test_terziario_confesercenti_level_ordering(self) -> None:
        """Q is highest-order level; VII is lowest-order level."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["Q"] == max(orders.values())
        assert orders["VII"] == min(orders.values())

    def test_terziario_confesercenti_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_terziario_confesercenti_hourly_divisor(self) -> None:
        """Hourly divisor: 168 (Art. 211 CCNL 2019, 40h/week)."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(168)

    def test_terziario_confesercenti_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_terziario_confesercenti_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_terziario_confesercenti_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), maximum 10 scatti."""
        ccnl = load_ccnl("terziario-confesercenti.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadTurismoFederalberghi:
    """Tests for CCNL Turismo — Federalberghi/Faita (H052)."""

    def test_turismo_federalberghi_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        assert ccnl.meta.ccnl_id == "turismo-federalberghi"
        assert ccnl.meta.cnel_code == "H052"

    def test_turismo_federalberghi_has_10_levels(self) -> None:
        """Contract has exactly 10 levels: A, B, 1-6s, 6, 7."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 10
        assert codes == {"A", "B", "1", "2", "3", "4", "5", "6s", "6", "7"}

    def test_turismo_federalberghi_level4_salary_tranche1(self) -> None:
        """Level 4 first tranche (lug 2024): 1620.69 EUR/month."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2024, 7, 1)) == Decimal("1620.69")

    def test_turismo_federalberghi_level4_salary_tranche3(self) -> None:
        """Level 4 third tranche (mag 2026): 1695.69 EUR/month."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        lv = ccnl.level_by_code("4")
        assert lv.base_salary.value_at(date(2026, 5, 1)) == Decimal("1695.69")

    def test_turismo_federalberghi_level_ordering(self) -> None:
        """Level A is highest-order; level 7 is lowest-order."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["A"] == max(orders.values())
        assert orders["7"] == min(orders.values())

    def test_turismo_federalberghi_additional_months(self) -> None:
        """Additional months: 14 (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            14
        )

    def test_turismo_federalberghi_hourly_divisor(self) -> None:
        """Hourly divisor: 172 (Art. 151 CCNL 2010, 40h/week)."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(172)

    def test_turismo_federalberghi_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_turismo_federalberghi_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_turismo_federalberghi_seniority_cadence(self) -> None:
        """Seniority: triennale (36 months), maximum 6 scatti."""
        ccnl = load_ccnl("turismo-federalberghi.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 6


class TestLoadFunzioniCentraliAran:
    """Tests for CCNL Comparto Funzioni Centrali 2022-2024 (S005)."""

    def test_funzioni_centrali_aran_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        assert ccnl.meta.ccnl_id == "funzioni-centrali-aran"
        assert ccnl.meta.cnel_code == "S005"

    def test_funzioni_centrali_aran_has_4_levels(self) -> None:
        """Contract has exactly 4 levels: OPERATORI, ASSISTENTI, FUNZIONARI, ELEVATE."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        codes = {lv.code for lv in ccnl.levels}
        assert len(ccnl.levels) == 4
        assert codes == {
            "OPERATORI",
            "ASSISTENTI",
            "FUNZIONARI",
            "ELEVATE_PROFESSIONALITA",
        }

    def test_funzioni_centrali_aran_funzionari_salary_tranche1(self) -> None:
        """FUNZIONARI first tranche (9/5/2022): 1958.49 EUR/month."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        lv = ccnl.level_by_code("FUNZIONARI")
        assert lv.base_salary.value_at(date(2022, 5, 9)) == Decimal("1958.49")

    def test_funzioni_centrali_aran_funzionari_salary_tranche2(self) -> None:
        """FUNZIONARI second tranche (1/1/2024): 2113.59 EUR/month."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        lv = ccnl.level_by_code("FUNZIONARI")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("2113.59")

    def test_funzioni_centrali_aran_level_ordering(self) -> None:
        """ELEVATE_PROFESSIONALITA is highest-order; OPERATORI is lowest-order."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert orders["ELEVATE_PROFESSIONALITA"] == max(orders.values())
        assert orders["OPERATORI"] == min(orders.values())

    def test_funzioni_centrali_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_funzioni_centrali_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 156 (Art. 29 c.3, 36h/week)."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_funzioni_centrali_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: all levels have no fixed allowances."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_funzioni_centrali_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_funzioni_centrali_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (differenziali non automatici, Art. 16)."""
        ccnl = load_ccnl("funzioni-centrali-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0
