"""The daily divisors of the full-time week of the days stated."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.leave.models import LeaveEntitlementTier, LeaveRules
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


@pytest.mark.parametrize(
    ("slug", "days", "ferie"),
    [
        ("studi-professionali-confprofessioni", 6, 26),
        ("studi-professionali-confprofessioni", 5, 22),
        ("multiservizi-anip", 6, 26),
    ],
)
def test_the_week_sets_the_ferie_of_a_year(slug: str, days: int, ferie: int) -> None:
    """Studi art. 99, Multiservizi art. 42: 26 on six days, 22 on five."""
    ccnl = with_week_days(load_ccnl(slug), days)
    assert ccnl.work_rules is not None
    assert ccnl.work_rules.leave_rules is not None
    assert ccnl.work_rules.leave_rules.default_annual_days == ferie


def test_week_days_leave_excludes_seniority_tiers() -> None:
    """A seniority tier beside the days of the week is ambiguous: rejected."""
    ccnl = load_ccnl("studi-professionali-confprofessioni")
    assert ccnl.work_rules is not None
    leave = ccnl.work_rules.leave_rules
    assert leave is not None
    tier = LeaveEntitlementTier(annual_days=Decimal(22))
    with pytest.raises(ValidationError, match="exclude seniority"):
        LeaveRules.model_validate({
            **leave.model_dump(),
            "entitlement_tiers": (tier.model_dump(),),
        })


@pytest.mark.parametrize(
    ("slug", "days", "divisor"),
    [
        ("pulizia-artigianato-confartigianato", 6, 26),
        ("pulizia-artigianato-confartigianato", 5, 22),
        ("multiservizi-anip", 6, 26),
        ("studi-professionali-confprofessioni", 6, 26),
    ],
)
def test_the_week_sets_the_divisor_of_a_day_of_ferie_left(
    slug: str, days: int, divisor: int
) -> None:
    """Pulizia art. 34, Multiservizi art. 19: /22 or /26; Studi art. 137: 26."""
    ccnl = with_week_days(load_ccnl(slug), days)
    assert ccnl.work_rules is not None
    assert ccnl.work_rules.leave_rules is not None
    termination = ccnl.work_rules.leave_rules.termination
    assert termination is not None
    assert termination.ferie_divisor == divisor


def test_a_week_without_termination_keeps_none() -> None:
    """A divisor of the week but no settlement rule to carry it."""
    ccnl = load_ccnl("pulizia-artigianato-confartigianato")
    assert ccnl.work_rules is not None
    leave = ccnl.work_rules.leave_rules
    assert leave is not None
    rules = ccnl.work_rules.model_copy(
        update={"leave_rules": leave.model_copy(update={"termination": None})}
    )
    ccnl = with_week_days(ccnl.model_copy(update={"work_rules": rules}), 6)
    assert ccnl.work_rules is not None
    assert ccnl.work_rules.leave_rules is not None
    assert ccnl.work_rules.leave_rules.termination is None
    assert ccnl.work_rules.leave_rules.default_annual_days == 26
