"""What a cumulated sick-pay treatment rests on: unknown facts that could matter.

Bands of CCNL Federmeccanica, Sez. Quarta Titolo VI Art. 2: 122 full-pay and
183 comporto days up to 3 years of seniority, 153 and 274 over 3 years; the
chain restarts after 61 days of work; short absences of at most 5 days.
"""

from __future__ import annotations

from dataclasses import replace
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
    CumulativeTreatment,
    SicknessWorker,
)
from ccnl_engine.payroll.domain.sick_cumulation_report import cumulation_report
from ccnl_engine.payroll.domain.sickness import SicknessEpisode

_ONE = Decimal(1)
_CUMULATION = SicknessCumulation(
    window_years=3,
    reset_after_days=61,
    reduced_integration_rate=Decimal("0.80"),
    bands=(
        SicknessSeniorityBand(
            seniority_months_from=0, full_pay_days=122, comporto_days=183
        ),
        SicknessSeniorityBand(
            seniority_months_from=36, full_pay_days=153, comporto_days=274
        ),
    ),
    short_absences=ShortAbsenceReduction(
        max_days=5, from_event=4, first_days=3, rates=(Decimal("0.66"),)
    ),
)
_RULES = SicknessRules(
    carenza_integration_rate=_ONE,
    full_pay_integration_rate=_ONE,
    cumulation=_CUMULATION,
)
_KNOWN = SicknessWorker(
    seniority=SeniorityFact(12, date(2026, 1, 1), SenioritySource.PAYSLIP)
)
_MARCH = SicknessEpisode("m", date(2026, 3, 2), date(2026, 3, 13))


def _treatment(
    episode: SicknessEpisode = _MARCH,
    worker: SicknessWorker = _KNOWN,
    *earlier: SicknessEpisode,
) -> CumulativeTreatment:
    return CumulativeTreatment(_RULES, _CUMULATION, episode, earlier, worker)


def test_known_facts_and_a_short_count_rest_on_nothing() -> None:
    """Twelve days of March with the seniority and the whole history known."""
    report = cumulation_report(_treatment(), (date(2026, 3, 2), date(2026, 3, 13)))
    assert (report.chain_days, report.window_days) == (12, 12)
    assert not any((
        report.reduced,
        report.seniority_reach,
        report.band_changes,
        report.history_reach,
        report.exemption_reach,
    ))


@pytest.mark.parametrize(
    ("last", "reach"), [(date(2026, 5, 2), False), (date(2026, 5, 3), True)]
)
def test_unknown_seniority_matters_past_the_first_band(last: date, reach: bool) -> None:
    """From 1 January, 3 May is day 123, past the 122 days of the first band."""
    episode = SicknessEpisode("a", date(2026, 1, 1), last)
    report = cumulation_report(
        _treatment(episode, SicknessWorker()), (date(2026, 5, 1), last)
    )
    assert report.seniority_reach is reach


def test_the_band_can_change_within_the_days_paid() -> None:
    """35 months on 1 January are 36 on 1 February."""
    worker = SicknessWorker(
        seniority=SeniorityFact(35, date(2026, 1, 1), SenioritySource.PAYSLIP)
    )
    episode = SicknessEpisode("a", date(2026, 1, 20), date(2026, 2, 10))
    report = cumulation_report(
        _treatment(episode, worker), (date(2026, 2, 1), date(2026, 2, 10))
    )
    assert report.band_changes
    assert report.band.full_pay_days == 122


@pytest.mark.parametrize(
    ("span", "reduced"),
    [
        ((date(2026, 4, 1), date(2026, 4, 30)), False),
        ((date(2026, 5, 1), date(2026, 5, 31)), True),
        ((date(2026, 7, 3), date(2026, 7, 31)), False),
    ],
    ids=["within_full_pay", "crosses_day_122", "past_the_comporto"],
)
def test_reduced_days_paid(span: tuple[date, date], reduced: bool) -> None:
    """From 1 January: day 123 is 3 May, day 184 (past the comporto) 3 July."""
    episode = SicknessEpisode("a", date(2026, 1, 1), span[1])
    assert cumulation_report(_treatment(episode), span).reduced is reduced


