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


@pytest.mark.parametrize(
    ("base", "category", "payments"),
    [
        (_BASE, WorkerCategory.OPERAIO, _THIRTEEN),
        (_BASE, None, _THIRTEEN),
        (
            InpsSicknessBase(Decimal(900), Decimal(0), paid_days=15),
            WorkerCategory.IMPIEGATO,
            _THIRTEEN,
        ),
        (_BASE, WorkerCategory.IMPIEGATO, None),
    ],
    ids=["operaia", "unknown_category", "partial_month", "no_payments"],
)
def test_the_engine_does_not_compute_every_base(
    base: InpsSicknessBase,
    category: WorkerCategory | None,
    payments: Decimal | None,
) -> None:
    """Art. 23 c. 5 and a month not worked in full stay on the run's pay."""
    assert maternity_daily_base(base, category, payments) == (None, False)
