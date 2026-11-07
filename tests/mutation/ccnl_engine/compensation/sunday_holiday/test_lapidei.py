"""Lapidei industria art. 18: a holiday on a Sunday or the rest day pays 1/25.

"Qualora una delle festività indicate alle lettere b), c) e d) cada di
domenica o nel giorno di riposo compensativo ai sensi dell'art. 19, al
lavoratore deve essere corrisposto, in aggiunta alla normale retribuzione
mensile, l'importo di una quota giornaliera della retribuzione globale di
fatto, pari ad 1/25 della retribuzione mensile" (CCNL 2008, p. 26).  On 1
November 2026, a Sunday, the worker resting on Sunday is paid a quota.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.compensation.sunday_holiday.services import CAPABILITY
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.rest_day.inputs import Weekday
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.run.types import PeriodId

_CENT = Decimal("0.01")


def test_ognissanti_on_the_sunday_rest_pays_a_twenty_fifth() -> None:
    """The quota is the monthly pay of the run over 25."""
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(20)),
            period_id=PeriodId(2026, 11),
            payment_date=date(2026, 11, 27),
            ccnl_id="lapidei-industria",
            level_code="C",
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=(),
            sector=EmploymentSector.PRIVATE,
            weekly_rest_day=Weekday.SUNDAY,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )

    (decision,) = [d for d in result.decisions if d.capability == CAPABILITY]
    assert decision.amount is not None
    assert str(decision.inputs["days"]) == "2026-11-01"
    monthly = result.period_gross - decision.amount
    assert decision.amount == (monthly / 25).quantize(_CENT, rounding=ROUND_HALF_UP)
