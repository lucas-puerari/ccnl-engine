"""Bundled CCNL data files load with their expected values.

Covers Dirigenza Istruzione Ricerca Aran, Istruzione Ricerca Aran, Sanita
Privata Aiop Aris, Lavoro Domestico Convivente, Lavoro Domestico Non
Convivente.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl


class TestLoadDirigenzaIstruzioneRicercaAran:
    """Tests for CCNL Area Dirigenza Istruzione e Ricerca 2022-2024 (S325)."""

    def test_dirigenza_istruzione_ricerca_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        assert ccnl.meta.ccnl_id == "dirigenza-istruzione-ricerca-aran"
        assert ccnl.meta.cnel_code == "S325"

    def test_dirigenza_istruzione_ricerca_aran_has_2_levels(self) -> None:
        """Contract has exactly 2 levels: PRIMA_FASCIA and SECONDA_FASCIA."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        assert len(ccnl.levels) == 2
        assert {lv.code for lv in ccnl.levels} == {
            "PRIMA_FASCIA",
            "SECONDA_FASCIA",
        }

    def test_dirigenza_istruzione_ricerca_aran_salary_tranche1(self) -> None:
        """SECONDA_FASCIA first tranche (2021-01-01): 3616.59 EUR/month."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        lv = ccnl.level_by_code("SECONDA_FASCIA")
        assert lv.base_salary.value_at(date(2021, 1, 1)) == Decimal("3616.59")

    def test_dirigenza_istruzione_ricerca_aran_salary_tranche2(self) -> None:
        """PRIMA_FASCIA second tranche (1/1/2024): 4908.30 EUR/month."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        lv = ccnl.level_by_code("PRIMA_FASCIA")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("4908.30")

    def test_dirigenza_istruzione_ricerca_aran_level_ordering(self) -> None:
        """PRIMA_FASCIA has highest order; SECONDA_FASCIA has lowest."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "PRIMA_FASCIA"
        assert min(orders, key=lambda k: orders[k]) == "SECONDA_FASCIA"

    def test_dirigenza_istruzione_ricerca_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_dirigenza_istruzione_ricerca_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 165 (38h/week, SIMPLIFICATION)."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_dirigenza_istruzione_ricerca_aran_no_fixed_allowances(self) -> None:
        """Conglobated model: no fixed allowances (posizione variabile)."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_dirigenza_istruzione_ricerca_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_dirigenza_istruzione_ricerca_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (no automatic scatti)."""
        ccnl = load_ccnl("dirigenza-istruzione-ricerca-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadIstruzioneRicercaAran:
    """Tests for CCNL Comparto Istruzione e Ricerca 2022-2024 (S305)."""

    def test_istruzione_ricerca_aran_loads(self) -> None:
        """File loads and has correct id and CNEL code."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        assert ccnl.meta.ccnl_id == "istruzione-ricerca-aran"
        assert ccnl.meta.cnel_code == "S305"

    def test_istruzione_ricerca_aran_has_7_levels(self) -> None:
        """Contract has exactly 7 levels (4 ATA + 3 docente groups)."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        assert len(ccnl.levels) == 7
        assert {lv.code for lv in ccnl.levels} == {
            "COLLABORATORE_SCOLASTICO",
            "OPERATORE",
            "ASSISTENTE",
            "DOCENTE_INFANZIA_PRIMARIA",
            "DOCENTE_DIPLOMATO_SECONDARIA",
            "DOCENTE_SECONDARIA",
            "FUNZIONARIO_ED_ESPERTO",
        }

    def test_istruzione_ricerca_aran_assistente_salary_tranche1(self) -> None:
        """ASSISTENTE first tranche (2022-01-01): 1401.28 EUR/month."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        lv = ccnl.level_by_code("ASSISTENTE")
        assert lv.base_salary.value_at(date(2022, 1, 1)) == Decimal("1401.28")

    def test_istruzione_ricerca_aran_assistente_salary_tranche2(self) -> None:
        """ASSISTENTE second tranche (1/1/2024): 1496.85 EUR/month."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        lv = ccnl.level_by_code("ASSISTENTE")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1496.85")

    def test_istruzione_ricerca_aran_level_ordering(self) -> None:
        """FUNZIONARIO_ED_ESPERTO has highest order; COLLABORATORE has lowest."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "FUNZIONARIO_ED_ESPERTO"
        assert min(orders, key=lambda k: orders[k]) == "COLLABORATORE_SCOLASTICO"

    def test_istruzione_ricerca_aran_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only)."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_istruzione_ricerca_aran_hourly_divisor(self) -> None:
        """Hourly divisor: 156 (36h/week standard, SIMPLIFICATION)."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_istruzione_ricerca_aran_no_fixed_allowances(self) -> None:
        """Conglobated tabellare: no fixed allowances modelled."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_istruzione_ricerca_aran_tax_sector(self) -> None:
        """Contract declares PUBBLICA_AMMINISTRAZIONE tax sector."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        assert ccnl.meta.tax_sector == TaxSector.PUBBLICA_AMMINISTRAZIONE

    def test_istruzione_ricerca_aran_seniority_cadence(self) -> None:
        """Seniority: maximum_count=0 (fasce not automatic scatti)."""
        ccnl = load_ccnl("istruzione-ricerca-aran.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadSanitaPrivataAiopAris:
    """Tests for CCNL Case di Cura Private - Personale Non Medico (AIOP/ARIS)."""

    def test_sanita_privata_aiop_aris_loads(self) -> None:
        """Contract id and CNEL code match expected values."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        assert ccnl.meta.ccnl_id == "sanita-privata-aiop-aris"
        assert ccnl.meta.cnel_code == "T011"

    def test_sanita_privata_aiop_aris_has_28_levels(self) -> None:
        """Contract has exactly 28 levels covering categories A to E."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        assert len(ccnl.levels) == 28
        assert {lv.code for lv in ccnl.levels} == {
            "A",
            "A1",
            "A2",
            "A3",
            "A4",
            "B",
            "B1",
            "B2",
            "B3",
            "B4",
            "C",
            "C1",
            "C2",
            "C3",
            "C4",
            "D",
            "D1",
            "D2",
            "D3",
            "D4",
            "DS",
            "DS1",
            "DS2",
            "DS3",
            "DS4",
            "E",
            "E1",
            "E2",
        }

    def test_sanita_privata_aiop_aris_level_a_salary(self) -> None:
        """Level A salary at 2026-01-01: 1467.45 EUR/month (Tabella 1)."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        lv = ccnl.level_by_code("A")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1467.45")

    def test_sanita_privata_aiop_aris_level_e2_salary(self) -> None:
        """Level E2 salary at 2026-01-01: 3554.39 EUR/month (Tabella 1)."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        lv = ccnl.level_by_code("E2")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("3554.39")

    def test_sanita_privata_aiop_aris_level_ordering(self) -> None:
        """E2 has highest order (order 28); A has lowest (order 1)."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "E2"
        assert min(orders, key=lambda k: orders[k]) == "A"

    def test_sanita_privata_aiop_aris_additional_months(self) -> None:
        """Additional months: 13 (tredicesima only, Art. 50/66)."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_sanita_privata_aiop_aris_hourly_divisor(self) -> None:
        """Hourly divisor: 156 (Art. 58: monthly/26/6 for 36h/week)."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(156)

    def test_sanita_privata_aiop_aris_no_fixed_allowances(self) -> None:
        """Conglobated tabellare (Art. 55): no fixed allowances."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_sanita_privata_aiop_aris_tax_sector(self) -> None:
        """Contract declares TERZIARIO tax sector."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_sanita_privata_aiop_aris_seniority_cadence(self) -> None:
        """Seniority frozen at 1993-12-31 per Art. 56; maximum_count=0."""
        ccnl = load_ccnl("sanita-privata-aiop-aris.json")
        si = ccnl.parameters.seniority_increments
        # cadence_months is inert when maximum_count=0
        assert si.cadence_months == 24
        assert si.maximum_count == 0


class TestLoadLavoroDomesticoConvivente:
    """Tests for lavoro-domestico-convivente.json (DOMINA/FIDALDO, CNEL H501)."""

    def test_lavoro_domestico_convivente_loads(self) -> None:
        """id='lavoro-domestico-convivente', cnel_code='H501'."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        assert ccnl.meta.ccnl_id == "lavoro-domestico-convivente"
        assert ccnl.meta.cnel_code == "H501"

    def test_lavoro_domestico_convivente_has_8_levels(self) -> None:
        """Eight levels: A, AS, B, BS, C, CS, D, DS."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "A",
            "AS",
            "B",
            "BS",
            "C",
            "CS",
            "D",
            "DS",
        }

    def test_lavoro_domestico_convivente_level_a_salary(self) -> None:
        """Level A salary at 2026-01-01: 908.10 EUR/month (Domina Tab.A)."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        lv = ccnl.level_by_code("A")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("908.10")

    def test_lavoro_domestico_convivente_level_ds_salary(self) -> None:
        """Level DS salary at 2026-01-01: 1474.73 EUR/month (Domina Tab.A)."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        lv = ccnl.level_by_code("DS")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1474.73")

    def test_lavoro_domestico_convivente_level_ordering(self) -> None:
        """DS has highest order (8); A has lowest (1)."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "DS"
        assert min(orders, key=lambda k: orders[k]) == "A"

    def test_lavoro_domestico_convivente_additional_months(self) -> None:
        """Additional months: 13 (tredicesima, Art. 39 CCNL 28/10/2025)."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_lavoro_domestico_convivente_hourly_divisor(self) -> None:
        """Hourly divisor: 234 (54 h/week x 52/12, Art. 14 c. 1 lett. a)."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(234)

    def test_lavoro_domestico_convivente_d_ds_indennita(self) -> None:
        """D and DS have indennità di funzione 207.69; A-CS have none."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        for code in ("A", "AS", "B", "BS", "C", "CS"):
            codes = [a.code for a in ccnl.level_by_code(code).fixed_allowances]
            assert codes == ["vitto_alloggio"]
        for code in ("D", "DS"):
            lv = ccnl.level_by_code(code)
            assert [a.code for a in lv.fixed_allowances] == [
                "INDENNITA_FUNZIONE",
                "vitto_alloggio",
            ]
            assert lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1)) == Decimal(
                "207.69"
            )

    def test_lavoro_domestico_convivente_board_and_lodging(self) -> None:
        """Every level has board and lodging in kind, Tabella F 2026 x 30.

        Art. 36 c. 3: (2.33 + 2.33 + 2.00) x 30 = 199.80 per month, not
        reduced for reduced hours (art. 14 c. 2).
        """
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        for lv in ccnl.levels:
            (board,) = (a for a in lv.fixed_allowances if a.code == "vitto_alloggio")
            assert board.in_kind
            assert not board.part_time_proportionable
            assert board.monthly.value_at(date(2026, 1, 1)) == Decimal("199.80")

    def test_lavoro_domestico_convivente_tax_sector(self) -> None:
        """Contract declares LAVORO_DOMESTICO tax sector."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        assert ccnl.meta.tax_sector == TaxSector.LAVORO_DOMESTICO

    def test_lavoro_domestico_convivente_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 7 scatti."""
        ccnl = load_ccnl("lavoro-domestico-convivente.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 7


class TestLoadLavoroDomesticoNonConvivente:
    """Tests for lavoro-domestico-non-convivente.json (DOMINA, CNEL H501)."""

    def test_lavoro_domestico_non_convivente_loads(self) -> None:
        """id='lavoro-domestico-non-convivente', cnel_code='H501'."""
        ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
        assert ccnl.meta.ccnl_id == "lavoro-domestico-non-convivente"
        assert ccnl.meta.cnel_code == "H501"

    def test_lavoro_domestico_non_convivente_has_8_levels(self) -> None:
        """Eight levels: A, AS, B, BS, C, CS, D, DS."""
        ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
        assert len(ccnl.levels) == 8
        assert {lv.code for lv in ccnl.levels} == {
            "A",
            "AS",
            "B",
            "BS",
            "C",
            "CS",
            "D",
            "DS",
        }

    def test_lavoro_domestico_non_convivente_level_a_salary(self) -> None:
        """Level A monthly salary: 6.51 EUR/h x 40 x 52 / 12 = 1128.40 EUR."""
        ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
        lv = ccnl.level_by_code("A")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1128.40")

    def test_lavoro_domestico_non_convivente_level_ds_salary(self) -> None:
        """Level DS monthly salary: 9.97 EUR/h x 40 x 52 / 12 = 1728.13 EUR."""
        ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
        lv = ccnl.level_by_code("DS")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1728.13")

    def test_lavoro_domestico_non_convivente_level_ordering(self) -> None:
        """DS has highest order (8); A has lowest (1)."""
        ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
        orders = {lv.code: lv.order for lv in ccnl.levels}
        assert max(orders, key=lambda k: orders[k]) == "DS"
        assert min(orders, key=lambda k: orders[k]) == "A"

    def test_lavoro_domestico_non_convivente_additional_months(self) -> None:
        """Additional months: 13 (tredicesima, Art. 39 CCNL 28/10/2025)."""
        ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_lavoro_domestico_non_convivente_hourly_divisor(self) -> None:
        """Hourly divisor: 40 h/week x 52 / 12 = 173.33 (Art. 14 c. 1 lett. b)."""
        ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
        divisor = ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1))
        assert divisor == Decimal("173.33")

    def test_lavoro_domestico_assistance_contribution(self) -> None:
        """Art. 54 c. 2: 0.06 EUR per paid hour, 0.02 of it from the worker."""
        for slug in (
            "lavoro-domestico-non-convivente.json",
            "lavoro-domestico-convivente.json",
        ):
            assistance = load_ccnl(slug).parameters.assistance_contribution
            assert assistance is not None
            day = date(2026, 1, 1)
            assert assistance.employee_per_hour.value_at(day) == Decimal("0.02")
            assert assistance.employer_per_hour.value_at(day) == Decimal("0.04")

    def test_lavoro_domestico_non_convivente_no_fixed_allowances(self) -> None:
        """All levels have no fixed allowances (function indennità not applicable)."""
        ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
        for lv in ccnl.levels:
            assert lv.fixed_allowances == ()

    def test_lavoro_domestico_non_convivente_tax_sector(self) -> None:
        """Contract declares LAVORO_DOMESTICO tax sector."""
        ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
        assert ccnl.meta.tax_sector == TaxSector.LAVORO_DOMESTICO

    def test_lavoro_domestico_non_convivente_seniority_cadence(self) -> None:
        """Seniority: biennale (24 months), maximum 7 scatti."""
        ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 7
