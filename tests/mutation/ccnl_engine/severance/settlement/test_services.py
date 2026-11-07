"""Months of service and average rate of the TFR settlement.

Art. 2120 c. 1 c.c.: "computandosi come mese intero le frazioni di mese
uguali o superiori a 15 giorni".  Art. 19 c. 1 TUIR: the rate is the
average IRPEF rate of the TFR over the years of service times 12.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.employment.inputs import FixedTerm, Permanent
from ccnl_engine.severance.settlement.models import (
    TfrFixedTermDeduction,
    TfrReferenceIncome,
    TfrSeparateTaxation,
    TfrServicePeriod,
    TfrSettlementRules,
)
from ccnl_engine.severance.settlement.services import average_rate, months_of_service
from ccnl_engine.severance.settlement.tax.rules import fixed_term_deduction
from ccnl_engine.types import Bracket

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

_RULES = TfrSettlementRules(
    year=2026,
    separate_taxation=TfrSeparateTaxation(),
    reference_income=TfrReferenceIncome(multiplier=Decimal(12)),
    service_period=TfrServicePeriod(month_minimum_days=15),
    fixed_term_deduction=TfrFixedTermDeduction(
        per_year=Decimal("61.97"), max_months=24
    ),
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


@pytest.mark.parametrize(
    ("contract", "months", "hours", "deduction"),
    [
        # 61.97 * 20 / 12 = 103.283.
        (FixedTerm(), 20, None, "103.28"),
        # Two years, the longest term that takes it: 61.97 * 2.
        (FixedTerm(), 24, None, "123.94"),
        (FixedTerm(), 25, None, "0"),
        # Half time: 103.283 / 2 = 51.64.
        (FixedTerm(), 20, (20, 40), "51.64"),
        (FixedTerm(), 20, (40, 40), "103.28"),
        (Permanent(), 20, None, "0"),
    ],
)
def test_the_deduction_of_a_short_fixed_term(
    contract: FixedTerm | Permanent,
    months: int,
    hours: tuple[int, int] | None,
    deduction: str,
) -> None:
    """Art. 19 c. 1-ter TUIR: a fixed term of up to two years, by the month."""
    weekly, full = (None, None) if hours is None else hours
    request = SimpleNamespace(
        contract_type=contract,
        weekly_hours=None if weekly is None else SimpleNamespace(value=weekly),
        full_time_weekly_hours=None if full is None else SimpleNamespace(value=full),
    )
    ctx = cast("RunContext", SimpleNamespace(request=request))

    assert fixed_term_deduction(ctx, _RULES, months) == Decimal(deduction)
