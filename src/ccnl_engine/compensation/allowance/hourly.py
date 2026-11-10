"""Pay role allowances quoted per hour on hours paid in a run."""

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.errors import MissingRequiredFactError
from ccnl_engine.pay_item.rounding.policies import money


def pay_hourly_allowances(
    chain: MonthlyPayChain, hours: Decimal | None, as_of: date
) -> MonthlyPayChain:
    """Replace zero monthly placeholders with the per-hour earned amounts.

    Returns:
        A chain with hourly allowances earned on the stated paid hours;
        without hours, no hourly amount is inferred. The caller applies this
        only after deciding that the run posts the month's pay.

    Raises:
        MissingRequiredFactError: An active hourly allowance has no paid hours.
    """
    if hours is None:
        if any(a.hourly is not None for a, _ in chain.allowances):
            msg = "hourly role allowance requires paid hours in PeriodFacts"
            raise MissingRequiredFactError(msg, feature="base_salary")
        return chain
    return replace(
        chain,
        allowances=tuple(
            (a, money(a.hourly.value_at(as_of) * hours) if a.hourly else value)
            for a, value in chain.allowances
        ),
    )
