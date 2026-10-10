"""Compensations of an employer whose TFR leaves the company.

D.Lgs. 252/2005 art. 10: when the TFR maturando of a worker goes to a
complementary pension fund or to the Fondo Tesoreria INPS, the employer is
exempted, in the same percentage of the TFR conferred, from the Fondo di
garanzia TFR contribution (c. 2) and from the social contributions of the
points of D.L. 203/2005 art. 8 (c. 3).  The engine models the TFR of a run
as conferred whole or kept whole, so the percentage is 100% or zero.

Both exemptions reduce the employer contributions of the run, never below
zero.  An apprentice takes the art. 8 relief only: whether the apprentice
rate includes a Fondo di garanzia share to exempt is not sourced, and the
run records the :data:`APPRENTICE_GUARANTEE_FUND` limitation.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.contribution.inputs_pension_fund import PensionFundEnrolment
from ccnl_engine.payroll.contribution.results import ContributionComponent
from ccnl_engine.payroll.employment.inputs import Apprentice
from ccnl_engine.payroll.period.services_shared import _ZERO

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.amount.types import _AmountsInput
    from ccnl_engine.payroll.contribution.results import ContributionBreakdown
    from ccnl_engine.payroll.contribution.services import TfrAccrual
    from ccnl_engine.payroll.period.services_run_context import RunContext
    from ccnl_engine.tax.severance.models import TfrCompensation

__all__ = [
    "APPRENTICE_GUARANTEE_FUND",
    "GUARANTEE_FUND_COMPONENT",
    "RELIEF_COMPONENT",
    "tfr_compensation_paths",
    "with_tfr_compensation",
]

#: Component of the Fondo di garanzia TFR exemption (D.Lgs. 252/2005 art. 10 c. 2).
GUARANTEE_FUND_COMPONENT = "tfr_guarantee_fund_exemption"
#: Component of the art. 8 D.L. 203/2005 relief (D.Lgs. 252/2005 art. 10 c. 3).
RELIEF_COMPONENT = "tfr_relief_exemption"
#: Engine limitation of an apprentice whose TFR leaves the company.
APPRENTICE_GUARANTEE_FUND = "tfr_compensation_apprentice_guarantee_fund"
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


def tfr_compensation_paths(ctx: RunContext) -> frozenset[str]:
    """Return the limitation path of an apprentice whose TFR leaves the company.

    Returns:
        :data:`APPRENTICE_GUARANTEE_FUND` when the run is of an apprentice
        whose TFR goes to a pension fund or to the Fondo Tesoreria, in a
        sector with compensations; nothing otherwise.
    """
    request = ctx.request
    if ctx.contract.year_rules.tfr.compensation is None or not isinstance(
        request.contract_type, Apprentice
    ):
        return frozenset()
    pension = request.pension_fund
    to_fund = isinstance(pension, PensionFundEnrolment) and pension.tfr_to_fund
    if to_fund or request.tfr_treasury_fund:
        return frozenset({APPRENTICE_GUARANTEE_FUND})
    return frozenset()
