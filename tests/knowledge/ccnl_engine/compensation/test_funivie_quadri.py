"""Funivie ANEF art. 5 c. 3: the Quadri function allowance of EUR 118.79.

"A decorrere dalla data di riconoscimento per iscritto della qualifica di
quadro da parte dell'azienda, verrà corrisposta ai lavoratori interessati
una indennità di funzione di importo pari a € 118,79 mensili" (testo unico
coordinato 2025, p. 15), to the quadri chosen among levels I super and I.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.run.types import PeriodId


def _allowance(level: str, roles: frozenset[str]) -> Decimal | None:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(20)),
            period_id=PeriodId(2026, 3),
            payment_date=date(2026, 3, 27),
            ccnl_id="funivie-anef",
            level_code=level,
            opening_state=PeriodState.zero(),
            roles=roles,
            events=(),
            sector=EmploymentSector.PRIVATE,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    amounts = [i.amount for i in result.pay_items if "IND_FUNZIONE_QUADRO" in i.item_id]
    return amounts[0] if amounts else None


@pytest.mark.parametrize("level", ["1S", "1"])
def test_a_quadro_of_level_1s_or_1_is_paid_the_allowance(level: str) -> None:
    """EUR 118.79 a month with the role."""
    assert _allowance(level, frozenset({"quadro"})) == Decimal("118.79")


def test_the_level_alone_does_not_pay_it() -> None:
    """Without the written recognition (the role) there is no allowance."""
    assert _allowance("1", frozenset()) is None
