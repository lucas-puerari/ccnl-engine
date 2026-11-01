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
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.termination.inputs import TerminationTFREvent

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.severance.settlement.fund.services import _Fund
    from ccnl_engine.severance.settlement.models import TfrSettlementRules
    from ccnl_engine.types import Bracket

from ccnl_engine.severance.settlement.gap.models import (
    _ADVANCES,
    _ADVANCES_OVERWITHHELD,
    _ADVANCES_UNKNOWN,
    _BEFORE_2001,
    _NO_RULES,
    _REVALUATIONS_UNKNOWN,
    _Gap,
)

#: Capability of the TFR settlement, as the events name it.
CAPABILITY = "termination_tfr"
_KIND = "tfr_settlement_item"
_ZERO = Decimal(0)
_ONE = Decimal(1)
_MONTHS = 12
_AT_INPS = frozenset({PublicEndOfService.TFS, PublicEndOfService.TFR_INPS})
#: First day of the TFR taxed under D.Lgs. 47/2000 (art. 11 c. 1).
_NEW_RULES_FROM = date(2001, 1, 1)
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
        unknown or paid advances; a caller rate
        needs only the revaluations.
    """
    if fund.amount and fund.revaluations is None:
        return _REVALUATIONS_UNKNOWN
    if event.separate_tax_rate is not None:
        return None
    if months is None:
        return _NO_RULES
    return _rate_gap(ctx, fund)


def _rate_gap(ctx: RunContext, fund: _Fund) -> _Gap | None:
    """Return why the engine does not compute the rate, ``None`` when it does.

    Returns:
        The gap of an employment started before 2001 or of unknown or paid
        advances.
    """
    period = ctx.request.employment_period
    if period is not None and period.started_on < _NEW_RULES_FROM:
        return _BEFORE_2001
    if fund.advances is None:
        return _ADVANCES_UNKNOWN
    stated = fund.advances_taxable is not None and fund.advances_tax is not None
    return _ADVANCES if fund.advances and not stated else None


def separate_tax(
    run: tuple[RunContext, TfrSettlementRules | None, int | None],
    fund: _Fund,
    taxable: Decimal,
    caller: Decimal | None,
    inputs: dict[str, Decimal | str],
) -> Decimal | _Gap:
    """Return the separate tax of the TFR paid, recording how in ``inputs``.

    The rate is the average rate of the TFR of the whole employment: the
    taxable paid plus the taxable of the advances (art. 19 c. 4 TUIR:
    "considerando l'importo accantonato, aumentato delle anticipazioni");
    the tax of that whole, less the deduction of a short fixed term, less
    the tax already withheld on the advances ("salvo conguaglio all'atto
    della liquidazione definitiva"), is the tax of the payout.  A caller
    rate is applied to the taxable paid alone.

    Returns:
        The tax, or the gap of advances taxed more than the whole TFR, whose
        refund is not computed.
    """
    ctx, rules, months = run
    if caller is not None or rules is None or months is None:
        return max(_ZERO, money(max(taxable, _ZERO) * (caller or _ZERO)))
    advanced, withheld = fund.advances_taxable or _ZERO, fund.advances_tax or _ZERO
    base = taxable + advanced
    brackets = ctx.contract.year_rules.irpef_brackets
    reference, rate = average_rate(base, months, brackets, rules)
    deduction = fixed_term_deduction(ctx, rules, months)
    inputs["reference_income"] = money(reference)
    inputs["average_rate"] = rate
    inputs["brackets_year"] = str(ctx.contract.year_rules.year)
    inputs["fixed_term_deduction"] = deduction
    if advanced or withheld:
        inputs["advances_taxable"] = advanced
        inputs["advances_tax"] = withheld
    whole = max(_ZERO, money(max(base, _ZERO) * rate) - deduction)
    return _ADVANCES_OVERWITHHELD if whole < withheld else whole - withheld


def fixed_term_deduction(
    ctx: RunContext, rules: TfrSettlementRules, months: int
) -> Decimal:
    """Return the deduction of art. 19 c. 1-ter TUIR from the TFR tax.

    Returns:
        ``per_year`` times the months of service over 12 of a fixed term of
        at most ``max_months``, times the weekly over the full-time hours of
        a part time, to the cent; zero for any other employment.
    """
    deduction, request = rules.fixed_term_deduction, ctx.request
    if not isinstance(request.contract_type, FixedTerm):
        return _ZERO
    if months > deduction.max_months:
        return _ZERO
    weekly, full = request.weekly_hours, request.full_time_weekly_hours
    share = _ONE
    if weekly is not None and full is not None and weekly.value < full.value:
        share = Decimal(weekly.value) / Decimal(full.value)
    return money(deduction.per_year * months / _MONTHS * share)


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
