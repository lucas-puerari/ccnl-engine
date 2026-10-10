"""Settlement of extra-month ratei on a run, as extra-month earnings.

When the employment ends before an extra month's payment month, the ratei
accrued up to the termination are paid on the last regular run as
extra-month earnings (``it/earning/extra_month`` policy: ordinary IRPEF,
INPS and TFR base).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.accrual.models_extra_month_schedule import ExtraMonthKind
from ccnl_engine.payroll.amount.facade import ExtraMonthEarning, PayItem
from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.ledger.models import AccountKind, LedgerEntry
from ccnl_engine.payroll.period.services_shared import (
    _ZERO,
    _apply_extra_month_policy,
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.accrual.models import ExtraMonthAccrual
    from ccnl_engine.payroll.amount.facade import CompetencePeriod
    from ccnl_engine.payroll.amount.policies import PolicyContext, PolicyResolver
    from ccnl_engine.payroll.amount.types_chain import MonthlyPayChain
    from ccnl_engine.payroll.assurance.models_decision import CalculationIssue
    from ccnl_engine.payroll.event.handlers_totals import _EventTotals

__all__ = ["ExtraMonthSettlement", "settle_extra_months"]

_EXTRA_KIND = "extra_month_earning"


@dataclass(frozen=True)
class ExtraMonthSettlement:
    """Earnings of the ratei liquidated on a run and the bases they enter.

    Attributes:
        items: One extra-month earning per settled extra month.
        entries: Cash-earning ledger entries of the items.
        inps_base: Amount entering the INPS contribution base.
        tfr_base: Amount entering the TFR base.
        irpef_base: Amount entering the ordinary IRPEF base.
        issues: Facts missing to settle an amount.
    """

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    inps_base: Decimal = _ZERO
    tfr_base: Decimal = _ZERO
    irpef_base: Decimal = _ZERO
    issues: tuple[CalculationIssue, ...] = ()

    def added_to(self, totals: _EventTotals) -> _EventTotals:
        """Return ``totals`` with the settled amounts added to its bases.

        Returns:
            A copy of ``totals`` with larger INPS, TFR and IRPEF bases and
            the issues.
        """
        return replace(
            totals,
            inps_base=totals.inps_base + self.inps_base,
            tfr_base=totals.tfr_base + self.tfr_base,
            irpef_base=totals.irpef_base + self.irpef_base,
            issues=totals.issues + self.issues,
        )


def settle_extra_months(
    settlements: tuple[ExtraMonthAccrual, ...],
    chain: MonthlyPayChain,
    competence_period: CompetencePeriod,
    payment_date: date,
    run_id: str,
    resolver: PolicyResolver,
    context: PolicyContext,
) -> ExtraMonthSettlement:
    """Pay the ratei of ``settlements`` on this run.

    Each extra month pays ``chain`` restricted to the allowances of that
    extra month, every component scaled by the accrued fraction and rounded
    to cents.  A settlement with no qualifying month pays nothing.

    Returns:
        The earnings, their ledger entries and the bases they enter.
    """
    due = [
        (accrual, _gross(chain, accrual))
        for accrual in settlements
        if accrual.months > 0
    ]
    if not due:
        return ExtraMonthSettlement()
    resolution = _require_resolution(resolver, _EXTRA_KIND, context)
    treatment = _treatment_from_resolution(resolution)
    items: list[PayItem] = []
    entries: list[LedgerEntry] = []
    for accrual, gross in due:
        item_id = f"extra_month_{accrual.kind.value}_{run_id}"
        items.append(
            ExtraMonthEarning(
                item_id=item_id,
                competence_period=competence_period,
                payment_date=payment_date,
                quantity=accrual.fraction,
                amount=gross,
                month_number=14 if accrual.kind is ExtraMonthKind.FOURTEENTH else 13,
                source=f"ratei at termination: {accrual.months}/12",
            )
        )
        entries.append(
            _make_entry(
                item_id,
                item_id,
                _EXTRA_KIND,
                competence_period,
                payment_date,
                AccountKind.CASH_EARNINGS,
                gross,
                policy_id=resolution.policy_id,
            )
        )
    total = sum((gross for _, gross in due), _ZERO)
    return ExtraMonthSettlement(
        items=tuple(items),
        entries=tuple(entries),
        inps_base=total if treatment.inps else _ZERO,
        tfr_base=total if treatment.tfr else _ZERO,
        irpef_base=total if treatment.irpef else _ZERO,
    )


def _gross(chain: MonthlyPayChain, accrual: ExtraMonthAccrual) -> Decimal:
    """Return the gross of ``accrual`` on ``chain``.

    Returns:
        Sum of the scaled extra-month components.
    """
    scaled = _apply_extra_month_policy(chain, accrual.kind.value, accrual.fraction)
    return money(scaled.base + scaled.seniority + scaled.allowances_total)
