"""Tests for engine.irpef.

Covers irpef_gross(), work_income_deduction(), trattamento_integrativo(),
surtax_from_brackets(), and apply_sterilizzazione_detrazioni().

Every branch is tested: zero/negative income, each statutory band boundary,
4-decimal truncation, the 65 EUR increment, TI requisito logic, and surtax.
"""

from decimal import Decimal
from typing import Any

from ccnl_engine.engine.payroll.service.irpef import (
    apply_sterilizzazione_detrazioni,
    irpef_gross,
    surtax_from_brackets,
    trattamento_integrativo,
    work_income_deduction,
)
from ccnl_engine.engine.surtax.domain.rules import SurtaxBracket
from ccnl_engine.engine.tax.domain.rules import (
    SterilizzazioneDetrazioniRules,
    TrattamentoIntegrativoRules,
    YearRules,
)
from tests.helpers import make_year_rules

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_IRPEF_BRACKETS_2026: list[dict[str, Any]] = [
    {"up_to": "28000.00", "rate": "0.23"},
    {"up_to": "50000.00", "rate": "0.33"},
    {"up_to": None, "rate": "0.43"},
]


def _rules() -> YearRules:
    """Minimal YearRules with the 2026 IRPEF brackets.

    Returns:
        A YearRules instance with the 2026 bracket schedule.
    """
    return make_year_rules(brackets=_IRPEF_BRACKETS_2026)


# ---------------------------------------------------------------------------
# irpef_gross
# ---------------------------------------------------------------------------


class TestIrpefGross:
    """Unit tests for irpef_gross()."""

    def test_zero_income(self) -> None:
        """Zero income yields zero tax (early return branch)."""
        assert irpef_gross(Decimal(0), _rules()) == Decimal("0.00")

    def test_negative_income(self) -> None:
        """Negative income yields zero tax (early return branch)."""
        assert irpef_gross(Decimal(-100), _rules()) == Decimal("0.00")

    def test_income_in_first_bracket(self) -> None:
        """Income fully inside the first bracket: only 23% applies.

        10,000 * 0.23 = 2,300.00. The break path (taxable_income <= prev_limit)
        is exercised on the second bracket iteration.
        """
        result = irpef_gross(Decimal("10000.00"), _rules())
        assert result == Decimal("2300.00")

    def test_income_at_first_bracket_boundary(self) -> None:
        """Income exactly at the first bracket boundary (28,000)."""
        result = irpef_gross(Decimal("28000.00"), _rules())
        assert result == Decimal("6440.00")  # 28000 * 0.23

    def test_income_spanning_two_brackets(self) -> None:
        """Income in the second bracket: 23% on first 28k + 33% on excess.

        35,000: 28,000 * 0.23 = 6,440 + 7,000 * 0.33 = 2,310 = 8,750.
        The unbounded bracket branch (taxable_income > prev_limit = False) is
        exercised on the third iteration.
        """
        result = irpef_gross(Decimal("35000.00"), _rules())
        assert result == Decimal("8750.00")

    def test_income_in_third_bracket(self) -> None:
        """Income above 50k: all three brackets apply.

        60,000:
          28,000 * 0.23 = 6,440.00
          22,000 * 0.33 = 7,260.00
          10,000 * 0.43 = 4,300.00
          Total = 18,000.00
        """
        result = irpef_gross(Decimal("60000.00"), _rules())
        assert result == Decimal("18000.00")


# ---------------------------------------------------------------------------
# work_income_deduction — Art. 13 co. 1 TUIR statutory formula (2026)
# Source: AdE circolare 4/E/2025, p. 6; truncation per Art. 13 co. 6.
# ---------------------------------------------------------------------------


