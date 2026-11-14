"""Compensations of an employer whose TFR leaves the company.

D.Lgs. 252/2005 art. 10: when the TFR maturando of a worker goes to a
complementary pension fund or to the Fondo Tesoreria INPS, the employer is
exempted, in the same percentage of the TFR conferred, from the Fondo di
garanzia TFR contribution (c. 2) and from the social contributions of the
points of D.L. 203/2005 art. 8 (c. 3).  The engine models the TFR of a run
as conferred whole or kept whole, so the percentage is 100% or zero.

Both exemptions reduce the employer contributions of the run, never below
zero.  An apprentice takes the art. 8 relief only: the 10% apprentice rate
(L. 296/2006 art. 1 c. 773) is split by the D.M. 28 marzo 2007 among FPLD,
CUAF, malattia, maternità and INAIL, with no Fondo di garanzia share to
exempt (INPS circ. 108/2018 par. 3.2).
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.contribution.results import ContributionComponent
from ccnl_engine.employment.inputs import Apprentice
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _ZERO

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.amount.types import _AmountsInput
    from ccnl_engine.contribution.results import ContributionBreakdown
    from ccnl_engine.contribution.services import TfrAccrual
    from ccnl_engine.severance.models import TfrCompensation

__all__ = [
    "GUARANTEE_FUND_COMPONENT",
    "RELIEF_COMPONENT",
    "with_tfr_compensation",
]

#: Component of the Fondo di garanzia TFR exemption (D.Lgs. 252/2005 art. 10 c. 2).
GUARANTEE_FUND_COMPONENT = "tfr_guarantee_fund_exemption"
#: Component of the art. 8 D.L. 203/2005 relief (D.Lgs. 252/2005 art. 10 c. 3).
RELIEF_COMPONENT = "tfr_relief_exemption"
_EMPLOYER_BASES = ("non_ivs_employer", "ivs_employer")


def _base(breakdown: ContributionBreakdown) -> Decimal:
    """Return the INPS taxable base of the run, uncapped by the massimale.

    Returns:
        The base of the non-IVS employer component, else of the IVS one,
        else zero.
    """
    bases = {c.name: c.base for c in breakdown.components}
    return next((bases[name] for name in _EMPLOYER_BASES if name in bases), _ZERO)


def _rates(
    compensation: TfrCompensation, inp: _AmountsInput
) -> tuple[tuple[str, Decimal], ...]:
    """Return the exemptions the worker of the run takes, with their rates.

    Returns:
        ``(component, rate)`` pairs: the Fondo di garanzia exemption, except
        for an apprentice, then the art. 8 relief.
    """
    relief = ((RELIEF_COMPONENT, compensation.relief_rate),)
    if isinstance(inp.contract_type, Apprentice):
        return relief
    fund = compensation.guarantee_fund_rate_for(inp.category)
    return ((GUARANTEE_FUND_COMPONENT, fund), *relief)


def with_tfr_compensation(
    inp: _AmountsInput, breakdown: ContributionBreakdown, accrual: TfrAccrual
) -> ContributionBreakdown:
    """Return ``breakdown`` less the compensations of the TFR conferred.

    Returns:
        The breakdown with one negative employer component per exemption
        and the employer total reduced by them, never below zero; unchanged
        when the sector has no compensation rule or the TFR of the run stays
        in the company or its destination is unknown.
    """
    compensation = inp.rules.tfr.compensation
    if compensation is None or not accrual.conferred:
        return breakdown
    base = _base(breakdown)
    room = breakdown.employer
    components: list[ContributionComponent] = []
    for name, rate in _rates(compensation, inp):
        amount = min(money(base * rate), room)
        room -= amount
        components.append(ContributionComponent(name, base, -rate, -amount))
    credit = breakdown.employer - room
    if not credit:
        return breakdown
    return replace(
        breakdown, employer=room, components=(*breakdown.components, *components)
    )
