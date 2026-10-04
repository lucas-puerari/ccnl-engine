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
    SeniorityFact,
    SenioritySource,
)

_ENGINE = PayrollEngine.bundled()
_MIDPOINT = "apprenticeship_midpoint_allowances"
_APPRENTICE_SENIORITY = "apprentice_seniority"
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
                seniority=None
                if seniority is None
                else SeniorityFact(
                    seniority, date(2026, 6, 1), SenioritySource.PAYSLIP
                ),
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


@pytest.mark.parametrize(("seniority", "recorded"), [(120, True), (0, False)])
def test_apprentice_seniority_needs_matured_increments(
    seniority: int, recorded: bool
) -> None:
    """The unsourced apprentice seniority matters once increments mature."""
    result = _run(
        "turismo-confcommercio",
        "4",
        Apprentice(months_elapsed=1, track="professionalizzante_36"),
        seniority=seniority,
    )
    limitation_id = f"turismo-confcommercio/{_APPRENTICE_SENIORITY}"
    assert (limitation_id in _ids(result)) is recorded
    blockers = {(b.code, b.feature, b.detail) for b in result.blockers}
    blocker = (BlockerCode.OPEN_LIMITATION, "seniority", limitation_id)
    assert (blocker in blockers) is recorded


def test_sourced_apprentice_amount_records_no_limitation() -> None:
    """A CCNL with an apprentice amount has its apprentice rule modelled."""
    result = _run(
        "acconciatura-estetica-confartigianato",
        "3",
        Apprentice(months_elapsed=1, track="gruppo_1"),
        seniority=120,
    )
    assert not any(i.endswith(_APPRENTICE_SENIORITY) for i in _ids(result))


def test_apprentice_without_seniority_is_a_missing_fact() -> None:
    """Without the seniority the simplification cannot be ruled out.

    The level pays increments, so whether the apprentice has matured any
    is a fact: the run names it as missing instead of hiding the
    limitation behind a count of zero.
    """
    result = _run(
        "acconciatura-estetica-confartigianato",
        "3",
        Apprentice(months_elapsed=1, track="gruppo_1"),
    )
    assert (BlockerCode.MISSING_FACT, None, "seniority") in {
        (b.code, b.feature, b.detail) for b in result.blockers
    }
    assert not result.is_payable


def test_apprentice_seniority_without_level_series_is_kept() -> None:
    """A level series with no value at the date cannot show the amounts equal."""
    result = _run(
        "grafica-editoria-aieg",
        "C2",
        Apprentice(months_elapsed=0, track="triennale"),
        seniority=120,
    )
    assert f"grafica-editoria-aieg/{_APPRENTICE_SENIORITY}" in _ids(result)


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
