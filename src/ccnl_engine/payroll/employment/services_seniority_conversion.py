"""Seniority increments converted into pension fund contributions.

Previambiente art. 65 lett. A) bis: a new hire may opt for "la conversione
del trattamento degli aumenti periodici di anzianità [...] in misure
contributive"; the increments are no longer paid, and the employer pays the
fund "l'importo mensile corrispondente all'aumento periodico [...]
maggiorato del 10% e riproporzionato su 12 mensilità", which is "non [...]
computat[o] ad alcun effetto [...] ivi compreso il TFR".  A worker already
in service may ask for it on the increments still to mature (c. 6): those
"maturati alla data di presentazione della richiesta" stay in the pay
"in cifra fissa non assorbibile", and c. 7 converts none of them.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.contribution.inputs_pension_fund import (
    PENSION_FEATURE,
    PensionFundEnrolment,
)
from ccnl_engine.payroll.contribution.rules_pension_fund_lookup import fund_of
from ccnl_engine.payroll.employment.rules_seniority import seniority_maximum
from ccnl_engine.payroll.employment.services_seniority import seniority_months_at

if TYPE_CHECKING:
    from ccnl_engine.contract.fund.models import SeniorityConversion
    from ccnl_engine.contract.identity.facade import CCNL
    from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
    from ccnl_engine.payroll.period.services_run_context import RunContext

__all__ = ["converted_seniority", "kept_seniority_months", "seniority_conversion"]

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


def kept_seniority_months(request: PeriodCalculationRequest) -> int:
    """Return the months of service whose increments stay in the pay.

    Returns:
        The months completed on the date of the request of a worker already
        in service; zero for a new hire or an unknown seniority.
    """
    enrolment = request.pension_fund
    day = (
        enrolment.seniority_converted_on
        if isinstance(enrolment, PensionFundEnrolment)
        else None
    )
    if day is None or request.seniority is None:
        return 0
    return request.seniority.months_at(day)


def converted_seniority(ctx: RunContext) -> Decimal:
    """Return the monthly amount the converted increments pay the fund.

    Returns:
        The increments matured after the request (months of service over
        the cadence of the CCNL, within the maximum of the CCNL, less those
        kept in the pay, at most the maximum of the conversion) times the
        amount of the level; zero without a conversion or a known seniority.
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
    rules = contract.ccnl.parameters.seniority_increments
    most = seniority_maximum(rules, contract.level.code, ctx.worker_category)
    kept = min(kept_seniority_months(ctx.request) // rules.cadence_months, most)
    matured = min(months // rules.cadence_months, most)
    count = min(max(matured - kept, 0), conversion.maximum_count)
    return series.value_at(day) * count
