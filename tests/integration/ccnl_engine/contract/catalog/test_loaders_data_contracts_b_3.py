"""Bundled CCNL data files load with their expected values.

Covers Recapito Corrispondenza Fise, Servizi Postali Appalto Fise, Portieri
Fabbricati Confedilizia.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.contract.identity.facade import TaxSector


class TestLoadRecapitoCorrispondenzaFise:
    """Tests for CCNL Recapito Corrispondenza FISE-ARE (K711)."""

    def test_recapito_corrispondenza_fise_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert ccnl.meta.ccnl_id == "recapito-corrispondenza-fise"
        assert ccnl.meta.cnel_code == "K711"

    def test_recapito_corrispondenza_fise_has_8_levels(self) -> None:
        """Contract has exactly 8 levels with codes 1,2,3S,3,4,5S,5,6."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3S", "3", "4", "5S", "5", "6"}

    def test_recapito_corrispondenza_fise_level3_salary_feb2024(self) -> None:
        """Level 3 base salary at 2024-02-01: 1567.29 EUR (1st tranche)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 2, 1)) == Decimal("1567.29")

    def test_recapito_corrispondenza_fise_level3_salary_jun2026(self) -> None:
        """Level 3 base salary at 2026-06-01: 1687.29 EUR (4th tranche)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2026, 6, 1)) == Decimal("1687.29")

    def test_recapito_corrispondenza_fise_level_ordering(self) -> None:
        """Level 1 is highest; level 6 is lowest."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "6"
        assert ordered[-1].code == "1"

    def test_recapito_corrispondenza_fise_additional_months(self) -> None:
        """14 mensilita: tredicesima + quattordicesima."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_recapito_corrispondenza_fise_hourly_divisor(self) -> None:
        """Hourly divisor 173 (confirmed from ilccnl.it cross-check)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 173

    def test_recapito_corrispondenza_fise_edr_allowance(self) -> None:
        """All 8 levels have EDR=10.33 as fixed_allowance (split model)."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        for lv in ccnl.levels:
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "EDR"

    def test_recapito_corrispondenza_fise_tax_sector(self) -> None:
        """tax_sector == TERZIARIO."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_recapito_corrispondenza_fise_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), max 8 scatti."""
        ccnl = load_ccnl("recapito-corrispondenza-fise.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 8


class TestLoadServiziPostaliAppaltoFise:
    """Tests for CCNL Servizi Postali in Appalto (FISE-ARE, K721)."""

    def test_servizi_postali_appalto_fise_loads(self) -> None:
        """Contract loads with correct id and CNEL code K721."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert ccnl.meta.ccnl_id == "servizi-postali-appalto-fise"
        assert ccnl.meta.cnel_code == "K721"

    def test_servizi_postali_appalto_fise_has_7_levels(self) -> None:
        """7 levels: 1, 2, 3S, 3, 4S, 4, 5."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3S", "3", "4S", "4", "5"}

    def test_servizi_postali_appalto_fise_level3_salary_jan2024(self) -> None:
        """Level 3 base salary at 2024-01-01: 1448.09 EUR (1st tranche)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1448.09")

    def test_servizi_postali_appalto_fise_level3_salary_dec2025(self) -> None:
        """Level 3 base salary at 2025-12-01: 1509.09 EUR (3rd tranche)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv.base_salary.value_at(date(2025, 12, 1)) == Decimal("1509.09")

    def test_servizi_postali_appalto_fise_level_ordering(self) -> None:
        """Level 1 is highest (order=7); level 5 is lowest (order=1)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "5"
        assert ordered[-1].code == "1"

    def test_servizi_postali_appalto_fise_additional_months(self) -> None:
        """14 mensilita: tredicesima (Art. 37) + quattordicesima (Art. 38)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert val == Decimal(14)

    def test_servizi_postali_appalto_fise_hourly_divisor(self) -> None:
        """Hourly divisor 173 (Art. 33 explicit)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == 173

    def test_servizi_postali_appalto_fise_fixed_allowances(self) -> None:
        """All 7 levels have IND-INT and EDR as fixed allowances (split model)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        for lv in ccnl.levels:
            codes = {a.code for a in lv.fixed_allowances}
            assert codes == {"IND-INT", "EDR"}

    def test_servizi_postali_appalto_fise_tax_sector(self) -> None:
        """tax_sector == TERZIARIO."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_servizi_postali_appalto_fise_seniority_cadence(self) -> None:
        """Seniority: biennale (24 mo), max=10, first at 48 mo (impiegati)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 10
        assert si.first_cadence_months == 48

    def test_servizi_postali_appalto_fise_operaio_seniority_max_1(self) -> None:
        """Operaio maximum_count=1 (Art. 35A single premio)."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        si = ccnl.parameters.seniority_increments
        assert si.maximum_count_by_category.get(WorkerCategory.OPERAIO) == 1

    def test_servizi_postali_appalto_fise_seniority_category_amounts(
        self,
    ) -> None:
        """Operaio and impiegato have different seniority amounts at L2."""
        ccnl = load_ccnl("servizi-postali-appalto-fise.json")
        si = ccnl.parameters.seniority_increments
        op = si.amount_by_level_by_category[WorkerCategory.OPERAIO]["2"]
        imp = si.amount_by_level_by_category[WorkerCategory.IMPIEGATO]["2"]
        assert op.value_at(date(2026, 1, 1)) == Decimal("56.66")
        assert imp.value_at(date(2026, 1, 1)) == Decimal("62.62")


class TestLoadPortieriFabbricatiConfedilizia:
    """Tests for CCNL Dipendenti da Proprietari di Fabbricati (H401)."""

    def test_portieri_fabbricati_confedilizia_loads(self) -> None:
        """Contract loads with correct id and CNEL code H401."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert ccnl.meta.ccnl_id == "portieri-fabbricati-confedilizia"
        assert ccnl.meta.cnel_code == "H401"

    def test_portieri_fabbricati_confedilizia_has_11_levels(self) -> None:
        """11 levels: B1-B5, C3, C4, D1-D4 (A and C1/C2 excluded)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert len(ccnl.levels) == 11
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "B1",
            "B2",
            "B3",
            "B4",
            "B5",
            "C3",
            "C4",
            "D1",
            "D2",
            "D3",
            "D4",
        }

    def test_portieri_fabbricati_confedilizia_level_b1_salary_2026(
        self,
    ) -> None:
        """B1 base salary at 2026-01-01: 1519.10 EUR (1st tranche)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "B1")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1519.10")

    def test_portieri_fabbricati_confedilizia_level_c3_salary_2028(
        self,
    ) -> None:
        """C3 base salary at 2028-01-01: 1868.50 EUR (3rd tranche)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        lv = next(lv for lv in ccnl.levels if lv.code == "C3")
        assert lv.base_salary.value_at(date(2028, 1, 1)) == Decimal("1868.50")

    def test_portieri_fabbricati_confedilizia_level_ordering(self) -> None:
        """C3 is highest (order=11); B5 is lowest (order=1)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        ordered = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert ordered[0].code == "B5"
        assert ordered[-1].code == "C3"

    def test_portieri_fabbricati_confedilizia_additional_months(self) -> None:
        """13 mensilita: tredicesima only (Art. 130 Gratifica natalizia)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        val = ccnl.parameters.additional_months.value_at(date(2026, 6, 1))
        assert val == Decimal(13)

    def test_portieri_fabbricati_confedilizia_hourly_divisor(self) -> None:
        """Hourly divisor 173 (40 h/week, Art. 60/62/69 CCNL)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1)) == 173

    def test_portieri_fabbricati_confedilizia_no_fixed_allowances(
        self,
    ) -> None:
        """All 11 levels have empty fixed_allowances (conglobated model)."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_portieri_fabbricati_confedilizia_tax_sector(self) -> None:
        """tax_sector == TERZIARIO."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_portieri_fabbricati_confedilizia_seniority_cadence(self) -> None:
        """Seniority: triennale (36 mo), max=12 scatti."""
        ccnl = load_ccnl("portieri-fabbricati-confedilizia.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 12
