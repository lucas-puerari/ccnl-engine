"""The fund of an enrolment among the funds of a CCNL, and the categories it covers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.pension_fund import PENSION_FEATURE
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.contract.domain.fund_contribution import EmployerFund
    from ccnl_engine.contract.domain.identity import CCNL

__all__ = ["check_category", "fund_of"]


def fund_of(ccnl: CCNL, code: str) -> EmployerFund:
    """Return the fund ``code`` of ``ccnl``.

    Returns:
        The fund whose code is ``code``.

    Raises:
        InvalidInputError: When the CCNL has no fund with that code.
    """
    funds = ccnl.parameters.employer_funds
    for fund in funds:
        if fund.code == code:
            return fund
    known = [f.code for f in funds]
    msg = (
        f"pension fund {code!r} is not a fund of CCNL {ccnl.meta.ccnl_id}; "
        f"its funds are {known}"
    )
    raise InvalidInputError(msg, feature=PENSION_FEATURE)


def check_category(fund: EmployerFund, category: WorkerCategory | None) -> None:
    """Reject a worker outside the categories the fund covers.

    Raises:
        InvalidInputError: When the fund is restricted and the category is
            unknown or not among those it covers.
    """
    allowed = fund.applies_to_categories
    if allowed is None or category in allowed:
        return
    msg = (
        f"pension fund {fund.code} covers the categories "
        f"{[c.value for c in allowed]}; the worker category is "
        f"{None if category is None else category.value!r}"
    )
    raise InvalidInputError(msg, feature=PENSION_FEATURE)
