"""Bundled CCNL data files load with their expected values.

Covers Turismo Confcommercio, Edilizia Ance, Cooperative Sociali.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.apprenticeship import (
    ApprenticeshipPercentage,
)
from ccnl_engine.contract.domain.identity import CCNL, TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl

# ---------------------------------------------------------------------------
# CCNL Turismo — Confcommercio (H052)
# ---------------------------------------------------------------------------


class TestLoadTurismoConfcommercio:
    """Structural and data-integrity tests for turismo-confcommercio.json."""

    def test_turismo_loads(self) -> None:
        """File must parse without errors; id and CNEL code must match."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert ccnl.meta.ccnl_id == "turismo-confcommercio"
        assert ccnl.meta.cnel_code == "H052"

    def test_turismo_has_ten_levels(self) -> None:
        """CCNL Turismo defines exactly 10 classification levels."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert len(ccnl.levels) == 10
        assert {lv.code for lv in ccnl.levels} == {
            "QA",
            "QB",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6S",
            "6",
            "7",
        }

    def test_turismo_level3_salary_july_2024(self) -> None:
        """Level 3 base salary from 2024-07-01 must be 1717.55 (first tranche)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        l3 = next(lv for lv in ccnl.levels if lv.code == "3")
        assert l3.base_salary.value_at(date(2024, 7, 1)) == Decimal("1717.55")

    def test_turismo_level3_salary_june_2025(self) -> None:
        """Level 3 base salary from 2025-06-01 must be 1759.94 (second tranche)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        l3 = next(lv for lv in ccnl.levels if lv.code == "3")
        assert l3.base_salary.value_at(date(2025, 6, 1)) == Decimal("1759.94")

    def test_turismo_level_ordering(self) -> None:
        """QA must have the highest order; level 7 the lowest."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "7"
        assert by_order[-1].code == "QA"

    def test_turismo_seniority_cadence(self) -> None:
        """Scatti are quadriennali (48 months), maximum 6."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 48
        assert si.maximum_count == 6

    def test_turismo_fourteen_months(self) -> None:
        """Contract has 14 monthly salaries per year (tredicesima + quattordicesima)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        value = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert value == Decimal(14)

    def test_turismo_no_fixed_allowances(self) -> None:
        """All levels have no fixed_allowances (minimum conglobated in base_salary)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        for level in ccnl.levels:
            assert level.fixed_allowances == (), (
                f"Level {level.code} should have no fixed_allowances"
            )

    def test_turismo_apprenticeship_percentage(self) -> None:
        """Apprenticeship uses percentage model: 80/85/90/100% (rinnovo 2024).

        The 36-month track covers levels 5, 4, 3, 2, 6S (4 periods including
        open-ended 100% at month 36+); the 24-month track covers level 6.
        """
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert isinstance(ccnl.apprenticeship[0], ApprenticeshipPercentage)
        assert ccnl.apprenticeship[0].destination_levels == ("5", "4", "3", "2", "6S")
        periods = ccnl.apprenticeship[0].periods
        assert len(periods) == 4
        assert periods[0].percentage == Decimal("0.80")
        assert periods[1].percentage == Decimal("0.85")
        assert periods[2].percentage == Decimal("0.90")
        assert periods[3].percentage == Decimal("1.00")
        assert periods[3].months_until is None

    def test_turismo_hourly_divisor(self) -> None:
        """Hourly divisor must be 172 (40 h/week standard for turismo)."""
        ccnl = load_ccnl("turismo-confcommercio.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(172)


# ---------------------------------------------------------------------------
# CCNL Edilizia — ANCE (F012)
# ---------------------------------------------------------------------------


class TestLoadEdiliziaAnce:
    """Structural and data-integrity tests for edilizia-ance.json."""

    def test_edilizia_loads(self) -> None:
        """load_ccnl loads the edilizia JSON and returns the expected identifiers."""
        ccnl = load_ccnl("edilizia-ance.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.ccnl_id == "edilizia-ance"
        assert ccnl.meta.cnel_code == "F012"

    def test_edilizia_has_seven_levels(self) -> None:
        """Edilizia ANCE CCNL must contain exactly 7 classification levels."""
        ccnl = load_ccnl("edilizia-ance.json")
        assert len(ccnl.levels) == 7
        codes = {lv.code for lv in ccnl.levels}
        assert codes == {"1", "2", "3", "4", "5", "6", "7"}

    def test_edilizia_level3_salary_feb_2025(self) -> None:
        """Level 3 conglobated minimum on 2025-02-01 must be EUR 1917.05."""
        ccnl = load_ccnl("edilizia-ance.json")
        lv3 = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv3.base_salary.value_at(date(2025, 2, 1)) == Decimal("1917.05")

    def test_edilizia_level3_salary_march_2026(self) -> None:
        """Level 3 conglobated minimum on 2026-03-01 must be EUR 1982.05."""
        ccnl = load_ccnl("edilizia-ance.json")
        lv3 = next(lv for lv in ccnl.levels if lv.code == "3")
        assert lv3.base_salary.value_at(date(2026, 3, 1)) == Decimal("1982.05")

    def test_edilizia_level_ordering(self) -> None:
        """Level 7 must have the highest order; level 1 the lowest."""
        ccnl = load_ccnl("edilizia-ance.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "1"
        assert by_order[-1].code == "7"

    def test_edilizia_thirteen_months(self) -> None:
        """Contract must have 13 monthly salaries per year (gratifica natalizia)."""
        ccnl = load_ccnl("edilizia-ance.json")
        value = ccnl.parameters.additional_months.value_at(date(2026, 1, 1))
        assert value == Decimal(13)

    def test_edilizia_hourly_divisor(self) -> None:
        """Hourly divisor must be 173 (40 h/week, verified from official tariff)."""
        ccnl = load_ccnl("edilizia-ance.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(173)

    def test_edilizia_no_fixed_allowances(self) -> None:
        """All levels have no fixed_allowances (minimum conglobated in base_salary)."""
        ccnl = load_ccnl("edilizia-ance.json")
        for level in ccnl.levels:
            assert level.fixed_allowances == (), (
                f"Level {level.code} should have no fixed_allowances"
            )

    def test_edilizia_tax_sector(self) -> None:
        """CCNL must declare tax_sector EDILIZIA."""
        ccnl = load_ccnl("edilizia-ance.json")
        assert ccnl.meta.tax_sector == TaxSector.EDILIZIA

    def test_edilizia_seniority_cadence(self) -> None:
        """Seniority increments must be biennale (24 months), max 5 scatti."""
        ccnl = load_ccnl("edilizia-ance.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_edilizia_apprenticeship_standard_percentage(self) -> None:
        """Apprenticeship: 1 track, levels 2-7, percentage 72/72/78/78/85/90/100%.

        Since CNCE n.660/2019 the CCNL abolished under-classification and uses
        percentage-based pay on the destination level for all levels 2-7 over 36 months
        (6 semesters at 72/72/78/78/85/90%, then 100%). Level 1 is not eligible.
        """
        ccnl = load_ccnl("edilizia-ance.json")
        assert len(ccnl.apprenticeship) == 1
        track = ccnl.apprenticeship[0]
        assert isinstance(track, ApprenticeshipPercentage)
        assert track.name == "standard"
        assert set(track.destination_levels) == {"2", "3", "4", "5", "6", "7"}
        pcts = [p.percentage for p in track.periods]
        assert pcts[:6] == [
            Decimal("0.72"),
            Decimal("0.72"),
            Decimal("0.78"),
            Decimal("0.78"),
            Decimal("0.85"),
            Decimal("0.90"),
        ]
        assert pcts[-1] == Decimal("1.00")
        assert track.periods[-1].months_until is None


# ---------------------------------------------------------------------------
# CCNL Cooperative Sociali — T151
# ---------------------------------------------------------------------------


class TestLoadCooperativeSociali:
    """Unit tests for CCNL Cooperative Sociali (T151) data file."""

    def test_cooperative_sociali_loads(self) -> None:
        """File loads as valid CCNL with correct id and CNEL code T151."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.ccnl_id == "cooperative-sociali"
        assert ccnl.meta.cnel_code == "T151"

    def test_cooperative_sociali_has_16_levels(self) -> None:
        """Contract must contain exactly 16 levels (13 base + 3 Quadro)."""
        ccnl = load_ccnl("cooperative-sociali.json")
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
        ccnl = load_ccnl("cooperative-sociali.json")
        d2 = next(lv for lv in ccnl.levels if lv.code == "D2")
        assert d2.base_salary.value_at(date(2024, 2, 1)) == Decimal("1660.99")

    def test_cooperative_sociali_level_d2_salary_oct2024(self) -> None:
        """D2 conglobated minimum at second tranche (Oct 2024) must be 1694.41."""
        ccnl = load_ccnl("cooperative-sociali.json")
        d2 = next(lv for lv in ccnl.levels if lv.code == "D2")
        assert d2.base_salary.value_at(date(2024, 10, 1)) == Decimal("1694.41")

    def test_cooperative_sociali_level_ordering(self) -> None:
        """F2Q must have the highest order; A1 the lowest."""
        ccnl = load_ccnl("cooperative-sociali.json")
        by_order = sorted(ccnl.levels, key=lambda lv: lv.order)
        assert by_order[0].code == "A1"
        assert by_order[-1].code == "F2Q"

    def test_cooperative_sociali_additional_months(self) -> None:
        """13 months before 2025, 13.5 from January 2025 (quattordicesima)."""
        ccnl = load_ccnl("cooperative-sociali.json")
        am = ccnl.parameters.additional_months
        assert am.value_at(date(2024, 6, 1)) == Decimal(13)
        assert am.value_at(date(2025, 1, 1)) == Decimal("13.5")

    def test_cooperative_sociali_hourly_divisor(self) -> None:
        """Hourly divisor must be 165 (38 h/week, art. 75 CCNL)."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert ccnl.parameters.hourly_divisor.periods[0].value == Decimal(165)

    def test_cooperative_sociali_q_levels_funzione_allowance(self) -> None:
        """E2Q/F1Q/F2Q must carry exactly one IDF fixed allowance each."""
        ccnl = load_ccnl("cooperative-sociali.json")
        expected = {"E2Q": "77.47", "F1Q": "154.94", "F2Q": "232.41"}
        for code, amount in expected.items():
            lv = next(lvl for lvl in ccnl.levels if lvl.code == code)
            assert len(lv.fixed_allowances) == 1
            assert lv.fixed_allowances[0].code == "IND_FUN"
            val = lv.fixed_allowances[0].monthly.value_at(date(2026, 1, 1))
            assert val == Decimal(amount)

    def test_cooperative_sociali_tax_sector(self) -> None:
        """CCNL must declare tax_sector TERZIARIO."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert ccnl.meta.tax_sector == TaxSector.TERZIARIO

    def test_cooperative_sociali_seniority_cadence(self) -> None:
        """Seniority increments: biennale (24 months), maximum 5 scatti."""
        ccnl = load_ccnl("cooperative-sociali.json")
        si = ccnl.parameters.seniority_increments
        assert si.cadence_months == 24
        assert si.maximum_count == 5

    def test_cooperative_sociali_apprenticeship_three_tracks(self) -> None:
        """Three tracks by category duration: 18m (A2), 24m (B/C), 36m (D/E)."""
        ccnl = load_ccnl("cooperative-sociali.json")
        assert len(ccnl.apprenticeship) == 3
        by_name = {t.name: t for t in ccnl.apprenticeship}
        # 18m track: A2 only, split at 9m
        t18 = by_name["professionalizzante_18m"]
        assert t18.destination_levels == ("A2",)
        assert t18.periods[0].months_until == 9
        assert t18.periods[0].percentage == Decimal("0.85")  # type: ignore[union-attr]
        # 24m track: B, C1, C2, C3
        t24 = by_name["professionalizzante_24m"]
        assert set(t24.destination_levels) == {"B", "C1", "C2", "C3"}
        assert t24.periods[0].months_until == 12
        # 36m track: D and E levels
        t36 = by_name["professionalizzante_36m"]
        assert set(t36.destination_levels) == {"D1", "D2", "D3", "E1", "E2"}
        assert t36.periods[0].months_until == 18
        assert t36.periods[-1].months_until is None
