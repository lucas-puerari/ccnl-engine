"""The exemption of the IVS share of a working mother of three or more.

L. 213/2023 art. 1 c. 180 and INPS circ. 27/2024: 100% of the IVS
contributions of the worker, up to 250 EUR a month ("€ 3.000/12"), 8.06
EUR a day "per i rapporti di lavoro instaurati o risolti nel corso del
mese", not cut for a part-time worker; permanent employments of the public
and private sectors, domestic work excluded; pay periods to 31 December
2026, until the month the youngest child turns eighteen.  UniEmens
<CodiceCausale> "ELA3".  It cuts the employee contributions, so it raises
the taxable income of the run.
"""

from __future__ import annotations

import calendar
from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contribution.exemption.inputs import EXEMPTION_FEATURE
from ccnl_engine.contribution.results import ContributionComponent
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.employment.inputs import Permanent
from ccnl_engine.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.contribution.results import ContributionBreakdown
    from ccnl_engine.period.context.services import RunContext

__all__ = [
    "MOTHERS_COMPONENT",
    "mother_cap",
    "mothers_decisions",
    "with_mother_exemption",
]

#: Component of the exemption in the INPS breakdown.
MOTHERS_COMPONENT = "mothers_ivs_exemption"
_MONTH = Decimal(250)
_DAY = Decimal("8.06")
_LAST = date(2026, 12, 31)
_FIRST = date(2024, 1, 1)
_AGE = 18
_ZERO = Decimal(0)


def mother_cap(ctx: RunContext) -> Decimal | None:
    """Return the cap of the exemption in the month of the run.

    Returns:
        250.00, or 8.06 a day of employment when it starts or ends in the
        month; ``None`` without the exemption or outside its months.

    Raises:
        InvalidInputError: For a contract that is not permanent, or domestic
            work.
    """
    exemption = ctx.request.mothers_exemption
    if exemption is None:
        return None
    if not isinstance(ctx.request.contract_type, Permanent):
        msg = "Employment.mothers_exemption: the exemption is for permanent contracts"
        raise InvalidInputError(msg, feature=EXEMPTION_FEATURE)
    if ctx.contract.year_rules.inps is None:
        msg = "Employment.mothers_exemption: domestic work takes no exemption"
        raise InvalidInputError(msg, feature=EXEMPTION_FEATURE)
    competence = ctx.contract.tctx.competence
    first = competence.replace(day=1)
    last = first.replace(day=calendar.monthrange(first.year, first.month)[1])
    born = exemption.youngest_child_born_on
    adult = date(born.year + _AGE, born.month, 1)
    if first < _FIRST or first > _LAST or first > adult:
        return None
    period = ctx.request.employment_period
    hired = first if period is None else max(first, period.started_on)
    ended = last if period is None or period.ended_on is None else period.ended_on
    left = min(last, ended)
    if hired == first and left == last:
        return _MONTH
    return _DAY * ((left - hired).days + 1)


def with_mother_exemption(
    cap: Decimal | None, breakdown: ContributionBreakdown
) -> ContributionBreakdown:
    """Return ``breakdown`` with the worker's IVS cut by the exemption.

    Returns:
        The breakdown with a negative employee component and the employee
        total cut by the IVS share, up to ``cap``; unchanged without one.
    """
    if cap is None:
        return breakdown
    ivs = next((c for c in breakdown.components if c.name == "ivs_employee"), None)
    if ivs is None or ivs.amount <= 0:
        return breakdown
    amount = min(ivs.amount, cap)
    component = ContributionComponent(MOTHERS_COMPONENT, ivs.base, -ivs.rate, -amount)
    return replace(
        breakdown,
        employee=breakdown.employee - amount,
        components=(*breakdown.components, component),
    )


def mothers_decisions(
    ctx: RunContext, breakdown: ContributionBreakdown
) -> tuple[CalculationDecision, ...]:
    """Trace the exemption of the worker's IVS share.

    Returns:
        One decision with the amount and the code ELA3 when the month falls
        within the exemption; none otherwise.
    """
    cap = mother_cap(ctx)
    if cap is None:
        return ()
    amount = -sum(
        (c.amount for c in breakdown.components if c.name == MOTHERS_COMPONENT),
        _ZERO,
    )
    return (
        CalculationDecision(
            capability=EXEMPTION_FEATURE,
            status=CalculationStatus.FINAL,
            reason_code="mothers_ivs_exemption_applied",
            rule="l-213-2023-art1-c180",
            rule_version=str(ctx.fiscal_year),
            inputs={"cap": str(cap), "code": "ELA3"},
            amount=amount,
        ),
    )
