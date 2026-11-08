"""Holiday top-up during compulsory maternity, net of already paid shares."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.provenance.source.rule.models import RuleProvenance

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.rules import MonthPay


class MaternityHoliday(BaseModel):
    """Daily pay target for a national holiday during maternity leave."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate: Decimal = Field(gt=Decimal(0), le=Decimal(1))
    provenance: RuleProvenance


def holiday_top_up(
    rate: Decimal,
    holidays: frozenset[date],
    first: date,
    last: date,
    pay: MonthPay,
    inps_daily: Decimal,
    integration: Decimal,
    covered: int,
    covered_end: date,
) -> Decimal:
    """Return additional holiday pay after allocating monthly integration.

    Returns:
        The employer share still due on the covered weekday holidays.
    """
    covered_pay = integration / Decimal(covered) if covered else Decimal(0)
    extra = Decimal(0)
    for day in holidays:
        if first <= day <= last and day.weekday() != 6:
            paid = covered_pay if day <= covered_end else Decimal(0)
            daily_pay = pay.deducted(day, day)[1]
            extra += money(max(rate * daily_pay - inps_daily - paid, Decimal(0)))
    return extra
