"""Opening balance with the stated contribution base of other employers."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.calendar.tax_year.rules import TaxYearPolicy
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.withholding.schedule.models import WithholdingSchedule


def validate_tax_year(
    period_id: PeriodId,
    payment_date: date,
    opening: PeriodState,
    schedule: WithholdingSchedule | None,
) -> None:
    """Reject an opening or withholding plan outside the payment's tax year.

    Raises:
        InvalidInputError: When the opening or schedule belongs to another
            tax year, or the opening carries obligations from the future.
    """
    competence = date(period_id.year, period_id.month, 1)
    tax_year = TaxYearPolicy().attribute(competence, payment_date).tax_year
    opening_year = opening.tax_year
    if opening_year is not None and opening_year != tax_year:
        msg = (
            f"run {period_id.year}-{period_id.month:02d} paid on "
            f"{payment_date.isoformat()} belongs to tax year {tax_year} "
            f"(TUIR art. 51 c. 1), but opening_state is for tax year "
            f"{opening_year}: open the new tax year with close_tax_year() "
            "on the closing state of the last run of the previous year"
        )
        raise InvalidInputError(msg, feature="tax_year")
    latest = opening.cash.obligations.latest_tax_year
    if latest is not None and latest > tax_year:
        msg = (
            f"opening_state carries an obligation opened in {latest}, after "
            f"the tax year of the run ({tax_year})"
        )
        raise InvalidInputError(msg, feature="tax_year")
    if schedule is not None and schedule.year != tax_year:
        msg = (
            f"withholding_schedule.year ({schedule.year}) "
            f"does not match tax year ({tax_year})"
        )
        raise InvalidInputError(msg, feature="tax_year")