class TestWorkIncomeDeduction:
    """Unit tests for work_income_deduction() using the correct 2026 formula."""

    def test_zero_income(self) -> None:
        """Zero income returns zero deduction (early return branch)."""
        assert work_income_deduction(Decimal(0)) == Decimal("0.00")

    def test_negative_income(self) -> None:
        """Negative income returns zero deduction."""
        assert work_income_deduction(Decimal(-1)) == Decimal("0.00")

    def test_income_below_lo_threshold(self) -> None:
        """Income < 15 000: flat deduction of EUR 1 955 (REVIEW.md R12 row 1)."""
        assert work_income_deduction(Decimal(10000)) == Decimal("1955.00")

    def test_income_at_lo_threshold(self) -> None:
        """Income exactly at 15 000: flat deduction EUR 1 955 (REVIEW.md R12)."""
        assert work_income_deduction(Decimal(15000)) == Decimal("1955.00")

    def test_income_in_mid_band_no_increment(self) -> None:
        """Income 20 000 in 15 000-28 000 band, no 65 EUR increment.

        ratio = trunc4((28000-20000)/13000) = trunc4(0.615384...) = 0.6153
        deduction = 1910 + 1190 * 0.6153 = 1910 + 732.207 = 2642.21
        Expected 2642.21 (REVIEW.md R12 row 3).
        """
        assert work_income_deduction(Decimal(20000)) == Decimal("2642.21")

    def test_income_at_mid_threshold_with_increment(self) -> None:
        """Income exactly at 28 000 (mid boundary): 1910 + 0 + 65 = 1975.

        28 000 falls in 25 001-35 000 so the 65 EUR increment applies.
        Expected 1975.00 (REVIEW.md R12 row 4).
        """
        assert work_income_deduction(Decimal(28000)) == Decimal("1975.00")

    def test_income_in_upper_band_with_increment(self) -> None:
        """Income 30 000 in 28 000-50 000 band, 65 EUR increment applies.

        ratio = trunc4((50000-30000)/22000) = trunc4(0.909090...) = 0.9090
        deduction = 1910 * 0.9090 = 1736.19; +65 = 1801.19
        Expected 1801.19 (REVIEW.md R12 row 5).
        """
        assert work_income_deduction(Decimal(30000)) == Decimal("1801.19")

    def test_income_in_upper_band_no_increment(self) -> None:
        """Income 40 000 in 28 000-50 000 band, beyond 35 000 (no increment).

        ratio = trunc4((50000-40000)/22000) = trunc4(0.454545...) = 0.4545
        deduction = 1910 * 0.4545 = 868.095 → 868.10 (rounded to 2 dp).
        """
        assert work_income_deduction(Decimal(40000)) == Decimal("868.10")

    def test_income_at_high_threshold(self) -> None:
        """Income exactly at 50 000: deduction is zero (boundary on _DETR_HIGH)."""
        assert work_income_deduction(Decimal(50000)) == Decimal("0.00")

    def test_income_above_high_threshold(self) -> None:
        """Income > 50 000: zero deduction."""
        assert work_income_deduction(Decimal(55000)) == Decimal("0.00")

    def test_increment_lower_boundary(self) -> None:
        """Income exactly at 25 000 is NOT in increment range (must be > 25 000)."""
        # ratio = trunc4((28000-25000)/13000) = trunc4(0.230769...) = 0.2307
        # deduction = 1910 + 1190 * 0.2307 = 1910 + 274.533 = 2184.53
        assert work_income_deduction(Decimal(25000)) == Decimal("2184.53")

    def test_increment_just_above_lower_boundary(self) -> None:
        """Income 25 001 is in increment range: 65 EUR added."""
        # ratio = trunc4((28000-25001)/13000) = trunc4(0.230692...) = 0.2306
        # deduction = 1910 + 1190 * 0.2306 + 65 = 1910 + 274.414 + 65 = 2249.41
        assert work_income_deduction(Decimal(25001)) == Decimal("2249.41")

    def test_increment_upper_boundary(self) -> None:
        """Income exactly at 35 000 is in increment range (inclusive)."""
        # In 28 000-50 000 band: ratio = trunc4((50000-35000)/22000)
        # = trunc4(0.681818...) = 0.6818
        # deduction = 1910 * 0.6818 + 65 = 1302.238 + 65 = 1367.24
        assert work_income_deduction(Decimal(35000)) == Decimal("1367.24")

    def test_increment_just_above_upper_boundary(self) -> None:
        """Income 35 001 is NOT in increment range: no 65 EUR."""
        # In 28 000-50 000 band: ratio = trunc4((50000-35001)/22000)
        # = trunc4(0.681772...) = 0.6817
        # deduction = 1910 * 0.6817 = 1302.047 → 1302.05
        assert work_income_deduction(Decimal(35001)) == Decimal("1302.05")


