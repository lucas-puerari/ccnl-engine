"""Bundled CCNL data files load with their expected values.

Covers Pulizia Artigianato Confartigianato, Aziende Termali Federterme,
Autoscuole Unasca, Agenti Immobilari Fiaip.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.employment.models_apprenticeship import (
    ApprenticeshipUnderClassification,
)
from ccnl_engine.contract.identity.facade import TaxSector


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
