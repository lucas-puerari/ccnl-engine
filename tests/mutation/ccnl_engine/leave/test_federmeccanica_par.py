"""Federmeccanica PAR (renewal of 22 November 2025, Art. 5): sector and shifts."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.leave.types import LeaveBucket

if TYPE_CHECKING:
    from ccnl_engine.leave.permit.models import PermitRules


def _rol() -> PermitRules:
    rules = load_ccnl("metalmeccanico-federmeccanica").work_rules
    assert rules is not None
    assert rules.leave_rules is not None
    return next(p for p in rules.leave_rules.permits if p.bucket is LeaveBucket.ROL)


@pytest.mark.parametrize(
    ("subsector", "shifts", "hours"),
    [
        ("auto", False, "104"),
        ("auto", True, "112"),
        ("steel", False, "124"),
        ("steel", True, "124"),
    ],
    ids=["generalita", "turnista", "siderurgico", "siderurgico-turnista"],
)
def test_par_hours_by_sector_and_shifts(
    subsector: str | None, shifts: bool, hours: str
) -> None:
    """104 hours; 124 in the steel sector; 8 more on 15+ shifts outside steel."""
    day = date(2026, 3, 1)
    got = _rol().hours_for(10, subsector=subsector, day=day, qualifying_shifts=shifts)
    assert got == Decimal(hours)


def test_an_unknown_sector_names_the_fact_for_a_turnista() -> None:
    """The 8 hours exclude steel: a turnista of an unstated sector is unknown."""
    (extra,) = _rol().extra_hours
    day = date(2026, 3, 1)
    assert extra.shift_fact_unknown(day, None, shifts=True)
    assert not extra.shift_fact_unknown(day, "auto", shifts=True)
    assert not extra.shift_fact_unknown(day, "steel", shifts=True)
