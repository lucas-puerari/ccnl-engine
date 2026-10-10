"""Bundled CCNL data files load with their expected values.

Covers Alimentaristi Cooperative E 016, Turismo Confesercenti, Rsa Aiop,
Autostrade Trafori.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.identity.facade import TaxSector


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
