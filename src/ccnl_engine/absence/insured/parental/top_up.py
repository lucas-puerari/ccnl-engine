"""CCNL supplement to the statutory parental leave indemnity."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.provenance.source.rule.models import RuleProvenance

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.models import MaternityRules
    from ccnl_engine.absence.insured.parental.inputs import ParentalLeaveEvent

__all__ = ["ParentalTopUp", "sixth_month_days"]


class ParentalTopUp(BaseModel):
    """Employer supplement capped by days previously supplemented.

    ``only_standard_rate`` excludes enhanced statutory months. Three months
    are represented as 90 days under the INPS thirty-day convention.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate: Annotated[Decimal, Field(gt=Decimal(0), le=Decimal(1))]
    max_days: int = Field(ge=1)
    valid_from: date | None = None
    only_standard_rate: bool = False
    provenance: RuleProvenance


def sixth_month_days(
    event: ParentalLeaveEvent, days: list[date], rules: MaternityRules | None
) -> tuple[list[date], bool]:
    """Select parental days in the 30 days after compulsory maternity.

    Returns:
        The covered days and whether a potentially covered leave lacks the
        end date needed to identify them.
    """
    if rules is None:
        return [], False
    if event.protection_ended_on is None:
        return [], event.started_on <= event.child_born_on + timedelta(days=180)
    first = event.protection_ended_on + timedelta(days=1)
    last = event.protection_ended_on + timedelta(days=rules.next_integration_days or 0)
    return [day for day in days if first <= day <= last], False


def sixth_month_integration(
    days: list[date],
    rates: dict[date, Decimal | None],
    daily: Decimal,
    rules: MaternityRules | None,
) -> Decimal:
    """Return the nonnegative sixth-month top-up net of the INPS share.

    Returns:
        Employer integration on eligible parental days, rounded to cents.
    """
    if rules is None:
        return Decimal(0)
    rate = rules.next_integration_rate or Decimal(0)
    return money(
        sum(
            (max(Decimal(0), (rate - (rates[day] or 0)) * daily) for day in days),
            Decimal(0),
        )
    )
