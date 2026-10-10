"""Cumulated CCNL sick pay: treatment chain, three-year comporto, short absences.

Rules of CCNL Federmeccanica, Sez. Quarta Titolo VI Art. 2 (FIOM-CGIL text
of 5 February 2021, pp. 196-199): up to 3 years of seniority, the first 122
days of the treatment chain in full and the later ones at 80%, comporto of
183 days "riferiti alle assenze complessivamente verificatesi nei tre anni
precedenti"; the treatment "ricomincia ex novo" for sickness "intervenuto
dopo un periodo di 61 giorni di calendario dalla ripresa del servizio"; the
first three days of the fourth short absence (at most 5 days) of a calendar
year at 66%, of the fifth and later at 50%.  Every count is read off the
calendar by hand.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.sickness.models import (
    ShortAbsenceReduction,
    SicknessCumulation,
    SicknessRules,
    SicknessSeniorityBand,
)
from ccnl_engine.payroll.domain.seniority_fact import SeniorityFact, SenioritySource
from ccnl_engine.payroll.domain.sick_cumulation import (
    CcnlDay,
    CumulativeTreatment,
    ShortAbsence,
    SicknessWorker,
    window_start,
)
from ccnl_engine.payroll.domain.sickness import SicknessEpisode

_ONE = Decimal(1)
_REDUCED = Decimal("0.80")
_CUMULATION = SicknessCumulation(
    window_years=3,
    reset_after_days=61,
    reduced_integration_rate=_REDUCED,
    bands=(
        SicknessSeniorityBand(
            seniority_months_from=0, full_pay_days=122, comporto_days=183
        ),
        SicknessSeniorityBand(
            seniority_months_from=36, full_pay_days=153, comporto_days=274
        ),
    ),
    short_absences=ShortAbsenceReduction(
        max_days=5,
        from_event=4,
        first_days=3,
        rates=(Decimal("0.66"), Decimal("0.50")),
    ),
)
_RULES = SicknessRules(
    carenza_integration_rate=_ONE,
    full_pay_integration_rate=_ONE,
    cumulation=_CUMULATION,
)


def _episode(
    episode_id: str, first: date, last: date, exempt: bool | None = None
) -> SicknessEpisode:
    return SicknessEpisode(episode_id, first, last, short_absence_exempt=exempt)


def _treatment(
    episode: SicknessEpisode,
    *earlier: SicknessEpisode,
    worker: SicknessWorker | None = None,
) -> CumulativeTreatment:
    return CumulativeTreatment(
        _RULES, _CUMULATION, episode, earlier, worker or SicknessWorker()
    )


def _seniority(months: int) -> SicknessWorker:
    fact = SeniorityFact(months, date(2026, 1, 1), SenioritySource.PAYSLIP)
    return SicknessWorker(seniority=fact)


_SPRING = _episode("spring", date(2026, 1, 1), date(2026, 5, 31))


@pytest.mark.parametrize(
    ("start", "chain"),
    [(date(2026, 7, 31), 151), (date(2026, 8, 1), 0)],
    ids=["60_days_of_work", "61_days_of_work"],
)
def test_the_chain_restarts_after_61_days_of_work(start: date, chain: int) -> None:
    """Back at work on 1 June: 1 June to 30 July are 60 days, to 31 July 61.

    January to May are 31 + 28 + 31 + 30 + 31 = 151 days.
    """
    treatment = _treatment(_episode("next", start, start), _SPRING)
    assert treatment.chain[0] == chain


def test_the_window_is_the_three_years_ending_on_the_day() -> None:
    """FIOM-CGIL: sickness on 10 March 2022 counts from 11 March 2019."""
    assert window_start(date(2022, 3, 10), 3) == date(2019, 3, 11)


def test_the_window_of_29_february_starts_on_1_march() -> None:
    """2025 has no 29 February: 28 February 2025 is the day before."""
    assert window_start(date(2028, 2, 29), 3) == date(2025, 3, 1)


def test_the_window_keeps_the_days_within_three_years() -> None:
    """On 5 March 2026 the window starts on 6 March 2023: 6-10 March count."""
    old = _episode("old", date(2023, 3, 1), date(2023, 3, 10))
    treatment = _treatment(_episode("new", date(2026, 3, 4), date(2026, 3, 9)), old)
    assert treatment.window_days(date(2026, 3, 5)) == 5 + 2


def test_day_122_is_paid_in_full_and_day_123_at_80() -> None:
    """From 1 January, day 122 is 2 May and day 123 is 3 May."""
    treatment = _treatment(_SPRING)
    assert treatment.day(1, date(2026, 5, 2)).rate == _ONE
    assert treatment.day(1, date(2026, 5, 3)) == CcnlDay(False, _REDUCED, _REDUCED)
    assert treatment.first_reduced() == date(2026, 5, 3)


def test_day_184_is_past_the_comporto() -> None:
    """From 1 January, day 183 is 2 July and day 184 is 3 July."""
    long = _episode("long", date(2026, 1, 1), date(2026, 7, 31))
    treatment = _treatment(long)
    assert not treatment.day(1, date(2026, 7, 2)).beyond_comporto
    assert treatment.day(1, date(2026, 7, 3)).beyond_comporto


@pytest.mark.parametrize(
    ("months", "full_pay_days"), [(35, 122), (36, 153)], ids=["35", "36"]
)
def test_the_band_is_the_one_of_the_first_day(months: int, full_pay_days: int) -> None:
    """Months of seniority on 1 January 2026, the first day of the episode."""
    treatment = _treatment(_SPRING, worker=_seniority(months))
    assert treatment.band.full_pay_days == full_pay_days


def _shorts(*exempt: bool | None) -> tuple[SicknessEpisode, ...]:
    """Return two-day absences from the Mondays of February 2026.

    Returns:
        One episode per exemption, from 2, 9, 16 and 23 February.
    """
    return tuple(
        _episode(f"s{k}", date(2026, 2, 2 + 7 * k), date(2026, 2, 3 + 7 * k), flag)
        for k, flag in enumerate(exempt)
    )


_MARCH = date(2026, 3, 2), date(2026, 3, 3)


@pytest.mark.parametrize(
    ("earlier", "own", "expected"),
    [
        ((False, False, False), False, ShortAbsence(Decimal("0.66"))),
        ((False, False, False, False), False, ShortAbsence(Decimal("0.50"))),
        ((False, False, False), True, ShortAbsence()),
        ((False, False, False), None, ShortAbsence(unknown=True)),
        ((False, False, None), False, ShortAbsence(_ONE, unknown=True)),
        ((False, False, True), False, ShortAbsence()),
        ((False, False), None, ShortAbsence()),
    ],
    ids=[
        "fourth",
        "fifth",
        "own_exempt",
        "own_unknown",
        "earlier_unknown",
        "earlier_exempt_not_counted",
        "third",
    ],
)
def test_rank_of_a_short_absence(
    earlier: tuple[bool | None, ...], own: bool | None, expected: ShortAbsence
) -> None:
    """The absences of February rank the one of 2-3 March."""
    episode = _episode("m", *_MARCH, own)
    assert _treatment(episode, *_shorts(*earlier)).short == expected


def test_a_long_absence_is_not_short() -> None:
    """Six days are more than the five of a short absence."""
    episode = _episode("m", date(2026, 3, 2), date(2026, 3, 7), False)
    assert _treatment(episode, *_shorts(False, False, False)).short == ShortAbsence()


def test_short_absences_of_another_year_do_not_count() -> None:
    """Three absences of December 2025 leave March 2026 the first."""
    december = tuple(
        _episode(f"d{k}", date(2025, 12, 1 + 7 * k), date(2025, 12, 2 + 7 * k), False)
        for k in range(3)
    )
    episode = _episode("m", *_MARCH, False)
    assert _treatment(episode, *december).short == ShortAbsence()


def test_the_first_three_days_of_a_fourth_short_absence_are_reduced() -> None:
    """Days 1-3 at 66%, waiting days included; day 4 in full."""
    episode = _episode("m", date(2026, 3, 2), date(2026, 3, 5), False)
    treatment = _treatment(episode, *_shorts(False, False, False))
    third = treatment.day(3, date(2026, 3, 4))
    assert third == CcnlDay(False, Decimal("0.66"), Decimal("0.66"))
    assert treatment.day(4, date(2026, 3, 5)).rate == _ONE
