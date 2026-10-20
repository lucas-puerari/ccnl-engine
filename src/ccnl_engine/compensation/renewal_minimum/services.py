"""Whether the minimo of a run may carry renewal increments, and the outcome.

A run pays the minimo of a table in force on its competence date.  When a
table of the level took effect within the signing window of the renewal
regime, on or before that date, the minimo may include increments of a
renewal signed within the window: the regime is assessed on it by
:func:`~ccnl_engine.compensation.renewal_minimum.rules.assess_renewal_minimum`.

When the CCNL lists the renewal and the table before it, the increment is
measured: :func:`renewal_settlement` takes it out of the ordinary IRPEF base
of the run and posts its substitute tax.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.renewal_minimum.rules import (
    INCREMENT_TAXED,
    RenewalMinimum,
    RenewalMinimumAssessment,
    assess_renewal_minimum,
    pre_renewal_minimum,
    qualifying_starts,
    renewal_table_from,
)
from ccnl_engine.event.allocation.services import worker_facts_of
from ccnl_engine.extra_month.settlement.services import ExtraMonthSettlement
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.ledger.remittance.models import REGIME_CODES
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _make_entry

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

__all__ = ["renewal_minimum", "renewal_settlement"]

#: Pay item kind the substitute tax on the minimo is posted against.
_KIND = "base_salary"


def renewal_minimum(ctx: RunContext) -> RenewalMinimumAssessment | None:
    """Assess the renewal regime on the minimo the run pays.

    Returns:
        The assessment, or ``None`` when the employer is not a withholding
        agent (a household employer applies no substitute tax), the regime
        is not in force in the tax year, the run pays no minimo, no table
        of the level took effect within the signing window by the
        competence date, or the CCNL lists its renewals and none signed
        within the window has started yet (its tables in the window are not
        renewals, e.g. an IPCA adjustment).
    """
    regime = ctx.var_pay_rules.rinnovo
    year = ctx.fiscal_year
    minimum = ctx.chain.base
    if not ctx.withholding_agent or not regime.in_force(year) or minimum <= 0:
        return None
    contract = ctx.contract
    competence = contract.tctx.competence
    series = contract.level.base_salary
    renewals = contract.ccnl.parameters.renewals
    table_from = renewal_table_from(series, regime, competence)
    if table_from is None or (
        renewals and not qualifying_starts(renewals, regime, competence)
    ):
        return None
    pre = pre_renewal_minimum(series, renewals, regime, competence, contract.level.code)
    return assess_renewal_minimum(
        regime,
        worker_facts_of(ctx.request, withholding_agent=True),
        year,
        RenewalMinimum(
            minimum=minimum,
            table_from=table_from,
            increment=_increment(minimum, series.value_at(competence), pre),
            pre_renewal=pre,
        ),
    )


def _increment(paid: Decimal, full: Decimal, pre: Decimal | None) -> Decimal | None:
    """Return the renewal increment inside the minimo the run pays.

    The increment of the full-time table (``full`` less ``pre``) is scaled
    like the minimo of the run, part time, proration and extra month alike.

    Returns:
        The increment to the cent, ``None`` without the table before the
        renewal.
    """
    if pre is None or full <= 0:
        return None
    return money(paid * max(full - pre, Decimal(0)) / full)


def renewal_settlement(ctx: RunContext) -> ExtraMonthSettlement:
    """Take a taxed renewal increment out of the ordinary IRPEF base.

    Returns:
        A negative IRPEF base of the increment and the ledger entry of its
        substitute tax; nothing when the increment is not taxed.
    """
    assessment = renewal_minimum(ctx)
    if assessment is None or assessment.decision.reason_code != INCREMENT_TAXED:
        return ExtraMonthSettlement()
    decision = assessment.decision
    increment = decision.inputs["increment"]
    if not isinstance(increment, Decimal) or not increment:
        return ExtraMonthSettlement()
    tax = decision.amount or Decimal(0)
    regime = ctx.var_pay_rules.rinnovo
    item_id = f"{regime.regime_id}_minimum_{ctx.run_id}"
    entry = _make_entry(
        item_id,
        item_id,
        _KIND,
        ctx.cp,
        ctx.contract.tctx.payment,
        AccountKind.SUBSTITUTE_TAX,
        tax,
        remittance_code=REGIME_CODES.get(regime.regime_id),
    )
    return ExtraMonthSettlement(entries=(entry,), irpef_base=-increment)
