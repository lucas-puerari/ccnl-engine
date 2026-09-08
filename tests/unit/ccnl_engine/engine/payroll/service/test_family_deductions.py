"""Unit tests for Art. 12 TUIR family deduction service functions."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.engine.payroll.domain.family import FamilyComposition
from ccnl_engine.engine.payroll.service.family_deductions import (
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
        """Build a standard spouse-like breakpoint list for testing.

        Returns:
            Four-entry list with a flat 690 band and a terminal open bracket.
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
        """Income above all explicit bands falls to the open terminal (deduction 0)."""
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


class TestSpouseDeduction:
    """_spouse_deduction — Art. 12 c. 1 lett. a evaluation against 2026 rules."""

    def test_typical_income_returns_flat_690(self) -> None:
        """Income in the 15001-40000 range yields the flat EUR 690 deduction."""
        result = _spouse_deduction(_D("26843.44"), _RULES.spouse)
        assert result == _D("690.00")

    def test_zero_income_first_band(self) -> None:
        """Income = 0 falls into first breakpoint (income_up_to=0, deduction=800)."""
        result = _spouse_deduction(_D("0"), _RULES.spouse)
        assert result == _D("800.00")

    def test_above_ceiling_returns_zero(self) -> None:
        """Income above EUR 80k exceeds the taper ceiling; deduction is zero."""
        result = _spouse_deduction(_D("90000"), _RULES.spouse)
        assert result == _D("0.00")


class TestChildrenDeduction:
    """_children_deduction — Art. 12 c. 1 lett. c tapering computation."""

    def test_no_children_returns_zero(self) -> None:
        """Zero children yields zero deduction."""
        result = _children_deduction(_D("26843.44"), _RULES.children, 0, 0)
        assert result == _D("0.00")

    def test_one_standard_child(self) -> None:
        """One standard child: taper applied to base_amount 950."""
        result = _children_deduction(_D("26843.44"), _RULES.children, 1, 0)
        assert result == _D("681.57")

    def test_one_disabled_child(self) -> None:
        """One disabled child: taper applied to disabled_amount 1220."""
        taper = (_D("95000") - _D("26843.44")) / _D("95000")
        expected = money(_D("1220") * taper)
        result = _children_deduction(_D("26843.44"), _RULES.children, 0, 1)
        assert result == expected

    def test_two_children_extend_ceiling(self) -> None:
        """Two children raise the income ceiling by the per-child increment."""
        taper = (_D("110000") - _D("26843.44")) / _D("110000")
        expected = money(money(_D("950") * taper) * 2)
        result = _children_deduction(_D("26843.44"), _RULES.children, 2, 0)
        assert result == expected

    def test_above_ceiling_returns_zero(self) -> None:
        """Income above the effective ceiling makes taper zero; deduction is zero."""
        result = _children_deduction(_D("100000"), _RULES.children, 1, 0)
        assert result == _D("0.00")


class TestOtherDeduction:
    """_other_deduction — Art. 12 c. 1 lett. d ascendenti conviventi."""

    def test_zero_ascendenti_returns_zero(self) -> None:
        """Zero ascendenti yields zero deduction."""
        result = _other_deduction(_D("26843.44"), _RULES.other_dependents, 0)
        assert result == _D("0.00")

    def test_one_ascendente(self) -> None:
        """One ascendente: taper applied to amount 750."""
        taper = (_D("80000") - _D("26843.44")) / _D("80000")
        expected = money(money(_D("750") * taper) * 1)
        result = _other_deduction(_D("26843.44"), _RULES.other_dependents, 1)
        assert result == expected

    def test_above_ceiling_returns_zero(self) -> None:
        """Income above EUR 80k ceiling makes taper zero; deduction is zero."""
        result = _other_deduction(_D("90000"), _RULES.other_dependents, 1)
        assert result == _D("0.00")


class TestComputeFamilyDeductions:
    """compute_family_deductions — integration of all three deduction paths."""

    def test_all_zeros_no_dependents(self) -> None:
        """Empty FamilyComposition yields four zero values."""
        family = FamilyComposition()
        sp, ch, ot, total = compute_family_deductions(family, _D("26843.44"), _RULES)
        assert sp == _D("0.00")
        assert ch == _D("0.00")
        assert ot == _D("0.00")
        assert total == _D("0.00")

    def test_spouse_only(self) -> None:
        """Spouse-only family: spouse=690, others=0, total=690."""
        family = FamilyComposition(spouse_dependent=True)
        sp, ch, ot, total = compute_family_deductions(family, _D("26843.44"), _RULES)
        assert sp == _D("690.00")
        assert ch == _D("0.00")
        assert ot == _D("0.00")
        assert total == _D("690.00")

    def test_child_21(self) -> None:
        """One eligible child: children deduction 681.57, total matches."""
        family = FamilyComposition(children_21_or_older=1)
        _sp, ch, _ot, total = compute_family_deductions(family, _D("26843.44"), _RULES)
        assert ch == _D("681.57")
        assert total == _D("681.57")

    def test_spouse_and_child(self) -> None:
        """Spouse + child: total = 690 + 681.57 = 1371.57."""
        family = FamilyComposition(spouse_dependent=True, children_21_or_older=1)
        sp, ch, _ot, total = compute_family_deductions(family, _D("26843.44"), _RULES)
        assert sp == _D("690.00")
        assert ch == _D("681.57")
        assert total == _D("1371.57")

    def test_ascendente_only(self) -> None:
        """One ascendente: other deduction > 0; total equals other."""
        family = FamilyComposition(ascendenti_conviventi=1)
        _sp, _ch, ot, total = compute_family_deductions(family, _D("26843.44"), _RULES)
        assert ot > _D("0.00")
        assert total == ot

    def test_returns_four_tuple(self) -> None:
        """Return value is always a 4-tuple."""
        result = compute_family_deductions(
            FamilyComposition(spouse_dependent=True), _D("50000"), _RULES
        )
        assert len(result) == 4

    def test_high_income_all_zero(self) -> None:
        """Very high income makes all tapers zero; total is zero."""
        family = FamilyComposition(
            spouse_dependent=True,
            children_21_or_older=1,
            ascendenti_conviventi=1,
        )
        sp, ch, ot, total = compute_family_deductions(family, _D("200000"), _RULES)
        assert sp == _D("0.00")
        assert ch == _D("0.00")
        assert ot == _D("0.00")
        assert total == _D("0.00")

    def test_disabled_child_only(self) -> None:
        """Disabled-only child uses disabled_amount for the deduction."""
        family = FamilyComposition(children_21_or_older_disabled=1)
        _sp, ch, _ot, total = compute_family_deductions(family, _D("26843.44"), _RULES)
        assert ch > _D("0.00")
        assert total == ch