_IMPORTED = replace(_KNOWN, known_from=date(2026, 1, 1))


@pytest.mark.parametrize(
    ("worker", "reach"),
    [
        (_IMPORTED, True),
        (replace(_IMPORTED, hired_on=date(2026, 1, 1)), False),
        (replace(_IMPORTED, hired_on=date(2025, 11, 1)), False),
        (replace(_IMPORTED, hired_on=date(2025, 6, 1)), True),
    ],
    ids=["hire_unknown", "hired_on_the_first_known_day", "61_days", "214_days"],
)
def test_unknown_history_could_pass_a_threshold(
    worker: SicknessWorker, reach: bool
) -> None:
    """Twelve days of March, the episodes known from 1 January 2026.

    Hired on 1 November 2025, at most 61 days are unknown: 12 + 61 is below
    the 122 full-pay days and the 183 comporto days.  Hired on 1 June 2025,
    214 days are: 12 + 214 passes both.
    """
    span = (date(2026, 3, 2), date(2026, 3, 13))
    assert cumulation_report(_treatment(worker=worker), span).history_reach is reach


def test_a_chain_far_from_the_unknown_days_only_counts_the_comporto() -> None:
    """Hired 1 July 2025: 184 unknown days, 12 + 184 > 183, past the comporto."""
    worker = replace(_IMPORTED, hired_on=date(2025, 7, 1))
    span = (date(2026, 3, 2), date(2026, 3, 13))
    assert cumulation_report(_treatment(worker=worker), span).history_reach


def test_unknown_history_reaches_only_a_chain_it_could_link_to() -> None:
    """Hired 1 September 2025, so 122 days of 2025 are unknown.

    Known from 1 January, the March chain (2-13 March) could follow an
    unknown episode with 60 days of work: 12 + 122 = 134 is past its 122
    full-pay days.  Known from 5 January, a chain from 9 March is 63 days
    of work away from any unknown day, so it restarts, and 12 + 126 = 138
    stays within the 183 comporto days.
    """
    linked = replace(_IMPORTED, hired_on=date(2025, 9, 1))
    span = (date(2026, 3, 2), date(2026, 3, 13))
    assert cumulation_report(_treatment(worker=linked), span).history_reach
    late = SicknessEpisode("m", date(2026, 3, 9), date(2026, 3, 20))
    unlinked = replace(linked, known_from=date(2026, 1, 5))
    report = cumulation_report(
        _treatment(late, unlinked), (date(2026, 3, 9), date(2026, 3, 20))
    )
    assert not report.history_reach


def test_short_absences_before_the_known_history_could_reduce_one() -> None:
    """Known from 1 February: January could hold three short absences."""
    worker = replace(_KNOWN, known_from=date(2026, 2, 1), hired_on=date(2026, 1, 1))
    short = SicknessEpisode("s", date(2026, 3, 2), date(2026, 3, 3))
    report = cumulation_report(
        _treatment(short, worker), (date(2026, 3, 2), date(2026, 3, 3))
    )
    assert report.history_reach


def test_an_exemption_unstated_where_it_matters() -> None:
    """The fourth short absence of the year without its exemption stated."""
    earlier = tuple(
        SicknessEpisode(
            f"s{k}",
            date(2026, 2, 2 + 7 * k),
            date(2026, 2, 3 + 7 * k),
            short_absence_exempt=False,
        )
        for k in range(3)
    )
    short = SicknessEpisode("s", date(2026, 3, 2), date(2026, 3, 3))
    report = cumulation_report(
        _treatment(short, _KNOWN, *earlier), (date(2026, 3, 2), date(2026, 3, 3))
    )
    assert report.exemption_reach
