"""The notice bands of a CCNL: their checks and the band of a worker."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.event.handlers import EventEffect
from ccnl_engine.inputs import SeniorityFact, SenioritySource
from ccnl_engine.termination.notice.handlers import _band as _band_of
from ccnl_engine.termination.notice.inputs import NoticeIndemnityEvent
from ccnl_engine.termination.notice.models import NoticeBand, NoticeRules, NoticeStart
from ccnl_engine.termination.notice.rules import notice_period
from ccnl_engine.termination.notice.services import NoticeTerms

_D, _R = TerminationCause.DISMISSAL, TerminationCause.RESIGNATION
_WORK = load_ccnl("metalmeccanico-federmeccanica").work_rules
assert _WORK is not None
assert _WORK.notice is not None
RULES = _WORK.notice


def _band(up: int | None, months: int = 1, days: int = 0) -> NoticeBand:
    return NoticeBand(
        levels=("A",),
        causes=(_D,),
        up_to_months=up,
        months=months,
        days=days,
        indemnity_months=Decimal(1),
    )


@pytest.mark.parametrize(
    ("bands", "match"),
    [
        ((_band(60), _band(None), _band(120)), "grow in service"),
        ((_band(60), _band(60), _band(None)), "grow in service"),
        ((_band(60),), "grow in service"),
        ((_band(None), _band(None)), "grow in service"),
    ],
)
def test_the_bands_of_a_level_grow_to_an_open_end(
    bands: tuple[NoticeBand, ...], match: str
) -> None:
    """For each level and cause: ceilings once, growing, the last open."""
    with pytest.raises(ValidationError, match=match):
        NoticeRules(bands=bands, provenance=RULES.provenance)


def test_a_band_has_a_length() -> None:
    """Zero months and zero days is no notice."""
    with pytest.raises(ValidationError, match="months or days"):
        _band(None, months=0)


def test_the_band_of_a_level_cause_and_service() -> None:
    """The ceiling is inclusive; another cause or level has none."""
    rules = NoticeRules(
        bands=(_band(60), _band(None, months=2)), provenance=RULES.provenance
    )

    assert rules.band("A", _D, 60) is rules.bands[0]
    assert rules.band("A", _D, 61) is rules.bands[1]
    assert rules.band("A", _R, 1) is None
    assert rules.band("B", _D, 1) is None


_I, _O = WorkerCategory.IMPIEGATO, WorkerCategory.OPERAIO


def _of(category: WorkerCategory, up: int | None, days: int) -> NoticeBand:
    return NoticeBand(
        levels=("A",), causes=(_D,), up_to_months=up, days=days, categories=(category,)
    )


def test_the_band_of_a_category() -> None:
    """Each category its own ladder; an unknown category matches none of them."""
    bands = (_of(_I, 36, 30), _of(_I, None, 60), _of(_O, None, 12))
    rules = NoticeRules(bands=bands, provenance=RULES.provenance)

    assert rules.band("A", _D, 36, _I) is bands[0]
    assert rules.band("A", _D, 37, _I) is bands[1]
    assert rules.band("A", _D, 200, _O) is bands[2]
    assert rules.band("A", _D, 1) is None
    assert rules.band("A", _D, 1, WorkerCategory.QUADRO) is None


def test_a_band_without_categories_serves_every_category() -> None:
    """No categories named: the band of any category, known or not."""
    rules = NoticeRules(bands=(_band(None),), provenance=RULES.provenance)
    assert rules.band("A", _D, 1, _O) is rules.bands[0]
    assert rules.band("A", _D, 1) is rules.bands[0]


def test_each_category_grows_to_an_open_end() -> None:
    """A ladder per category: the operai without an open band fail."""
    with pytest.raises(ValidationError, match=r"\(operaio\)"):
        NoticeRules(
            bands=(_of(_I, None, 30), _of(_O, 48, 12)), provenance=RULES.provenance
        )


def test_a_band_may_start_on_its_own_day() -> None:
    """The band's start overrides the CCNL's; none keeps it."""
    own = NoticeBand(levels=("A",), causes=(_D,), days=12, starts=NoticeStart.DAY_AFTER)
    assert own.starts is NoticeStart.DAY_AFTER
    assert _band(None).starts is None


@pytest.mark.parametrize(
    ("received", "months", "days", "last"),
    [
        (date(2026, 2, 28), 1, 0, date(2026, 3, 28)),
        (date(2026, 1, 31), 1, 0, date(2026, 2, 28)),
        (date(2026, 3, 10), 1, 15, date(2026, 4, 25)),
        (date(2026, 12, 20), 0, 10, date(2026, 12, 30)),
        (date(2026, 11, 30), 2, 0, date(2027, 1, 30)),
    ],
)
def test_the_notice_runs_from_the_next_day(
    received: date, months: int, days: int, last: date
) -> None:
    """Art. 2963 c.c.: the corresponding day of the last month, then days."""
    band = _band(None, months, days)
    period = notice_period(band, received)

    assert period.first_day == date.fromordinal(received.toordinal() + 1)
    assert (period.last_day, period.band) == (last, band)


@pytest.mark.parametrize(
    ("received", "first", "last"),
    [
        (date(2026, 3, 10), date(2026, 3, 16), date(2026, 5, 14)),
        (date(2026, 3, 15), date(2026, 3, 16), date(2026, 5, 14)),
        (date(2026, 3, 16), date(2026, 4, 1), date(2026, 5, 30)),
        (date(2026, 12, 20), date(2027, 1, 1), date(2027, 3, 1)),
    ],
)
def test_a_notice_from_the_first_or_the_sixteenth(
    received: date, first: date, last: date
) -> None:
    """60 days from the first 1st or 16th after the act."""
    period = notice_period(
        _band(None, months=0, days=60), received, NoticeStart.FIRST_OR_SIXTEENTH
    )

    assert (period.first_day, period.last_day, period.days) == (first, last, 60)


@pytest.mark.parametrize(
    ("months", "days", "last", "length"),
    [(2, 0, date(2026, 5, 9), 61), (0, 50, date(2026, 4, 28), 50)],
    ids=["two-months", "fifty-days"],
)
def test_a_notice_from_the_day_of_the_act(
    months: int, days: int, last: date, length: int
) -> None:
    """OOSS: the day the act is received is the first day of notice.

    2 months on 10 March run to 9 May (61 days); 50 days to 28 April.
    """
    period = notice_period(
        _band(None, months=months, days=days), date(2026, 3, 10), NoticeStart.SAME_DAY
    )

    assert (period.first_day, period.last_day) == (date(2026, 3, 10), last)
    assert period.days == length


def test_the_days_left_unworked() -> None:
    """Leaving before the notice ends leaves its last days; after, none."""
    period = notice_period(_band(None, 1), date(2026, 2, 28))

    assert period.days == 28
    assert period.unworked_days(date(2026, 3, 20)) == 8
    assert period.unworked_days(date(2026, 2, 28)) == 28
    assert period.unworked_days(date(2026, 3, 28)) == 0
    assert period.unworked_days(date(2026, 4, 2)) == 0


def test_a_level_the_ccnl_notice_omits_has_no_indemnity() -> None:
    """No band for the level: an incomplete rule issue, no amount."""
    terms = NoticeTerms(
        rules=NoticeRules(bands=(_band(None),), provenance=RULES.provenance),
        level="Z",
        seniority=SeniorityFact.since(date(2020, 1, 1), SenioritySource.PAYSLIP),
        ended_on=date(2026, 3, 31),
        ended_by=_D,
        just_cause=False,
        permanent=True,
        monthly=Decimal(2000),
        yearly_payments=Decimal(13),
        rule="ccnl/x:work_rules.notice",
        rule_version="1",
    )

    effect = _band_of(NoticeIndemnityEvent(date(2026, 3, 1)), terms)

    assert isinstance(effect, EventEffect)
    assert [(i.code, i.cause) for i in effect.issues] == [
        ("notice_band_missing", "rule")
    ]
