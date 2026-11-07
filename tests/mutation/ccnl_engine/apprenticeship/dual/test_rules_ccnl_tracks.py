"""The first- and third-level tracks of seven CCNLs, read off their tables.

Each case is a month of work hours only, so the base salary is the rate
of the period times the base salary of the level the period pays at.

- Commercio and Confesercenti, art. 69: first level 50/50/65/70% of the
  qualified worker's pay by year of the contract; third level two then one
  level below the destination by half of the programme.
- Edilizia ANCE, art. 92 (ANCE text of 4 April 2019): first level at the
  conventional level 2 or 1, 65-90% by semester; third level 70-90% by
  semester for six semesters, nothing for the 7th and 8th.
- Quadri e impiegati agricoli, All. F: first level 45/55/60/70% by year,
  third level 80% up to 12 months, 70% above.
- Metalmeccanico artigianato, accordo 1 February 2018: third level 70%
  then 80% by half, 80% up to 12 months.
- Formazione professionale, all. 13: third level 70/80/90/100% by year.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.apprenticeship.dual.rules import dual_chain
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.ladder.rules import level_below
from ccnl_engine.employment.apprentice.inputs import (
    Apprentice,
    ApprenticeshipProgramme,
    DualHours,
)
from ccnl_engine.errors import OutOfScopeError
from ccnl_engine.pay_item.rounding.policies import money

_JUNE = date(2026, 6, 1)
_WORK = DualHours(Decimal(0), Decimal(0), Decimal(100))
_FIRST = ApprenticeshipProgramme.FIRST_LEVEL
_THIRD = ApprenticeshipProgramme.THIRD_LEVEL


def _base(ccnl_id: str, level: str, apprentice: Apprentice) -> Decimal:
    ccnl = load_ccnl(ccnl_id)
    return dual_chain(
        ccnl,
        ccnl.level_by_code(level),
        apprentice,
        0,
        frozenset(),
        _JUNE,
        worker_category=None,
        seniority_months=None,
    ).base


def _expected(ccnl_id: str, level: str, below: int, rate: str) -> Decimal:
    ccnl = load_ccnl(ccnl_id)
    paid = level_below(ccnl.levels, ccnl.level_by_code(level), below)
    return money(paid.base_salary.value_at(_JUNE) * Decimal(rate))


@pytest.mark.parametrize(
    ("ccnl_id", "level", "track", "months", "paid_at", "rate"),
    [
        ("commercio-confcommercio", "4", None, 23, "4", "0.50"),
        ("commercio-confcommercio", "4", None, 24, "4", "0.65"),
        ("commercio-confcommercio", "4", None, 36, "4", "0.70"),
        ("terziario-confesercenti", "IV", None, 0, "IV", "0.50"),
        ("edilizia-ance", "3", "diploma_ifts", 7, "2", "0.70"),
        ("edilizia-ance", "3", "qualifica_altri", 36, "1", "0.90"),
        ("edilizia-ance-impiegati", "6", "diploma_ifts", 30, "2", "0.90"),
        ("impiegati-tecnici-agricoli", "3", None, 12, "3", "0.55"),
        ("metalmeccanico-artigianato", "3", None, 47, "3", "0.70"),
        ("formazione-professionale", "V", None, 0, "V", "0.50"),
    ],
)
def test_first_level(
    ccnl_id: str, level: str, track: str | None, months: int, paid_at: str, rate: str
) -> None:
    """The rate of the period at the destination or conventional level."""
    apprentice = Apprentice(months, track=track, programme=_FIRST, hours=_WORK)
    assert _base(ccnl_id, level, apprentice) == _expected(ccnl_id, paid_at, 0, rate)


@pytest.mark.parametrize(
    ("ccnl_id", "level", "months", "length", "below", "rate"),
    [
        ("commercio-confcommercio", "4", 3, 24, 2, "1"),
        ("commercio-confcommercio", "4", 12, 24, 1, "1"),
        ("terziario-confesercenti", "IV", 20, 24, 1, "1"),
        ("edilizia-ance", "4", 0, None, 0, "0.70"),
        ("edilizia-ance-impiegati", "5", 13, None, 0, "0.78"),
        ("edilizia-ance-impiegati", "5", 35, None, 0, "0.90"),
        ("impiegati-tecnici-agricoli", "3", 3, 12, 0, "0.80"),
        ("impiegati-tecnici-agricoli", "3", 3, 13, 0, "0.70"),
        ("metalmeccanico-artigianato", "3", 11, 24, 0, "0.70"),
        ("metalmeccanico-artigianato", "3", 12, 24, 0, "0.80"),
        ("metalmeccanico-artigianato", "3", 3, 10, 0, "0.80"),
        ("formazione-professionale", "V", 40, None, 0, "1"),
    ],
)
def test_third_level(
    ccnl_id: str, level: str, months: int, length: int | None, below: int, rate: str
) -> None:
    """The rate of the period at the level the period pays at."""
    apprentice = Apprentice(
        months, programme=_THIRD, programme_months=length, hours=_WORK
    )
    assert _base(ccnl_id, level, apprentice) == _expected(ccnl_id, level, below, rate)


def test_the_blank_ance_semesters_are_not_paid() -> None:
    """Art. 92: the 7th and 8th semesters of the third level are blank."""
    apprentice = Apprentice(36, programme=_THIRD, hours=_WORK)
    with pytest.raises(OutOfScopeError, match="sets no pay"):
        _base("edilizia-ance-impiegati", "5", apprentice)
