"""The maternity daily base of art. 23 D.Lgs. 151/2001."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.rules import maternity_daily_base
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.sickness.base.inputs import InpsSicknessBase

_BASE = InpsSicknessBase(Decimal(1800), Decimal(0))
_THIRTEEN = Decimal(13)


def test_an_impiegata_of_a_whole_month() -> None:
    """(1800 + 1800 / 12) / 30 = 65 (c. 4 and c. 2)."""
    assert maternity_daily_base(_BASE, WorkerCategory.IMPIEGATO, _THIRTEEN) == (
        Decimal(65),
        True,
    )


def test_without_the_pay_before_the_base_is_computable_but_missing() -> None:
    """The fact is missing, the rule is not."""
    assert maternity_daily_base(None, WorkerCategory.QUADRO, _THIRTEEN) == (None, True)


def test_an_operaia_divides_by_her_days() -> None:
    """INPS circ. 10/1980 par. 2.4, the sickness base: 1800 / 24 + 150 / 25 = 81."""
    base = InpsSicknessBase(Decimal(1800), Decimal(0), paid_days=24)
    assert maternity_daily_base(base, WorkerCategory.OPERAIO, _THIRTEEN) == (
        Decimal(81),
        True,
    )


def test_a_partial_month_divides_by_the_days_worked() -> None:
    """900 / 15 + (1800 / 12) / 30 = 65, with the pay of a whole month."""
    base = InpsSicknessBase(
        Decimal(900), Decimal(0), paid_days=15, full_month_pay=Decimal(1800)
    )
    assert maternity_daily_base(base, WorkerCategory.IMPIEGATO, _THIRTEEN) == (
        Decimal(65),
        True,
    )


@pytest.mark.parametrize(
    "base",
    [
        _BASE,
        InpsSicknessBase(Decimal(900), Decimal(0), paid_days=15),
    ],
    ids=["operaia_without_days", "partial_month_without_whole_pay"],
)
def test_a_base_missing_its_facts_is_computable_but_unknown(
    base: InpsSicknessBase,
) -> None:
    """The rule exists: the missing days or whole pay are a missing fact."""
    category = (
        WorkerCategory.OPERAIO if base.paid_days is None else WorkerCategory.IMPIEGATO
    )
    assert maternity_daily_base(base, category, _THIRTEEN) == (None, True)


@pytest.mark.parametrize(
    ("category", "payments"),
    [(None, _THIRTEEN), (WorkerCategory.IMPIEGATO, None)],
    ids=["unknown_category", "no_payments"],
)
def test_without_category_or_payments_the_engine_cannot_compute(
    category: WorkerCategory | None, payments: Decimal | None
) -> None:
    """No category or no monthly payments: the run keeps its own pay."""
    assert maternity_daily_base(_BASE, category, payments) == (None, False)
