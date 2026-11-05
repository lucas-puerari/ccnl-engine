"""The daily divisors of the full-time week of the days stated."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.working_time.week.rules import with_week_days

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL


def _absence(ccnl: CCNL) -> DailyDivisorMethod:
    assert ccnl.work_rules is not None
    assert ccnl.work_rules.absence_rules is not None
    return ccnl.work_rules.absence_rules.daily_divisor_method


def _clause_divisor(ccnl: CCNL) -> Decimal | None:
    assert ccnl.work_rules is not None
    assert ccnl.work_rules.sunday_holidays is not None
    return ccnl.work_rules.sunday_holidays.divisor


def test_a_six_day_logistica_week_divides_by_26_with_its_provenance() -> None:
    """Art. 61 c. 3: 26 for the non-travelling staff on six days."""
    ccnl = with_week_days(load_ccnl("logistica-trasporto-confetra"), 6)

    assert _absence(ccnl) is DailyDivisorMethod.BY_26
    assert ccnl.work_rules is not None
    rules = ccnl.work_rules.absence_rules
    assert rules is not None
    assert rules.provenance is not None
    assert rules.provenance.location is not None
    assert (rules.provenance.location.quote or "").endswith("mensile per 26.")


def test_a_five_day_pulizia_week_divides_by_22() -> None:
    """Art. 34: 22 'nel caso di settimana corta'."""
    ccnl = with_week_days(load_ccnl("pulizia-artigianato-confartigianato"), 5)

    assert _absence(ccnl) is DailyDivisorMethod.BY_22


def test_a_six_day_bcc_week_divides_the_holiday_by_26() -> None:
    """Art. 114: 6 x 52 / 12 = 26; the absence rule keeps its method."""
    base = load_ccnl("bcc-credito-cooperativo")
    ccnl = with_week_days(base, 6)

    assert _clause_divisor(ccnl) == Decimal(26)
    assert _absence(ccnl) is _absence(base)


@pytest.mark.parametrize(
    ("slug", "days"),
    [
        ("logistica-trasporto-confetra", None),
        ("logistica-trasporto-confetra", 5),
        ("logistica-trasporto-confetra-viaggiante", 6),
        ("bcc-credito-cooperativo", 5),
        ("commercio-confcommercio", 6),
    ],
)
def test_a_week_without_a_divisor_of_its_own_keeps_the_ccnl(
    slug: str, days: int | None
) -> None:
    """Not stated, the default week, or a CCNL with one divisor."""
    ccnl = load_ccnl(slug)
    assert with_week_days(ccnl, days) is ccnl


def test_a_ccnl_without_work_rules_is_unchanged() -> None:
    """Nothing to swap."""
    ccnl = load_ccnl("pulizia-artigianato-confartigianato")
    ccnl = ccnl.model_copy(update={"work_rules": None})
    assert with_week_days(ccnl, 5) is ccnl


def test_work_rules_without_absence_or_clause_are_unchanged() -> None:
    """A week of the CCNL but no rule to read it."""
    ccnl = load_ccnl("pulizia-artigianato-confartigianato")
    assert ccnl.work_rules is not None
    rules = ccnl.work_rules.model_copy(
        update={"absence_rules": None, "sunday_holidays": None}
    )
    ccnl = ccnl.model_copy(update={"work_rules": rules})
    assert with_week_days(ccnl, 5) is ccnl
