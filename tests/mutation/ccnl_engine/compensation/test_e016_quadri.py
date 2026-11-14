"""Cooperazione alimentare art. 23: the quadri function allowance.

"la misura minima della indennità di funzione è di €. 120,00 (centoventi)
per i quadri di livello 1A e di €. 90,00 (novanta) per i quadri di primo
livello" (TU 2019-2023, p. 33), with "la non automaticità tra appartenenza
al livello e attribuzione della qualifica di quadro".
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
            ccnl_id="alimentaristi-cooperative-e016",
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


@pytest.mark.parametrize(("level", "amount"), [("1A", "120.00"), ("1", "90.00")])
def test_a_quadro_of_level_1a_or_1_is_paid_the_allowance(
    level: str, amount: str
) -> None:
    """EUR 120 at 1A and EUR 90 at level 1 with the role."""
    assert _allowance(level, frozenset({"quadro"})) == Decimal(amount)


def test_the_level_alone_does_not_pay_it() -> None:
    """Without the qualifica of quadro (the role) there is no allowance."""
    assert _allowance("1A", frozenset()) is None
