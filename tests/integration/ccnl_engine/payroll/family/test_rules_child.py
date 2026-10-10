"""Children deduction of art. 12 c. 1 lett. c TUIR on the 2026 bundle.

Expected values computed by hand from the text quoted in
:mod:`tests.knowledge.ccnl_engine.payroll.family.oracles_2026`.  At a reddito
complessivo
of 50,000 one child gives (95,000 - 50,000) / 95,000 = 0.473684... -> 0.4736
(c. 4), 950 x 0.4736 = 449.92 a year.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.family.inputs import Dependent, DependentRelationship
from ccnl_engine.payroll.family.rules_child import (
    child_due_months,
    children_deductions,
)
from ccnl_engine.tax.annual.loaders_optional import load_family_deduction_rules
from tests.integration.ccnl_engine.payroll.family.builders_dependents import (
    declared_dependent,
)
from tests.knowledge.ccnl_engine.payroll.family import oracles_2026 as family_2026

_D = Decimal
_RULES = load_family_deduction_rules(2026)
_INCOME = _D(50000)


def _child(born: date, **kwargs: object) -> Dependent:
    return declared_dependent(
        relationship=DependentRelationship.CHILD,
        birth_date=born,
        **kwargs,  # type: ignore[arg-type]
    )


def _one(child: Dependent, income: Decimal = _INCOME) -> Decimal:
    (deduction,) = children_deductions([child], income, _RULES, sole_parent=False)
    return deduction.amount


@pytest.mark.parametrize(
    ("born", "disabled", "months", "expected"),
    [
        # 25 all year: 12 months
        (date(2001, 3, 1), False, 12, "449.92"),
        # turns 21 on 10 May 2026: May to December, 449.92 x 8 / 12
        (date(2005, 5, 10), False, 8, "299.95"),
        # turns 21 on 1 January 2026: the whole year
        (date(2005, 1, 1), False, 12, "449.92"),
        # turns 21 on 31 December 2026: December only, 449.92 / 12
        (date(2005, 12, 31), False, 1, "37.49"),
        # turns 21 in January 2027: never in 2026
        (date(2006, 1, 5), False, 0, "0.00"),
        # turns 30 on 20 September 2026: January to September, x 9 / 12
        (date(1996, 9, 20), False, 9, "337.44"),
        # turns 30 on 1 January 2026: the month of the 30th birthday counts
        (date(1996, 1, 1), False, 1, "37.49"),
        # 30 before 2026: never
        (date(1995, 12, 31), False, 0, "0.00"),
        # 30 in September but disabled (art. 3 L. 104/1992): all year
        (date(1996, 9, 20), True, 12, "449.92"),
        # disabled but under 21 all year: covered by the assegno unico
        (date(2010, 1, 1), True, 0, "0.00"),
    ],
)
def test_age_band_is_evaluated_per_month(
    born: date, disabled: bool, months: int, expected: str
) -> None:
    """From the month of the 21st birthday to that of the 30th (c. 3)."""
    child = _child(born, disabled=disabled)
    assert len(child_due_months(child, _RULES.children, 2026)) == months
    assert _one(child) == _D(expected)
    assert family_2026.child_deduction(_INCOME, months=months) == _D(expected)


def test_birthday_and_dependency_interval_combine() -> None:
    """Turns 21 in May, leaves in October: May to October, 449.92 x 6 / 12."""
    child = _child(date(2005, 5, 10), dependent_until=date(2026, 10, 3))
    assert len(child_due_months(child, _RULES.children, 2026)) == 6
    assert _one(child) == _D("224.96")


@pytest.mark.parametrize(
    ("born", "own_income", "months"),
    [
        # turns 24 in 2026: 4,000 limit for the whole year
        (date(2002, 12, 31), _D(4000), 12),
        (date(2002, 12, 31), _D("4000.01"), 0),
        # turns 25 in 2026, even on 31 December: 2,840.51 for the whole year
        (date(2001, 12, 31), _D("2840.51"), 12),
        (date(2001, 12, 31), _D("2840.52"), 0),
    ],
)
def test_own_income_limit_depends_on_the_age_reached_in_the_year(
    born: date, own_income: Decimal, months: int
) -> None:
    """C. 2: 4,000 for children "di età non superiore a ventiquattro anni"."""
    child = _child(born, own_income=own_income)
    assert len(child_due_months(child, _RULES.children, 2026)) == months


def test_not_resident_child_has_no_month() -> None:
    """C. 2-bis: the family member resident abroad gives no deduction."""
    child = _child(date(2001, 3, 1), residency_eligibility=False)
    assert len(child_due_months(child, _RULES.children, 2026)) == 0


@pytest.mark.parametrize(
    ("income", "children", "expected"),
    [
        ("0", 1, "0.00"),  # ratio 1: not due (c. 4)
        ("0.01", 1, "949.91"),  # 0.99999989 -> 0.9999; 949.905
        ("50000", 1, "449.92"),
        ("94999.99", 1, "0.00"),  # 0.01 / 95,000 -> 0.0000
        ("95000", 1, "0.00"),  # ratio 0
        ("95000.01", 1, "0.00"),  # ratio below 0
        # two children: ceiling 110,000; 60,000 / 110,000 -> 0.5454; 518.13 each
        ("50000", 2, "518.13"),
        ("109999.99", 2, "0.00"),
        # three children: ceiling 125,000; 75,000 / 125,000 = 0.6; 570 each
        ("50000", 3, "570.00"),
    ],
)
def test_ceiling_and_frontiers(income: str, children: int, expected: str) -> None:
    """95,000 raised by 15,000 for each child after the first, for all."""
    kids = [_child(date(2000 + n, 3, 1)) for n in range(children)]
    deductions = children_deductions(kids, _D(income), _RULES, sole_parent=False)
    assert [d.amount for d in deductions] == [_D(expected)] * children
    assert family_2026.child_deduction(_D(income), children) == _D(expected)


def test_child_not_entitled_does_not_raise_the_ceiling() -> None:
    """A child under 21 gives no right, so the ceiling stays at 95,000."""
    kids = [_child(date(2001, 3, 1)), _child(date(2012, 3, 1))]
    first, second = children_deductions(kids, _INCOME, _RULES, sole_parent=False)
    assert first.amount == _D("449.92")
    assert second.amount == _D(0)


def test_shared_child_takes_its_share() -> None:
    """50% between the parents: 449.92 x 50% = 224.96."""
    child = _child(date(2001, 3, 1), allocation_pct=_D(50))
    assert _one(child) == _D("224.96")
    assert family_2026.child_deduction(_INCOME, share=_D(50)) == _D("224.96")


class TestSoleParent:
    """Lett. c, last period: the first child takes lett. a when better."""

    def test_eldest_child_takes_the_spouse_deduction(self) -> None:
        """R 30,000: child 950 x 0.6842 = 649.99, spouse 710; eldest gets 710.

        (95,000 - 30,000) / 95,000 = 0.684210... -> 0.6842.  With two
        children the ceiling is 110,000: 80,000 / 110,000 -> 0.7272, 690.84.
        """
        younger = _child(date(2003, 3, 1))
        eldest = _child(date(2001, 3, 1))
        first, second = children_deductions(
            [younger, eldest], _D(30000), _RULES, sole_parent=True
        )
        assert first.amount == _D("690.84")
        assert second.amount == _D(710)

    def test_twins_given_as_one_value_take_it_once(self) -> None:
        """The same declared child twice: one takes 710, the other 690.84."""
        twin = _child(date(2001, 3, 1))
        first, second = children_deductions(
            [twin, twin], _D(30000), _RULES, sole_parent=True
        )
        assert first.amount == _D(710)
        assert second.amount == _D("690.84")

    def test_child_deduction_kept_when_better(self) -> None:
        """R 1,000: child 950 x 0.9894 = 939.93, spouse 800 - 110 x 0.0666."""
        (deduction,) = children_deductions(
            [_child(date(2001, 3, 1))], _D(1000), _RULES, sole_parent=True
        )
        assert deduction.amount == _D("939.93")

    def test_without_entitled_child_nothing_changes(self) -> None:
        """A sole parent of a child under 21 has no deduction."""
        (deduction,) = children_deductions(
            [_child(date(2012, 3, 1))], _D(30000), _RULES, sole_parent=True
        )
        assert deduction.amount == _D(0)
