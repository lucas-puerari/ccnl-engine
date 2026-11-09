"""The ordinary five-day week and the agreed six-day exception under art. 19."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.absence.policies import resolve_absence
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.event.facade import AbsenceEvent
from ccnl_engine.working_time.hourly.policies import HourlyTerms
from ccnl_engine.working_time.week.rules import with_week_days


def _absence_terms(*, days: int | None = None) -> HourlyTerms:
    ccnl = load_ccnl("multiservizi-anip")
    assert ccnl.work_rules is not None
    work = ccnl.work_rules
    assert work.absence_rules is not None
    assert work.time_supplements is not None
    # Isolate the verified daily divisor: the hourly base remains a separate
    # unresolved clause of this agreement, so supply its evidence for this case.
    supplement = work.time_supplements.model_copy(
        update={"hourly_base_provenance": work.absence_rules.provenance}
    )
    ccnl = ccnl.model_copy(
        update={"work_rules": work.model_copy(update={"time_supplements": supplement})}
    )
    return HourlyTerms(
        ccnl=with_week_days(ccnl, days),
        chain=MonthlyPayChain(
            base=Decimal("1716.00"), seniority=Decimal(0), allowances=()
        ),
    )


def test_unverified_hourly_base_is_not_assumed() -> None:
    """The divisor alone does not derive EUR 1,716/22 without an hourly base."""
    ccnl = load_ccnl("multiservizi-anip")
    terms = HourlyTerms(
        ccnl=ccnl,
        chain=MonthlyPayChain(
            base=Decimal("1716.00"), seniority=Decimal(0), allowances=()
        ),
    )
    with pytest.raises(MissingRuleError, match="no verified hourly base"):
        resolve_absence(
            AbsenceEvent(date(2024, 3, 18), Decimal(8), working_days=1), terms
        )


def test_five_day_default_deducts_one_twenty_second() -> None:
    """At EUR 1,716 monthly, one unpaid working day deducts 1716/22 = 78.00."""
    quota = resolve_absence(
        AbsenceEvent(date(2024, 3, 18), Decimal(8), working_days=1),
        _absence_terms(),
    )

    assert quota.amount == Decimal("78.00")
    assert quota.method is DailyDivisorMethod.BY_22


def test_six_day_week_uses_one_twenty_sixth() -> None:
    """At EUR 1,716 monthly, one agreed six-day absence deducts 1716/26 = 66.00."""
    quota = resolve_absence(
        AbsenceEvent(date(2024, 3, 18), Decimal(8), working_days=1),
        _absence_terms(days=6),
    )

    assert quota.amount == Decimal("66.00")
    assert quota.method is DailyDivisorMethod.BY_26
