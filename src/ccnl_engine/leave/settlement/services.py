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

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.leave.settlement.models import (
    PERMIT_DEADLINE,
    TERMINATION_RESIDUAL_LEAVE,
    LeaveSettlement,
    SettlementTerms,
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
    from ccnl_engine.leave.balance.models import LeaveAccount
    from ccnl_engine.leave.models import LeaveRules

__all__ = ["LEAVE_HISTORY_UNKNOWN", "settle_leave"]

_KIND = "leave_settlement_item"
_ZERO = Decimal(0)
_TWELVE = Decimal(12)


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
    deadline = terms.deadline
    provenance = (
        deadline.provenance
        if deadline is not None
        else None
        if basis is None
        else basis.provenance
    )
    field = "termination" if deadline is None else "permit_deadline"
    return CalculationDecision(
        capability=TERMINATION_RESIDUAL_LEAVE if deadline is None else PERMIT_DEADLINE,
        status=status,
        reason_code=reason,
        rule=f"{leave.ruleset}:work_rules.leave_rules.{field}",
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
                source=f"residual {bucket} at "
                f"{'termination' if terms.deadline is None else 'the deadline'}, "
                f"{bucket.unit}",
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
