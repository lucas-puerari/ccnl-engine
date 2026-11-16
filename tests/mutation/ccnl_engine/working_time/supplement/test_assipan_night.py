"""Hand oracle: the night work of the Panificazione Assipan.

CCNL 26 February 2025, art. 34 bis (PDF p. 54): "Il lavoro svolto tra le
ore 21 e fino alle ore 4, sarà compensato con una maggiorazione del 50 %
sulla retribuzione normale".  Level VI, March 2026: 1,434.02 paga base and
17.60 premio di produzione over 173 (art. 50) = 8.3909 an hour; 8 night
hours at 50% = 33.56, the hours themselves paid by the monthly pay.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.working_time.inputs import NightShiftEvent
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run


def test_eight_night_hours_add_half_the_hourly_pay() -> None:
    """The band adds the 50% alone: no hours paid apart."""
    event = NightShiftEvent(date(2026, 3, 10), hours=Decimal(8))
    result = _run(event, ccnl=("panificazione-assipan", "VI"))
    (decision,) = (d for d in result.decisions if d.capability == "night_work")
    assert (decision.amount, decision.inputs.get("hours_amount")) == (
        Decimal("33.56"),
        None,
    )
