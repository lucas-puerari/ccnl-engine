"""The chain of a month split by a promotion, component by component."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.change.rules import (
    MID_MONTH_CHANGE,
    blended,
    month_change,
)
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.compensation.models import Allowance
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import SeniorityFact, SeniorityPromotion, SenioritySource
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest

_SHARE = Decimal(1) / Decimal(3)


def _allowance(code: str) -> Allowance:
    return Allowance.model_validate({
        "code": code,
        "description": code,
        "monthly": {
            "periods": [{"valid_from": "2026-01-01", "valid_until": None, "value": "1"}]
        },
    })


def test_each_component_takes_its_share_of_each_level() -> None:
    """A third after: base, seniority, a shared and a one-sided allowance."""
    before = MonthlyPayChain(
        base=Decimal(300),
        seniority=Decimal(30),
        allowances=((_allowance("A"), Decimal(60)), (_allowance("OLD"), Decimal(9))),
        limitations=("before",),
        seniority_excluded_from=frozenset({13}),
    )
    after = MonthlyPayChain(
        base=Decimal(600),
        seniority=Decimal(60),
        allowances=((_allowance("A"), Decimal(90)), (_allowance("NEW"), Decimal(12))),
        limitations=("after",),
        seniority_excluded_from=frozenset({14}),
    )
    chain = blended(before, after, _SHARE)

    assert (chain.base, chain.seniority) == (Decimal(400), Decimal(40))
    assert {a.code: v for a, v in chain.allowances} == {
        "A": Decimal(70),
        "OLD": Decimal(6),
        "NEW": Decimal(4),
    }
    assert chain.limitations == ("after", MID_MONTH_CHANGE)
    assert chain.seniority_excluded_from == frozenset({14})


def test_a_month_without_an_employment_period_is_the_calendar_month() -> None:
    """March 2026: 26 Mondays to Saturdays, 14 from Monday 16."""
    request = cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            seniority=SeniorityFact(
                0,
                date(2026, 1, 1),
                SenioritySource.PAYSLIP,
                promotion=SeniorityPromotion(date(2026, 3, 16), "5"),
            ),
            period_id=PeriodId(year=2026, month=3),
            employment_period=None,
        ),
    )
    change = month_change(
        request, load_ccnl("commercio-confcommercio"), RunKind.REGULAR
    )
    assert change is not None
    assert change.share == Decimal(14) / Decimal(26)
    assert change.from_level == "5"


@pytest.mark.parametrize(
    ("ccnl", "reason"),
    [
        (
            "agenti-immobiliari-fiaip",
            "the CCNL sets no daily quota whose payable days split the month",
        ),
        (
            "edilizia-ance",
            "a CCNL that pays a category by the hour has one monthly total",
        ),
    ],
)
def test_the_rejection_names_the_promotion(ccnl: str, reason: str) -> None:
    """The message, the field and the feature of a month that cannot split."""
    request = cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            seniority=SeniorityFact(
                0,
                date(2026, 1, 1),
                SenioritySource.PAYSLIP,
                promotion=SeniorityPromotion(date(2026, 3, 16), "5"),
            ),
            period_id=PeriodId(year=2026, month=3),
            employment_period=None,
        ),
    )
    with pytest.raises(InvalidInputError) as error:
        month_change(request, load_ccnl(ccnl), RunKind.REGULAR)
    assert str(error.value).endswith(
        f"a change of level inside the month of the run cannot be paid: {reason}"
    )
    assert (error.value.field, error.value.feature) == (
        "SeniorityFact.promotion",
        "employment_change",
    )
