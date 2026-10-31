"""Indemnity for the leave left at the end of the employment.

D.Lgs. 66/2003 art. 10 c. 2 forbids paying the four weeks of ferie in place
of the time off "salvo il caso di risoluzione del rapporto di lavoro": the
run that closes the employment pays every residual of the account, at the
basis of the CCNL (:class:`~ccnl_engine.leave.models.LeaveTermination`),
as a ``leave_settlement_item`` (ordinary IRPEF, INPS and TFR base, policy
``it/leave/settlement``), and settles the balances so that a later run of
the same employment pays nothing again.

The ``termination_residual_leave`` decision is taken on every run that
closes the employment, whatever the CCNL: final when the residual is paid
from exact balances, provisional when a balance rests on an estimate, and
incomplete, with nothing paid, when the CCNL accrues no leave, gives no
basis for the indemnity, the balances imported miss the leave of the
previous provider, or a bucket was taken beyond its accrual (the recovery
of leave granted in advance is not sourced).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.ledger.models import AccountKind, LedgerEntry
from ccnl_engine.pay_item.facade import LeaveSettlementItem, PayItem
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.leave.balance.models import LeaveAccount
    from ccnl_engine.leave.handlers import LeaveTerms
    from ccnl_engine.leave.models import LeaveRules
    from ccnl_engine.pay_item.facade import CompetencePeriod
    from ccnl_engine.pay_item.policies import PolicyContext, PolicyResolver

__all__ = [
    "TERMINATION_RESIDUAL_LEAVE",
    "LeaveSettlement",
    "SettlementTerms",
    "settle_leave",
]

#: Capability of the indemnity for the residual leave.
TERMINATION_RESIDUAL_LEAVE = "termination_residual_leave"
_KIND = "leave_settlement_item"
_ZERO = Decimal(0)
_TWELVE = Decimal(12)


@dataclass(frozen=True)
class SettlementTerms:
    """What the indemnity of a run that closes the employment is paid from.

    Attributes:
        leave: Leave rules of the CCNL, with its ruleset.
        monthly_pay: Monthly pay of a fully employed month (the retribuzione
            di fatto the CCNL divides).
        hourly_divisor: Hourly divisor of the CCNL on the run date, ``None``
            when not in force.
        part_time_ratio: Weekly over full-time hours of a part-time worker,
            ``None`` for a full-time worker: the hourly quota of a permit is
            that of the full-time pay.
        competence_period: Competence period of the run.
        payment_date: Payment date of the run.
        tag: Run identifier, the tag of the item ids.
        resolver: Policy resolver of the pay-item kinds.
        context: Context the policy is resolved in.
    """

    leave: LeaveTerms
    monthly_pay: Decimal
    hourly_divisor: Decimal | None
    part_time_ratio: Decimal | None
    competence_period: CompetencePeriod
    payment_date: date
    tag: str
    resolver: PolicyResolver
    context: PolicyContext


@dataclass(frozen=True)
class LeaveSettlement:
    """Indemnity of the residual leave, the bases it enters and its decision.

    Attributes:
        account: The leave account after the settlement.
        decision: The ``termination_residual_leave`` decision.
        items: One leave settlement item per bucket paid.
        entries: Cash-earning ledger entries of the items.
        inps_base: Amount entering the INPS contribution base.
        tfr_base: Amount entering the TFR base.
        irpef_base: Amount entering the ordinary IRPEF base.
        issues: Facts missing to pay the indemnity.
    """

    account: LeaveAccount
    decision: CalculationDecision
    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    inps_base: Decimal = _ZERO
    tfr_base: Decimal = _ZERO
    irpef_base: Decimal = _ZERO
    issues: tuple[CalculationIssue, ...] = field(default=())


#: Issue of a closing run whose imported balances miss the leave.
LEAVE_HISTORY_UNKNOWN = CalculationIssue(
    code="leave_history_unknown",
    message=(
        "the opening balances were imported without the leave balances of the "
        "previous provider: the residual leave of the employment is not known "
        "and is not paid; state OpeningBalances.leave_balances"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="leave_balances",
    capability=TERMINATION_RESIDUAL_LEAVE,
)


def _residuals(account: LeaveAccount) -> dict[LeaveBucket, Decimal]:
    """Return the residual twelfths of each bucket not yet settled.

    Returns:
        Bucket to the sum of the residual twelfths of its balances.
    """
    residuals: dict[LeaveBucket, Decimal] = {}
    for balance in account.unsettled():
        residuals[balance.bucket] = (
            residuals.get(balance.bucket, _ZERO) + balance.residual_twelfths
        )
    return residuals


def _blocking_reason(
    rules: LeaveRules | None,
    account: LeaveAccount,
    residuals: dict[LeaveBucket, Decimal],
    terms: SettlementTerms,
) -> str | None:
    """Return why the residual cannot be paid, ``None`` when it can.

    Returns:
        The reason code of an incomplete decision.
    """
    if rules is None or not rules.buckets:
        return "leave_accrual_not_modelled"
    basis = rules.termination
    if basis is None:
        return "termination_basis_not_sourced"
    if not account.known:
        return LEAVE_HISTORY_UNKNOWN.code
    if any(value < _ZERO for value in residuals.values()):
        return "leave_taken_beyond_accrual"
    daily = {p.bucket for p in rules.permits if p.day_hours is not None}
    hourly = any(
        b is not LeaveBucket.FERIE and b not in daily and v > _ZERO
        for b, v in residuals.items()
    )
    if hourly and (not basis.permits_hourly or terms.hourly_divisor is None):
        return "permit_basis_not_sourced"
    return None


def _quota(
    bucket: LeaveBucket, rules: LeaveRules, terms: SettlementTerms
) -> tuple[Decimal, Decimal]:
    """Return the divisor of one day or hour of ``bucket``, and the pay divided.

    Returns:
        ``(divisor, pay)``: the ferie divisor of the monthly pay; for a
        permit, of the full-time monthly pay, the ferie divisor times the
        hours of a day of a bucket paid by the day, else the hourly divisor.
    """
    divisor = rules.termination.ferie_divisor  # type: ignore[union-attr]
    if bucket is LeaveBucket.FERIE:
        return divisor, terms.monthly_pay
    ratio = terms.part_time_ratio
    pay = terms.monthly_pay if ratio is None else terms.monthly_pay / ratio
    day = next((p.day_hours for p in rules.permits if p.bucket is bucket), None)
    if day is not None:
        return divisor * day, pay
    return terms.hourly_divisor, pay  # type: ignore[return-value]


def _decision(
    terms: SettlementTerms,
    status: CalculationStatus,
    reason: str,
    inputs: dict[str, Decimal | str],
    amount: Decimal | None,
) -> CalculationDecision:
    leave = terms.leave
    rules = leave.rules
    basis = None if rules is None else rules.termination
    provenance = None if basis is None else basis.provenance
    return CalculationDecision(
        capability=TERMINATION_RESIDUAL_LEAVE,
        status=status,
        reason_code=reason,
        rule=f"{leave.ruleset}:work_rules.leave_rules.termination",
        rule_version=leave.version,
        inputs=inputs,
        source=None if provenance is None else provenance.location,
        amount=amount,
    )


def settle_leave(account: LeaveAccount, terms: SettlementTerms) -> LeaveSettlement:
    """Pay the residual leave of ``account`` on the run that closes the employment.

    Returns:
        The settlement: the items, entries and bases of the indemnity with
        the account settled, or nothing paid with an incomplete decision.
    """
    rules = terms.leave.rules
    residuals = _residuals(account)
    inputs: dict[str, Decimal | str] = {
        f"{bucket}_residual": value / _TWELVE for bucket, value in residuals.items()
    }
    reason = _blocking_reason(rules, account, residuals, terms)
    if reason is not None or rules is None:
        issues = (
            (LEAVE_HISTORY_UNKNOWN,) if reason == LEAVE_HISTORY_UNKNOWN.code else ()
        )
        return LeaveSettlement(
            account=account,
            decision=_decision(
                terms, CalculationStatus.INCOMPLETE, str(reason), inputs, None
            ),
            issues=issues,
        )
    resolution = _require_resolution(terms.resolver, _KIND, terms.context)
    treatment = _treatment_from_resolution(resolution)
    items: list[PayItem] = []
    entries: list[LedgerEntry] = []
    for bucket, twelfths in residuals.items():
        if twelfths <= _ZERO:
            continue
        divisor, pay = _quota(bucket, rules, terms)
        amount = money(twelfths * pay / (_TWELVE * divisor))
        item_id = f"leave_{bucket}_{terms.tag}"
        inputs[f"{bucket}_divisor"] = divisor
        items.append(
            LeaveSettlementItem(
                item_id=item_id,
                competence_period=terms.competence_period,
                payment_date=terms.payment_date,
                quantity=twelfths / _TWELVE,
                amount=amount,
                source=f"residual {bucket} at termination, {bucket.unit}",
            )
        )
        entries.append(
            _make_entry(
                item_id,
                item_id,
                _KIND,
                terms.competence_period,
                terms.payment_date,
                AccountKind.CASH_EARNINGS,
                amount,
                policy_id=resolution.policy_id,
            )
        )
    total = sum((i.amount for i in items), _ZERO)
    inputs["monthly_pay"] = terms.monthly_pay
    exact = all(b.exact for b in account.unsettled())
    return LeaveSettlement(
        account=account.settled(),
        decision=_decision(
            terms,
            CalculationStatus.FINAL if exact else CalculationStatus.PROVISIONAL,
            ("residual_leave_paid" if items else "no_residual_leave")
            if exact
            else "residual_leave_estimated",
            inputs,
            total,
        ),
        items=tuple(items),
        entries=tuple(entries),
        inps_base=total if treatment.inps else _ZERO,
        tfr_base=total if treatment.tfr else _ZERO,
        irpef_base=total if treatment.irpef else _ZERO,
    )
