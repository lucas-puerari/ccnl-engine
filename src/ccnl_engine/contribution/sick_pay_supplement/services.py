"""Additional sickness contribution of the employers of an INPS regime.

INPS indemnifies the staff of some employers at the rates of a regime
(:class:`~ccnl_engine.sickness.indemnity.models.SickPayRegime`), and those
employers pay an additional sickness contribution on the INPS taxable pay:
the pubblici esercizi pay 0.77% (INPS circ. 71/1985, from D.M. 1 febbraio
1957; authorisation code 9P).  The CCNL names the regime in
``work_rules.sickness_rules.inps_regime`` and the INPS table of the year
holds the rate; the contribution is the employer's alone and is not IVS,
so the massimale does not cap it.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.contribution.results import ContributionComponent
from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.amount.types import _AmountsInput
    from ccnl_engine.contribution.results import ContributionBreakdown

__all__ = ["EMPLOYER_COMPONENT", "with_sick_pay_supplement"]

#: Component of the additional sickness contribution.
EMPLOYER_COMPONENT = "sick_pay_supplement_employer"


def with_sick_pay_supplement(
    inp: _AmountsInput, breakdown: ContributionBreakdown, base: Decimal
) -> ContributionBreakdown:
    """Return ``breakdown`` with the supplement of the regime of the CCNL.

    Args:
        inp: Input of the amounts of the run.
        breakdown: INPS breakdown of the run so far.
        base: INPS taxable pay of the run, uncapped.

    Returns:
        The breakdown with the employer component added to its total;
        ``breakdown`` when the CCNL names no regime.

    Raises:
        DataIntegrityError: When the INPS table of the year has no
            supplement for the regime the CCNL names.
    """
    regime = inp.sick_pay_regime
    if regime is None or inp.rules.inps is None:
        return breakdown
    supplement = inp.rules.inps.sick_pay_supplements.get(regime)
    if supplement is None:
        msg = (
            f"INPS rates of {inp.rules.year}: no sick_pay_supplements entry "
            f"for the regime {regime!r} the CCNL names"
        )
        raise DataIntegrityError(msg)
    amount = money(base * supplement.employer_rate)
    component = ContributionComponent(
        EMPLOYER_COMPONENT, base, supplement.employer_rate, amount
    )
    return replace(
        breakdown,
        employer=breakdown.employer + amount,
        components=(*breakdown.components, component),
    )
