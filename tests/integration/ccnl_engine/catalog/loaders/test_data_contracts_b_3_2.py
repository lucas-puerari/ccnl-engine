"""Bundled CCNL data files load with their expected values.

Covers Metalmeccanica Cooperative, Scuole Privatelaiche Aninsei, Istituzioni
Servizi Socio Assistenziali Anaste, Scuole Maternie Fism, Occhiali Occhialeria
Industria.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.apprenticeship.models import UnderClassificationPeriod
from ccnl_engine.catalog.loaders import load_ccnl


class TestLoadMetalmeccanicaCooperative:
    """Tests for CCNL Metalmeccanica - Cooperative (C016)."""

    def test_metalmeccanica_cooperative_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("metalmeccanica-cooperative")
        assert ccnl.meta.ccnl_id == "metalmeccanica-cooperative"
        assert ccnl.meta.cnel_code == "C016"

    def test_metalmeccanica_cooperative_has_9_levels(self) -> None:
        """Contract has exactly 9 levels with correct codes."""
        ccnl = load_ccnl("metalmeccanica-cooperative")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"D1", "D2", "C1", "C2", "C3", "B1", "B2", "B3", "A1"}

    def test_metalmeccanica_cooperative_level_d1_salary_2025(self) -> None:
        """D1 base salary at first tranche (2025-06-01)."""
        ccnl = load_ccnl("metalmeccanica-cooperative")
        d1 = next(lv for lv in ccnl.levels if lv.code == "D1")
        assert d1.base_salary.value_at(date(2025, 6, 1)) == Decimal("1754.06")

    def test_metalmeccanica_cooperative_level_a1_salary_2026(self) -> None:
        """A1 base salary at second tranche (2026-06-01)."""
        ccnl = load_ccnl("metalmeccanica-cooperative")
        a1 = next(lv for lv in ccnl.levels if lv.code == "A1")
        assert a1.base_salary.value_at(date(2026, 6, 1)) == Decimal("3054.52")

    def test_metalmeccanica_cooperative_level_ordering(self) -> None:
        """A1 is the highest-order level; D1 is the lowest."""
        ccnl = load_ccnl("metalmeccanica-cooperative")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "D1"
        assert by_order[-1].code == "A1"

    def test_metalmeccanica_cooperative_additional_months(self) -> None:
        """Contract provides 13 additional months (tredicesima only)."""
        ccnl = load_ccnl("metalmeccanica-cooperative")
        assert ccnl.parameters.additional_months.value_at(date(2026, 6, 1)) == Decimal(
            13
        )

    def test_metalmeccanica_cooperative_hourly_divisor(self) -> None:
        """Hourly divisor is 173 (40h/week, metalmeccanici standard)."""
        ccnl = load_ccnl("metalmeccanica-cooperative")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 6, 1)) == Decimal(173)

    def test_metalmeccanica_cooperative_fixed_allowances(self) -> None:
        """A1 and B3 have IND_FUN allowances; all others have none."""
        ccnl = load_ccnl("metalmeccanica-cooperative")
        a1 = next(lv for lv in ccnl.levels if lv.code == "A1")
        b3 = next(lv for lv in ccnl.levels if lv.code == "B3")
        c2 = next(lv for lv in ccnl.levels if lv.code == "C2")
        assert len(a1.fixed_allowances) == 1
        assert a1.fixed_allowances[0].code == "IND_FUN"
        assert a1.fixed_allowances[0].monthly.value_at(date(2026, 6, 1)) == Decimal(
            "180.00"
        )
        assert len(b3.fixed_allowances) == 1
        assert b3.fixed_allowances[0].monthly.value_at(date(2026, 6, 1)) == Decimal(
            "120.00"
        )
        assert c2.fixed_allowances == ()

    def test_metalmeccanica_cooperative_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("metalmeccanica-cooperative")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_metalmeccanica_cooperative_seniority_cadence(self) -> None:
        """Seniority increments: biennali (24 months), max 5."""
        ccnl = load_ccnl("metalmeccanica-cooperative")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5


class TestLoadScuolePrivatelaicheAninsei:
    """Tests for CCNL Scuole Private Laiche ANINSEI (T231)."""

    def test_scuole_private_laiche_aninsei_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei")
        assert ccnl.meta.ccnl_id == "scuole-private-laiche-aninsei"
        assert ccnl.meta.cnel_code == "T231"

    def test_scuole_private_laiche_aninsei_has_9_levels(self) -> None:
        """Contract has exactly 9 levels with the expected codes."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei")
        assert len(ccnl.levels) == 9
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"I", "II", "III", "IV", "V", "VI", "VII", "VIII_A", "VIII_B"}

    def test_scuole_private_laiche_aninsei_level4_salary_2024(self) -> None:
        """Level IV base salary at first tranche (2024-06-15) = 1397.56 EUR."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei")
        lv = next(x for x in ccnl.levels if x.code == "IV")
        assert lv.base_salary.value_at(date(2024, 6, 15)) == Decimal("1397.56")

    def test_scuole_private_laiche_aninsei_level4_salary_2026(self) -> None:
        """Level IV base salary at third tranche (2026-01-01) = 1491.38 EUR."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei")
        lv = next(x for x in ccnl.levels if x.code == "IV")
        assert lv.base_salary.value_at(date(2026, 1, 1)) == Decimal("1491.38")

    def test_scuole_private_laiche_aninsei_level_ordering(self) -> None:
        """Lowest order is I (1), highest order is VIII_B (9)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "I"
        assert by_order[-1].code == "VIII_B"

    def test_scuole_private_laiche_aninsei_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei")
        assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == Decimal(
            13
        )

    def test_scuole_private_laiche_aninsei_hourly_divisor(self) -> None:
        """Hourly divisor = 165 (38h/week, Art. 27)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 1, 1)) == Decimal(165)

    def test_scuole_private_laiche_aninsei_only_salario_di_anzianita(self) -> None:
        """Conglobated model: the only allowances are the art. 24 bands."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei")
        for lv in ccnl.levels:
            assert all(a.code.startswith("SAL_ANZ_") for a in lv.fixed_allowances)
            assert len(lv.fixed_allowances) == 7

    def test_scuole_private_laiche_aninsei_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_scuole_private_laiche_aninsei_seniority_cadence(self) -> None:
        """Seniority frozen: maximum_count=0 (milestone-based, Art. 24)."""
        ccnl = load_ccnl("scuole-private-laiche-aninsei")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadIstituzioniServiziSocioAssistenzialiAnaste:
    """Tests for CCNL Istituzioni e Servizi Socio-Assistenziali ANASTE (T131)."""

    def test_anaste_nurse_allowance(self) -> None:
        """Art. 70 c. 2: 155 a month on 12 payments, role infermiere, levels 6-7."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        for code in ("6", "7"):
            (allowance,) = ccnl.level_by_code(code).fixed_allowances
            assert allowance.code == "INDENNITA_PROFESSIONALE_INFERMIERI"
            assert allowance.role == "infermiere"
            assert allowance.months_per_year == 12
            assert allowance.monthly.value_at(date(2026, 1, 1)) == Decimal("155.00")

    def test_anaste_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        assert ccnl.meta.ccnl_id == "istituzioni-servizi-socio-assistenziali-anaste"
        assert ccnl.meta.cnel_code == "T131"

    def test_anaste_has_12_levels(self) -> None:
        """Contract has exactly 12 levels with the expected codes."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        assert len(ccnl.levels) == 12
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"Q", "10", "9", "8", "7", "6", "5", "4", "3S", "3", "2", "1"}

    def test_anaste_level6_salary_pre2025(self) -> None:
        """Level 6 base salary before 2025-08-01 = 1604.06 EUR (Art. 69)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        lv = next(x for x in ccnl.levels if x.code == "6")
        assert lv.base_salary.value_at(date(2024, 1, 1)) == Decimal("1604.06")

    def test_anaste_level6_salary_2025(self) -> None:
        """Level 6 base salary from 2025-08-01 = 1696.37 EUR (CCNL rinnovo)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        lv = next(x for x in ccnl.levels if x.code == "6")
        assert lv.base_salary.value_at(date(2025, 8, 1)) == Decimal("1696.37")

    def test_anaste_level_ordering(self) -> None:
        """Lowest order is level 1 (order=1), highest is Q (order=12)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_anaste_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only, Art. 74)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        assert ccnl.parameters.additional_months.value_at(date(2025, 8, 1)) == Decimal(
            13
        )

    def test_anaste_hourly_divisor(self) -> None:
        """Hourly divisor = 164 (38h/week, Art. 72)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        assert ccnl.parameters.hourly_divisor.value_at(date(2025, 8, 1)) == Decimal(164)

    def test_anaste_level_q_fixed_allowance(self) -> None:
        """Level Q has indennita di funzione 77.47 EUR/month (Art. 70)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        lv_q = next(x for x in ccnl.levels if x.code == "Q")
        assert len(lv_q.fixed_allowances) == 1
        fa = lv_q.fixed_allowances[0]
        assert fa.code == "INDENNITA_FUNZIONE"
        assert fa.monthly.value_at(date(2025, 8, 1)) == Decimal("77.47")

    def test_anaste_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_anaste_seniority_cadence(self) -> None:
        """Seniority: cadence 36 months, max 10 scatti (Art. 73)."""
        ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 36
        assert si.maximum_count == 10


