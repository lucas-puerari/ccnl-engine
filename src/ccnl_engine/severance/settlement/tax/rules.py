"""Months of service, the average rate and the tax gaps of a TFR settlement."""

from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationStatus,
)
from ccnl_engine.employment.fact.inputs import PublicEndOfService
from ccnl_engine.employment.inputs import FixedTerm
from ccnl_engine.irpef.rules import _exact_marginal_tax
from ccnl_engine.termination.inputs import TerminationTFREvent

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.severance.settlement.fund.services import _Fund
    from ccnl_engine.severance.settlement.models import TfrSettlementRules
    from ccnl_engine.types import Bracket

from ccnl_engine.severance.settlement.gap.models import (
    _ADVANCES,
    _ADVANCES_UNKNOWN,
    _NO_RULES,
    _REVALUATIONS_UNKNOWN,
    _SHORT_TERM,
    _Gap,
)

#: Capability of the TFR settlement, as the events name it.
CAPABILITY = "termination_tfr"
_KIND = "tfr_settlement_item"
_ZERO = Decimal(0)
_MONTHS = 12
_AT_INPS = frozenset({PublicEndOfService.TFS, PublicEndOfService.TFR_INPS})
#: Months of service up to which a fixed term takes the art. 19 c. 1-ter deduction.
_SHORT_FIXED_TERM = 24
_FINAL = CalculationStatus.FINAL
_INCOMPLETE = CalculationStatus.INCOMPLETE


def months_of_service(started_on: date, ended_on: date, minimum_days: int) -> int:
    """Return the months of service from ``started_on`` to ``ended_on``.

    Each calendar month of the employment counts as one when the worker
    is employed every day of it or at least ``minimum_days`` days of it
    (art. 2120 c. 1 c.c.).

    Returns:
        The months, zero when ``ended_on`` precedes ``started_on``.
    """
    months = 0
    year, month = started_on.year, started_on.month
    while (year, month) <= (ended_on.year, ended_on.month):
        last = calendar.monthrange(year, month)[1]
        first_day = max(started_on, date(year, month, 1))
        last_day = min(ended_on, date(year, month, last))
        days = (last_day - first_day).days + 1
        if days == last or days >= minimum_days:
            months += 1
        year, month = (year + 1, 1) if month == _MONTHS else (year, month + 1)
    return months


def _tax_gap(
    ctx: RunContext, fund: _Fund, months: int | None, event: TerminationTFREvent
) -> _Gap | None:
    """Return why the tax is not computed, ``None`` when it is.

    Returns:
        The gap of unknown revaluations, of a year without rules, of
        unknown or paid advances or of a short fixed term; a caller rate
        needs only the revaluations.
    """
    if fund.amount and fund.revaluations is None:
        return _REVALUATIONS_UNKNOWN
    if event.separate_tax_rate is not None:
        return None
    if months is None:
        return _NO_RULES
    return _rate_gap(ctx, fund, months)


def _rate_gap(ctx: RunContext, fund: _Fund, months: int) -> _Gap | None:
    """Return why the engine does not compute the rate, ``None`` when it does.

    Returns:
        The gap of unknown or paid advances or of a short fixed term.
    """
    if fund.advances is None:
        return _ADVANCES_UNKNOWN
    if fund.advances:
        return _ADVANCES
    short = months <= _SHORT_FIXED_TERM
    if short and isinstance(ctx.request.contract_type, FixedTerm):
        return _SHORT_TERM
    return None


def average_rate(
    taxable: Decimal,
    months: int,
    brackets: Sequence[Bracket],
    rules: TfrSettlementRules,
) -> tuple[Decimal, Decimal]:
    """Return the reference income and the average rate of ``taxable``.

    Returns:
        The reference income (taxable over the years of service times the
        multiplier) and the average rate (gross IRPEF on it at the brackets
        of the year over it, not rounded); zeros without a taxable or a
        month of service.
    """
    if taxable <= _ZERO or months <= 0:
        return _ZERO, _ZERO
    years = Decimal(months) / _MONTHS
    reference = taxable * rules.reference_income.multiplier / years
    return reference, _exact_marginal_tax(reference, brackets) / reference
