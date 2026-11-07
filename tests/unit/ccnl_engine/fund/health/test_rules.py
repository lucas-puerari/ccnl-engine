"""Which workers a health fund covers: contract, fixed-term length, hours."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.employment.fixed_term.inputs import FixedTerm
from ccnl_engine.employment.inputs import Permanent
from ccnl_engine.fund.contractual.policies import ends_within
from ccnl_engine.fund.health.models import ContractualFund
from ccnl_engine.fund.health.rules import excluded
from ccnl_engine.inputs import EmploymentPeriod, WeeklyHours

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

_ONE = {"periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "1"}]}
_PROVENANCE = {"status": "assumed", "location": None, "note": "test"}


def _fund(**fields: object) -> ContractualFund:
    return ContractualFund.model_validate({
        "code": "fund",
        "description": "fund",
        "employer": {"monthly": _ONE},
        "provenance": _PROVENANCE,
        **fields,
    })


def _ctx(
    contract: object, ends: date | None = None, hours: int | None = None
) -> RunContext:
    return cast(
        "RunContext",
        SimpleNamespace(
            request=SimpleNamespace(
                contract_type=contract,
                employment_period=EmploymentPeriod(date(2026, 1, 15), ends),
                weekly_hours=None if hours is None else WeeklyHours(Decimal(hours)),
            )
        ),
    )


@pytest.mark.parametrize(
    ("ends", "out"),
    [(date(2027, 1, 14), True), (date(2027, 1, 15), False), (None, False)],
)
def test_a_fixed_term_must_reach_the_months(ends: date | None, out: bool) -> None:
    """Twelve months from 15 January end on 15 January of the next year."""
    fund = _fund(minimum_fixed_term_months=12)
    assert excluded(fund, _ctx(FixedTerm(renewals=0), ends)) is out


def test_the_length_binds_only_a_fixed_term() -> None:
    """A permanent contract with a stated end is not measured."""
    fund = _fund(minimum_fixed_term_months=12)
    assert excluded(fund, _ctx(Permanent(), date(2026, 3, 1))) is False


@pytest.mark.parametrize(("hours", "out"), [(18, True), (19, False), (None, False)])
def test_short_part_time_is_left_out(hours: int | None, out: bool) -> None:
    """Below the weekly hours the worker is not covered; full time is."""
    fund = _fund(minimum_weekly_hours="19")
    assert excluded(fund, _ctx(Permanent(), hours=hours)) is out


def test_a_permanent_only_fund_leaves_out_a_fixed_term() -> None:
    """The contract check comes first."""
    assert excluded(_fund(permanent_only=True), _ctx(FixedTerm(renewals=0))) is True


def test_ends_within_clamps_to_a_short_month() -> None:
    """One month from 31 January is 28 February."""
    assert ends_within(date(2026, 1, 31), date(2026, 2, 27), 1) is True
    assert ends_within(date(2026, 1, 31), date(2026, 2, 28), 1) is False
