"""Bundled CCNL data files load with their expected values.

Covers Cooperative Consorzi Agricoli, Anas, Vigilanza Privata Federdat Gpg,
Vigilanza Privata Federdat Sf, Sistemazioni Idraulico Forestali Impiegati.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.apprenticeship import (
    ApprenticeshipPercentage,
)
from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl


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
