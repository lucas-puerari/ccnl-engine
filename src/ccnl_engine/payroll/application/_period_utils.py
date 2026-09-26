"""Shared private utilities for period calculation sub-modules."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import DataIntegrityError
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.payroll.domain.policy import (
    ContributionAxis,
    PolicyContext,
    PolicyResolution,
    PolicyResolver,
    TaxAxis,
    TfrAxis,
)
from ccnl_engine.payroll.domain.treatment import EventTreatment

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.employment import SeniorityMonths, WeeklyHours
    from ccnl_engine.payroll.service.types import MonthlyPayChain

_ZERO = Decimal(0)


def _int_value(fact: WeeklyHours | SeniorityMonths | None) -> int | None:
    return None if fact is None else fact.value


def _effective_resolver(resolver: PolicyResolver | None) -> PolicyResolver:
    return resolver if resolver is not None else PolicyResolver.load()


def _require_resolution(
    resolver: PolicyResolver,
    kind: str,
    context: PolicyContext,
) -> PolicyResolution:
    resolution = resolver.resolve(kind, context)
    if resolution is None:
        msg = f"No policy rule found for pay-item kind '{kind}' on {context.as_of}"
        raise DataIntegrityError(msg)
    return resolution


def _treatment_from_resolution(resolution: PolicyResolution) -> EventTreatment:
    inps = resolution.contribution in {
        ContributionAxis.INCLUDED,
        ContributionAxis.CAPPED,
        ContributionAxis.SPECIAL_BASE,
    }
    tfr = resolution.tfr == TfrAxis.INCLUDED
    substitute = resolution.tax == TaxAxis.SUBSTITUTE
    irpef = not substitute and resolution.tax not in {
        TaxAxis.NOT_APPLICABLE,
        TaxAxis.EXEMPT,
    }
    return EventTreatment(inps=inps, tfr=tfr, irpef=irpef, substitute=substitute)


def _make_entry(
    entry_id: str,
    pay_item_id: str,
    pay_item_kind: str,
    competence_period: CompetencePeriod,
    payment_date: date,
    account: AccountKind,
    amount: Decimal,
    policy_id: str | None = None,
) -> LedgerEntry:
    return LedgerEntry(
        entry_id=entry_id,
        competence_period=competence_period,
        payment_date=payment_date,
        pay_item_id=pay_item_id,
        pay_item_kind=pay_item_kind,
        account=account,
        amount=amount,
        source_item_id=pay_item_id,
        policy_decision_id=policy_id,
    )


def _sum_ledger(entries: tuple[LedgerEntry, ...], account: AccountKind) -> Decimal:
    """Sum all ledger entry amounts for a given account kind.

    Returns:
        Total for ``account`` in ``entries``, or zero when no entry is present.
    """
    return sum((e.amount for e in entries if e.account == account), _ZERO)


def _apply_extra_month_policy(
    chain: MonthlyPayChain, run_kind: str, fraction: Decimal
) -> MonthlyPayChain:
    """Adjust a pay chain for the run kind (tredicesima / quattordicesima).

    Keeps the allowances paid in the extra month and scales every component
    by ``fraction``, rounding each to cents.

    Args:
        chain: Pay chain of a regular month.
        run_kind: Kind of the run; a regular run keeps ``chain`` unchanged.
        fraction: Share of a monthly pay due, the rateo times the
            contractual fraction of the extra month.

    Returns:
        Adjusted :class:`~ccnl_engine.payroll.service.types.MonthlyPayChain`.
    """
    if run_kind not in {"thirteenth", "fourteenth"}:
        return chain
    months_threshold = 14 if run_kind == "fourteenth" else 13
    chain = chain.for_extra_month(months_threshold)
    if fraction < Decimal(1):
        chain = chain.scaled(fraction)
    return chain
