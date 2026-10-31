"""A sickness episode across the end of the year and a pay rise.

Commercio level 4 (impiegato), sick from Monday 21 December 2026 to 15
February 2027: monthly pay 1,292.46 + 526.29 (contingenza, EDR, terzo
elemento) = 1,818.75 to January, 1,858.76 from the tranche of 1 February
2027 (paga base 1,332.46).  The days are deducted at a 26th of the pay of
their month; the episode keeps its day count across the runs and the
tax years, so the carenza is paid once, in December, and the 66.66% INPS
band and the 100% CCNL top-up start on its 21st day, 10 January 2027.

An operaio agricolo a tempo determinato sick across the same year end has
no CCNL top-up and nothing advanced: INPS pays him directly.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.events import SicknessEpisode
from ccnl_engine.inputs import (
    EmploymentPeriod,
    FixedTerm,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from ccnl_engine.period.services import bundled_policies, bundled_repository
from ccnl_engine.year.competence.services import calculate_competence_year
from ccnl_engine.year.tax_year.closing.rules import close_tax_year
from tests.integration.ccnl_engine.surtax.residence.builders import resident
from tests.unit.ccnl_engine.builders import year_plan

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2025, 1, 1)
_TWENTY_SIXTH = Decimal(26)


def _runs(
    ccnl: str, level: str, ended_on: date, **employment: object
) -> list[PeriodResult]:
    episode = SicknessEpisode("e1", date(2026, 12, 21), ended_on)
    months = range(1, ended_on.month + 1)
    common: Mapping[str, object] = {
        "facts": resident(),
        "employment_period": EmploymentPeriod(_HIRED, None),
        "seniority": SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
        **employment,
    }
    first = calculate_competence_year(
        year_plan(2026, ccnl, level, events={12: (episode,)}, **common),  # type: ignore[arg-type]
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    second = calculate_competence_year(
        year_plan(
            2027,
            ccnl,
            level,
            events=dict.fromkeys(months, (episode,)),
            opening_state=close_tax_year(first.period_results[-1].closing_state),
            **common,  # type: ignore[arg-type]
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    december = next(
        r
        for r in first.period_results
        if r.run is not None and r.run.month == 12 and r.run.run_kind.value == "regular"
    )
    return [december, *second.period_results[: len(months)]]


def _commercio() -> tuple[dict[str, object], ...]:
    runs = _runs(
        "commercio-confcommercio",
        "4",
        date(2027, 2, 15),
        category=WorkerCategory.IMPIEGATO,
    )
    return tuple(
        dict(next(d for d in r.decisions if d.capability == "sickness").inputs)
        for r in runs
    )


def test_the_episode_keeps_its_day_count_across_the_year() -> None:
    """Carenza in December only; day 12 on 1 January, day 21 on 10 January."""
    december, january, february = _commercio()

    assert december["segments"] == (
        "2026-12-21..2026-12-23:carenza:index=1:units=3:inps=0:worker=1;"
        "2026-12-24..2026-12-31:indemnified:index=4:units=7:inps=0.50:worker=0.75"
    )
    assert january["segments"] == (
        "2027-01-01..2027-01-09:indemnified:index=12:units=8:inps=0.50:worker=0.75;"
        "2027-01-10..2027-01-31:indemnified:index=21:units=18:inps=0.6666:worker=1"
    )
    assert february["segments"] == (
        "2027-02-01..2027-02-15:indemnified:index=43:units=13:inps=0.6666:worker=1"
    )
    assert (january["carenza_pay"], february["carenza_pay"]) == (Decimal(0),) * 2


def test_each_month_deducts_at_its_own_pay() -> None:
    """10 days of 1,818.75; the whole of January; 13 days of 1,858.76."""
    december, january, february = _commercio()
    old, new = Decimal("1818.75"), Decimal("1858.76")

    assert december["absence"] == (old * 10 / _TWENTY_SIXTH).quantize(Decimal("0.01"))
    assert december["carenza_pay"] == (old * 3 / _TWENTY_SIXTH).quantize(
        Decimal("0.01")
    )
    assert january["absence"] == old
    assert february["absence"] == (new * 13 / _TWENTY_SIXTH).quantize(Decimal("0.01"))


def test_an_agricultural_fixed_term_episode_is_paid_by_inps_alone() -> None:
    """No CCNL top-up, nothing advanced, the count carried into January."""
    runs = _runs(
        "operai-agricoli-florovivaisti",
        "Area1",
        date(2027, 1, 12),
        category=WorkerCategory.OPERAIO,
        contract_type=FixedTerm(),
    )
    december, january = (
        next(d for d in r.decisions if d.capability == "sickness").inputs for r in runs
    )

    assert january["segments"] == (
        "2027-01-01..2027-01-09:indemnified:index=12:units=8:inps=0.50:worker=0.50;"
        "2027-01-10..2027-01-12:indemnified:index=21:units=2:inps=0.6666:"
        "worker=0.6666"
    )
    for month in (december, january):
        assert (month["inps_indemnity"], month["employer_integration"]) == (
            Decimal(0),
            Decimal(0),
        )
