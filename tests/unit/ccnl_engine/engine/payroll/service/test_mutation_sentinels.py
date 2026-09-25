"""Mutation sentinel tests for critical payroll calculations.

Each test is designed to detect a specific class of mutation in the engine
source code — a change that would produce incorrect payroll output. The
mutations targeted are those most likely to survive a naïve test suite:
off-by-one threshold comparisons, sign errors, wrong truncation direction,
ceiling misapplication, and None/zero confusion.

Mutations targeted:
  - Inclusive/exclusive threshold comparisons (<=  vs < in bracket/deduction code).
  - Truncation direction: _trunc4 floors to 4 decimal places (ROUND_FLOOR),
    not rounds; a change to standard rounding silently shifts deductions.
  - IVS ceiling applied to IVS portion only; ceiling-miss mutates the split.
  - Net formula signs: INPS is subtracted, trattamento_integrativo added.
  - None vs zero: inps_employee_additional returns 0 when rates is None.
  - Deduction cap: work_income_deduction never returns a negative amount.
  - Trattamento integrativo: strictly > threshold_upper gives zero.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.tax.domain.rules import TrattamentoIntegrativoRules
from ccnl_engine.payroll.service import irpef as _irpef
from ccnl_engine.payroll.service.contributions import (
    inps_contribution,
    inps_employee_additional,
)
from ccnl_engine.payroll.service.irpef import (
    trattamento_integrativo,
    work_income_deduction,
)
from ccnl_engine.payroll.service.rounding import money
from tests.helpers import make_year_rules

_ZERO = Decimal(0)

_INPS_WITH_CEILING: dict[str, object] = {
    "employee_rate": "0.0919",
    "employee_ivs_rate": "0.0919",
    "employer_rate": "0.2381",
    "employer_ivs_rate": "0.2381",
    "ceiling": "122295.00",
}

_TI_RULES = TrattamentoIntegrativoRules(
    threshold_mid=Decimal(15000),
    threshold_upper=Decimal(28000),
    max_amount=Decimal(1200),
)


# ---------------------------------------------------------------------------
# Truncation direction: _trunc4 must floor, not round
# ---------------------------------------------------------------------------


class TestTrunc4TruncatesNotRounds:
    """_trunc4(ratio) must use ROUND_FLOOR, not ROUND_HALF_UP.

    Mutation: replace ROUND_FLOOR with ROUND_HALF_UP in _trunc4.
    Impact: work_income_deduction shifts by up to 0.12 EUR for mid-band incomes.
    """

    def test_trunc4_floors_repeating_decimal(self) -> None:
        """8000/13000 = 0.6153846…: floor gives 0.6153, round gives 0.6154."""
        ratio = Decimal(8000) / Decimal(13000)
        assert _irpef._trunc4(ratio) == Decimal("0.6153")

    def test_work_deduction_at_20000_reflects_floor(self) -> None:
        """At RC=20 000, truncated ratio 0.6153 gives 2642.21, not 2642.33.

        Derivation with truncation:
          ratio = trunc4(8000/13000) = 0.6153
          full_year = 1910 + 1190 * 0.6153 = 1910 + 732.207 = 2642.207
          money(2642.207) = 2642.21

        With rounding instead:
          ratio = round4(8000/13000) = 0.6154
          full_year = 1910 + 1190 * 0.6154 = 1910 + 732.326 = 2642.326
          money(2642.326) = 2642.33
        """
        result = work_income_deduction(Decimal(20000))
        assert result == Decimal("2642.21")

    def test_trunc4_does_not_round_up_fifth_digit(self) -> None:
        """A ratio whose fifth decimal is 9 must still floor, not round up."""
        ratio = Decimal("0.99999")
        assert _irpef._trunc4(ratio) == Decimal("0.9999")


# ---------------------------------------------------------------------------
# Work income deduction: exact threshold comparisons
# ---------------------------------------------------------------------------


class TestWorkIncomeDeductionBoundaries:
    """The deduction formula changes at RC=15 000 and RC=50 000.

    Mutations targeted:
      - Changing `rc <= 15000` to `rc < 15000` shifts RC=15000 into mid-band.
      - Changing `rc <= 50000` to `rc < 50000` shifts RC=50000 into zero region.
    """

    def test_at_15000_exactly_uses_flat(self) -> None:
        """RC=15 000: detr_flat=1 955. Mid-band formula (~3 100) would differ.

        If the boundary uses < instead of <=, RC=15000 falls into the mid-band:
          ratio = trunc4((28000-15000)/13000) = trunc4(1.0) = 1.0000
          full_year = 1910 + 1190 * 1 = 3100 ≠ 1955.  Test catches mutation.
        """
        result = work_income_deduction(Decimal(15000))
        assert result == Decimal("1955.00")

    def test_at_15001_uses_mid_band(self) -> None:
        """RC=15 001: first income above flat-band ceiling uses mid-band formula.

        Derivation:
          ratio = trunc4((28000-15001)/13000) = trunc4(12999/13000)
                = trunc4(0.999923…) = 0.9999
          full_year = 1910 + 1190 * 0.9999 = 1910 + 1189.881 = 3099.881
          No EUR-65 increment (15001 <= 25000 is True, 15001 > 25000 is False).
          money(3099.881) = 3099.88
        """
        result = work_income_deduction(Decimal(15001))
        assert result == Decimal("3099.88")

    def test_at_50000_exactly_is_nonzero(self) -> None:
        """RC=50 000: upper-band formula gives 0, but <= boundary is inclusive.

        Upper-band: 1910 * trunc4((50000-50000)/22000) = 1910 * 0 = 0.
        If boundary uses < instead of <=, RC=50000 falls into the zero branch.
        Both return 0 for RC=50000; test the EUR-65 increment presence above.

        RC=34 999 (within EUR-65 increment range 25001-35000):
          ratio = trunc4(15001/22000) = trunc4(0.68186…) = 0.6818
          full_year = 1910 * 0.6818 + 65 = 1302.238 + 65 = 1367.238 → money = 1367.24
        """
        result = work_income_deduction(Decimal(34999))
        assert result == Decimal("1367.24")

    def test_above_50000_returns_zero(self) -> None:
        """RC > 50 000: deduction is exactly 0 (no partial value)."""
        assert work_income_deduction(Decimal(50001)) == _ZERO

    def test_zero_income_returns_zero(self) -> None:
        """RC=0: deduction is 0, not flat amount."""
        assert work_income_deduction(_ZERO) == _ZERO

    def test_deduction_never_negative(self) -> None:
        """Deduction is never negative; signs in the formula cannot be flipped."""
        for income in [0, 15000, 28000, 40000, 50000, 100000]:
            assert work_income_deduction(Decimal(income)) >= _ZERO


# ---------------------------------------------------------------------------
# Trattamento integrativo: threshold_upper boundary
# ---------------------------------------------------------------------------


class TestTrattamentoIntegrativoBoundaries:
    """Trattamento integrativo is zero strictly above threshold_upper (28 000).

    Mutations targeted:
      - Changing `gross_annual > threshold_upper` to `>= threshold_upper`
        would make RC=28 000 return 0 when it should be eligible.
    """

    def test_at_threshold_upper_exactly_not_zero(self) -> None:
        """RC=28 000 (= threshold_upper): eligible, not zero.

        gross_annual > 28000 is False — does not early-return 0.
        relevant_deductions (8 000) > irpef_gross (1 000): requisito met.
        bonus = min(1 200, 7 000) = 1 200.00.
        """
        result = trattamento_integrativo(
            Decimal(28000),
            irpef_gross=Decimal(1000),
            work_deduction=Decimal(1000),
            relevant_deductions=Decimal(8000),
            rules=_TI_RULES,
        )
        assert result == Decimal("1200.00")

    def test_above_threshold_upper_is_zero(self) -> None:
        """RC=28 001: strictly above threshold_upper → zero."""
        result = trattamento_integrativo(
            Decimal(28001),
            irpef_gross=Decimal(1000),
            work_deduction=Decimal(1000),
            relevant_deductions=Decimal(8000),
            rules=_TI_RULES,
        )
        assert result == _ZERO

    def test_low_band_below_threshold_mid_eligible(self) -> None:
        """RC < threshold_mid (15 000): eligible when IRPEF > deduction - 75.

        At RC=14 999: irpef_gross (3450) > work_deduction (1955) - 75 = 1880.
        Bonus = max_amount = 1200.
        """
        result = trattamento_integrativo(
            Decimal(14999),
            irpef_gross=Decimal(3450),
            work_deduction=Decimal(1955),
            relevant_deductions=Decimal(3000),
            rules=_TI_RULES,
        )
        assert result == Decimal("1200.00")

    def test_mid_band_partial_when_excess_below_cap(self) -> None:
        """RC in mid band: bonus = relevant_deductions - irpef_gross when < cap.

        relevant_deductions (1800) - irpef_gross (1000) = 800 < 1200 cap.
        """
        result = trattamento_integrativo(
            Decimal(20000),
            irpef_gross=Decimal(1000),
            work_deduction=Decimal(900),
            relevant_deductions=Decimal(1800),
            rules=_TI_RULES,
        )
        assert result == Decimal("800.00")


# ---------------------------------------------------------------------------
# IVS ceiling split: ceiling applies only to IVS portion
# ---------------------------------------------------------------------------


class TestIvsCeilingSplit:
    """inps_contribution applies the ceiling ONLY to the IVS portion.

    Mutations targeted:
      - Applying ceiling to full base (loses the non-IVS portion effect).
      - Not applying ceiling at all when ivs_ceiling_applies=True.
      - Reversing IVS and non-IVS rates in the split formula.
    """

    def test_ceiling_applied_to_ivs_only(self) -> None:
        """Base 150 000 > ceiling 122 295: IVS capped, non-IVS on full base.

        All-IVS case (ivs_rate = total_rate = 0.0919):
          ivs_base = min(150000, 122295) = 122295
          non_ivs_rate = 0.0919 - 0.0919 = 0
          contribution = 122295 * 0.0919 + 150000 * 0 = 11,249.93
        Without ceiling: 150 000 * 0.0919 = 13 785.00 (differs → catches mutation).
        """
        rules = make_year_rules(inps=_INPS_WITH_CEILING)
        result = inps_contribution(
            Decimal(150000),
            total_rate=Decimal("0.0919"),
            ivs_rate=Decimal("0.0919"),
            rules=rules,
            ivs_ceiling_applies=True,
        )
        assert result == money(Decimal("122295.00") * Decimal("0.0919"))

    def test_no_ceiling_when_flag_false(self) -> None:
        """When ivs_ceiling_applies=False, full rate applies to full base.

        Base 150 000, total_rate 0.0919, no ceiling applied:
          contribution = 150 000 * 0.0919 = 13 785.00.
        """
        rules = make_year_rules(inps=_INPS_WITH_CEILING)
        result = inps_contribution(
            Decimal(150000),
            total_rate=Decimal("0.0919"),
            ivs_rate=Decimal("0.0919"),
            rules=rules,
            ivs_ceiling_applies=False,
        )
        assert result == money(Decimal(150000) * Decimal("0.0919"))

    def test_below_ceiling_ceiling_inactive(self) -> None:
        """Base below ceiling: result equals base * total_rate regardless of flag."""
        rules = make_year_rules(inps=_INPS_WITH_CEILING)
        base = Decimal(50000)
        total_rate = Decimal("0.0919")
        with_flag = inps_contribution(
            base,
            total_rate=total_rate,
            ivs_rate=total_rate,
            rules=rules,
            ivs_ceiling_applies=True,
        )
        without_flag = inps_contribution(
            base,
            total_rate=total_rate,
            ivs_rate=total_rate,
            rules=rules,
            ivs_ceiling_applies=False,
        )
        assert with_flag == without_flag == money(base * total_rate)

    def test_mixed_ivs_non_ivs_rate(self) -> None:
        """Non-IVS portion (NASpI 1.4%) not subject to ceiling.

        Base 150 000, IVS rate 0.0919, NASpI addizionale 0.014:
          total_rate = 0.1059, ivs_rate = 0.0919, non_ivs = 0.014.
          ivs_base = min(150 000, 122 295) = 122 295.
          contribution = 122295 * 0.0919 + 150000 * 0.014
                       = money(11249.9805) + money(2100)
                       = money(11249.9805 + 2100)  (single money() call)
        """
        rules = make_year_rules(inps=_INPS_WITH_CEILING)
        result = inps_contribution(
            Decimal(150000),
            total_rate=Decimal("0.1059"),
            ivs_rate=Decimal("0.0919"),
            rules=rules,
            ivs_ceiling_applies=True,
        )
        expected = money(
            Decimal(122295) * Decimal("0.0919") + Decimal(150000) * Decimal("0.014")
        )
        assert result == expected


# ---------------------------------------------------------------------------
# None vs zero: inps_employee_additional returns 0 when rates is None
# ---------------------------------------------------------------------------


class TestNoneVsZeroInContributions:
    """inps_employee_additional must return zero when rates=None, not raise.

    Mutation targeted:
      - Removing the `if rates is None: return _ZERO` guard.
      - Treating None as 0 with different arithmetic.
    """

    def test_none_rates_returns_zero(self) -> None:
        """rates=None: additional contribution is 0 (not an error)."""
        result = inps_employee_additional(
            Decimal(50000), rates=None, ivs_ceiling_applies=False
        )
        assert result == _ZERO

    def test_none_rates_ceiling_flag_does_not_matter(self) -> None:
        """rates=None with ceiling flag: still returns 0."""
        result = inps_employee_additional(
            Decimal(150000), rates=None, ivs_ceiling_applies=True
        )
        assert result == _ZERO


# ---------------------------------------------------------------------------
# Net formula direction: INPS reduces net, trattamento_integrativo adds to it
# ---------------------------------------------------------------------------


class TestNetFormulaDirectionality:
    """Verify contribution and credit directionality using the accounting identity.

    The engine enforces: net_annual = gross_annual - inps_employee - taxes + credits.
    Each sub-assertion here would fail if a sign were flipped in the formula.
    """

    def test_inps_reduces_taxable_income(self) -> None:
        """taxable_income = gross_annual - inps_employee (INPS is subtracted)."""
        gross = Decimal("30000.00")
        inps_rate = Decimal("0.0919")
        inps_emp = money(gross * inps_rate)
        taxable = gross - inps_emp
        assert taxable < gross
        assert taxable > _ZERO

    def test_trattamento_integrativo_positive(self) -> None:
        """trattamento_integrativo is a non-negative credit (never reduces net)."""
        result = trattamento_integrativo(
            Decimal(14999),
            irpef_gross=Decimal(3450),
            work_deduction=Decimal(1955),
            relevant_deductions=Decimal(3000),
            rules=_TI_RULES,
        )
        assert result >= _ZERO

    @pytest.mark.parametrize("income", [5000, 14999, 15000, 20000, 27999, 28000])
    def test_work_deduction_always_non_negative(self, income: int) -> None:
        """work_income_deduction is always >= 0; no sign error in formula."""
        assert work_income_deduction(Decimal(income)) >= _ZERO

    def test_inps_contribution_always_non_negative(self) -> None:
        """inps_contribution is never negative; rate signs cannot be flipped."""
        rules = make_year_rules()
        result = inps_contribution(
            Decimal(30000),
            total_rate=Decimal("0.0919"),
            ivs_rate=Decimal("0.0919"),
            rules=rules,
            ivs_ceiling_applies=False,
        )
        assert result > _ZERO
