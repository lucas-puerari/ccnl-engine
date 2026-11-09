"""Holiday top-up during compulsory maternity, net of already paid shares."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.calendar.holiday.loaders import load_national_holidays
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.provenance.source.rule.models import RuleProvenance

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.rules import MonthPay


class MaternityHoliday(BaseModel):
    """Daily pay target for a holiday during maternity leave.

    Attributes:
        rate: Share of the daily pay the holiday reaches, INPS included.
        excluded_days: Codes of the national calendar (``MM-DD``) the clause
            does not cover, e.g. ``10-04``, a holiday from 2026.
        includes_patron_saint: Whether the employer's local patron saint day
            belongs to the holiday target when the employer states its date.
        provenance: The clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate: Decimal = Field(gt=Decimal(0), le=Decimal(1))
    excluded_days: tuple[str, ...] = ()
    includes_patron_saint: bool = False
    provenance: RuleProvenance

    def holidays(
        self, first: date, last: date, patron_saint_day: str | None = None
    ) -> frozenset[date]:
        """Return the covered holidays from ``first`` to ``last``.

        Returns:
            Their dates, the excluded national codes left out, plus the
            stated local patron saint day when the clause includes it.
        """
        calendar = load_national_holidays()
        kept = tuple(h for h in calendar.holidays if h.day not in self.excluded_days)
        days = set(calendar.model_copy(update={"holidays": kept}).between(first, last))
        if self.includes_patron_saint and patron_saint_day is not None:
            month, day = (int(part) for part in patron_saint_day.split("-"))
            for year in range(first.year, last.year + 1):
                try:
                    local = date(year, month, day)
                except ValueError:  # 29 February in a non-leap year
                    continue
                if first <= local <= last:
                    days.add(local)
        return frozenset(days)


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
