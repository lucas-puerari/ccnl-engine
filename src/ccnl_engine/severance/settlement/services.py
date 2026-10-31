"""TFR due at the termination and its separate taxation (artt. 17 and 19 TUIR).

A :class:`~ccnl_engine.events.TerminationTFREvent` without a caller payout
asks the engine for the TFR it pays and the tax it withholds:

- the TFR due is the fund at 31 December of the year before
  (``Employment.tfr_fund``), the quotas the runs of the termination year
  accrued with the employer (the accrual state, the run's own included)
  and the revaluation of the fund for the termination year, net of its
  17% substitute tax (art. 2120 c. 4-5 c.c., D.Lgs. 47/2000 art. 11);
- the taxable is the TFR less the revaluations already taxed at the
  substitute rate (art. 19 c. 1 TUIR): the fund less its stated
  ``revaluations``, plus the quotas of the year;
- the reference income is the taxable divided by the years and fraction
  of year of service, counted in months (art. 2120 c. 1 c.c.: a fraction
  of at least 15 days is a whole month), times 12; the average IRPEF rate
  on it, at the art. 11 brackets of the termination year, taxes the TFR.
  The offices reliquidate the tax later on the average rate of the five
  years before: the employer withholds at this rate.

The yearly revaluation of the past years was taxed at the substitute rate
when it was credited, so neither the payout nor the taxable counts it
twice.  The revaluation of the termination year for a fraction of year
(art. 2120 c. 5) needs the FOI index of the last month counted: until the
bundle holds it the TFR posted leaves the revaluation out and its decision
is incomplete, while the tax, which does not depend on it, stays final.

Not computed, with an incomplete decision and the fact or the reason in
an issue: a TFR at INPS (public TFS or TFR at INPS) or paid to a pension
fund (whose sums art. 19 c. 1 adds to the reference income; the employer
pays the share of the Fondo Tesoreria INPS, circ. 70/2007 par. 7.1); an
unknown fund or quotas of the year; a fund with advances (art. 19 c. 4,
the conguaglio of their tax); a fixed term of up to two years (the
deduction of art. 19 c. 1-ter); a termination in a year without
settlement rules, or paid in another tax year than the termination's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.employment.fact.inputs import PublicEndOfService
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.severance.settlement.decision.services import (
    _issues,
    _payout_decision,
    _tax_decision,
)
from ccnl_engine.severance.settlement.fund.services import (
    _destination_gap,
    _Fund,
    _fund,
    _quotas_before,
    _revaluation,
    _rules_of,
)
from ccnl_engine.severance.settlement.gap.models import (
    _FUND_UNKNOWN,
    _PERIOD_UNKNOWN,
    _QUOTAS_UNKNOWN,
    _Gap,
)
from ccnl_engine.severance.settlement.posting.services import _postings
from ccnl_engine.severance.settlement.tax.rules import (
    _tax_gap,
    average_rate,
    months_of_service,
)
from ccnl_engine.termination.inputs import TerminationTFREvent

if TYPE_CHECKING:
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.severance.settlement.models import TfrSettlementRules

__all__ = [
    "CAPABILITY",
    "TfrSettlement",
    "TfrSettlementEffect",
    "average_rate",
    "months_of_service",
    "settle_terminations",
    "tfr_settlement",
]

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


@dataclass(frozen=True)
class TfrSettlement:
    """The TFR due at the termination and its separate tax.

    Attributes:
        payout: TFR posted, ``None`` when not computed; without the
            revaluation of the year while :attr:`revaluation_pending`.
        payout_gap: Why the payout is not computed, ``None`` when it is.
        revaluation_pending: The revaluation of the termination year is
            not known and is left out of :attr:`payout`.
        tax: Separate tax withheld, ``None`` when not computed.
        tax_gap: Why the tax is not computed, ``None`` when it is.
        caller_rate: The rate the caller stated in place of the average
            rate, ``None`` when the engine computed it.
        inputs: Normalized inputs of the two decisions.
    """

    payout: Decimal | None
    payout_gap: _Gap | None
    revaluation_pending: bool = False
    tax: Decimal | None = None
    tax_gap: _Gap | None = None
    caller_rate: Decimal | None = None
    inputs: dict[str, Decimal | str] = field(default_factory=dict)


@dataclass(frozen=True)
class TfrSettlementEffect:
    """Items, entries, decisions and issues of the computed settlements.

    ``rate``: the rate the first settlement taxed with, which art. 19 c. 2
    TUIR applies to the other indemnities; ``None`` when none was taxed.
    """

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()
    rate: Decimal | None = None


def tfr_settlement(
    ctx: RunContext,
    event: TerminationTFREvent,
    run_quota: Decimal,
    *,
    run_to_pension_fund: bool = False,
) -> TfrSettlement:
    """Return the TFR due at the termination of ``event`` and its tax.

    Args:
        ctx: Context of the run that carries the event.
        event: The settlement, without a caller payout.
        run_quota: TFR the run itself accrued with the employer.
        run_to_pension_fund: The TFR of the run goes to a pension fund.

    Returns:
        The payout and the tax, each with the reason it is not computed.
    """
    gap = _destination_gap(ctx, run_to_pension_fund)
    if gap is not None:
        return TfrSettlement(None, gap)
    period = ctx.request.employment_period
    if period is None:
        return TfrSettlement(None, _PERIOD_UNKNOWN)
    year = event.event_date.year
    fund = _fund(ctx, year, period.started_on)
    if fund is None:
        return TfrSettlement(None, _FUND_UNKNOWN)
    before = _quotas_before(ctx, period.started_on)
    if before is None:
        return TfrSettlement(None, _QUOTAS_UNKNOWN)
    quotas = before + run_quota
    revaluation = _revaluation(ctx, fund)
    payout = fund.amount + quotas + (revaluation or _ZERO)
    rules = _rules_of(ctx, year)
    months = (
        None
        if rules is None
        else months_of_service(
            period.started_on,
            event.event_date,
            rules.service_period.month_minimum_days,
        )
    )
    inputs: dict[str, Decimal | str] = {
        "fund": fund.amount,
        "fund_year": str(year - 1),
        "quotas_before_run": before,
        "run_quota": run_quota,
        "revaluation": "not_computed" if revaluation is None else revaluation,
        "started_on": period.started_on.isoformat(),
        "ended_on": event.event_date.isoformat(),
        "months_of_service": "not_computed" if months is None else str(months),
        "years_of_service": (
            "not_computed" if months is None else Decimal(months) / _MONTHS
        ),
    }
    settlement = TfrSettlement(payout, None, revaluation is None, inputs=inputs)
    return _with_tax(settlement, (ctx, rules), fund, quotas, months, event)


def _with_tax(
    settlement: TfrSettlement,
    run: tuple[RunContext, TfrSettlementRules | None],
    fund: _Fund,
    quotas: Decimal,
    months: int | None,
    event: TerminationTFREvent,
) -> TfrSettlement:
    """Return ``settlement`` with its separate tax, or why it has none.

    Returns:
        The settlement with the taxable, the reference income, the rate
        and the tax in its inputs, or with the gap of the tax.
    """
    ctx, rules = run
    gap = _tax_gap(ctx, fund, months, event)
    if gap is not None:
        return TfrSettlement(
            settlement.payout,
            None,
            settlement.revaluation_pending,
            tax_gap=gap,
            inputs=settlement.inputs,
        )
    taxable = fund.amount - (fund.revaluations or _ZERO) + quotas
    inputs = {**settlement.inputs, "revaluations_taxed": fund.revaluations or _ZERO}
    inputs["taxable"] = taxable
    caller = event.separate_tax_rate
    if caller is not None or rules is None or months is None:
        # _tax_gap lets a settlement without rules through only with a rate.
        rate = caller or _ZERO
    else:
        brackets = ctx.contract.year_rules.irpef_brackets
        reference, rate = average_rate(taxable, months, brackets, rules)
        inputs["reference_income"] = money(reference)
        inputs["average_rate"] = rate
        inputs["brackets_year"] = str(ctx.contract.year_rules.year)
    tax = money(max(taxable, _ZERO) * rate)
    inputs["tax"] = tax
    return TfrSettlement(
        settlement.payout,
        None,
        settlement.revaluation_pending,
        tax=tax,
        caller_rate=event.separate_tax_rate,
        inputs=inputs,
    )


def _applied_rate(settlement: TfrSettlement) -> Decimal | None:
    if settlement.tax is None:
        return None
    if settlement.caller_rate is not None:
        return settlement.caller_rate
    rate = settlement.inputs.get("average_rate")
    return rate if isinstance(rate, Decimal) else None


def settle_terminations(
    ctx: RunContext, run_quota: Decimal, *, run_to_pension_fund: bool
) -> TfrSettlementEffect:
    """Return the computed TFR settlements of the run.

    Args:
        ctx: Context of the run.
        run_quota: TFR the run accrued with the employer.
        run_to_pension_fund: The TFR of the run goes to a pension fund.

    Returns:
        For each settlement event without a caller payout, its item and
        entries, its payout and tax decisions and its issues, with the ids
        the event handlers give (``<run>_evt<index>``).
    """
    effect = TfrSettlementEffect()
    for index, event in enumerate(ctx.request.events):
        if not isinstance(event, TerminationTFREvent) or not event.computed:
            continue
        settlement = tfr_settlement(
            ctx, event, run_quota, run_to_pension_fund=run_to_pension_fund
        )
        items, entries = _postings(ctx, f"{ctx.run_id}_evt{index}", settlement)
        effect = TfrSettlementEffect(
            effect.items + items,
            effect.entries + entries,
            (
                *effect.decisions,
                _payout_decision(ctx, settlement),
                _tax_decision(ctx, settlement),
            ),
            effect.issues + _issues(settlement),
            effect.rate if effect.rate is not None else _applied_rate(settlement),
        )
    return effect
