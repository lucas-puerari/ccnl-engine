"""The night-holiday work of Federmeccanica art. 7 rows h) and i), March 2026.

Not on shifts, or a shift worker before 22: 60% (row h), 35% with a
compensatory rest (row i).  A shift worker from 22 to 6: 65% and 40%, but
60% and 35% in the gestione e manutenzione of the aziende impiantistiche
with shifts over the 24 hours (paragraph after the table, from 1 June 2013).
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.decision.models import CalculationDecision
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.facade import HolidayWorkEvent, HolidayWorkKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

_SLUG = "metalmeccanico-federmeccanica"
_DAY = date(2026, 3, 19)


def _decision(
    kind: HolidayWorkKind, roles: frozenset[str] | None
) -> CalculationDecision | PeriodResult:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id=_SLUG,
            level_code="C3",
            opening_state=PeriodState.zero(),
            roles=roles,
            events=(HolidayWorkEvent(_DAY, hours=Decimal(8), kind=kind),),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    found = [
        d
        for d in result.decisions
        if d.capability == "holiday_work" and d.reason_code == "ccnl_supplement_applied"
    ]
    return found[0] if found else result


@pytest.mark.parametrize(
    ("kind", "roles", "band", "rate"),
    [
        (HolidayWorkKind.NIGHT_HOLIDAY, None, "FED_NOTTURNO_FESTIVO", "0.60"),
        (
            HolidayWorkKind.NIGHT_HOLIDAY_COMPENSATORY_REST,
            None,
            "FED_NOTTURNO_FESTIVO_RIPOSO",
            "0.35",
        ),
        (
            HolidayWorkKind.NIGHT_HOLIDAY_SHIFT,
            frozenset(),
            "FED_NOTTURNO_FESTIVO_TURNI",
            "0.65",
        ),
        (
            HolidayWorkKind.NIGHT_HOLIDAY_SHIFT,
            frozenset({"impianti_24h"}),
            "FED_NOTTURNO_FESTIVO_TURNI_IMPIANTI",
            "0.60",
        ),
        (
            HolidayWorkKind.NIGHT_HOLIDAY_SHIFT_COMPENSATORY_REST,
            frozenset(),
            "FED_NOTTURNO_FESTIVO_RIPOSO_TURNI",
            "0.40",
        ),
        (
            HolidayWorkKind.NIGHT_HOLIDAY_SHIFT_COMPENSATORY_REST,
            frozenset({"impianti_24h"}),
            "FED_NOTTURNO_FESTIVO_RIPOSO_TURNI_IMPIANTI",
            "0.35",
        ),
    ],
)
def test_the_band_of_each_night_holiday_work(
    kind: HolidayWorkKind, roles: frozenset[str] | None, band: str, rate: str
) -> None:
    """Each kind takes its row and column; 8 hours on the hourly base."""
    decision = _decision(kind, roles)

    assert isinstance(decision, CalculationDecision)
    base = decision.inputs["hourly_base_rate"]
    assert isinstance(base, Decimal)
    expected = (Decimal(8) * Decimal(rate) * base).quantize(
        Decimal("0.01"), ROUND_HALF_UP
    )
    assert (
        decision.inputs["band_code"],
        decision.inputs["band_supplement"],
        decision.inputs["work"],
        decision.amount,
    ) == (band, Decimal(rate), kind.value, expected)


def test_a_shift_night_holiday_without_roles_names_the_roles() -> None:
    """The 24-hour plant column needs Employment.roles; no band is guessed."""
    with pytest.raises(InvalidInputError, match=r"Employment\.roles"):
        _decision(HolidayWorkKind.NIGHT_HOLIDAY_SHIFT, None)


def test_a_non_shift_night_holiday_does_not_need_the_roles() -> None:
    """Only the shift kinds have a band reserved to a role."""
    decision = _decision(HolidayWorkKind.NIGHT_HOLIDAY, None)

    assert isinstance(decision, CalculationDecision)
