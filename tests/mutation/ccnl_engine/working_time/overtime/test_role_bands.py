"""Overtime bands of a role: Autoscuole art. 16 c. 6 and art. 15 c. 5.

Night overtime is paid 55%, the driving instructor's 40%; the first two
weekly overtime hours (the 40th and 41st of the 39-hour week) 15%, the third
25%, the fourth and further 30%.  At EUR 10 an hour.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import MissingRequiredFactError
from ccnl_engine.events import OvertimeEvent, OvertimeKind
from ccnl_engine.working_time.overtime.models import CCNLOvertimeBands
from ccnl_engine.working_time.overtime.policies import resolve_overtime_rate

_CCNL = load_ccnl("autoscuole-unasca")
_NIGHT = OvertimeEvent(
    date(2026, 6, 10), Decimal(1), Decimal(10), kind=OvertimeKind.NIGHT
)


@pytest.mark.parametrize(
    ("roles", "multiplier"),
    [
        (frozenset({"istruttore_guida"}), Decimal("1.40")),
        (frozenset(), Decimal("1.55")),
    ],
)
def test_the_instructor_band_replaces_the_night_band(
    roles: frozenset[str], multiplier: Decimal
) -> None:
    """40% for the instructor, 55% for every other worker."""
    bands = CCNLOvertimeBands.of(_CCNL, 2026, "2", roles=roles)
    assert resolve_overtime_rate(_NIGHT, bands).multiplier == multiplier


def test_unknown_roles_block_the_overtime_a_role_pays_apart() -> None:
    """Whether the worker is an instructor is a fact of the night overtime."""
    bands = CCNLOvertimeBands.of(_CCNL, 2026, "2", roles=None)
    with pytest.raises(MissingRequiredFactError, match=r"Employment\.roles"):
        resolve_overtime_rate(_NIGHT, bands)
    weekday = OvertimeEvent(date(2026, 6, 10), Decimal(1), Decimal(10))
    assert resolve_overtime_rate(weekday, bands).multiplier == Decimal("1.15")


def test_a_ccnl_without_role_bands_ignores_the_roles() -> None:
    """Concia has no role band: unknown roles change nothing."""
    concia = load_ccnl("concia-unic")
    assert CCNLOvertimeBands.of(concia, 2026, roles=None).bands == (
        CCNLOvertimeBands.of(concia, 2026).bands
    )


def test_the_weekly_overtime_table() -> None:
    """Hours 40-43 of the week: 15% + 15% + 25% + 30% = 10 x 4.85 = 48.50."""
    event = OvertimeEvent(
        date(2026, 6, 10),
        Decimal(4),
        Decimal(10),
        weekly_hours_before=Decimal(39),
    )
    bands = CCNLOvertimeBands.of(_CCNL, 2026, "2", roles=frozenset())
    rate = resolve_overtime_rate(event, bands)
    assert Decimal(4) * Decimal(10) * rate.multiplier == Decimal("48.50")