# ---------------------------------------------------------------------------
# trattamento_integrativo — Art. 1 D.L. 3/2020 as updated by L. 207/2024
# ---------------------------------------------------------------------------

_TI_RULES = TrattamentoIntegrativoRules(
    threshold_mid=Decimal(15000),
    threshold_upper=Decimal(28000),
    max_amount=Decimal(1200),
)


class TestTrattamentoIntegrativo:
    """Unit tests for trattamento_integrativo()."""

    # -- RC > 28 000 ----------------------------------------------------------

    def test_above_upper_threshold_zero(self) -> None:
        """RC > 28 000: bonus is always zero."""
        result = trattamento_integrativo(
            Decimal(30000),
            Decimal(5000),
            Decimal(1800),
            Decimal(1800),
            _TI_RULES,
        )
        assert result == Decimal("0.00")

    # -- RC ≤ 15 000 ----------------------------------------------------------

    def test_lower_band_bonus_granted(self) -> None:
        """RC=8300, IRPEF=1909, detr=1955 (full year): 1909 > 1955-75=1880.

        REVIEW.md R13: was returning zero instead of 1200.
        """
        result = trattamento_integrativo(
            Decimal(8300),
            Decimal(1909),
            Decimal(1955),
            Decimal(1955),
            _TI_RULES,
        )
        assert result == Decimal("1200.00")

    def test_lower_band_bonus_denied(self) -> None:
        """RC=10000, IRPEF=300, detr=1955: 300 ≤ 1880 → no bonus."""
        result = trattamento_integrativo(
            Decimal(10000),
            Decimal(300),
            Decimal(1955),
            Decimal(1955),
            _TI_RULES,
        )
        assert result == Decimal("0.00")

    def test_lower_band_exactly_at_threshold(self) -> None:
        """RC=10000, IRPEF=1880, detr=1955: 1880 = 1955-75 → not strictly >."""
        result = trattamento_integrativo(
            Decimal(10000),
            Decimal(1880),
            Decimal(1955),
            Decimal(1955),
            _TI_RULES,
        )
        assert result == Decimal("0.00")

    def test_lower_band_one_above_threshold(self) -> None:
        """RC=10000, IRPEF=1881: 1881 > 1955-75=1880 → bonus = 1200."""
        result = trattamento_integrativo(
            Decimal(10000),
            Decimal(1881),
            Decimal(1955),
            Decimal(1955),
            _TI_RULES,
        )
        assert result == Decimal("1200.00")

    # -- 15 000 < RC ≤ 28 000 -------------------------------------------------

    def test_mid_band_requisito_not_met(self) -> None:
        """RC=20000, IRPEF=4600, relevant=2642.21: IRPEF > deductions → 0.

        REVIEW.md R13: was returning 738.46 (wrong linear taper).
        """
        result = trattamento_integrativo(
            Decimal(20000),
            Decimal(4600),
            Decimal("2642.21"),
            Decimal("2642.21"),
            _TI_RULES,
        )
        assert result == Decimal("0.00")

    def test_mid_band_requisito_met_capped(self) -> None:
        """RC=20000, relevant_deductions > IRPEF by more than 1200: cap at 1200."""
        result = trattamento_integrativo(
            Decimal(20000),
            Decimal(1000),
            Decimal(2500),
            Decimal(3000),
            _TI_RULES,
        )
        assert result == Decimal("1200.00")

    def test_mid_band_requisito_met_partial(self) -> None:
        """RC=20000, relevant - IRPEF = 500: bonus = 500."""
        result = trattamento_integrativo(
            Decimal(20000),
            Decimal(2000),
            Decimal(2500),
            Decimal(2500),
            _TI_RULES,
        )
        assert result == Decimal("500.00")

    def test_mid_band_exactly_at_mid_threshold(self) -> None:
        """RC exactly at 15000 uses the lower-band check (≤ threshold_mid)."""
        # IRPEF=1909, detr=1955, corrective=75: 1909 > 1955-75=1880 → 1200
        result = trattamento_integrativo(
            Decimal(15000),
            Decimal(1909),
            Decimal(1955),
            Decimal(1955),
            _TI_RULES,
        )
        assert result == Decimal("1200.00")

    def test_mid_band_exactly_at_upper_threshold(self) -> None:
        """RC exactly at 28000: above upper → zero (> threshold_upper check)."""
        result = trattamento_integrativo(
            Decimal(28001),
            Decimal(3000),
            Decimal(2000),
            Decimal(2000),
            _TI_RULES,
        )
        assert result == Decimal("0.00")


