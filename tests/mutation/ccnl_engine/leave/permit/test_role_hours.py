"""Federmeccanica art. 5: the PAR hour of the sottosettori of 1979.

"l'accordo del 1° settembre 1983 ha riconosciuto [...] un permesso
retribuito annuo di 8 ore, per i lavoratori delle imprese appartenenti ai
sottosettori [...]. Tale riduzione resta confermata per i soli lavoratori in
forza al 31 dicembre 2012" (CCNL 5 febbraio 2021, PDF p. 154).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.leave.types import LeaveBucket

if TYPE_CHECKING:
    from ccnl_engine.leave.permit.supplements import PermitExtraHours

_DAY = date(2026, 3, 1)
_ROLE = frozenset({"sottosettore_1979"})


def _rule() -> PermitExtraHours:
    rules = load_ccnl("metalmeccanico-federmeccanica").work_rules
    assert rules is not None
    assert rules.leave_rules is not None
    rol = next(p for p in rules.leave_rules.permits if p.bucket is LeaveBucket.ROL)
    return next(e for e in rol.extra_hours if e.role is not None)


@pytest.mark.parametrize(
    ("roles", "hired_on", "due"),
    [
        (_ROLE, date(2010, 5, 1), True),
        (_ROLE, date(2012, 12, 31), True),
        (_ROLE, None, True),
        (_ROLE, date(2013, 1, 1), False),
        (frozenset(), date(2010, 5, 1), False),
        (None, date(2010, 5, 1), False),
    ],
)
def test_the_hour_needs_the_role_and_service_at_the_end_of_2012(
    roles: frozenset[str] | None, hired_on: date | None, due: bool
) -> None:
    """The role and a hire by 31 December 2012."""
    rule = _rule()

    assert rule.hours == Decimal(8)
    assert rule.applies(_DAY, "general", None, roles=roles, hired_on=hired_on) is due


@pytest.mark.parametrize(
    ("roles", "hired_on", "unknown"),
    [
        (None, date(2010, 5, 1), True),
        (None, None, True),
        (None, date(2013, 1, 1), False),
        (frozenset(), date(2010, 5, 1), False),
        (_ROLE, date(2010, 5, 1), False),
    ],
)
def test_unstated_roles_are_unknown_only_for_a_possible_cohort(
    roles: frozenset[str] | None, hired_on: date | None, unknown: bool
) -> None:
    """A hire after 2012 never takes the hour: the roles do not matter."""
    rule = _rule()

    assert (
        rule.shift_fact_unknown(_DAY, "general", None, roles=roles, hired_on=hired_on)
        is unknown
    )


def test_a_rule_without_a_role_ignores_the_roles() -> None:
    """The 15-shift hours do not read the roles."""
    rules = load_ccnl("metalmeccanico-federmeccanica").work_rules
    assert rules is not None
    assert rules.leave_rules is not None
    rol = next(p for p in rules.leave_rules.permits if p.bucket is LeaveBucket.ROL)
    shifts = rol.extra_hours[0]

    assert shifts.applies(_DAY, "general", True, roles=None)
    assert not shifts.shift_fact_unknown(_DAY, "general", True, roles=None)


def test_the_yearly_hours_add_the_hour_for_the_cohort() -> None:
    """104 general hours, 112 for the cohort."""
    rules = load_ccnl("metalmeccanico-federmeccanica").work_rules
    assert rules is not None
    assert rules.leave_rules is not None
    rol = next(p for p in rules.leave_rules.permits if p.bucket is LeaveBucket.ROL)

    assert rol.hours_for(
        10, None, "general", day=_DAY, qualifying_shifts=False
    ) == Decimal(104)
    assert rol.hours_for(
        10,
        None,
        "general",
        day=_DAY,
        qualifying_shifts=False,
        roles=_ROLE,
        hired_on=date(2010, 1, 1),
    ) == Decimal(112)
