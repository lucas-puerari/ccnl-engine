"""Decision invariants: substitute tax, plafond and provenance.

These invariants check that the calculation decisions of a run agree with
what it posted and with the YTD accounts they draw on.

Implemented invariants:
    substitute_tax_plafond: the work-time regime cap account advances by
        the eligible amounts of the capped regime decisions and stays
        within their annual cap; each capped decision sees the cap left by
        the previous one and takes no more than it; the PdR eligible YTD
        advances by the ``bonus_pdr`` eligible amount and stays within the
        PdR annual limit when it is known.
    substitute_tax_eligibility: SUBSTITUTE_TAX posted by the run equals the
        substitute tax of its regime and PdR decisions; a regime decision
        that is not ``eligible`` has no eligible amount and no tax, so the
        whole amount stays ordinary; no decision taxes a nil eligible
        amount.  That the ordinary remainder reaches the IRPEF base is not
        visible in the result and is not checked here.
    decision_provenance: every final decision names a rule and a rule
        version.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.invariants._types import (
    InvariantCode,
    ReconciliationViolation,
    _sum_account,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.service.regime_eligibility import RegimeEligibility

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.invariants._types import RunFacts
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_state import PeriodState

__all__: list[str] = []

_ZERO = Decimal(0)
_PDR = "bonus_pdr"
_REGIME_SUFFIX = "_substitute_tax"
_PLAFOND = InvariantCode.SUBSTITUTE_TAX_PLAFOND
_ELIGIBILITY = InvariantCode.SUBSTITUTE_TAX_ELIGIBILITY


def _input(decision: CalculationDecision, name: str) -> Decimal:
    return Decimal(decision.inputs.get(name, _ZERO))


def _capped(result: PeriodResult) -> list[CalculationDecision]:
    return [
        d
        for d in result.decisions
        if d.capability.endswith(_REGIME_SUFFIX) and "annual_cap" in d.inputs
    ]


def _check_cap_chain(
    capped: list[CalculationDecision], opening_used: Decimal
) -> list[ReconciliationViolation]:
    """Check that each capped decision sees the cap the previous ones left.

    Returns:
        Violations for a ``cap_available`` that does not follow from the
        opening usage and the earlier eligible amounts, and for an eligible
        amount above it.
    """
    violations: list[ReconciliationViolation] = []
    used = opening_used
    for d in capped:
        available = _input(d, "cap_available")
        expected = max(_input(d, "annual_cap") - used, _ZERO)
        eligible = _input(d, "eligible_amount")
        if available != expected:
            violations.append(
                ReconciliationViolation(
                    invariant_id=_PLAFOND,
                    message=f"{d.capability} cap_available disagrees with the cap",
                    expected=expected,
                    actual=available,
                )
            )
        if eligible > available:
            violations.append(
                ReconciliationViolation(
                    invariant_id=_PLAFOND,
                    message=f"{d.capability} eligible amount exceeds the cap left",
                    expected=available,
                    actual=eligible,
                )
            )
        used += eligible
    return violations


def _check_regime_cap(
    result: PeriodResult, opening: PeriodState
) -> list[ReconciliationViolation]:
    """Check the work-time regime cap account against the capped decisions.

    Returns:
        Violations for a wrong advance, a used amount above the cap or a
        broken chain of ``cap_available``.
    """
    capped = _capped(result)
    used = result.closing_state.ytd.work_time_regime.used
    opening_used = opening.ytd.work_time_regime.used
    expected = opening_used + sum((_input(d, "eligible_amount") for d in capped), _ZERO)
    violations: list[ReconciliationViolation] = []
    if used != expected:
        violations.append(
            ReconciliationViolation(
                invariant_id=_PLAFOND,
                message="work_time_regime.used not advanced by the eligible amounts",
                expected=expected,
                actual=used,
            )
        )
    caps = {_input(d, "annual_cap") for d in capped}
    violations.extend(
        ReconciliationViolation(
            invariant_id=_PLAFOND,
            message=f"work_time_regime.used {used} exceeds the annual cap {cap}",
            expected=cap,
            actual=used,
        )
        for cap in sorted(caps)
        if used > cap
    )
    violations.extend(_check_cap_chain(capped, opening_used))
    return violations


def _check_pdr_cap(
    result: PeriodResult, opening: PeriodState, facts: RunFacts
) -> list[ReconciliationViolation]:
    """Check that the PdR eligible YTD advances and stays within its limit.

    Returns:
        Violations for a wrong advance or a YTD above ``facts.pdr_cap``.
    """
    pdr = result.closing_state.ytd.fringe.pdr
    eligible = (
        _input(d, "eligible_amount") for d in result.decisions if d.capability == _PDR
    )
    expected = opening.ytd.fringe.pdr + sum(eligible, _ZERO)
    violations: list[ReconciliationViolation] = []
    if pdr != expected:
        violations.append(
            ReconciliationViolation(
                invariant_id=_PLAFOND,
                message="fringe.pdr not advanced by the PdR eligible amount",
                expected=expected,
                actual=pdr,
            )
        )
    if facts.pdr_cap is not None and pdr > facts.pdr_cap:
        violations.append(
            ReconciliationViolation(
                invariant_id=_PLAFOND,
                message=f"fringe.pdr {pdr} exceeds the PdR limit {facts.pdr_cap}",
                expected=facts.pdr_cap,
                actual=pdr,
            )
        )
    return violations


def check_substitute_tax_plafond(
    result: PeriodResult, opening: PeriodState, facts: RunFacts
) -> list[ReconciliationViolation]:
    """Check that substitute-tax eligible amounts stay within their cap.

    Returns:
        Violations of the work-time regime cap and of the PdR limit.
    """
    return _check_regime_cap(result, opening) + _check_pdr_cap(result, opening, facts)


def _substitute_decisions(
    result: PeriodResult,
) -> list[CalculationDecision]:
    return [
        d
        for d in result.decisions
        if d.capability == _PDR or d.capability.endswith(_REGIME_SUFFIX)
    ]


def _eligibility_violations(d: CalculationDecision) -> list[ReconciliationViolation]:
    tax = d.amount if d.amount is not None else _ZERO
    eligible = _input(d, "eligible_amount")
    violations: list[ReconciliationViolation] = []
    is_regime = d.capability != _PDR
    if is_regime and d.inputs.get("eligibility") != RegimeEligibility.ELIGIBLE:
        if eligible != _ZERO or tax != _ZERO:
            violations.append(
                ReconciliationViolation(
                    invariant_id=_ELIGIBILITY,
                    message=(
                        f"{d.capability} is {d.inputs.get('eligibility')} but "
                        f"taxes {eligible} at the substitute rate"
                    ),
                    expected=_ZERO,
                    actual=eligible,
                )
            )
    elif tax > _ZERO and eligible <= _ZERO:
        violations.append(
            ReconciliationViolation(
                invariant_id=_ELIGIBILITY,
                message=f"{d.capability} posts substitute tax on no eligible amount",
                expected=_ZERO,
                actual=tax,
            )
        )
    return violations


def check_substitute_tax_eligibility(
    result: PeriodResult,
) -> list[ReconciliationViolation]:
    """Check that substitute tax is posted only on eligible amounts.

    Returns:
        Violations for a decision that taxes an ineligible amount and for a
        SUBSTITUTE_TAX total that no decision explains.
    """
    decisions = _substitute_decisions(result)
    violations: list[ReconciliationViolation] = []
    for d in decisions:
        violations.extend(_eligibility_violations(d))
    decided = sum((d.amount for d in decisions if d.amount is not None), _ZERO)
    posted = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
    if posted != decided:
        violations.append(
            ReconciliationViolation(
                invariant_id=_ELIGIBILITY,
                message="SUBSTITUTE_TAX total differs from the decided substitute tax",
                expected=decided,
                actual=posted,
            )
        )
    return violations


def check_decision_provenance(
    result: PeriodResult,
) -> list[ReconciliationViolation]:
    """Check that every final decision names its rule and rule version.

    Returns:
        One violation per final decision with a blank rule or rule version.
    """
    return [
        ReconciliationViolation(
            invariant_id=InvariantCode.DECISION_PROVENANCE,
            message=(
                f"final decision {d.capability} ({d.reason_code}) has no rule "
                "or rule version"
            ),
        )
        for d in result.decisions
        if d.status is CalculationStatus.FINAL
        and not (d.rule.strip() and d.rule_version.strip())
    ]
