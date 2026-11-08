"""Pay the loyalty premium on the hire anniversary in a regular run.

The fully employed run chain approximates the enumerated contractual pay
components (ANIEM Art. 45 items 1-14; CNA Art. 48 items 1-12). It does not
establish uninterrupted actual service or implement the dismissal pro rata.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.sunday_holiday.rules import monthly_pay
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.models import LoyaltyPremiumEarning
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from ccnl_engine.event.total.handlers import _EventTotals
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.period.context.services import RunContext

_ZERO = Decimal(0)
_KIND = "loyalty_premium_earning"


@dataclass(frozen=True)
class LoyaltySettlement:
    """The anniversary earning and its additions to the event bases."""

    items: tuple[LoyaltyPremiumEarning, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    amount: Decimal = _ZERO
    taxed: tuple[bool, bool, bool] = (False, False, False)

    def added_to(self, totals: _EventTotals) -> _EventTotals:
        """Return event totals with the policy-selected bases.

        Returns:
            The updated INPS, TFR and IRPEF event totals.
        """
        inps, tfr, irpef = (self.amount if flag else _ZERO for flag in self.taxed)
        return replace(
            totals,
            inps_base=totals.inps_base + inps,
            tfr_base=totals.tfr_base + tfr,
            irpef_base=totals.irpef_base + irpef,
            decisions=totals.decisions + self.decisions,
        )


def loyalty_premium(ctx: RunContext) -> LoyaltySettlement:
    """Pay a full monthly award on each qualifying hire anniversary month.

    Without a known employment period, or on a non-regular run, pay nothing.
    February 29 hires celebrate on February 28 in non-leap years.

    Returns:
        The award and its posting, or an empty settlement.
    """
    clause = ctx.contract.ccnl.parameters.loyalty_premium
    period = ctx.request.employment_period
    if (
        clause is None
        or period is None
        or ctx.run_kind is not RunKind.REGULAR
        or ctx.worker_category not in {WorkerCategory.IMPIEGATO, WorkerCategory.QUADRO}
    ):
        return LoyaltySettlement()
    month = ctx.request.period_id.month
    year = ctx.request.period_id.year
    if month != period.started_on.month:
        return LoyaltySettlement()
    anniversary = period.started_on.replace(
        year=year,
        day=min(period.started_on.day, calendar.monthrange(year, month)[1]),
    )
    if year - period.started_on.year < clause.service_years or (
        period.ended_on is not None and period.ended_on < anniversary
    ):
        return LoyaltySettlement()
    amount = money(clause.months * monthly_pay(ctx.regular_chain, frozenset()))
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    treatment = _treatment_from_resolution(resolution)
    item_id = f"loyalty_premium_{ctx.run_id}"
    payment = ctx.contract.tctx.payment
    item = LoyaltyPremiumEarning(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=clause.months,
        amount=amount,
        source="CCNL Art. 65 loyalty premium",
    )
    entry = _make_entry(
        item_id,
        item_id,
        _KIND,
        ctx.cp,
        payment,
        AccountKind.CASH_EARNINGS,
        amount,
        policy_id=resolution.policy_id,
    )
    return LoyaltySettlement(
        items=(item,),
        entries=(entry,),
        decisions=(
            CalculationDecision(
                capability="base_salary",
                status=CalculationStatus.FINAL,
                reason_code="loyalty_anniversary",
                rule="ccnl/art-65:loyalty-premium",
                rule_version=str(year),
                inputs={"service_years": str(clause.service_years), "monthly": amount},
                amount=amount,
            ),
        ),
        amount=amount,
        taxed=(treatment.inps, treatment.tfr, treatment.irpef),
    )
