"""Unit tests for Art. 12 TUIR family deduction service functions."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.engine.payroll.service.family_deductions import (
    _child_is_eligible,
    _children_deduction,
    _deduction_from_breakpoints,
    _interpolate,
    _other_deduction,
    _spouse_deduction,
    compute_family_deductions,
)
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.tax.domain.rules import DeductionBreakpoint
from ccnl_engine.engine.tax.service.loaders import load_family_deduction_rules

_RULES = load_family_deduction_rules(2026)
_D = Decimal
_SPOUSE = DependentRelationship.SPOUSE
_CHILD = DependentRelationship.CHILD
_ASCENDANT = DependentRelationship.ASCENDANT


def _dep(rel: DependentRelationship, **kw: object) -> Dependent:
    return Dependent(relationship=rel, **kw)  # type: ignore[arg-type]


def _fam(*deps: Dependent) -> FamilyComposition:
    return FamilyComposition(dependents=deps)


class TestInterpolate:
    """_interpolate — linear interpolation between deduction breakpoints."""

    def test_midpoint(self) -> None:
        """Mid-range income returns midpoint deduction."""
        result = _interpolate(_D("50"), _D("0"), _D("100"), _D("100"), _D("0"))
        assert result == _D("50.00")

    def test_at_lo_income(self) -> None:
        """Income at lo_income boundary returns lo_ded."""
        result = _interpolate(_D("0"), _D("0"), _D("100"), _D("200"), _D("0"))
        assert result == _D("200.00")

    def test_at_hi_income(self) -> None:
        """Income at hi_income boundary returns hi_ded."""
        result = _interpolate(_D("100"), _D("0"), _D("100"), _D("200"), _D("50"))
        assert result == _D("50.00")


class TestDeductionFromBreakpoints:
    """_deduction_from_breakpoints — piecewise-linear evaluation."""

    def _pts(self) -> list[DeductionBreakpoint]:
        """Four-entry list with a flat 690 band and a terminal open bracket.

        Returns:
            Standard spouse-like breakpoint list.
        """
        return [
            DeductionBreakpoint(income_up_to=_D("15000"), deduction=_D("690")),
            DeductionBreakpoint(income_up_to=_D("40000"), deduction=_D("690")),
            DeductionBreakpoint(income_up_to=_D("80000"), deduction=_D("0")),
            DeductionBreakpoint(income_up_to=None, deduction=_D("0")),
        ]

    def test_empty_list_returns_zero(self) -> None:
        """Empty breakpoint list yields zero."""
        assert _deduction_from_breakpoints(_D("1000"), []) == _D("0")

    def test_income_at_first_breakpoint(self) -> None:
        """Income <= first breakpoint income_up_to returns first deduction."""
        assert _deduction_from_breakpoints(_D("15000"), self._pts()) == _D("690.00")

    def test_income_in_flat_band(self) -> None:
        """Income in the 15001-40000 flat band returns 690 (both ends equal)."""
        assert _deduction_from_breakpoints(_D("30000"), self._pts()) == _D("690.00")

    def test_income_above_ceiling(self) -> None:
        """Income above all explicit bands falls to the open terminal."""
        assert _deduction_from_breakpoints(_D("100000"), self._pts()) == _D("0.00")

    def test_income_at_zero_first_breakpoint(self) -> None:
        """First breakpoint income_up_to=0: income <= 0 returns first deduction."""
        pts_zero = [
            DeductionBreakpoint(income_up_to=_D("0"), deduction=_D("800")),
            DeductionBreakpoint(income_up_to=_D("15000"), deduction=_D("690")),
            DeductionBreakpoint(income_up_to=None, deduction=_D("0")),
        ]
        assert _deduction_from_breakpoints(_D("0"), pts_zero) == _D("800.00")

    def test_income_above_all_explicit_breakpoints_no_null(self) -> None:
        """No None terminal: income > all bounds falls through to last deduction."""
        pts_no_null = [
            DeductionBreakpoint(income_up_to=_D("15000"), deduction=_D("690")),
            DeductionBreakpoint(income_up_to=_D("40000"), deduction=_D("0")),
        ]
        assert _deduction_from_breakpoints(_D("50000"), pts_no_null) == _D("0.00")


_INCOME_THRESHOLD = _D("2840.51")
_YOUNG_THRESHOLD = _D("4000.00")
_YOUNG_CUTOFF = 24


def _eligible(dep: Dependent) -> bool:
    """Call _child_is_eligible with standard 2026 thresholds.

    Returns:
        Eligibility flag from _child_is_eligible.
    """
    return _child_is_eligible(
        dep, 21, 2026, _INCOME_THRESHOLD, _YOUNG_THRESHOLD, _YOUNG_CUTOFF
    )


class TestChildIsEligible:
    """_child_is_eligible — age, income, and residency checks."""

    def test_no_birth_date_eligible(self) -> None:
        """No birth_date: age-eligible (caller_declared); income still checked."""
        assert _eligible(_dep(_CHILD)) is True

    def test_age_below_cutoff_ineligible(self) -> None:
        """Child under 21 (AUU covers them): not eligible."""
        dep = _dep(_CHILD, birth_date=date(2010, 1, 1))  # age 16
        assert _eligible(dep) is False

    def test_age_exactly_cutoff_eligible(self) -> None:
        """Child aged exactly 21 in ref_year: eligible."""
        dep = _dep(_CHILD, birth_date=date(2005, 6, 1))  # age 21
        assert _eligible(dep) is True

    def test_age_21_to_29_eligible(self) -> None:
        """Child aged 25: eligible."""
        dep = _dep(_CHILD, birth_date=date(2001, 3, 15))
        assert _eligible(dep) is True

    def test_age_30_non_disabled_ineligible(self) -> None:
        """Non-disabled child aged 30+: not eligible."""
        dep = _dep(_CHILD, birth_date=date(1995, 1, 1), disabled=False)
        assert _eligible(dep) is False

    def test_age_30_disabled_eligible(self) -> None:
        """Disabled child aged 30+: eligible."""
        dep = _dep(_CHILD, birth_date=date(1995, 1, 1), disabled=True)
        assert _eligible(dep) is True

    def test_residency_false_excluded(self) -> None:
        """Child with residency_eligibility=False is not eligible."""
        dep = _dep(_CHILD, birth_date=date(2001, 1, 1), residency_eligibility=False)
        assert _eligible(dep) is False

    def test_own_income_above_general_threshold_excluded(self) -> None:
        """Child aged 25 with own_income > 2840.51: not eligible."""
        dep = _dep(_CHILD, birth_date=date(2001, 1, 1), own_income=_D("5000"))
        assert _eligible(dep) is False

    def test_own_income_at_general_threshold_eligible(self) -> None:
        """Child aged 25 with own_income == 2840.51: eligible (inclusive)."""
        dep = _dep(_CHILD, birth_date=date(2001, 1, 1), own_income=_D("2840.51"))
        assert _eligible(dep) is True

    def test_young_child_income_below_young_threshold_eligible(self) -> None:
        """Age 22, income 3500 (> general threshold, < young threshold): eligible."""
        dep = _dep(_CHILD, birth_date=date(2004, 1, 1), own_income=_D("3500"))  # age 22
        assert _eligible(dep) is True

    def test_young_child_income_above_young_threshold_excluded(self) -> None:
        """Child under 24 with own_income > 4000: not eligible."""
        dep = _dep(_CHILD, birth_date=date(2004, 1, 1), own_income=_D("4001"))  # age 22
        assert _eligible(dep) is False

    def test_no_birth_date_high_income_excluded(self) -> None:
        """No birth_date but own_income > general threshold: not eligible."""
        dep = _dep(_CHILD, own_income=_D("5000"))
        assert _eligible(dep) is False


class TestSpouseDeduction:
    """_spouse_deduction — Art. 12 c. 1 lett. a evaluation."""

    def test_none_spouse_returns_zero(self) -> None:
        """No spouse: deduction is zero."""
        assert _spouse_deduction(_D("26843.44"), _RULES.spouse, None) == _D("0.00")

    def test_eligible_spouse_returns_deduction(self) -> None:
        """Spouse with own_income=0 (< threshold): yields 690 at typical income."""
        sp = _dep(_SPOUSE)
        assert _spouse_deduction(_D("26843.44"), _RULES.spouse, sp) == _D("690.00")

    def test_own_income_above_threshold_excluded(self) -> None:
        """Spouse with own_income > 2840.51 not fiscally dependent: zero deduction."""
        sp = _dep(_SPOUSE, own_income=_D("5000"))
        assert _spouse_deduction(_D("26843.44"), _RULES.spouse, sp) == _D("0.00")

    def test_months_6_halves_deduction(self) -> None:
        """6 months dependent: deduction is halved (pro-rated)."""
        sp_full = _dep(_SPOUSE)
        sp_half = _dep(_SPOUSE, months_dependent=6)
        full = _spouse_deduction(_D("26843.44"), _RULES.spouse, sp_full)
        half = _spouse_deduction(_D("26843.44"), _RULES.spouse, sp_half)
        assert half == money(full * _D("6") / _D("12"))

    def test_zero_income_returns_800(self) -> None:
        """Income = 0 → first breakpoint deduction (EUR 800)."""
        sp = _dep(_SPOUSE)
        assert _spouse_deduction(_D("0"), _RULES.spouse, sp) == _D("800.00")

    def test_above_ceiling_returns_zero(self) -> None:
        """Income above EUR 80k → zero deduction."""
        sp = _dep(_SPOUSE)
        assert _spouse_deduction(_D("90000"), _RULES.spouse, sp) == _D("0.00")

    def test_residency_false_returns_zero(self) -> None:
        """Spouse with residency_eligibility=False: zero deduction."""
        sp = _dep(_SPOUSE, residency_eligibility=False)
        assert _spouse_deduction(_D("26843.44"), _RULES.spouse, sp) == _D("0.00")

    def test_allocation_50_pct_halves_deduction(self) -> None:
        """50% allocation: deduction halved compared to 100%."""
        sp_full = _dep(_SPOUSE)
        sp_half = _dep(_SPOUSE, allocation_pct=_D("50"))
        full = _spouse_deduction(_D("26843.44"), _RULES.spouse, sp_full)
        half = _spouse_deduction(_D("26843.44"), _RULES.spouse, sp_half)
        assert half == money(full / _D("2"))


class TestChildrenDeduction:
    """_children_deduction — Art. 12 c. 1 lett. c tapering computation."""

    def test_no_children_returns_zero(self) -> None:
        """Empty child list yields zero deduction."""
        result = _children_deduction(_D("26843.44"), _RULES.children, [], 2026)
        assert result == _D("0.00")

    def test_one_standard_child_age_25(self) -> None:
        """One eligible child aged 25: taper applied to base_amount 950."""
        ch = _dep(_CHILD, birth_date=date(2001, 1, 1))
        result = _children_deduction(_D("26843.44"), _RULES.children, [ch], 2026)
        assert result == _D("681.57")

    def test_disabled_child_30_plus_eligible(self) -> None:
        """Disabled child aged 32: same base_amount as standard child."""
        ch = _dep(_CHILD, birth_date=date(1994, 1, 1), disabled=True)
        result = _children_deduction(_D("26843.44"), _RULES.children, [ch], 2026)
        taper = max(_D("0"), (_D("95000") - _D("26843.44")) / _D("95000"))
        expected = money(_D("950") * taper)
        assert result == expected

    def test_non_disabled_child_30_plus_excluded(self) -> None:
        """Non-disabled child aged 32 is not eligible: deduction is zero."""
        ch = _dep(_CHILD, birth_date=date(1994, 1, 1), disabled=False)
        result = _children_deduction(_D("26843.44"), _RULES.children, [ch], 2026)
        assert result == _D("0.00")

    def test_two_children_extend_ceiling(self) -> None:
        """Two eligible children raise income ceiling by per-child increment."""
        ch1 = _dep(_CHILD, birth_date=date(2001, 1, 1))
        ch2 = _dep(_CHILD, birth_date=date(2003, 1, 1))
        taper = (_D("110000") - _D("26843.44")) / _D("110000")
        per_child = money(_D("950") * taper)
        expected = money(per_child + per_child)
        result = _children_deduction(_D("26843.44"), _RULES.children, [ch1, ch2], 2026)
        assert result == expected

    def test_above_ceiling_returns_zero(self) -> None:
        """Income above effective ceiling makes taper zero."""
        ch = _dep(_CHILD, birth_date=date(2001, 1, 1))
        result = _children_deduction(_D("100000"), _RULES.children, [ch], 2026)
        assert result == _D("0.00")

    def test_allocation_50_pct(self) -> None:
        """50% allocation: deduction halved compared to 100%."""
        ch_full = _dep(_CHILD, birth_date=date(2001, 1, 1))
        ch_half = _dep(_CHILD, birth_date=date(2001, 1, 1), allocation_pct=_D("50"))
        full = _children_deduction(_D("26843.44"), _RULES.children, [ch_full], 2026)
        half = _children_deduction(_D("26843.44"), _RULES.children, [ch_half], 2026)
        assert half == money(full / _D("2"))

    def test_child_no_birth_date_eligible(self) -> None:
        """Child without birth_date is treated as eligible (caller_declared)."""
        ch = _dep(_CHILD)
        result = _children_deduction(_D("26843.44"), _RULES.children, [ch], 2026)
        assert result > _D("0.00")


class TestOtherDeduction:
    """_other_deduction — Art. 12 c. 1 lett. d ascendenti conviventi."""

    def test_empty_list_returns_zero(self) -> None:
        """No ascendants yields zero deduction."""
        result = _other_deduction(_D("26843.44"), _RULES.other_dependents, [])
        assert result == _D("0.00")

    def test_one_ascendente(self) -> None:
        """One eligible ascendant: taper applied to amount 750."""
        asc = _dep(_ASCENDANT)
        taper = (_D("80000") - _D("26843.44")) / _D("80000")
        expected = money(money(_D("750") * taper))
        result = _other_deduction(_D("26843.44"), _RULES.other_dependents, [asc])
        assert result == expected

    def test_non_cohabiting_excluded(self) -> None:
        """Non-cohabiting ascendant is not eligible."""
        asc = _dep(_ASCENDANT, cohabiting=False)
        result = _other_deduction(_D("26843.44"), _RULES.other_dependents, [asc])
        assert result == _D("0.00")

    def test_residency_ineligible_excluded(self) -> None:
        """Ascendant without residency eligibility is excluded."""
        asc = _dep(_ASCENDANT, residency_eligibility=False)
        result = _other_deduction(_D("26843.44"), _RULES.other_dependents, [asc])
        assert result == _D("0.00")

    def test_own_income_above_threshold_excluded(self) -> None:
        """Ascendant with own_income > 2840.51: not eligible."""
        asc = _dep(_ASCENDANT, own_income=_D("5000"))
        result = _other_deduction(_D("26843.44"), _RULES.other_dependents, [asc])
        assert result == _D("0.00")

    def test_above_ceiling_returns_zero(self) -> None:
        """Income above EUR 80k ceiling: taper is zero."""
        asc = _dep(_ASCENDANT)
        result = _other_deduction(_D("90000"), _RULES.other_dependents, [asc])
        assert result == _D("0.00")


class TestComputeFamilyDeductions:
    """compute_family_deductions — integration of all three deduction paths."""

    def test_all_zeros_no_dependents(self) -> None:
        """Empty FamilyComposition yields four zero values."""
        sp, ch, ot, total = compute_family_deductions(_fam(), _D("26843.44"), _RULES)
        assert sp == _D("0.00")
        assert ch == _D("0.00")
        assert ot == _D("0.00")
        assert total == _D("0.00")

    def test_spouse_only(self) -> None:
        """Spouse-only family: spouse=690, others=0, total=690."""
        sp, ch, ot, total = compute_family_deductions(
            _fam(_dep(_SPOUSE)), _D("26843.44"), _RULES
        )
        assert sp == _D("690.00")
        assert ch == _D("0.00")
        assert ot == _D("0.00")
        assert total == _D("690.00")

    def test_child_21(self) -> None:
        """One eligible child (age 25): children deduction 681.57."""
        ch_dep = _dep(_CHILD, birth_date=date(2001, 1, 1))
        _sp, ch, _ot, total = compute_family_deductions(
            _fam(ch_dep), _D("26843.44"), _RULES
        )
        assert ch == _D("681.57")
        assert total == _D("681.57")

    def test_spouse_and_child(self) -> None:
        """Spouse + child: total = 690 + 681.57 = 1371.57."""
        ch_dep = _dep(_CHILD, birth_date=date(2001, 1, 1))
        sp, ch, _ot, total = compute_family_deductions(
            _fam(_dep(_SPOUSE), ch_dep), _D("26843.44"), _RULES
        )
        assert sp == _D("690.00")
        assert ch == _D("681.57")
        assert total == _D("1371.57")

    def test_ascendente_only(self) -> None:
        """One ascendente: other deduction > 0; total equals other."""
        _sp, _ch, ot, total = compute_family_deductions(
            _fam(_dep(_ASCENDANT)), _D("26843.44"), _RULES
        )
        assert ot > _D("0.00")
        assert total == ot

    def test_returns_four_tuple(self) -> None:
        """Return value is always a 4-tuple."""
        result = compute_family_deductions(_fam(_dep(_SPOUSE)), _D("50000"), _RULES)
        assert len(result) == 4

    def test_high_income_all_zero(self) -> None:
        """Very high income makes all tapers zero; total is zero."""
        ch_dep = _dep(_CHILD, birth_date=date(2001, 1, 1))
        sp, ch, ot, total = compute_family_deductions(
            _fam(_dep(_SPOUSE), ch_dep, _dep(_ASCENDANT)),
            _D("200000"),
            _RULES,
        )
        assert sp == _D("0.00")
        assert ch == _D("0.00")
        assert ot == _D("0.00")
        assert total == _D("0.00")

    def test_disabled_child_same_base_amount(self) -> None:
        """Disabled child gets base_amount (950), not 1350 — no supplement."""
        ch_dep = _dep(_CHILD, birth_date=date(1994, 1, 1), disabled=True)
        _sp, ch, _ot, _total = compute_family_deductions(
            _fam(ch_dep), _D("26843.44"), _RULES
        )
        taper = max(_D("0"), (_D("95000") - _D("26843.44")) / _D("95000"))
        expected = money(_D("950") * taper)
        assert ch == expected
        assert ch < money((_D("950") + _D("400")) * taper)

    def test_child_high_income_yields_zero(self) -> None:
        """Child with own_income > 2840.51: excluded, deduction is zero."""
        ch_dep = _dep(_CHILD, birth_date=date(2001, 1, 1), own_income=_D("100000"))
        _sp, ch, _ot, total = compute_family_deductions(
            _fam(ch_dep), _D("26843.44"), _RULES
        )
        assert ch == _D("0.00")
        assert total == _D("0.00")

    def test_child_residency_false_yields_zero(self) -> None:
        """Child with residency_eligibility=False: excluded, deduction is zero."""
        ch_dep = _dep(_CHILD, birth_date=date(2001, 1, 1), residency_eligibility=False)
        _sp, ch, _ot, total = compute_family_deductions(
            _fam(ch_dep), _D("26843.44"), _RULES
        )
        assert ch == _D("0.00")
        assert total == _D("0.00")

    def test_two_spouses_raises(self) -> None:
        """FamilyComposition with two spouses raises ValidationError."""
        with pytest.raises(ValidationError, match="spouse"):
            _fam(_dep(_SPOUSE), _dep(_SPOUSE))

    def test_spouse_residency_false_yields_zero(self) -> None:
        """Spouse with residency_eligibility=False: deduction is zero."""
        sp = _dep(_SPOUSE, residency_eligibility=False)
        sp_val, _ch, _ot, total = compute_family_deductions(
            _fam(sp), _D("26843.44"), _RULES
        )
        assert sp_val == _D("0.00")
        assert total == _D("0.00")
