"""Bundled CCNL data files load with their expected values.

Covers Sistemazioni Idraulico Forestali Operai, Impianti Sportivi Sport,
Formazione Professionale, Concia Unic.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.identity.facade import TaxSector


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
