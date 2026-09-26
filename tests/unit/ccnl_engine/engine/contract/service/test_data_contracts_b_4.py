"""CCNL contract data tests (B): Energia through ServiziAmministrativi."""

from datetime import date
from decimal import Decimal

from ccnl_engine.engine.contract.domain.apprenticeship import (
    ApprenticeshipPercentage,
)
from ccnl_engine.engine.contract.domain.identity import TaxSector
from ccnl_engine.engine.contract.service.loaders import load_ccnl


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
