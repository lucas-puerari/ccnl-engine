"""The INAIL premium the employer accrues on the pay of the run.

The premium of the ordinary position is the taxable pay of the year times
the rate INAIL applies to the employer's position, per mille (art. 29 DPR
1124/1965; the INAIL basi di calcolo).  Its base is the one of the INPS
contributions: art. 12 L. 153/1969, as D.Lgs. 314/1997 art. 6 rewrote it,
for both.  The yearly self-assessment (autoliquidazione) settles the
premium on the pay of the year, which is the sum of the months: the run
accrues its month, an employer cost, never a deduction from the worker.

The rate is a fact of the employer's position
(``EmployerProfile.inail_rate``); where the sector sets one rate by law for
a category of workers (``YearRules.inail``: the operai agricoli), that rate
applies when the employer states none.  Without either no premium is
computed.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.models import EmployerContributionItem
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _make_entry, _require_resolution

if TYPE_CHECKING:
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext

__all__ = ["INAIL", "InailPremium", "inail_premium"]

#: Capability of the INAIL premium.
INAIL = "inail"
_KIND = "employer_contribution_item"
_RULE = "dpr-1124-1965-art29"
_PER_MILLE = Decimal(1000)


@dataclass(frozen=True)
class InailPremium:
    """The premium the run accrues, with its entry and decision."""

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()


def inail_premium(ctx: RunContext, base: Decimal) -> InailPremium:
    """Return the INAIL premium of the run on its contribution ``base``.

    Returns:
        Nothing without the employer's rate; the item, entry and decision of
        ``base`` times the rate per mille, rounded to the cent.
    """
    employer = ctx.request.employer
    rate = None if employer is None else employer.inail_rate
    sector = ctx.contract.year_rules.inail
    if rate is None and sector is not None and ctx.worker_category is not None:
        share = sector.rate_by_category.get(ctx.worker_category)
        rate = None if share is None else share * _PER_MILLE
    if rate is None:
        return InailPremium()
    amount = money(base * rate / _PER_MILLE)
    item_id = f"inail_{ctx.run_id}"
    payment = ctx.contract.tctx.payment
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    item = EmployerContributionItem(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=Decimal(1),
        amount=amount,
        source="DPR 1124/1965 art. 29",
    )
    entry = _make_entry(
        item_id,
        item_id,
        _KIND,
        ctx.cp,
        payment,
        AccountKind.EMPLOYER_CONTRIBUTIONS,
        amount,
        policy_id=resolution.policy_id,
    )
    decision = CalculationDecision(
        capability=INAIL,
        status=CalculationStatus.FINAL,
        reason_code="inail_premium_accrued",
        rule=_RULE,
        rule_version=str(ctx.fiscal_year),
        inputs={"base": str(base), "rate_per_mille": str(rate)},
        amount=amount,
    )
    return InailPremium(items=(item,), entries=(entry,), decisions=(decision,))
