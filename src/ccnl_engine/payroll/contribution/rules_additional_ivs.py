"""Additional 1% IVS charged to the worker (D.L. 384/1992 art. 3-ter).

INPS applies the 1% on the pay above the first pensionable band of the
year by the "criterio della mensilizzazione": each month on the pay of the
month above the band "rapportato a dodici mesi", without regard to the
annual band (circ. 6/2026 par. 5; circ. 7/2010 par. 3; msg. 5327/2015
par. 2.1).  The runs of one competence month share its threshold.  At year
end, or in the month the employment ends, the conguaglio settles the 1%
due on the pay of the year above the annual band, credit or debit to the
worker, deducting what this and the other employers already withheld
(msg. 5327/2015 par. 2.3; circ. 156/2025 par. 5).  Both stay within the
IVS massimale when it applies (circ. 6/2026 par. 6).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.contribution.results import ContributionComponent

if TYPE_CHECKING:
    from ccnl_engine.tax.contribution.models_additional_ivs import AdditionalIvsRule

__all__ = [
    "MONTHLY_COMPONENT",
    "SETTLEMENT_COMPONENT",
    "AdditionalIvsPosition",
    "additional_ivs",
]

#: Component of the 1% of a month above the monthly threshold.
MONTHLY_COMPONENT = "addizionale_1pct"
#: Component of the conguaglio of the 1% of the year.
SETTLEMENT_COMPONENT = "addizionale_1pct_conguaglio"

_ZERO = Decimal(0)


@dataclass(frozen=True)
class AdditionalIvsPosition:
    """Where a run stands toward the additional 1% IVS of its year.

    Attributes:
        month_base: INPS base this employment already declared for the
            competence month of the run, before it.
        withheld: Additional 1% withheld on the competence year before the
            run, by this and the other employments.
        settles: Whether the run settles the year: a run of competence
            December or of the month the employment ends.
    """

    month_base: Decimal = _ZERO
    withheld: Decimal = _ZERO
    settles: bool = False


def _within(base: Decimal, ceiling: Decimal | None) -> Decimal:
    return base if ceiling is None else min(base, ceiling)


def _monthly(
    rule: AdditionalIvsRule,
    period_base: Decimal,
    ytd_base: Decimal,
    ceiling: Decimal | None,
    month_base: Decimal,
) -> ContributionComponent:
    """Return the 1% of the run on the pay of its month above the threshold.

    The excess of the month is the base of the month within the massimale
    above the monthly threshold; the run takes the part of it its own base
    adds to the earlier runs of the month.

    Returns:
        The monthly component, its base the excess the run adds.
    """
    month_start = ytd_base - month_base

    def excess(month_total: Decimal) -> Decimal:
        within = _within(month_start + month_total, ceiling) - _within(
            month_start, ceiling
        )
        return max(_ZERO, within - rule.monthly_threshold)

    base = excess(month_base + period_base) - excess(month_base)
    return ContributionComponent(
        name=MONTHLY_COMPONENT,
        base=base,
        rate=rule.rate,
        amount=money(base * rule.rate),
    )


def _settlement(
    rule: AdditionalIvsRule,
    year_base: Decimal,
    ceiling: Decimal | None,
    withheld: Decimal,
) -> ContributionComponent:
    """Return the conguaglio of the 1% of the year.

    Returns:
        The settlement component: its base is the pay of the year within
        the massimale above the annual threshold, its amount the 1% of it
        less what was withheld, negative for a credit to the worker.
    """
    base = max(_ZERO, _within(year_base, ceiling) - rule.annual_threshold)
    return ContributionComponent(
        name=SETTLEMENT_COMPONENT,
        base=base,
        rate=rule.rate,
        amount=money(base * rule.rate) - withheld,
    )


def additional_ivs(
    rule: AdditionalIvsRule,
    period_base: Decimal,
    *,
    ytd_base: Decimal,
    ceiling: Decimal | None,
    position: AdditionalIvsPosition,
) -> ContributionComponent | None:
    """Return the additional 1% IVS of a run.

    Args:
        rule: Rate and thresholds of the year.
        period_base: INPS base of the run.
        ytd_base: INPS base of the competence year before the run, other
            employers included.
        ceiling: IVS massimale when it applies to the worker, else ``None``.
        position: The run's month base, the 1% already withheld and
            whether it settles the year.

    Returns:
        The monthly component, or the settlement one on a run that settles
        the year; ``None`` when its amount is zero.
    """
    component = (
        _settlement(rule, ytd_base + period_base, ceiling, position.withheld)
        if position.settles
        else _monthly(rule, period_base, ytd_base, ceiling, position.month_base)
    )
    return None if component.amount == _ZERO else component
