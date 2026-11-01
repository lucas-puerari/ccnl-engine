"""Bundled CCNL data files load with their expected values.

Covers Turismo Confcommercio, Edilizia Ance, Cooperative Sociali.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.agreement.facade import CCNL, TaxSector
from ccnl_engine.apprenticeship.models import (
    ApprenticeshipPercentage,
)
from ccnl_engine.catalog.loaders import load_ccnl

# ---------------------------------------------------------------------------
# CCNL Edilizia ANCE (F012), operai and impiegati files
# ---------------------------------------------------------------------------

_APPRENTICE_PCTS = [
    Decimal("0.72"),
    Decimal("0.72"),
    Decimal("0.78"),
    Decimal("0.78"),
    Decimal("0.85"),
    Decimal("0.90"),
    Decimal("1.00"),
]


class TestLoadEdiliziaAnce:
    """Structural and data-integrity tests for edilizia-ance.json (operai)."""

    def test_edilizia_loads(self) -> None:
        """load_ccnl loads the operai JSON and returns the expected identifiers."""
        ccnl = load_ccnl("edilizia-ance")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.ccnl_id == "edilizia-ance"
        assert ccnl.meta.cnel_code == "F012"
        assert ccnl.meta.tax_sector == TaxSector.EDILIZIA

    def test_edilizia_has_four_operai_levels(self) -> None:
        """The operai file holds levels 1-4, in order."""
        ccnl = load_ccnl("edilizia-ance")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert [lv.code for lv in by_order] == ["1", "2", "3", "4"]

    def test_edilizia_level3_salary(self) -> None:
        """Level 3 paga base: EUR 1387.56 from 2025-02-01, 1452.56 from 2026-03-01."""
        ccnl = load_ccnl("edilizia-ance")
        lv3 = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv3.base_salary.value_at(date(2025, 2, 1)) == Decimal("1387.56")
        assert lv3.base_salary.value_at(date(2026, 3, 1)) == Decimal("1452.56")

    def test_edilizia_twelve_months(self) -> None:
        """Operai are paid twelve months: the gratifica goes through the Cassa Edile."""
        ccnl = load_ccnl("edilizia-ance")
        value = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert value == Decimal(12)

    def test_edilizia_hourly_divisor(self) -> None:
        """Hourly divisor must be 173 (40 h/week)."""
        ccnl = load_ccnl("edilizia-ance")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_edilizia_contingenza_and_edr(self) -> None:
        """Every operai level carries the contingenza and the EDR."""
        ccnl = load_ccnl("edilizia-ance")
        for level in ccnl.levels:
            codes = [a.code for a in level.fixed_allowances]
            assert codes == ["CONTINGENZA", "EDR"], level.code

    def test_edilizia_operai_have_no_scatti(self) -> None:
        """Operai accrue no seniority increments."""
        ccnl = load_ccnl("edilizia-ance")
        assert ccnl.parameters.seniority_increments.maximum_count == 0

    def test_edilizia_apprenticeship_standard_percentage(self) -> None:
        """Standard track: levels 2-4, 72/72/78/78/85/90% then 100%."""
        ccnl = load_ccnl("edilizia-ance")
        (track,) = (t for t in ccnl.apprenticeship if t.name == "standard")
        assert isinstance(track, ApprenticeshipPercentage)
        assert track.name == "standard"
        assert set(track.destination_levels) == {"2", "3", "4"}
        assert [p.percentage for p in track.periods] == _APPRENTICE_PCTS
        assert track.periods[-1].months_until is None

    def test_edilizia_apprenticeship_artistic_works(self) -> None:
        """Lavorazioni artistiche: 48 months, semesters 7 and 8 at 90%."""
        ccnl = load_ccnl("edilizia-ance")
        (track,) = (
            t for t in ccnl.apprenticeship if t.name == "lavorazioni_artistiche"
        )
        assert isinstance(track, ApprenticeshipPercentage)
        assert [p.percentage for p in track.periods] == [
            *_APPRENTICE_PCTS[:-1],
            Decimal("0.90"),
            Decimal("0.90"),
            Decimal(1),
        ]
        assert track.periods[-2].months_until == 48


class TestLoadEdiliziaAnceImpiegati:
    """Structural and data-integrity tests for edilizia-ance-impiegati.json."""

    def test_edilizia_impiegati_loads(self) -> None:
        """load_ccnl loads the impiegati JSON with the shared CNEL code F012."""
        ccnl = load_ccnl("edilizia-ance-impiegati")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.ccnl_id == "edilizia-ance-impiegati"
        assert ccnl.meta.cnel_code == "F012"
        assert ccnl.meta.tax_sector == TaxSector.EDILIZIA

    def test_edilizia_impiegati_has_seven_levels(self) -> None:
        """The impiegati file holds levels 1-7, in order, level 7 the quadri."""
        ccnl = load_ccnl("edilizia-ance-impiegati")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert [lv.code for lv in by_order] == ["1", "2", "3", "4", "5", "6", "7"]
        assert "QUADRI_FUNZIONE" in {a.code for a in by_order[-1].fixed_allowances}

    def test_edilizia_impiegati_level3_salary(self) -> None:
        """Level 3 stipendio: EUR 1387.56 from 2025-02-01, 1452.56 from 2026-03-01."""
        ccnl = load_ccnl("edilizia-ance-impiegati")
        lv3 = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv3.base_salary.value_at(date(2025, 2, 1)) == Decimal("1387.56")
        assert lv3.base_salary.value_at(date(2026, 3, 1)) == Decimal("1452.56")

    def test_edilizia_impiegati_fourteen_months(self) -> None:
        """Impiegati: tredicesima (Art. 63) and premio annuo (Art. 64)."""
        ccnl = load_ccnl("edilizia-ance-impiegati")
        value = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert value == Decimal(14)

    def test_edilizia_impiegati_seniority_cadence(self) -> None:
        """Seniority increments must be biennale (24 months), max 5 scatti."""
        ccnl = load_ccnl("edilizia-ance-impiegati")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_edilizia_impiegati_apprenticeship_standard_percentage(self) -> None:
        """Apprenticeship: 1 track, levels 2-7, 72/72/78/78/85/90% then 100%.

        Since CNCE n.660/2019 the CCNL abolished under-classification and uses
        percentage-based pay on the destination level over 36 months. Level 1
        is not eligible.
        """
        ccnl = load_ccnl("edilizia-ance-impiegati")
        (track,) = ccnl.apprenticeship
        assert isinstance(track, ApprenticeshipPercentage)
        assert set(track.destination_levels) == {"2", "3", "4", "5", "6", "7"}
        assert [p.percentage for p in track.periods] == _APPRENTICE_PCTS
        assert track.periods[-1].months_until is None


# ---------------------------------------------------------------------------
# CCNL Cooperative Sociali — T151
# ---------------------------------------------------------------------------


class TestLoadCooperativeSociali:
    """Unit tests for CCNL Cooperative Sociali (T151) data file."""

    def test_cooperative_sociali_loads(self) -> None:
        """File loads as valid CCNL with correct id and CNEL code T151."""
        ccnl = load_ccnl("cooperative-sociali")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.ccnl_id == "cooperative-sociali"
        assert ccnl.meta.cnel_code == "T151"

    def test_cooperative_sociali_has_16_levels(self) -> None:
        """Contract must contain exactly 16 levels (13 base + 3 Quadro)."""
        ccnl = load_ccnl("cooperative-sociali")
        assert len(ccnl.levels) == 16
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {
            "A1",
            "A2",
            "B",
            "C1",
            "C2",
            "C3",
            "D1",
            "D2",
            "D3",
            "E1",
            "E2",
            "E2Q",
            "F1",
            "F1Q",
            "F2",
            "F2Q",
        }

    def test_cooperative_sociali_level_d2_salary_feb2024(self) -> None:
        """D2 conglobated minimum at first tranche (Feb 2024) must be 1660.99."""
        ccnl = load_ccnl("cooperative-sociali")
        d2 = next(lv for lv in ccnl.levels if lv.code == "D2")
        assert d2.base_salary.value_at(date(2024, 2, 1)) == Decimal("1660.99")

    def test_cooperative_sociali_level_d2_salary_oct2024(self) -> None:
        """D2 conglobated minimum at second tranche (Oct 2024) must be 1694.41."""
        ccnl = load_ccnl("cooperative-sociali")
        d2 = next(lv for lv in ccnl.levels if lv.code == "D2")
        assert d2.base_salary.value_at(date(2024, 10, 1)) == Decimal("1694.41")

    def test_cooperative_sociali_level_ordering(self) -> None:
        """F2Q must have the highest order; A1 the lowest."""
        ccnl = load_ccnl("cooperative-sociali")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "A1"
        assert by_order[-1].code == "F2Q"

    def test_cooperative_sociali_additional_months(self) -> None:
        """13 months before 2025, 13.5 from January 2025 (quattordicesima)."""
        ccnl = load_ccnl("cooperative-sociali")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2024, 6, 1)) == Decimal(13)
        assert am.value_at(date(2025, 1, 1)) == Decimal("13.5")

    def test_cooperative_sociali_hourly_divisor(self) -> None:
        """Hourly divisor must be 165 (38 h/week, art. 75 CCNL)."""
        ccnl = load_ccnl("cooperative-sociali")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(165)

    def test_cooperative_sociali_q_levels_funzione_allowance(self) -> None:
        """E2Q/F1Q/F2Q must carry exactly one IDF fixed allowance each."""
        ccnl = load_ccnl("cooperative-sociali")
        expected = {"E2Q": "77.47", "F1Q": "154.94", "F2Q": "232.41"}
        for code, amount in expected.items():
            lv = next(lvl for lvl in ccnl.levels if lvl.code == code)
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "IND_FUN"
            val = lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1))
            assert val == Decimal(amount)

    def test_cooperative_sociali_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO."""
        ccnl = load_ccnl("cooperative-sociali")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_cooperative_sociali_seniority_cadence(self) -> None:
        """Seniority increments: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("cooperative-sociali")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_cooperative_sociali_apprenticeship_three_tracks(self) -> None:
        """Three tracks by duration: 18m (A2, C2 OSS), 24m (B/C), 36m (D/E)."""
        ccnl = load_ccnl("cooperative-sociali")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        # 18m track: A2 and the OSS position C2 (Art. 28 N.3), split at 9m
        t18 = by_name["professionalizzante_18m"]
        assert t18.destination_levels == ("A2", "C2")
        assert t18.periods[0].months_until == 9
        assert t18.periods[0].percentage == Decimal("0.85")  # type: ignore[union-attr]
        # 24m track: B, C1, C3
        t24 = by_name["professionalizzante_24m"]
        assert set(t24.destination_levels) == {"B", "C1", "C3"}
        assert t24.periods[0].months_until == 12
        # 36m track: D and E levels
        t36 = by_name["professionalizzante_36m"]
        assert set(t36.destination_levels) == {"D1", "D2", "D3", "E1", "E2"}
        assert t36.periods[0].months_until == 18
        assert t36.periods[-1].months_until is None
