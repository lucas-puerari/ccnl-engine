"""Seniority increments converted into pension fund contributions.

Previambiente art. 65 lett. A) bis: a new hire may opt for "la conversione
del trattamento degli aumenti periodici di anzianità [...] in misure
contributive"; the increments are no longer paid, and the employer pays the
fund "l'importo mensile corrispondente all'aumento periodico [...]
maggiorato del 10% e riproporzionato su 12 mensilità", which is "non [...]
computat[o] ad alcun effetto [...] ivi compreso il TFR".
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._seniority import seniority_months_at
from ccnl_engine.payroll.domain.pension_fund import (
    PENSION_FEATURE,
    PensionFundEnrolment,
)
from ccnl_engine.payroll.service.pension_fund_lookup import fund_of
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.fund_contribution import SeniorityConversion
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest

__all__ = ["converted_seniority", "seniority_conversion"]

_ZERO = Decimal(0)


def seniority_conversion(
    ccnl: CCNL, request: PeriodCalculationRequest
) -> SeniorityConversion | None:
    """Return the conversion the worker opted for, if any.

    Returns:
        The conversion of the fund, ``None`` when the worker did not opt.

    Raises:
        InvalidInputError: When the worker opted and the fund has none.
    """
    enrolment = request.pension_fund
    if (
        not isinstance(enrolment, PensionFundEnrolment)
        or not enrolment.seniority_to_fund
    ):
        return None
    conversion = fund_of(ccnl, enrolment.fund_code).seniority_conversion
    if conversion is None:
        msg = (
            f"pension fund {enrolment.fund_code} converts no seniority "
            "increment: seniority_to_fund must be False"
        )
        raise InvalidInputError(msg, feature=PENSION_FEATURE)
    return conversion


def converted_seniority(ctx: RunContext) -> Decimal:
    """Return the monthly amount the converted increments pay the fund.

    Returns:
        The increments matured (months of service over the cadence of the
        CCNL, at most the maximum of the conversion) times the amount of the
        level; zero without a conversion or a known seniority.
    """
    contract = ctx.contract
    conversion = seniority_conversion(contract.ccnl, ctx.request)
    day = contract.tctx.competence
    months = seniority_months_at(ctx.request.seniority, day)
    series = (
        None if conversion is None else conversion.by_level.get(contract.level.code)
    )
    if conversion is None or months is None or series is None:
        return _ZERO
    cadence = contract.ccnl.parameters.seniority_increments.cadence_months
    count = min(months // cadence, conversion.maximum_count)
    return series.value_at(day) * count
