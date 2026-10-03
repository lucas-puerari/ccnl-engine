"""Model limitations through the public API: recorded where they apply only.

A known simplification is recorded in ``assurance.limitations`` on the runs
its predicate selects, and an open one with a monetary impact blocks the
amounts with an ``open_limitation`` blocker.  The same CCNL and level
without the triggering fact carries no such limitation.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    Apprentice,
    BlockerCode,
    EmployerProfile,
    Employment,
    Headcount,
    MonetaryImpact,
    OvertimeEvent,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
    Permanent,
    SeniorityMonths,
)

_ENGINE = PayrollEngine.bundled()
_MIDPOINT = "apprenticeship_midpoint_allowances"
_APPRENTICE_SENIORITY = "apprentice_seniority_simplified"
_CONCIA_OVERTIME = "concia-unic/higher_overtime_bands"


def _run(
    slug: str,
    level: str,
    contract_type: Apprentice | Permanent,
    *,
    seniority: int | None = None,
    facts: PeriodFacts | None = None,
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_slug=f"{slug}.json",
                level_code=level,
                contract_type=contract_type,
                seniority_months=None
                if seniority is None
                else SeniorityMonths(seniority),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=facts or PeriodFacts(),
        )
    )


def _ids(result: PeriodResult) -> set[str]:
    return {limitation.id for limitation in result.assurance.limitations}


def test_midpoint_period_records_a_blocking_limitation() -> None:
    """An apprentice paid the midpoint carries the limitation and its blocker."""
    result = _run("legno-arredamento-federlegno", "AE3", Apprentice(months_elapsed=30))
    (limitation,) = (lim for lim in result.assurance.limitations if lim.id == _MIDPOINT)
    assert limitation.monetary_impact is MonetaryImpact.YES
    assert (BlockerCode.OPEN_LIMITATION, "base_salary", _MIDPOINT) in {
        (b.code, b.feature, b.detail) for b in result.blockers
    }
    assert not result.is_payable


@pytest.mark.parametrize(
    "contract_type", [Apprentice(months_elapsed=6), Permanent()], ids=str
)
def test_midpoint_limitation_needs_the_midpoint_period(
    contract_type: Apprentice | Permanent,
) -> None:
    """Another period, or a permanent worker of the same level, is not affected."""
    result = _run("legno-arredamento-federlegno", "AE3", contract_type)
    assert _MIDPOINT not in _ids(result)
    assert all(b.detail != _MIDPOINT for b in result.blockers)


@pytest.mark.parametrize(("seniority", "recorded"), [(120, True), (None, False)])
def test_apprentice_seniority_needs_matured_increments(
    seniority: int | None, recorded: bool
) -> None:
    """The apprentice seniority simplification matters once increments mature."""
    result = _run(
        "acconciatura-estetica-confartigianato",
        "3",
        Apprentice(months_elapsed=1, track="gruppo_1"),
        seniority=seniority,
    )
    assert (_APPRENTICE_SENIORITY in _ids(result)) is recorded


def test_apprentice_seniority_without_level_series_is_kept() -> None:
    """A level series with no value at the date cannot show the amounts equal."""
    result = _run(
        "grafica-editoria-aieg",
        "C2",
        Apprentice(months_elapsed=0, track="triennale"),
        seniority=120,
    )
    assert _APPRENTICE_SENIORITY in _ids(result)


def test_overtime_limitation_needs_overtime() -> None:
    """A work-rule limitation concerns only the runs that execute the capability."""
    ordinary = _run("concia-unic", "C1", Permanent())
    overtime = _run(
        "concia-unic",
        "C1",
        Permanent(),
        facts=PeriodFacts(
            events=(
                OvertimeEvent(
                    event_date=date(2026, 6, 10),
                    hours=Decimal(2),
                    hourly_rate=Decimal(12),
                ),
            )
        ),
    )
    assert _CONCIA_OVERTIME not in _ids(ordinary)
    assert _CONCIA_OVERTIME in _ids(overtime)
