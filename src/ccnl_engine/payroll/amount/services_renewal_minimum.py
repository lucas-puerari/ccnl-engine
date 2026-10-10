"""Whether the minimo of a run may carry renewal increments, and the outcome.

A run pays the minimo of a table in force on its competence date.  When a
table of the level took effect within the signing window of the renewal
regime, on or before that date, the minimo may include increments of a
renewal signed within the window: the regime is assessed on it by
:func:`~ccnl_engine.payroll.amount.rules_renewal_minimum.assess_renewal_minimum`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.rules_renewal_minimum import (
    RenewalMinimum,
    RenewalMinimumAssessment,
    assess_renewal_minimum,
    renewal_table_from,
)
from ccnl_engine.payroll.event.services_allocation import worker_facts_of

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.services_run_context import RunContext

__all__ = ["renewal_minimum"]


def renewal_minimum(ctx: RunContext) -> RenewalMinimumAssessment | None:
    """Assess the renewal regime on the minimo the run pays.

    Returns:
        The assessment, or ``None`` when the employer is not a withholding
        agent (a household employer applies no substitute tax), the regime
        is not in force in the tax year, the run pays no minimo, or no
        table of the level took effect within the signing window by the
        competence date.
    """
    regime = ctx.var_pay_rules.rinnovo
    year = ctx.fiscal_year
    minimum = ctx.chain.base
    if not ctx.withholding_agent or not regime.in_force(year) or minimum <= 0:
        return None
    contract = ctx.contract
    table_from = renewal_table_from(
        contract.level.base_salary, regime, contract.tctx.competence
    )
    if table_from is None:
        return None
    return assess_renewal_minimum(
        regime,
        worker_facts_of(ctx.request, withholding_agent=True),
        year,
        RenewalMinimum(minimum=minimum, table_from=table_from),
    )
