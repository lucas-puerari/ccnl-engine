"""Revaluation of the TFR fund at 31 December and its substitute tax.

Art. 2120 c. 4 c.c. revalues the TFR, excluding the quota accrued in the
year, at 31 December of each year by 1.5% plus 75% of the yearly increase
of the ISTAT FOI index; D.Lgs. 47/2000 art. 11 cc. 3-4 taxes the
revaluation at 17%, charged to the fund.  Both change the TFR fund, not the
pay of the run: the revaluation is a decision of the December regular run,
never a ledger entry.  The run that ends the employment before 31 December
revalues the fund for a fraction of the year (c. 5): the fixed 1.5% for
the months of service of the year, a fraction of 15 days or more counting
as a whole month, and 75% of the increase of the index of the last month
counted over December of the year before (the coefficient ISTAT publishes
for a termination from the 15th of that month to the 14th of the next).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.employment.fact.inputs import PublicEndOfService
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.run.models import RunKind
from ccnl_engine.severance.revaluation.rules import (
    TERMINATION,
    YEAR_END,
    TfrRevaluation,
    not_computed,
    revalue,
)
from ccnl_engine.severance.services import (
    revaluation_rule_name,
    revaluation_rules,
)

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

__all__ = [
    "NO_OPENING_FUND",
    "TFR_FUND_UNKNOWN_CODE",
    "run_tfr_revaluation",
    "tfr_revaluation_decisions",
    "tfr_revaluation_issues",
]

#: Code of the issue of a revaluation whose opening fund is not known.
TFR_FUND_UNKNOWN_CODE = "tfr_fund_unknown"
#: Reason of a revaluation of an empty fund: nothing to revalue, no rule read.
NO_OPENING_FUND = "no_opening_fund"

#: Regimes of a public employee whose TFR the employer does not hold.
_AT_INPS = frozenset({PublicEndOfService.TFS, PublicEndOfService.TFR_INPS})
_UNKNOWN = "unknown"
_ZERO = Decimal(0)
_NO_FUND = Decimal("0.00")
_DECEMBER = 12


def _moment(ctx: RunContext) -> str | None:
    """Return when the run revalues the fund, ``None`` when it does not.

    A public employee under the TFS accrues no TFR, and the TFR at INPS
    is revalued by INPS (DPCM 20 dicembre 1999 art. 1 c. 6): neither run
    revalues a fund of the employer.

    Returns:
        ``termination`` on the run that closes the employment before 31
        December, ``year_end`` on the December regular run of an
        employment still in force at 31 December, ``None`` otherwise.
    """
    request, kind = ctx.request, ctx.run_kind
    if request.public_end_of_service in _AT_INPS:
        return None
    year, month = request.period_id.year, request.period_id.month
    period = request.employment_period
    ended = None if period is None else period.ended_on
    closes = kind is RunKind.TERMINATION or (
        kind is RunKind.REGULAR
        and ended is not None
        and (ended.year, ended.month) == (year, month)
    )
    if closes and ended != date(year, _DECEMBER, 31):
        return TERMINATION
    if kind is RunKind.REGULAR and month == _DECEMBER:
        return YEAR_END
    return None


def run_tfr_revaluation(ctx: RunContext) -> TfrRevaluation | None:
    """Return the revaluation of the TFR fund the run decides.

    The fund revalued is the one at 31 December of the year before
    (``Employment.tfr_fund``); an employment that starts in the year of
    the run has none.

    Returns:
        ``None`` on a run that does not revalue the fund; otherwise the
        revaluation: zero without a fund, not computed without the fact of
        the year, at termination or without the December index.
    """
    moment = _moment(ctx)
    if moment is None:
        return None
    request = ctx.request
    year = request.period_id.year
    stated = request.tfr_fund
    inputs: dict[str, Decimal | str] = {"moment": moment, "fund": _UNKNOWN}
    if stated is None:
        period = request.employment_period
        if period is None or period.started_on.year != year:
            return not_computed(moment, "required_fact_missing", inputs, missing=True)
        inputs["fund"] = _NO_FUND
        return TfrRevaluation(
            moment, NO_OPENING_FUND, CalculationStatus.FINAL, inputs, amount=_ZERO
        )
    if stated.year != year - 1:
        inputs["fund_year"] = str(stated.year)
        return not_computed(moment, "fund_of_another_year", inputs, missing=True)
    if not stated.amount:
        inputs["fund"] = stated.amount
        return TfrRevaluation(
            moment, NO_OPENING_FUND, CalculationStatus.FINAL, inputs, amount=_ZERO
        )
    rules = ctx.contract.year_rules.tfr_revaluation
    period = request.employment_period
    ended = None
    if moment == TERMINATION:
        ended = None if period is None else period.ended_on
    return revalue(moment, stated.amount, rules, year, ended)


def tfr_revaluation_decisions(ctx: RunContext) -> tuple[CalculationDecision, ...]:
    """Return the ``tfr_revaluation`` decision of the run, if it takes one.

    Returns:
        One decision on the run that revalues the fund, naming the rate
        rule of the year; nothing on any other run.
    """
    revaluation = run_tfr_revaluation(ctx)
    if revaluation is None:
        return ()
    year = ctx.request.period_id.year
    rules = ctx.contract.year_rules.tfr_revaluation
    read = revaluation_rules(rules, year)
    rule, provenance = (
        read[0]
        if read
        else (
            f"{revaluation_rule_name(rules, year)}:rate",
            None,
        )
    )
    ruleset = None if rules is None else rules.ruleset
    return (
        CalculationDecision(
            capability="tfr_revaluation",
            status=revaluation.status,
            reason_code=revaluation.reason,
            rule=rule,
            rule_version=str(year) if ruleset is None else ruleset.version,
            inputs=revaluation.inputs,
            source=(
                provenance.location if isinstance(provenance, RuleProvenance) else None
            ),
            amount=revaluation.amount,
        ),
    )


def tfr_revaluation_issues(ctx: RunContext) -> tuple[CalculationIssue, ...]:
    """Return the issue of a revaluation whose opening fund is not stated.

    Returns:
        One ``missing_fact`` issue for ``tfr_fund``, or nothing.
    """
    revaluation = run_tfr_revaluation(ctx)
    if revaluation is None or not revaluation.missing_fund:
        return ()
    year = ctx.request.period_id.year
    return (
        CalculationIssue(
            code=TFR_FUND_UNKNOWN_CODE,
            capability="tfr_revaluation",
            message=(
                f"tfr_revaluation: the TFR fund at 31 December {year - 1} is not "
                f"stated, so its revaluation at the end of {year} (art. 2120 c. 4 "
                "c.c.) is not computed: set Employment.tfr_fund"
            ),
            status=CalculationStatus.INCOMPLETE,
            fact="tfr_fund",
        ),
    )
