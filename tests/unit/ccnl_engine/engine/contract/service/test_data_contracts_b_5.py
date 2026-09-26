"""CCNL contract data tests (B): Energia through ServiziAmministrativi."""

from datetime import date
from decimal import Decimal

from ccnl_engine.engine.contract.domain.apprenticeship import (
    ApprenticeshipUnderClassification,
)
from ccnl_engine.engine.contract.domain.identity import TaxSector
from ccnl_engine.engine.contract.service.loaders import load_ccnl


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
