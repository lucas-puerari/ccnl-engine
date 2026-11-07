"""Deduction of an unpaid absence at the quota of the CCNL absence rule."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.absence.policies import resolve_absence
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.event.facade import AbsenceEvent
from ccnl_engine.working_time.hourly.policies import HourlyTerms

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL

_COMMERCIO = load_ccnl("commercio-confcommercio")
_DAY = date(2026, 3, 16)
_CHAIN = MonthlyPayChain(base=Decimal("1680.00"), seniority=Decimal(0), allowances=())


def _with_method(method: DailyDivisorMethod) -> CCNL:
    rules = _COMMERCIO.work_rules
    assert rules is not None
    assert rules.absence_rules is not None
    absence = rules.absence_rules.model_copy(update={"daily_divisor_method": method})
    work = rules.model_copy(update={"absence_rules": absence})
    return _COMMERCIO.model_copy(update={"work_rules": work})


def _terms(ccnl: CCNL = _COMMERCIO, **changes: object) -> HourlyTerms:
    values: dict[str, object] = {"ccnl": ccnl, "chain": _CHAIN}
    values.update(changes)
    return HourlyTerms(**values)  # type: ignore[arg-type]


def _absence(working_days: int | None = None) -> AbsenceEvent:
    return AbsenceEvent(_DAY, Decimal(4), working_days=working_days)


def test_an_hourly_rule_deducts_the_hours() -> None:
    """by_hourly: 4 h x 1680 / 168."""
    quota = resolve_absence(
        _absence(), _terms(_with_method(DailyDivisorMethod.BY_HOURLY))
    )

    assert quota.amount == Decimal("40.00")
    assert quota.divisor == Decimal(168)


def test_a_daily_rule_needs_the_working_days() -> None:
    """by_26 without working_days: the caller states the rate."""
    with pytest.raises(InvalidInputError, match="working_days is not stated") as error:
        resolve_absence(_absence(), _terms())

    assert error.value.field == "AbsenceEvent.working_days"


def test_a_part_time_day_is_not_a_26th() -> None:
    """by_26 for a part-time worker: the caller states the rate."""
    with pytest.raises(MissingRuleError, match="part-time worker"):
        resolve_absence(_absence(1), _terms(part_time=True))


def test_a_quota_of_unstated_days_is_not_derived() -> None:
    """by_25 leaves the payable days of a month open."""
    terms = _terms(_with_method(DailyDivisorMethod.BY_25))

    with pytest.raises(MissingRuleError, match="does not derive"):
        resolve_absence(_absence(1), terms)


def test_a_ccnl_without_work_rules_has_no_verified_rule() -> None:
    """No absence rule: status none."""
    bare = _COMMERCIO.model_copy(update={"work_rules": None})

    with pytest.raises(MissingRuleError, match="status none"):
        resolve_absence(_absence(1), _terms(bare))
