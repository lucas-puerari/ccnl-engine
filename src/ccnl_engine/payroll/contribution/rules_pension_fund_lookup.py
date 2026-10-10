"""The fund of an enrolment among the funds of a CCNL, and the categories it covers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.contribution.inputs_pension_fund import PENSION_FEATURE

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.contract.employment.models_category import WorkerCategory
    from ccnl_engine.contract.fund.models import EmployerFund
    from ccnl_engine.contract.identity.facade import CCNL
    from ccnl_engine.contract.identity.rules_validity import TimeSeries, ValidityPeriod
    from ccnl_engine.payroll.contribution.inputs_pension_fund import (
        PensionFundEnrolment,
    )

__all__ = ["check_category", "check_tfr_only", "fund_of", "in_force"]


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


def check_tfr_only(ccnl: CCNL, enrolment: PensionFundEnrolment) -> None:
    """Reject the TFR alone of a public employee.

    Perseo Sirio and Espero: the TFR alone is conferred "esclusivamente per
    i dipendenti del settore privato"; a public employee's TFR is a notional
    accrual of INPS that follows the contributions.

    Raises:
        InvalidInputError: When the enrolment confers the TFR alone on a
            CCNL of the public administrations.
    """
    if (
        enrolment.tfr_only
        and ccnl.meta.tax_sector is TaxSector.PUBBLICA_AMMINISTRAZIONE
    ):
        msg = (
            f"pension fund {enrolment.fund_code}: a public employee cannot "
            "confer the TFR alone; state employee_rate at least the minimum"
        )
        raise InvalidInputError(msg, feature=PENSION_FEATURE)


def in_force(
    series: TimeSeries | None, day: date
) -> tuple[ValidityPeriod, Decimal] | None:
    """Return the period of ``series`` in force on ``day`` with its value.

    Returns:
        ``None`` without a series, before it starts or on a gap.
    """
    period = None if series is None else series.period_at(day)
    if period is None or period.value is None:
        return None
    return period, period.value