class TestLoadScuoleMaternieFism:
    """Tests for CCNL Scuole Materne FISM (T271)."""

    def test_fism_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("scuole-materne-fism")
        assert ccnl.meta.ccnl_id == "scuole-materne-fism"
        assert ccnl.meta.cnel_code == "T271"

    def test_fism_has_8_levels(self) -> None:
        """Contract has exactly 8 levels with codes I through VIII."""
        ccnl = load_ccnl("scuole-materne-fism")
        assert len(ccnl.levels) == 8
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"I", "II", "III", "IV", "V", "VI", "VII", "VIII"}

    def test_fism_level5_salary_2023(self) -> None:
        """Level V base salary at first tranche (2023-09-01) = 1564.87 EUR."""
        ccnl = load_ccnl("scuole-materne-fism")
        lv = next(x for x in ccnl.levels if x.code == "V")
        assert lv.base_salary.value_at(date(2023, 9, 1)) == Decimal("1564.87")

    def test_fism_level5_salary_2026(self) -> None:
        """Level V base salary from 2026-09-01 (accord tranche) = 1679.76 EUR."""
        ccnl = load_ccnl("scuole-materne-fism")
        lv = next(x for x in ccnl.levels if x.code == "V")
        assert lv.base_salary.value_at(date(2026, 9, 1)) == Decimal("1679.76")

    def test_fism_level_ordering(self) -> None:
        """Lowest order is I (1), highest order is VIII (8)."""
        ccnl = load_ccnl("scuole-materne-fism")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "I"
        assert by_order[-1].code == "VIII"

    def test_fism_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only, Art. 49)."""
        ccnl = load_ccnl("scuole-materne-fism")
        assert ccnl.parameters.additional_months.value_at(date(2026, 9, 1)) == Decimal(
            13
        )

    def test_fism_hourly_divisor(self) -> None:
        """Hourly divisor = 160 (37h/week, Art. 51)."""
        ccnl = load_ccnl("scuole-materne-fism")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 9, 1)) == Decimal(160)

    def test_fism_fixed_allowances_are_the_salario_di_anzianita(self) -> None:
        """Conglobated pay: the only allowance is art. 46, from 1 September 2025."""
        ccnl = load_ccnl("scuole-materne-fism")
        for lv in ccnl.levels:
            (allowance,) = lv.fixed_allowances
            assert allowance.code == "SALARIO_ANZIANITA_2025"
            assert not allowance.monthly.applies_on(date(2025, 8, 31))
            assert allowance.monthly.applies_on(date(2025, 9, 1))

    def test_fism_tax_sector(self) -> None:
        """Tax sector is terziario."""
        ccnl = load_ccnl("scuole-materne-fism")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_fism_seniority_frozen(self) -> None:
        """Seniority frozen: maximum_count=0 (historic scatti frozen, Arts. 44-46)."""
        ccnl = load_ccnl("scuole-materne-fism")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 1
        assert si.maximum_count == 0


class TestLoadOcchialiOcchialeriaIndustria:
    """Tests for D271 CCNL Occhiali e Occhialeria — Industria (ANFAO)."""

    def test_occhiali_loads(self) -> None:
        """Contract loads with correct id and CNEL code."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        assert ccnl.meta.ccnl_id == "occhiali-occhialeria-industria"
        assert ccnl.meta.cnel_code == "D271"

    def test_occhiali_has_10_levels(self) -> None:
        """Contract has exactly 10 levels with correct codes."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        assert len(ccnl.levels) == 10
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "3S", "4", "4S", "5", "5S", "6", "Q"}

    def test_occhiali_level4_salary_2023(self) -> None:
        """Level 4 tabular minimum at 01/05/2023 first tranche = 1887.96."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2023, 5, 1)) == Decimal("1887.96")

    def test_occhiali_level4_salary_2026(self) -> None:
        """Level 4 tabular minimum at 01/03/2026 renewal tranche = 2042.96."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        lv = next(lv for lv in ccnl.levels if lv.code == "4")
        assert lv.base_salary.value_at(date(2026, 3, 1)) == Decimal("2042.96")

    def test_occhiali_level_ordering(self) -> None:
        """Q is highest order (10); level 1 is lowest order (1)."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "Q"

    def test_occhiali_additional_months(self) -> None:
        """Additional months = 13 (tredicesima only)."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        assert ccnl.parameters.additional_months.value_at(date(2026, 3, 1)) == Decimal(
            13
        )

    def test_occhiali_hourly_divisor(self) -> None:
        """Hourly divisor = 173 (standard 40h/week)."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        assert ccnl.parameters.hourly_divisor.value_at(date(2026, 3, 1)) == Decimal(173)

    def test_occhiali_level_q_fixed_allowance(self) -> None:
        """Level Q carries INDENNITA_FUNZIONE allowance of 82.63 EUR/month."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        lv = next(lv for lv in ccnl.levels if lv.code == "Q")
        assert len(lv.fixed_allowances) == 1
        fa = lv.fixed_allowances[0]
        assert fa.code == "INDENNITA_FUNZIONE"
        assert fa.monthly.value_at(date(2026, 3, 1)) == Decimal("82.63")

    def test_occhiali_tax_sector(self) -> None:
        """Tax sector is industria."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        assert ccnl.meta.tax_sector == TaxSector.INDUSTRIA

    def test_occhiali_seniority_cadence(self) -> None:
        """Seniority: 24-month cadence, max 5 scatti biennali."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_occhiali_non_q_no_fixed_allowances(self) -> None:
        """Conglobated model: all non-Q levels have no fixed allowances."""
        ccnl = load_ccnl("occhiali-occhialeria-industria")
        for lv in ccnl.levels:
            if lv.code != "Q":
                assert lv.fixed_allowances == ()


def test_metalmeccanica_cooperative_apprenticeship_durations() -> None:
    """Allegato 10 art. 8: 85/90/95% in thirds of 36, 30 or 24 months."""
    tracks = {t.name: t for t in load_ccnl("metalmeccanica-cooperative").apprenticeship}
    for months in (36, 30, 24):
        third = months // 3
        periods = tracks[f"professionalizzante_{months}"].periods
        assert [(p.months_from, getattr(p, "percentage", None)) for p in periods] == [
            (0, Decimal("0.85")),
            (third, Decimal("0.90")),
            (2 * third, Decimal("0.95")),
            (months, Decimal("1.00")),
        ]


def test_scuole_materne_fism_apprenticeship_by_duration() -> None:
    """Art. 27.8: 90/95/100% by semester (I-III), 90% then 100% (IV-VIII)."""
    tracks = {t.name: t for t in load_ccnl("scuole-materne-fism").apprenticeship}
    short, long_ = tracks["livelli_1_3"], tracks["livelli_4_8"]
    assert short.destination_levels == ("I", "II", "III")
    assert [getattr(p, "percentage", None) for p in short.periods] == [
        Decimal("0.90"),
        Decimal("0.95"),
        Decimal("1.00"),
    ]
    assert [(p.months_from, getattr(p, "percentage", None)) for p in long_.periods] == [
        (0, Decimal("0.90")),
        (12, Decimal("1.00")),
    ]


def test_acconciatura_group_1_reduced_track() -> None:
    """Tabella 3 (renewal of 20 May 2024 p. 6): 100% from the ninth semester."""
    tracks = {
        t.name: t
        for t in load_ccnl("acconciatura-estetica-confartigianato").apprenticeship
    }
    reduced = [
        (p.months_from, getattr(p, "percentage", None))
        for p in tracks["gruppo_1_ridotto"].periods
    ]
    assert reduced[-1] == (48, Decimal("1.00"))
    ordinary = [
        (p.months_from, getattr(p, "percentage", None))
        for p in tracks["gruppo_1"].periods
    ]
    assert (48, Decimal("0.95")) in ordinary


def test_informatica_apprenticeship_durations_and_seniority() -> None:
    """Art. 30 (2018): 36, 30 or 24 months in thirds; no increment accrues."""
    ccnl = load_ccnl("informatica-pmi-unimatica")
    tracks = {t.name: t for t in ccnl.apprenticeship}
    for months in (36, 30, 24):
        third = months // 3
        periods = tracks[f"professionalizzante_{months}"].periods
        assert [p.months_from for p in periods] == [0, third, 2 * third]
    amount = ccnl.parameters.seniority_increments.apprentice_amount
    assert amount is not None
    assert amount.value_at(date(2026, 6, 1)) == Decimal("0.00")


def test_fiaip_specialist_apprenticeship_track() -> None:
    """Art. 55: 24 months from V to III; Art. 40: two levels below, then one."""
    ccnl = load_ccnl("agenti-immobiliari-fiaip")
    track = ccnl.apprenticeship_track_named("III-mediazione-specialistico-24m")
    assert list(track.destination_levels) == ["III"]
    steps = [
        (p.months_from, p.levels_below)
        for p in track.periods
        if isinstance(p, UnderClassificationPeriod)
    ]
    assert steps == [(0, 2), (12, 1), (24, 0)]
    assert len(ccnl.apprenticeship_tracks_for("III")) == 2


def test_comunicazione_function_allowance_from_august_2026() -> None:
    """Nota a verbale 15 July 2026: separate from 1 August, nothing before."""
    level = load_ccnl("comunicazione-artigianato-confartigianato").level_by_code("1A")
    (allowance,) = [a for a in level.fixed_allowances if a.code == "IND_FUN"]
    assert allowance.monthly.value_at(date(2026, 7, 31)) == Decimal("0.00")
    assert allowance.monthly.value_at(date(2026, 8, 1)) == Decimal("51.65")
