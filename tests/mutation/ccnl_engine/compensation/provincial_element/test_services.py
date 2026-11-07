"""The Commercio terzo elemento nazionale and the provincial element fact."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.provincial_element.services import (
    without_replaced_elements,
)
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_ELEMENT = "TERZO_ELEMENTO_NAZIONALE"


def _run(in_force: bool | None) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=9),
            payment_date=date(2026, 9, 27),
            ccnl_id="commercio-confcommercio",
            level_code="4",
            employer=EmployerProfile(
                headcount=Headcount(50), provincial_pay_element=in_force
            ),
            opening_state=PeriodState.zero(),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _element(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if _ELEMENT in i.item_id), Decimal(0)
    )


def test_no_provincial_element_pays_the_national_one() -> None:
    """Art. 215: 2.07 a month where no provincial third element is in force."""
    result = _run(in_force=False)
    assert _element(result) == Decimal("2.07")
    assert all(i.code != "provincial_pay_element_unknown" for i in result.issues)


@pytest.mark.parametrize("in_force", [True, None], ids=["replaced", "unknown"])
def test_a_provincial_or_unknown_element_leaves_it_out(in_force: bool | None) -> None:
    """Not due where replaced; unknown, left out and named as a missing fact."""
    result = _run(in_force)
    assert _element(result) == 0
    named = [
        i.fact for i in result.issues if i.code == "provincial_pay_element_unknown"
    ]
    assert named == ([] if in_force else ["provincial_pay_element"])


_ALIMENTARI = "alimentari-pmi-unionalimentari"


@pytest.mark.parametrize(
    ("kind", "in_force", "day", "expected"),
    [
        # The EGR of level 4, the only element a company premium replaces.
        ("second_level_premium", None, date(2027, 1, 1), ("EGR",)),
        # Stated true: left out, nothing unknown.
        ("second_level_premium", True, date(2027, 1, 1), ()),
        # No element of the other kind: the CCNL is kept whole.
        ("provincial_element", None, date(2027, 1, 1), ()),
    ],
    ids=["unknown", "replaced", "other-kind"],
)
def test_the_elements_of_each_kind_apart(
    kind: str, in_force: bool | None, day: date, expected: tuple[str, ...]
) -> None:
    """Only the elements of the kind, of the level, in force on the day."""
    ccnl = load_ccnl(_ALIMENTARI)
    kept, unknown = without_replaced_elements(ccnl, "4", kind, in_force, day)
    codes = {a.code for lv in kept.levels for a in lv.fixed_allowances}

    assert unknown == expected
    assert ("EGR" in codes) is (kind == "provincial_element")
    assert (kept is ccnl) is (kind == "provincial_element")
