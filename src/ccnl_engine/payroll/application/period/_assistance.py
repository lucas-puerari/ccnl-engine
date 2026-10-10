"""Rates, rule and decision of the contractual assistance contribution."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.identity.rules_validity import rule_scope
from ccnl_engine.payroll.application.amounts._assistance import (
    CAPABILITY,
    AssistanceTerms,
)
from ccnl_engine.payroll.application.period._run_decisions import _ccnl_rule
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.identity.facade import CCNL
    from ccnl_engine.payroll.application.amounts._assistance import (
        AssistanceContribution,
    )
    from ccnl_engine.payroll.application.period._rule_lookup import Rule

__all__ = ["assistance_decision", "assistance_rules", "assistance_terms"]

#: Location of the contribution in a CCNL file.
_PATH = "parameters.assistance_contribution"


def assistance_terms(ccnl: CCNL, as_of: date) -> AssistanceTerms | None:
    """Return the rates per paid hour the CCNL charges on *as_of*.

    Returns:
        ``None`` when the CCNL charges no assistance contribution.
    """
    contribution = ccnl.parameters.assistance_contribution
    if contribution is None:
        return None
    with rule_scope(ruleset=ccnl.meta.ccnl_id, feature=CAPABILITY):
        return AssistanceTerms(
            employee_per_hour=contribution.employee_per_hour.value_at(as_of),
            employer_per_hour=contribution.employer_per_hour.value_at(as_of),
            provenance=contribution.provenance,
        )


def assistance_rules(ccnl: CCNL, year: int) -> tuple[Rule, ...]:
    """Return the rule of the contribution, when the CCNL charges one.

    Returns:
        The contribution clause with its provenance, empty without one.
    """
    contribution = ccnl.parameters.assistance_contribution
    if contribution is None:
        return ()
    return ((f"{_ccnl_rule(ccnl, year)[0]}:{_PATH}", contribution.provenance),)


def assistance_decision(
    ccnl: CCNL, assistance: AssistanceContribution | None, year: int
) -> CalculationDecision | None:
    """Return the decision recording the contribution of the run.

    Returns:
        A decision with reason ``hourly_rate_applied``, the hours, rates and
        shares, and both shares as amount; ``None`` when the CCNL charges no
        contribution.
    """
    if assistance is None:
        return None
    rule, version = _ccnl_rule(ccnl, year)
    terms = assistance.terms
    return CalculationDecision(
        capability=CAPABILITY,
        status=CalculationStatus.FINAL,
        reason_code="hourly_rate_applied",
        rule=f"{rule}:{_PATH}",
        rule_version=version,
        inputs={
            "hours": assistance.hours,
            "employee_per_hour": terms.employee_per_hour,
            "employer_per_hour": terms.employer_per_hour,
            "employee": assistance.employee,
            "employer": assistance.employer,
        },
        source=terms.provenance.location,
        amount=assistance.employee + assistance.employer,
    )
