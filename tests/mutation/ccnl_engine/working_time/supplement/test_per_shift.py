"""The indennità per turn of the scuola, Tabella E1.8 (CCNL 18/1/2024).

ATA of the istituzioni educative: 17,05 for a night or a holiday turn,
34,65 for a night and holiday turn; the turns, not the hours, are paid.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.event.facade import HolidayWorkEvent, HolidayWorkKind, NightShiftEvent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.supplement.models import SupplementBand

if TYPE_CHECKING:
    from ccnl_engine.decision.models import CalculationDecision

_DAY = date(2026, 3, 19)
_ROLE = frozenset({"istituzione_educativa"})


def _decision(
    event: NightShiftEvent | HolidayWorkEvent, roles: frozenset[str] | None = _ROLE
) -> CalculationDecision:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="istruzione-ricerca-aran",
            level_code="ASSISTENTE",
            opening_state=PeriodState.zero(),
            roles=roles,
            events=(event,),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    (decision,) = (
        d for d in result.decisions if d.reason_code == "ccnl_supplement_applied"
    )
    return decision


@pytest.mark.parametrize(
    ("event", "band", "amount"),
    [
        (NightShiftEvent(_DAY, shifts=3), "SCU_TURNO_NOTTURNO", "51.15"),
        (HolidayWorkEvent(_DAY, shifts=1), "SCU_TURNO_FESTIVO", "17.05"),
        (
            HolidayWorkEvent(_DAY, kind=HolidayWorkKind.NIGHT_HOLIDAY, shifts=2),
            "SCU_TURNO_NOTTURNO_FESTIVO",
            "69.30",
        ),
    ],
)
def test_each_turn_takes_its_amount(
    event: NightShiftEvent | HolidayWorkEvent, band: str, amount: str
) -> None:
    """3 x 17,05, 1 x 17,05 and 2 x 34,65."""
    decision = _decision(event)

    assert (
        decision.inputs["band_code"],
        decision.inputs["per_shift"],
        decision.inputs["hours"],
        decision.amount,
    ) == (band, "true", Decimal(event.shifts or 0), Decimal(amount))


def test_the_turns_must_be_stated() -> None:
    """A band paid per turn rejects an event of hours only."""
    with pytest.raises(InvalidInputError, match=r"NightShiftEvent\.shifts"):
        _decision(NightShiftEvent(_DAY, hours=Decimal(8)))


def test_the_role_of_the_institution_is_needed() -> None:
    """Unstated roles: the role is missing; an ordinary school owes nothing."""
    with pytest.raises(InvalidInputError, match=r"Employment\.roles"):
        _decision(NightShiftEvent(_DAY, shifts=1), roles=None)
    with pytest.raises(MissingRuleError, match="only for the roles"):
        _decision(NightShiftEvent(_DAY, shifts=1), roles=frozenset())


def test_a_band_is_paid_per_hour_or_per_turn() -> None:
    """Both units at once are rejected."""
    band = {
        "code": "X",
        "description": "x",
        "work": "night",
        "rate": {
            "periods": [{"valid_from": "2024-01-01", "valid_until": None, "value": "1"}]
        },
        "fixed_per_hour": True,
        "per_shift": True,
        "hours_paid_apart": False,
        "provenance": {"status": "missing"},
    }
    with pytest.raises(ValueError, match="per hour or per turn"):
        SupplementBand.model_validate(band)


def test_an_event_of_turns_alone_is_valid_and_needs_something() -> None:
    """Turns alone stand for the hours; nothing at all is rejected."""
    assert NightShiftEvent(_DAY, shifts=2).hours is None
    with pytest.raises(InvalidInputError, match="turns"):
        NightShiftEvent(_DAY)
    with pytest.raises(InvalidInputError, match="shifts"):
        HolidayWorkEvent(_DAY, shifts=0)
