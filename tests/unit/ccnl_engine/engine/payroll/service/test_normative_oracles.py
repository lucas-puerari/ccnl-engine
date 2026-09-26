"""Normative oracle tests for Italian tax formula functions (fiscal year 2026).

Every expected value is derived step-by-step from the applicable statute.
These tests are intentionally independent of the engine implementation and
serve as an auditable bridge between law and code.

Primary sources
---------------
- Art. 11 TUIR (IRPEF marginal brackets): D.Lgs. 216/2023
- Art. 13 c. 1 TUIR (work-income deduction): L. 207/2024
- Art. 13 c. 6 TUIR (4-decimal truncation of intermediate ratios)
- Art. 1 D.L. 3/2020 (trattamento integrativo): updated by L. 207/2024
- Art. 1 c. 6 L. 207/2024 (ulteriore detrazione lavoro dipendente)
- Art. 12 TUIR (family deductions): 2026 parameters
- Art. 50 TUIR / D.Lgs. 360/1998 (regional/municipal surtax)
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from ccnl_engine.tax.domain.ruleset import YearRules

from ccnl_engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.service.family_deductions import (
    _children_deduction,
    _spouse_deduction,
    compute_family_deductions,
)
from ccnl_engine.payroll.service.irpef import (
    irpef_gross,
    surtax_from_brackets,
    work_income_deduction,
)
from ccnl_engine.payroll.service.irpef_credits import (
    trattamento_integrativo,
    ulteriore_detrazione_lavoro,
)
from ccnl_engine.payroll.service.rounding import money
from ccnl_engine.tax.domain.credit_rules import (
    TrattamentoIntegrativoRules,
    UlterioreDetrazioneRules,
)
from ccnl_engine.tax.domain.surtax_rules import SurtaxBracket
from ccnl_engine.tax.service.tax_optional_loaders import (
    load_family_deduction_rules,
)
from tests.helpers import make_year_rules

# ---------------------------------------------------------------------------
# 2026 IRPEF bracket schedule (Art. 11 TUIR as amended by D.Lgs. 216/2023)
# Rate 23% on 0-28 000; 33% on 28 001-50 000; 43% above 50 000.
# ---------------------------------------------------------------------------

_IRPEF_BRACKETS_2026: list[dict[str, Any]] = [
    {"up_to": "28000.00", "rate": "0.23"},
    {"up_to": "50000.00", "rate": "0.33"},
    {"up_to": None, "rate": "0.43"},
]


def _rules() -> YearRules:
    return make_year_rules(brackets=_IRPEF_BRACKETS_2026)


# Shared rule constants
_TI_RULES = TrattamentoIntegrativoRules(
    threshold_mid=Decimal(15000),
    threshold_upper=Decimal(28000),
    max_amount=Decimal(1200),
)

_UD_RULES = UlterioreDetrazioneRules(
    threshold_low=Decimal(20000),
    threshold_mid=Decimal(32000),
    threshold_high=Decimal(40000),
    max_amount=Decimal(1000),
)

_FAM_RULES = load_family_deduction_rules(2026)

_D = Decimal
_SPOUSE = DependentRelationship.SPOUSE
_CHILD = DependentRelationship.CHILD


def _dep(rel: DependentRelationship, **kw: object) -> Dependent:
    return Dependent(relationship=rel, **kw)  # type: ignore[arg-type]


def _bracket(up_to: float | None, rate: str) -> SurtaxBracket:
    return SurtaxBracket(
        up_to=Decimal(str(up_to)) if up_to is not None else None,
        rate=Decimal(rate),
    )


# ---------------------------------------------------------------------------
# Art. 11 TUIR - IRPEF bracket oracles at every band transition
# ---------------------------------------------------------------------------


class TestIrpefBracketOracles:
    """Exact IRPEF amounts derived from Art. 11 TUIR 2026 statutory rates."""

    def test_income_at_second_bracket_boundary(self) -> None:
        """RC=50 000: second bracket upper boundary.

        Derivation (Art. 11 TUIR):
          28 000 * 23% = 6 440.00
          22 000 * 33% = 7 260.00
          Total       = 13 700.00
        """
        assert irpef_gross(Decimal(50000), _rules()) == Decimal("13700.00")

    def test_income_just_above_first_bracket_boundary(self) -> None:
        """RC=28 001: first income in the 33% bracket.

        Derivation (Art. 11 TUIR):
          28 000 * 23% = 6 440.00
               1 * 33% =     0.33
          Total        = 6 440.33
        """
        assert irpef_gross(Decimal(28001), _rules()) == Decimal("6440.33")

    def test_income_just_above_second_bracket_boundary(self) -> None:
        """RC=50 001: first income subject to the 43% top rate.

        Derivation (Art. 11 TUIR):
          28 000 * 23% = 6 440.00
          22 000 * 33% = 7 260.00
               1 * 43% =     0.43
          Total        = 13 700.43
        """
        assert irpef_gross(Decimal(50001), _rules()) == Decimal("13700.43")


# ---------------------------------------------------------------------------
# Art. 13 c. 1 TUIR - work-income deduction oracles at band boundaries
# 2026 statutory constants (L. 207/2024 / circolare AdE 4/E/2025 p. 6):
#   RC <= 15 000: EUR 1 955 (flat)
#   15 000 < RC <= 28 000: 1 910 + 1 190 * trunc4((28 000-RC)/13 000)
#   28 000 < RC <= 50 000: 1 910 * trunc4((50 000-RC)/22 000)
#   RC > 50 000: 0
#   +65 EUR when 25 000 < RC <= 35 000 (increment band)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("rc", "expected"),
    [
        pytest.param(
            Decimal(14999),
            Decimal("1955.00"),
            id="just_below_lo_threshold",
            # RC=14 999 <= 15 000: flat deduction 1 955.
        ),
        pytest.param(
            Decimal(15001),
            Decimal("3099.88"),
            id="just_above_lo_threshold",
            # RC=15 001 enters mid band. No increment (15 001 < 25 001).
            # ratio = trunc4(12 999 / 13 000) = trunc4(0.9999230769...) = 0.9999
            # full_year = 1 910 + 1 190 * 0.9999 = 1 910 + 1 189.881 = 3 099.881
            # money(3 099.881) = 3 099.88 (ROUND_HALF_UP)
        ),
        pytest.param(
            Decimal(49999),
            Decimal("0.00"),
            id="one_cent_below_high_threshold_truncation_to_zero",
            # RC=49 999 in upper band. No increment (> 35 000).
            # ratio = trunc4(1 / 22 000) = trunc4(0.0000454545...) = 0.0000
            # full_year = 1 910 * 0.0000 = 0
            # 4-decimal truncation causes deduction to vanish before RC reaches 50 000.
        ),
    ],
)
class TestWorkDeductionBoundaryOracles:
    """Art. 13 c. 1 TUIR - exact boundary values, full year."""

    def test_oracle(self, rc: Decimal, expected: Decimal) -> None:
        """Assert work_income_deduction returns the statutory expected value."""
        assert work_income_deduction(rc) == expected


# ---------------------------------------------------------------------------
# Art. 13 c. 1 TUIR - part-year pro-rata oracles
# The full-year deduction, in cents, is scaled by eligible_work_days / 365.
# The four-decimal truncation of art. 13 c. 6 covers the income ratios only.
# ---------------------------------------------------------------------------


class TestWorkDeductionProrataOracles:
    """Art. 13 c. 6 TUIR - exact pro-rata values for part-year workers."""

    def test_flat_band_182_days(self) -> None:
        """RC=10 000, 182 days: full-year 1 955 scaled by 182/365.

        Derivation:
          full_year = 1 955 (flat band, RC <= 15 000)
          result    = money(1 955 * 182 / 365) = money(974.8219...) = 974.82
        """
        result = work_income_deduction(Decimal(10000), eligible_work_days=182)
        assert result == Decimal("974.82")

    def test_flat_band_full_year_returns_exact_flat(self) -> None:
        """RC=10 000, 365 days: full-year amount returned unchanged.

        Derivation:
          full_year = 1 955
          prorata path skipped (eligible_work_days == 365)
          result = money(1 955) = 1 955.00
        """
        result = work_income_deduction(Decimal(10000), eligible_work_days=365)
        assert result == Decimal("1955.00")

    def test_mid_band_182_days_exact(self) -> None:
        """RC=20 000, 182 days: mid-band full-year scaled by 182/365.

        Derivation:
          ratio     = trunc4(8 000 / 13 000) = trunc4(0.615384...) = 0.6153
          full_year = 1 910 + 1 190 * 0.6153 = 2 642.207, in cents 2 642.21
          result    = money(2 642.21 * 182 / 365) = money(1 317.4887...) = 1 317.49
        """
        result = work_income_deduction(Decimal(20000), eligible_work_days=182)
        assert result == Decimal("1317.49")


# ---------------------------------------------------------------------------
# Art. 1 D.L. 3/2020 - trattamento integrativo boundary oracles
# 2026 thresholds: threshold_mid=15 000, threshold_upper=28 000, max=1 200.
# ---------------------------------------------------------------------------


class TestTrattamentoIntegrativoOracles:
    """Art. 1 D.L. 3/2020 - trattamento integrativo at exact thresholds."""

    def test_part_year_amount_follows_the_days(self) -> None:
        """RC=10 000, 182 days: 1 200 "rapportato al periodo di lavoro".

        Derivation:
          10 000 <= 15 000: low band; irpef_gross 2 300 exceeds the work
          deduction 974.82 less the corrective money(75 * 182 / 365) = 37.40.
          bonus = money(1 200 * 182 / 365) = money(598.3561...) = 598.36;
          the truncated day ratio 0.4986 would give 598.32.
        """
        result = trattamento_integrativo(
            Decimal(10000),
            Decimal(2300),
            Decimal("974.82"),
            Decimal("974.82"),
            _TI_RULES,
            eligible_work_days=182,
        )
        assert result == Decimal("598.36")

    def test_upper_threshold_exact_uses_mid_band_logic(self) -> None:
        """RC=28 000 (exactly at threshold_upper) uses mid-band logic, not zero.

        Derivation:
          28 000 > 28 000 is False: not returned early.
          28 000 <= 15 000 is False: mid-band applies.
          relevant_deductions (8 000) > irpef_gross (1 000): requisito met.
          bonus = min(1 200, 8 000 - 1 000) = min(1 200, 7 000) = 1 200.
        """
        result = trattamento_integrativo(
            Decimal(28000),
            Decimal(1000),
            Decimal(1000),
            Decimal(8000),
            _TI_RULES,
        )
        assert result == Decimal("1200.00")

    def test_rc_15001_enters_mid_band(self) -> None:
        """RC=15 001 (first income past threshold_mid) uses mid-band logic.

        Derivation:
          15 001 > 28 000 is False; 15 001 <= 15 000 is False.
          Mid-band: relevant_deductions (2 000) > irpef_gross (500).
          bonus = min(1 200, 2 000 - 500) = min(1 200, 1 500) = 1 200.
        """
        result = trattamento_integrativo(
            Decimal(15001),
            Decimal(500),
            Decimal(1000),
            Decimal(2000),
            _TI_RULES,
        )
        assert result == Decimal("1200.00")

    def test_mid_band_partial_bonus_exact(self) -> None:
        """RC=20 000: bonus = relevant_deductions - irpef_gross when below cap.

        Derivation:
          relevant_deductions (1 700) - irpef_gross (1 000) = 700.
          700 < 1 200 (cap): bonus = 700.
        """
        result = trattamento_integrativo(
            Decimal(20000),
            Decimal(1000),
            Decimal(900),
            Decimal(1700),
            _TI_RULES,
        )
        assert result == Decimal("700.00")


# ---------------------------------------------------------------------------
# Art. 1 c. 6 L. 207/2024 - ulteriore detrazione lavoro dipendente oracles
# 2026 thresholds: low=20 000, mid=32 000, high=40 000, max=1 000.
# ---------------------------------------------------------------------------


class TestUlterioreDetrazioneOracles:
    """Art. 1 c. 6 L. 207/2024 - exact taper and boundary oracle values."""

    def test_taper_midpoint(self) -> None:
        """RC=36 000 in taper zone: max_amount * (40 000-36 000) / 8 000.

        Derivation:
          span = 40 000 - 32 000 = 8 000
          full_year = 1 000 * (40 000 - 36 000) / 8 000 = 1 000 * 0.5 = 500
          result = 500 (unrounded, full year)
        """
        assert ulteriore_detrazione_lavoro(Decimal(36000), _UD_RULES) == Decimal(500)

    def test_part_year_flat_band_exact(self) -> None:
        """RC=25 000 (flat band), 91 days: max_amount * 91/365.

        Derivation:
          full_year = 1 000 (flat band, 20 000 < 25 000 <= 32 000)
          result    = money(1 000 * 91 / 365) = money(249.3150...) = 249.32
        """
        result = ulteriore_detrazione_lavoro(
            Decimal(25000), _UD_RULES, eligible_work_days=91
        )
        assert result == Decimal("249.32")

    def test_part_year_taper_band_exact(self) -> None:
        """RC=36 000 (taper), 182 days: tapered full-year * 182/365.

        Derivation:
          full_year = 1 000 * (40 000 - 36 000) / 8 000 = 500
          result    = money(500 * 182 / 365) = money(249.3150...) = 249.32
        """
        result = ulteriore_detrazione_lavoro(
            Decimal(36000), _UD_RULES, eligible_work_days=182
        )
        assert result == Decimal("249.32")


# ---------------------------------------------------------------------------
# Art. 50 TUIR / D.Lgs. 360/1998 - surtax bracket oracles
# ---------------------------------------------------------------------------


class TestSurtaxBracketOracles:
    """Art. 50 TUIR - addizionale IRPEF bracket oracle values."""

    def test_two_bracket_exact_boundary(self) -> None:
        """Income exactly at first bracket ceiling: all in lower rate.

        Derivation (flat 1.23% to 20 000, then 2.05%):
          20 000 * 1.23% = 246.00
        """
        bs = [_bracket(20000, "0.0123"), _bracket(None, "0.0205")]
        assert surtax_from_brackets(Decimal(20000), bs) == Decimal("246.00")

    def test_two_bracket_one_cent_above(self) -> None:
        """Income one cent above bracket boundary: tiny upper-bracket amount.

        Derivation:
          20 000    * 1.23% = 246.00000
               0.01 * 2.05% =   0.000205
          Total (money)     = 246.00 (rounds to 246.00, ROUND_HALF_UP)
        """
        bs = [_bracket(20000, "0.0123"), _bracket(None, "0.0205")]
        assert surtax_from_brackets(Decimal("20000.01"), bs) == Decimal("246.00")

    def test_regional_four_bracket_exact(self) -> None:
        """Four-bracket schedule: oracle at 60 000.

        Derivation:
          15 000 * 1.62% = 243.00
          13 000 * 2.73% = 354.90
          22 000 * 3.40% = 748.00
          10 000 * 3.50% = 350.00
          Total          = 1 695.90
        """
        bs = [
            _bracket(15000, "0.0162"),
            _bracket(28000, "0.0273"),
            _bracket(50000, "0.0340"),
            _bracket(None, "0.0350"),
        ]
        assert surtax_from_brackets(Decimal(60000), bs) == Decimal("1695.90")


# ---------------------------------------------------------------------------
# Art. 12 TUIR - family deduction oracles (2026 statutory rules)
# ---------------------------------------------------------------------------


class TestFamilyDeductionOracles:
    """Art. 12 TUIR family deductions at canonical income level 26 843.44."""

    def test_spouse_deduction_at_canonical_income(self) -> None:
        """RC=26 843.44, fiscally dependent spouse: deduction = 690.

        Art. 12 c. 1 lett. a: for RC in [15 001, 40 000] the deduction is EUR 690.
        Derivation: income 26 843.44 falls in the flat band; result = 690.
        """
        sp = _dep(_SPOUSE)
        result = _spouse_deduction(_D("26843.44"), _FAM_RULES.spouse, sp)
        assert result == _D("690.00")

    def test_child_deduction_taper_formula(self) -> None:
        """One eligible child (age 25), RC=26 843.44: taper applied to 950.

        Art. 12 c. 1 lett. c:
          ceiling = 95 000 (one child)
          taper   = (95 000 - 26 843.44) / 95 000
          result  = money(950 * taper), pro-rated 12/12, 100% allocation
        """
        ch = _dep(_CHILD, birth_date=date(2001, 1, 1))
        result = _children_deduction(_D("26843.44"), _FAM_RULES.children, [ch], 2026)
        taper = max(_D("0"), (_D("95000") - _D("26843.44")) / _D("95000"))
        expected = money(_D("950") * taper)
        assert result == expected

    def test_full_family_oracle_spouse_and_one_child(self) -> None:
        """RC=26 843.44, spouse + 1 eligible child: total = spouse + child.

        Derivation:
          spouse = 690.00
          child  = money(950 * taper) where taper = (95000-26843.44)/95000
          total  = money(spouse + child)
        """
        sp_dep = _dep(_SPOUSE)
        ch_dep = _dep(_CHILD, birth_date=date(2001, 1, 1))
        fam = FamilyComposition(dependents=(sp_dep, ch_dep))
        sp, ch, _, total = compute_family_deductions(fam, _D("26843.44"), _FAM_RULES)
        assert sp == _D("690.00")
        taper = max(_D("0"), (_D("95000") - _D("26843.44")) / _D("95000"))
        assert ch == money(_D("950") * taper)
        assert total == money(sp + ch)
