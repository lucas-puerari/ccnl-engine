"""The pay items and ledger entries of a TFR settlement."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationStatus,
)
from ccnl_engine.employment.fact.inputs import PublicEndOfService
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.ledger.remittance.models import SEVERANCE_WITHHOLDING
from ccnl_engine.pay_item.facade import TfrSettlementItem
from ccnl_engine.pay_item.services import _make_entry, _require_resolution

if TYPE_CHECKING:
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.severance.settlement.services import TfrSettlement

#: Capability of the TFR settlement, as the events name it.
CAPABILITY = "termination_tfr"
_KIND = "tfr_settlement_item"
_ZERO = Decimal(0)
_MONTHS = 12
_AT_INPS = frozenset({PublicEndOfService.TFS, PublicEndOfService.TFR_INPS})
#: Months of service up to which a fixed term takes the art. 19 c. 1-ter deduction.
_SHORT_FIXED_TERM = 24
_FINAL = CalculationStatus.FINAL
_INCOMPLETE = CalculationStatus.INCOMPLETE


def _postings(
    ctx: RunContext, evt_id: str, settlement: TfrSettlement
) -> tuple[tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Return the item and entries of the TFR and its tax, when computed.

    Returns:
        The settlement item with its ``tfr_settlement`` entry and, when
        the tax is computed, the ``separate_tax`` entry; nothing without a
        payout.
    """
    if settlement.payout is None:
        return (), ()
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    payment = ctx.contract.tctx.payment
    item = TfrSettlementItem(
        item_id=evt_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=Decimal(1),
        amount=settlement.payout,
    )
    entries = [
        _make_entry(
            f"tfr_settle_{evt_id}",
            evt_id,
            _KIND,
            ctx.cp,
            payment,
            AccountKind.TFR_SETTLEMENT,
            settlement.payout,
            policy_id=resolution.policy_id,
        )
    ]
    if settlement.tax is not None:
        entries.append(
            _make_entry(
                f"sep_tax_{evt_id}",
                evt_id,
                _KIND,
                ctx.cp,
                payment,
                AccountKind.SEPARATE_TAX,
                settlement.tax,
                policy_id=resolution.policy_id,
                remittance_code=SEVERANCE_WITHHOLDING,
            )
        )
    return (item,), tuple(entries)
