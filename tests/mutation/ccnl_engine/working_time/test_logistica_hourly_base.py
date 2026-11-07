"""Hand oracle: the hourly base and the holiday supplements of Logistica, March 2026.

- Art. 13 c. 8 (p. 39): "per la determinazione della retribuzione oraria, si
  divide la retribuzione mensile per 168".
- Art. 61 c. 1 (pp. 85-86): the retribuzione globale is the minimo, the
  seniority and the listed elements, among them the indennità di funzione of
  the quadri (51.65); the EDR of 2021 is not in it.
- Art. 12 c. 4 (p. 38): 50% on holiday work within the ordinary hours; "per
  il personale viaggiante il lavoro prestato di domenica e/o festivi è
  maggiorato del 50%".
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.event.facade import HolidayWorkEvent, HolidayWorkKind, OvertimeEvent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.decision.models import CalculationDecision

_LOGISTICA = "logistica-trasporto-confetra"
_VIAGGIANTE = "logistica-trasporto-confetra-viaggiante"
_HOURS = Decimal(8)


def _run(slug: str, level: str, *events: object) -> PeriodResult:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id=slug,
            level_code=level,
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=events,  # type: ignore[arg-type]
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


def _decision(
    result: PeriodResult, capability: str, reason: str
) -> CalculationDecision:
    (found,) = [
        d
        for d in result.decisions
        if d.capability == capability and d.reason_code == reason
    ]
    return found


def test_the_quadro_hour_counts_the_function_allowance_not_the_2021_edr() -> None:
    """(2574.98 + 51.65) / 168; 8 h x 50% = 62.54, 4 h x 130% = 81.30."""
    result = _run(
        _LOGISTICA,
        "Q",
        HolidayWorkEvent(date(2026, 3, 19), hours=_HOURS),
        OvertimeEvent(date(2026, 3, 10), Decimal(4)),
    )
    holiday = _decision(result, "holiday_work", "ccnl_supplement_applied")
    overtime = _decision(result, "overtime", "ccnl_hourly_rate_derived")

    assert holiday.amount == Decimal("62.54")
    assert overtime.amount == Decimal("81.30")
    assert holiday.inputs["hourly_base_monthly"] == Decimal("2626.63")
    assert "hourly_base[EDR_2021]" not in holiday.inputs


@pytest.mark.parametrize("kind", [HolidayWorkKind.SUNDAY, HolidayWorkKind.HOLIDAY])
def test_the_travelling_staff_take_half_on_sunday_and_holidays(
    kind: HolidayWorkKind,
) -> None:
    """Level L110, 1646.32 / 168: 8 h x 50% = 39.20."""
    result = _run(
        _VIAGGIANTE,
        "L110",
        HolidayWorkEvent(date(2026, 3, 15), hours=_HOURS, kind=kind),
    )

    assert _decision(result, "holiday_work", "ccnl_supplement_applied").amount == (
        Decimal("39.20")
    )


def test_the_sunday_of_the_other_workers_is_left_to_the_caller() -> None:
    """20% by day, 50% by night: the hours of the Sunday are not known."""
    with pytest.raises(MissingRuleError, match="no sunday supplement band"):
        _run(
            _LOGISTICA,
            "3",
            HolidayWorkEvent(
                date(2026, 3, 15), hours=_HOURS, kind=HolidayWorkKind.SUNDAY
            ),
        )
