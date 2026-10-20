"""Months of service and average rate of the TFR settlement.

Art. 2120 c. 1 c.c.: "computandosi come mese intero le frazioni di mese
uguali o superiori a 15 giorni".  Art. 19 c. 1 TUIR: the rate is the
average IRPEF rate of the TFR over the years of service times 12.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.severance.settlement.models import (
    TfrReferenceIncome,
    TfrSeparateTaxation,
    TfrServicePeriod,
    TfrSettlementRules,
)
from ccnl_engine.severance.settlement.services import average_rate, months_of_service
from ccnl_engine.types import Bracket

_RULES = TfrSettlementRules(
    year=2026,
    separate_taxation=TfrSeparateTaxation(),
    reference_income=TfrReferenceIncome(multiplier=Decimal(12)),
    service_period=TfrServicePeriod(month_minimum_days=15),
)
_BRACKETS = (
    Bracket(up_to=Decimal(28000), rate=Decimal("0.23")),
    Bracket(up_to=Decimal(50000), rate=Decimal("0.33")),
    Bracket(up_to=None, rate=Decimal("0.43")),
)


@pytest.mark.parametrize(
    ("started_on", "ended_on", "months"),
    [
        (date(2024, 1, 1), date(2026, 10, 31), 34),
        (date(2026, 1, 17), date(2026, 3, 31), 3),
        (date(2026, 1, 18), date(2026, 3, 31), 2),
        (date(2026, 2, 1), date(2026, 2, 28), 1),
        (date(2026, 3, 1), date(2026, 4, 14), 1),
        (date(2026, 3, 1), date(2026, 4, 15), 2),
        (date(2026, 3, 10), date(2026, 3, 20), 0),
    ],
)
def test_a_fraction_of_at_least_15_days_is_a_month(
    started_on: date, ended_on: date, months: int
) -> None:
    """Whole months count; a part month counts from its 15th day."""
    assert months_of_service(started_on, ended_on, 15) == months


def test_the_average_rate_spans_the_brackets() -> None:
    """EUR 12,000 over 48 months: reference income 36,000.

    IRPEF = 28,000 x 23% + 8,000 x 33% = 9,080; rate = 9,080 / 36,000.
    """
    reference, rate = average_rate(Decimal(12000), 48, _BRACKETS, _RULES)
    assert reference == Decimal(36000)
    assert rate == Decimal(9080) / Decimal(36000)


@pytest.mark.parametrize(("taxable", "months"), [(Decimal(0), 12), (Decimal(1), 0)])
def test_nothing_taxable_has_no_rate(taxable: Decimal, months: int) -> None:
    """No taxable or no month of service: zero income and rate."""
    assert average_rate(taxable, months, _BRACKETS, _RULES) == (Decimal(0), Decimal(0))
