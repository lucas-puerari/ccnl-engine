"""The decision of the una tantum a run pays from the CCNL data.

:func:`~ccnl_engine.compensation.una_tantum.rules.una_tantum_events` pays
the una tantum of the month as arrears; the run also records its own
decision, so the capability ``una_tantum`` is traced.  It is provisional:
the readings of each agreement are the open limitation
:data:`~ccnl_engine.compensation.una_tantum.rules.UNA_TANTUM`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.una_tantum.rules import una_tantum_events
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.decision.rules import _ccnl_rule

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

__all__ = ["CAPABILITY", "una_tantum_decisions"]

#: Capability of the una tantum of a renewal.
CAPABILITY = "una_tantum"


def una_tantum_decisions(ctx: RunContext) -> tuple[CalculationDecision, ...]:
    """Trace the una tantum the run meets.

    Returns:
        One provisional decision with the amount paid, nil when the
        employment is not owed it; none in a month without an installment.
    """
    request, ccnl = ctx.request, ctx.contract.ccnl
    events, met = una_tantum_events(request, ccnl, ctx.payment.run_id.kind)
    if not met:
        return ()
    month = request.period_id
    unas = [
        una
        for una in ccnl.parameters.una_tantum
        if any(
            (i.paid_in.year, i.paid_in.month) == (month.year, month.month)
            for i in una.installments
        )
    ]
    rule, version = _ccnl_rule(ccnl, month.year)
    amount = sum((event.amount for event in events), Decimal(0))
    return (
        CalculationDecision(
            capability=CAPABILITY,
            status=CalculationStatus.PROVISIONAL,
            reason_code="contractual_una_tantum" if events else "una_tantum_not_owed",
            rule=f"{rule}:parameters.una_tantum[{unas[0].code}]",
            rule_version=version,
            source=unas[0].provenance.location,
            inputs={"una_tantum": ",".join(una.code for una in unas)},
            amount=amount,
        ),
    )