# ---------------------------------------------------------------------------
# surtax_from_brackets
# ---------------------------------------------------------------------------


def _brackets(*specs: tuple[float | None, str]) -> list[SurtaxBracket]:
    """Build a SurtaxBracket list from (up_to, rate) tuples.

    Returns:
        A list of SurtaxBracket instances.
    """
    return [
        SurtaxBracket(
            up_to=Decimal(str(up_to)) if up_to is not None else None,
            rate=Decimal(rate),
        )
        for up_to, rate in specs
    ]


class TestSurtaxFromBrackets:
    """Unit tests for surtax_from_brackets()."""

    def test_zero_income(self) -> None:
        """Zero income → zero surtax."""
        bs = _brackets((None, "0.0123"))
        assert surtax_from_brackets(Decimal(0), bs) == Decimal("0.00")

    def test_negative_income(self) -> None:
        """Negative income → zero surtax."""
        bs = _brackets((None, "0.0123"))
        assert surtax_from_brackets(Decimal(-100), bs) == Decimal("0.00")

    def test_flat_rate(self) -> None:
        """Single unbounded bracket: flat rate on full income."""
        bs = _brackets((None, "0.0123"))
        # 30 000 * 1.23% = 369.00
        assert surtax_from_brackets(Decimal(30000), bs) == Decimal("369.00")

    def test_marginal_brackets(self) -> None:
        """Multiple brackets: marginal computation across slices.

        Lazio-style: 1.62% ≤15k, 2.68% ≤28k, 3.31% ≤50k, 3.33%+.
        Income 30000: 15000*1.62%+13000*2.68%+2000*3.31% = 657.60.
        """
        bs = _brackets(
            (15000, "0.0162"),
            (28000, "0.0268"),
            (50000, "0.0331"),
            (None, "0.0333"),
        )
        assert surtax_from_brackets(Decimal(30000), bs) == Decimal("657.60")

    def test_income_within_first_bracket(self) -> None:
        """Income inside the first finite bracket: 10000 * 1.67% = 167.00."""
        bs = _brackets((28000, "0.0167"), (50000, "0.0287"), (None, "0.0333"))
        assert surtax_from_brackets(Decimal(10000), bs) == Decimal("167.00")

    def test_income_exactly_at_bracket_boundary(self) -> None:
        """Income at a bracket upper bound: 15000 * 1.33% = 199.50."""
        bs = _brackets((15000, "0.0133"), (None, "0.0193"))
        assert surtax_from_brackets(Decimal(15000), bs) == Decimal("199.50")

    def test_income_above_all_brackets(self) -> None:
        """Income above all finite brackets: 28k*1.67%+22k*2.87%+10k*3.33% = 1432."""
        bs = _brackets((28000, "0.0167"), (50000, "0.0287"), (None, "0.0333"))
        assert surtax_from_brackets(Decimal(60000), bs) == Decimal("1432.00")

    def test_soglia_below_income_no_effect(self) -> None:
        """Soglia below taxable income: full income taxed. 20000 * 0.8% = 160.00."""
        bs = _brackets((None, "0.008"))
        assert surtax_from_brackets(Decimal(20000), bs, Decimal(5000)) == Decimal(
            "160.00"
        )

    def test_soglia_equal_to_income(self) -> None:
        """Income exactly equal to soglia → zero surtax."""
        bs = _brackets((None, "0.008"))
        assert surtax_from_brackets(Decimal(12000), bs, Decimal(12000)) == Decimal(
            "0.00"
        )

    def test_soglia_above_income(self) -> None:
        """Income below soglia → zero surtax."""
        bs = _brackets((None, "0.008"))
        assert surtax_from_brackets(Decimal(8000), bs, Decimal(12000)) == Decimal(
            "0.00"
        )

    def test_zero_rate_bracket(self) -> None:
        """A zero-rate flat bracket yields zero."""
        bs = _brackets((None, "0"))
        assert surtax_from_brackets(Decimal(30000), bs) == Decimal("0.00")


