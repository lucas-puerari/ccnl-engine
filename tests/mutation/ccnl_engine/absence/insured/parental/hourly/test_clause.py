"""The CCNL rule on the parental leave by the hour.

INPS circ. 152/2015 par. 2.1: the general criterion of art. 32 c. 1-ter
D.Lgs. 151/2001 applies "in assenza di una contrattazione collettiva che
disciplini compiutamente il congedo parentale su base oraria", and with it
the leave by the hour "non può essere fruito nei medesimi giorni in cui il
genitore fruisce di riposi giornalieri per allattamento".
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.parental.hourly.handlers import (
    HOURLY_CCNL_LIMITATION,
)
from ccnl_engine.absence.insured.parental.hourly.models import ParentalHourlyClause
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import LeaveHours, NursingRestEvent
from ccnl_engine.provenance.source.rule.models import (
    ProvenanceStatus,
    RuleProvenance,
)
from tests.mutation.ccnl_engine.absence.insured.parental.hourly.test_handlers import (
    _BORN,
    _leave,
)
from tests.mutation.ccnl_engine.absence.insured.parental.test_handlers import _run

_RECORD = RuleProvenance(status=ProvenanceStatus.MISSING)
_COMMERCIO = ("commercio-confcommercio", "4")
_METAL = ("metalmeccanico-federmeccanica", "C3")


@pytest.mark.parametrize(
    ("clause", "day", "own"),
    [
        (ParentalHourlyClause(provenance=_RECORD), date(2026, 3, 2), False),
        (
            ParentalHourlyClause(day_hours=Decimal(6), provenance=_RECORD),
            date(2026, 3, 2),
            True,
        ),
        (
            ParentalHourlyClause(
                day_hours=Decimal(6),
                effective_from=date(2026, 8, 7),
                provenance=_RECORD,
            ),
            date(2026, 8, 6),
            False,
        ),
        (
            ParentalHourlyClause(
                day_hours=Decimal(6),
                effective_from=date(2026, 8, 7),
                provenance=_RECORD,
            ),
            date(2026, 8, 7),
            True,
        ),
    ],
)
def test_the_hours_of_the_ccnl_apply_from_their_date(
    clause: ParentalHourlyClause, day: date, own: bool
) -> None:
    """No hours set, or before the clause: the general criterion."""
    assert clause.sets_hours_on(day) is own


def test_a_silent_ccnl_applies_the_criterion() -> None:
    """Commercio sets no hourly rule: the limitation does not concern it."""
    work = load_ccnl("commercio-confcommercio").work_rules
    assert work is not None
    assert work.parental_hourly is not None
    assert work.parental_hourly.day_hours is None
    leave = replace(_leave(2, 3), local_hourly_agreement=False)
    result = _run(leave, ccnl_id=_COMMERCIO[0], level_code=_COMMERCIO[1])
    assert HOURLY_CCNL_LIMITATION not in {lim.id for lim in result.limitations}


def test_an_unrecorded_ccnl_keeps_the_limitation() -> None:
    """Metalmeccanico: its rule is not in the bundle yet."""
    result = _run(replace(_leave(2, 3), local_hourly_agreement=False))
    assert HOURLY_CCNL_LIMITATION in {lim.id for lim in result.limitations}


def test_no_hourly_leave_on_a_day_of_nursing_rest() -> None:
    """Under the criterion a day holding both is rejected."""
    leave = replace(_leave(2, 3), local_hourly_agreement=False)
    rests = NursingRestEvent((LeaveHours(date(2026, 3, 3), Decimal(2)),), _BORN)
    with pytest.raises(InvalidInputError, match="nursing rest"):
        _run(leave, rests, ccnl_id=_COMMERCIO[0], level_code=_COMMERCIO[1])


@pytest.mark.parametrize(
    ("agreement", "ccnl"),
    [
        (None, _COMMERCIO),
        (True, _COMMERCIO),
        (False, _METAL),
    ],
    ids=["agreement-unknown", "local-agreement", "ccnl-unrecorded"],
)
def test_the_check_needs_the_criterion(
    agreement: bool | None, ccnl: tuple[str, str]
) -> None:
    """An agreement that may allow it, or an unrecorded CCNL: not rejected."""
    leave = replace(_leave(2, 3), local_hourly_agreement=agreement)
    rests = NursingRestEvent((LeaveHours(date(2026, 3, 9), Decimal(2)),), _BORN)
    other_day = _run(leave, rests, ccnl_id=ccnl[0], level_code=ccnl[1])
    assert other_day.period_gross > 0
    same = NursingRestEvent((LeaveHours(date(2026, 3, 3), Decimal(2)),), _BORN)
    assert _run(leave, same, ccnl_id=ccnl[0], level_code=ccnl[1]).period_gross > 0
