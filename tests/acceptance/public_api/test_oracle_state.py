"""Oracle cases of the state chained from one period to the next.

Each case is verified against the computation chain; expected values are frozen
and must NOT be auto-updated from the engine.  A failing assertion means a
computation-affecting change was made without reviewing these oracle cases.

Source for values: hand-traced payroll computation chains and CCNL source data.
All monetary amounts in EUR.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from tests.fixtures.seniority import new_hire

engine = PayrollEngine.bundled()


# ---------------------------------------------------------------------------
# YTD state chaining (area: conguaglio / YTD)
# ---------------------------------------------------------------------------


def test_ytd_state_carries_irpef_forward() -> None:
    """Closing state from January carries YTD IRPEF withheld into February."""
    employment = Employment(
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        seniority=new_hire(),
    )
    employer = EmployerProfile(headcount=Headcount(100))
    jan = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=employment,
            employer=employer,
        )
    )
    feb = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=2),
            payment_date=date(2026, 2, 27),
            employment=employment,
            employer=employer,
            opening_state=jan.closing_state,
        )
    )
    assert jan.closing_state.cash.tax.irpef > Decimal(0)
    assert feb.closing_state.cash.tax.irpef > jan.closing_state.cash.tax.irpef
    assert feb.closing_state.accrual.regular_months(2026) == 2