# ---------------------------------------------------------------------------
# apply_sterilizzazione_detrazioni (Art. 1 c. 3-4 L. 199/2025)
# ---------------------------------------------------------------------------

_STRD_RULES = SterilizzazioneDetrazioniRules(
    threshold=Decimal("200000.00"),
    reduction=Decimal("440.00"),
)


class TestApplySterilizzazioneDetrazioni:
    """Unit tests for apply_sterilizzazione_detrazioni()."""

    def test_below_threshold_unchanged(self) -> None:
        """Income at or below threshold: deductions returned unchanged."""
        work, fam = apply_sterilizzazione_detrazioni(
            Decimal(0), Decimal(1200), Decimal("200000.00"), _STRD_RULES
        )
        assert work == Decimal(0)
        assert fam == Decimal(1200)

    def test_above_threshold_family_reduced(self) -> None:
        """Income > 200k: family deduction reduced by 440 (work is already 0)."""
        work, fam = apply_sterilizzazione_detrazioni(
            Decimal(0), Decimal(1000), Decimal(250000), _STRD_RULES
        )
        assert work == Decimal("0.00")
        assert fam == Decimal("560.00")

    def test_above_threshold_family_floored_at_zero(self) -> None:
        """Reduction larger than family deduction: family deduction → 0."""
        work, fam = apply_sterilizzazione_detrazioni(
            Decimal(0), Decimal(300), Decimal(300000), _STRD_RULES
        )
        assert work == Decimal("0.00")
        assert fam == Decimal("0.00")

    def test_above_threshold_work_absorbed_first(self) -> None:
        """Reduction absorbed by work deduction before touching family."""
        # Hypothetical: work=200, family=500, reduction=440 → total=260
        # work=min(200, 260)=200, family=260-200=60
        work, fam = apply_sterilizzazione_detrazioni(
            Decimal(200), Decimal(500), Decimal(250000), _STRD_RULES
        )
        assert work == Decimal("200.00")
        assert fam == Decimal("60.00")

    def test_rules_none_unchanged(self) -> None:
        """When rules is None, deductions are returned unchanged."""
        work, fam = apply_sterilizzazione_detrazioni(
            Decimal(700), Decimal(800), Decimal(250000), None
        )
        assert work == Decimal(700)
        assert fam == Decimal(800)
