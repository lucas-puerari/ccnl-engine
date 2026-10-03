"""Every bundled CCNL either computes 2026 or raises a typed engine error.

A run reads the rule series of its CCNL on the competence date.  A date
the bundle has no value for must reach the caller as
:class:`~ccnl_engine.MissingRuleError`, never as a bare ``ValueError``.
The scan covers the first level of every CCNL, every level of the CCNLs
whose pay tables start during 2026 or whose series declare a gap, each
month of 2026, without seniority, with no month of service and with a
seniority past every increment.
"""

from __future__ import annotations

from datetime import date
from functools import partial
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    CcnlEngineError,
    EmployerProfile,
    Employment,
    Headcount,
    MissingRuleError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    SeniorityFact,
    SenioritySource,
    YearInput,
)
from ccnl_engine.contract.service.discovery import list_contracts
from ccnl_engine.contract.service.loaders import load_ccnl

if TYPE_CHECKING:
    from collections.abc import Callable

    from ccnl_engine.contract.domain.identity import CCNL

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_ALL_CCNL: list[CCNL] = [load_ccnl(c.ccnl_id + ".json") for c in list_contracts()]
_YEAR_START = date(2026, 1, 1)
#: Months of service past the last increment of every CCNL.
_LONG_SERVICE = 400


def _seniorities(month: int) -> tuple[SeniorityFact | None, ...]:
    as_of = date(2026, month, 1)
    return (
        None,
        SeniorityFact(0, as_of, SenioritySource.PAYSLIP),
        SeniorityFact(_LONG_SERVICE, as_of, SenioritySource.PAYSLIP),
    )


def _scanned_levels(ccnl: CCNL) -> tuple[str, ...]:
    """Return the levels a scan of ``ccnl`` runs.

    Returns:
        Every level when a pay table starts after 1 January 2026 or a
        series declares a gap; the first level otherwise.
    """
    levels = sorted(ccnl.levels, key=lambda level: level.order)
    raw = ccnl.model_dump_json()
    late = any(lv.base_salary.periods[0].valid_from > _YEAR_START for lv in levels)
    if late or '"gap_kind":"' in raw:
        return tuple(level.code for level in levels)
    return (levels[0].code,)


def _outcome(call: Callable[[], object]) -> str | None:
    """Run ``call`` and describe a failure that is not a typed engine error.

    Returns:
        ``None`` for a result or a typed error carrying its context; the
        exception otherwise.
    """
    try:
        call()
    except MissingRuleError as error:
        located = (error.ruleset, error.feature, error.as_of, error.remediation)
        return None if None not in located else f"unlocated {error!r}"
    except CcnlEngineError:
        return None
    except Exception as error:  # noqa: BLE001 - the scan reports any leak
        return f"{type(error).__name__}: {error}"
    return None


def _period(slug: str, level: str, month: int, seniority: SeniorityFact | None) -> None:
    _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=Employment(
                ccnl_slug=slug, level_code=level, seniority=seniority
            ),
            employer=_EMPLOYER,
            facts=PeriodFacts(),
        )
    )


@pytest.mark.parametrize("ccnl", _ALL_CCNL, ids=lambda c: c.meta.ccnl_id)
def test_every_month_of_2026_is_computed_or_typed(ccnl: CCNL) -> None:
    """No run of 2026 leaks a technical exception from a series lookup."""
    slug = f"{ccnl.meta.ccnl_id}.json"
    leaks = [
        f"{level} {month:02d} {seniority}: {leak}"
        for level in _scanned_levels(ccnl)
        for month in range(1, 13)
        for seniority in _seniorities(month)
        if (leak := _outcome(partial(_period, slug, level, month, seniority)))
        is not None
    ]
    assert leaks == []


@pytest.mark.parametrize("ccnl", _ALL_CCNL, ids=lambda c: c.meta.ccnl_id)
def test_the_year_2026_is_computed_or_typed(ccnl: CCNL) -> None:
    """A full year of the first level leaks no technical exception."""
    level = min(ccnl.levels, key=lambda lv: lv.order).code
    employment = Employment(
        ccnl_slug=f"{ccnl.meta.ccnl_id}.json",
        level_code=level,
        seniority=SeniorityFact(0, _YEAR_START, SenioritySource.PAYSLIP),
    )
    request = YearInput(year=2026, employment=employment, employer=_EMPLOYER)

    assert _outcome(lambda: _ENGINE.calculate_year(request)) is None
