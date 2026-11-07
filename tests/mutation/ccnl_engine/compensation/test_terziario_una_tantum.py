"""The una tantum of the Terziario Confesercenti renewal of 22 March 2024 (p. 50).

"suddivisibile in 15 quote mensili [...] nel periodo che va dal 1° gennaio
2022 al 31 marzo 2023", paid "la prima rata [...] con la retribuzione di
luglio 2024, la seconda rata [...] con la retribuzione di luglio 2025";
level IV 175,00 an installment.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.una_tantum.rules import una_tantum_events
from ccnl_engine.inputs import EmploymentPeriod, Permanent
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest

_TERZIARIO = load_ccnl("terziario-confesercenti")


def _paid(hired: date, year: int) -> Decimal:
    request = cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            period_id=PeriodId(year=year, month=7),
            payment_date=date(year, 7, 27),
            level_code="IV",
            employment_period=EmploymentPeriod(hired),
            weekly_hours=None,
            full_time_weekly_hours=None,
            contract_type=Permanent(),
        ),
    )
    events, _ = una_tantum_events(request, _TERZIARIO, RunKind.REGULAR)
    return sum((e.amount for e in events), Decimal(0))


def test_a_worker_of_the_whole_period_takes_both_installments() -> None:
    """175.00 in July 2024 and July 2025."""
    assert (_paid(date(2020, 1, 1), 2024), _paid(date(2020, 1, 1), 2025)) == (
        Decimal("175.00"),
        Decimal("175.00"),
    )


def test_a_hire_of_january_2023_takes_three_fifteenths() -> None:
    """January to March 2023: 3 of 15 months, 35.00."""
    assert _paid(date(2023, 1, 1), 2024) == Decimal("35.00")


def test_a_hire_after_signature_takes_nothing() -> None:
    """Not in force on 22 March 2024."""
    assert _paid(date(2024, 4, 1), 2024) == 0
