"""Revaluation of a TFR fund for a year or a fraction of it (art. 2120 c.c.).

C. 4 revalues the fund at 31 December of the year before by 1.5% plus 75%
of the yearly increase of the ISTAT FOI index; c. 5, at a termination
within the year, by the fixed 1.5% for the months of service of the year
(a fraction of 15 days or more counts as a whole month) plus 75% of the
increase of the index of the last month counted over December of the year
before.  D.Lgs. 47/2000 art. 11 cc. 3-4 taxes the revaluation at 17%.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.severance.revaluation.models import TfrRevaluationRules

__all__ = ["TERMINATION", "YEAR_END", "TfrRevaluation", "not_computed", "revalue"]

#: Moment of the December regular run of an employment in force at 31 December.
YEAR_END = "year_end"
#: Moment of the run that ends the employment before 31 December.
TERMINATION = "termination"
_ZERO = Decimal(0)
_DECEMBER = 12
#: Days of the month of a termination that count it whole (art. 2120 c. 5).
_HALF_MONTH = 15


@dataclass(frozen=True)
class TfrRevaluation:
    """The revaluation a run decided, and why.

    Attributes:
        moment: ``year_end`` on the December regular run, ``termination``
            on the run that ends the employment before 31 December.
        reason: Reason code of the decision.
        status: Final when the amount is known, incomplete otherwise.
        inputs: Normalized inputs of the decision.
        amount: Revaluation of the fund, ``None`` when not computed.
        missing_fund: The opening fund is not stated for the year.
        substitute_tax: Substitute tax charged on :attr:`amount`.
    """

    moment: str
    reason: str
    status: CalculationStatus
    inputs: dict[str, Decimal | str]
    amount: Decimal | None = None
    missing_fund: bool = False
    substitute_tax: Decimal = _ZERO

    @property
    def net(self) -> Decimal | None:
        """Revaluation credited to the fund, net of its tax; ``None`` if unknown."""
        return None if self.amount is None else self.amount - self.substitute_tax


def not_computed(
    moment: str, reason: str, inputs: dict[str, Decimal | str], *, missing: bool
) -> TfrRevaluation:
    """Return a revaluation the run does not compute.

    Returns:
        An incomplete revaluation of ``reason``, without an amount.
    """
    return TfrRevaluation(
        moment, reason, CalculationStatus.INCOMPLETE, inputs, missing_fund=missing
    )


def _months(ended: date) -> int:
    """Return the months of the year of a termination on ``ended``.

    Returns:
        The whole months before the month of ``ended``, plus that month
        when the employment lasts 15 days or more of it (art. 2120 c. 5).
    """
    return ended.month - 1 + (1 if ended.day >= _HALF_MONTH else 0)


def _rate(
    rules: TfrRevaluationRules | None, year: int, ended: date | None
) -> Decimal | None:
    """Return the rate of the year, or of its months up to ``ended``.

    Returns:
        The annual rate at the year end, the rate of the months of the year
        at a termination; ``None`` without the rules or the index of *year*.
    """
    if rules is None or rules.year != year:
        return None
    return rules.annual_rate() if ended is None else rules.fraction_rate(_months(ended))


def _index_inputs(
    rules: TfrRevaluationRules, rate: Decimal, ended: date | None
) -> dict[str, Decimal | str]:
    """Return the decision inputs that show how the rate was built.

    Returns:
        The rate and its parts; the December index at the year end, the
        months, the last day and the index of the last month at a
        termination.
    """
    index = rules.price_index
    inputs: dict[str, Decimal | str] = {
        "fixed_rate": rules.rate.fixed,
        "index_share": rules.rate.index_share,
        "previous_december_index": index.previous_december,
        "link_coefficient": index.link_coefficient,
        "rate": rate,
    }
    if ended is None:
        inputs["december_index"] = index.december or _ZERO
        return inputs
    months = _months(ended)
    inputs |= {"months": Decimal(months), "ended_on": ended.isoformat()}
    if months:
        inputs["month_index"] = (
            index.monthly[months - 1]
            if months <= len(index.monthly)
            else index.december or _ZERO
        )
    return inputs


def revalue(
    moment: str,
    fund: Decimal,
    rules: TfrRevaluationRules | None,
    year: int,
    ended: date | None = None,
) -> TfrRevaluation:
    """Return the revaluation of a positive fund for *year*.

    Args:
        moment: When the run revalues the fund.
        fund: The fund at 31 December of the year before.
        rules: The revaluation rules of the bundle.
        year: Year of the run.
        ended: Last day of the employment, on a termination.

    Returns:
        The final revaluation, or a not-computed one when a termination has
        no last day, *year* has no rules or no index of the month (December
        at the year end), or the rate is negative (no source says how a
        negative rate applies).
    """
    inputs: dict[str, Decimal | str] = {"moment": moment, "fund": fund}
    if moment == TERMINATION and ended is None:
        return not_computed(moment, "termination_not_computed", inputs, missing=False)
    rate = _rate(rules, year, ended)
    if rules is None or rate is None:
        return not_computed(moment, "price_index_not_published", inputs, missing=False)
    inputs |= _index_inputs(rules, rate, ended)
    if rate < 0:
        return not_computed(moment, "negative_rate", inputs, missing=False)
    amount = money(fund * rate)
    tax = money(amount * rules.substitute_tax.rate)
    inputs |= {
        "substitute_tax_rate": rules.substitute_tax.rate,
        "substitute_tax": tax,
        "net_revaluation": amount - tax,
    }
    return TfrRevaluation(
        moment,
        "revalued",
        CalculationStatus.FINAL,
        inputs,
        amount=amount,
        substitute_tax=tax,
    )
