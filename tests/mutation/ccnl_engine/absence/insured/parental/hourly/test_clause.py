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
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.absence.insured.parental.hourly import handlers
from ccnl_engine.absence.insured.parental.hourly.handlers import (
    HOURLY_CCNL_LIMITATION,
    _day_hours,
    _limitations,
)
from ccnl_engine.absence.insured.parental.hourly.models import ParentalHourlyClause
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import (
    HourlyParentalLeaveEvent,
    LeaveHours,
    NursingRestEvent,
    ParentalLeaveTaken,
)
from ccnl_engine.provenance.source.rule.models import (
    ProvenanceStatus,
    RuleProvenance,
)
from tests.mutation.ccnl_engine.absence.insured.parental.hourly.test_handlers import (
    _BORN,
    _leave,
)
from tests.mutation.ccnl_engine.absence.insured.parental.test_handlers import _run

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.services import InsuredTerms

_RECORD = RuleProvenance(status=ProvenanceStatus.MISSING)
_COMMERCIO = ("commercio-confcommercio", "4")
_UNRECORDED = ("consorzi-agrari-assocap", "1")


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
    """Gas-acqua: its rule is not in the bundle yet."""
    leave = replace(_leave(2, 3), local_hourly_agreement=False)
    result = _run(leave, ccnl_id=_UNRECORDED[0], level_code=_UNRECORDED[1])
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
        (False, _UNRECORDED),
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


@pytest.mark.parametrize(
    ("clause", "part_time", "hours"),
    [
        (None, None, None),
        (ParentalHourlyClause(provenance=_RECORD), None, None),
        (
            ParentalHourlyClause(
                day_hours=Decimal(6),
                effective_from=date(2026, 3, 3),
                provenance=_RECORD,
            ),
            None,
            None,
        ),
        (
            ParentalHourlyClause(day_hours=Decimal(6), provenance=_RECORD),
            None,
            Decimal(6),
        ),
        (
            ParentalHourlyClause(day_hours=Decimal(6), provenance=_RECORD),
            Decimal("0.5"),
            Decimal(6),
        ),
        (
            ParentalHourlyClause(
                day_hours=Decimal(6), part_time_scaled=True, provenance=_RECORD
            ),
            Decimal("0.5"),
            Decimal(3),
        ),
        (
            ParentalHourlyClause(
                day_hours=Decimal(6), part_time_scaled=True, provenance=_RECORD
            ),
            None,
            Decimal(6),
        ),
    ],
)
def test_the_hours_of_a_day_of_leave(
    clause: ParentalHourlyClause | None,
    part_time: Decimal | None,
    hours: Decimal | None,
) -> None:
    """In force on the first day, 2 March; scaled for a part time if the CCNL says."""
    terms = SimpleNamespace(hourly_clause=clause, part_time=part_time)
    assert _day_hours(_leave(2, 3), cast("InsuredTerms", terms)) == hours


def test_the_run_makes_the_days_with_the_ccnl_hours(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Six hours a day of leave: four hours on 2 and 3 March, then 4 on the 4th."""
    monkeypatch.setattr(handlers, "_day_hours", lambda *_: Decimal(6))
    leave = replace(_leave(2, 3, 4), local_hourly_agreement=False)
    result = _run(leave, ccnl_id=_COMMERCIO[0], level_code=_COMMERCIO[1])
    (item,) = (i for i in result.pay_items if i.kind == "maternity_item")
    assert item.absence_days == 2
    assert HOURLY_CCNL_LIMITATION not in {lim.id for lim in result.limitations}


def test_only_an_unrecorded_ccnl_takes_the_limitation() -> None:
    """A recorded rule, with hours or not, is applied."""
    clause = ParentalHourlyClause(day_hours=Decimal(6), provenance=_RECORD)
    assert HOURLY_CCNL_LIMITATION not in _limitations((), clause, unpublished=False)
    assert HOURLY_CCNL_LIMITATION in _limitations((), None, unpublished=False)


def test_an_aran_ccnl_makes_the_days_with_its_six_hours() -> None:
    """Università: 6 hours from 19 January 2024; 4 + 4 + 4 hours are 2 days."""
    leave = replace(_leave(2, 3, 4), local_hourly_agreement=False)
    result = _run(leave, ccnl_id="universita-aran", level_code="COLLABORATORE")
    (item,) = (i for i in result.pay_items if i.kind == "maternity_item")
    assert item.absence_days == 2


@pytest.mark.parametrize(
    ("clause", "day", "criterion"),
    [
        (ParentalHourlyClause(provenance=_RECORD), date(2026, 3, 2), True),
        (
            ParentalHourlyClause(regulated=True, provenance=_RECORD),
            date(2026, 3, 2),
            False,
        ),
        (
            ParentalHourlyClause(day_hours=Decimal(6), provenance=_RECORD),
            date(2026, 3, 2),
            False,
        ),
        (
            ParentalHourlyClause(
                regulated=True, effective_from=date(2026, 3, 3), provenance=_RECORD
            ),
            date(2026, 3, 2),
            True,
        ),
        (
            ParentalHourlyClause(
                regulated=True, effective_from=date(2026, 3, 3), provenance=_RECORD
            ),
            date(2026, 3, 3),
            False,
        ),
    ],
)
def test_the_criterion_applies_without_regulation(
    clause: ParentalHourlyClause, day: date, criterion: bool
) -> None:
    """Art. 32 c. 1-ter: "In caso di mancata regolamentazione [...] delle modalità"."""
    assert clause.criterion_on(day) is criterion


def test_a_regulated_ccnl_takes_the_average_day() -> None:
    """No hours of its own: a day of leave is the average daily hours."""
    terms = SimpleNamespace(
        hourly_clause=ParentalHourlyClause(regulated=True, provenance=_RECORD),
        part_time=Decimal("0.5"),
    )
    assert _day_hours(_leave(2, 3), cast("InsuredTerms", terms)) == Decimal(8)


def test_federmeccanica_takes_blocks_of_two_hours() -> None:
    """Blocks of 2 hours, art. 5: four of them on an 8-hour day are one day."""
    leave = HourlyParentalLeaveEvent(
        tuple(LeaveHours(date(2026, 3, d), Decimal(2)) for d in (2, 3, 4, 5)),
        _BORN,
        ParentalLeaveTaken(0, 0, 0),
        Decimal(8),
        protection_ended_on=date(2025, 9, 1),
        local_hourly_agreement=False,
    )
    rests = NursingRestEvent((LeaveHours(date(2026, 3, 3), Decimal(2)),), _BORN)
    result = _run(leave, rests)
    (item,) = (
        i
        for i in result.pay_items
        if i.kind == "maternity_item" and "evt0" in i.item_id
    )
    assert item.absence_days == 1
