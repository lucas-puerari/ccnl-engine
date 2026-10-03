"""Decision of the pension fund contributions of one run."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._run_decisions import _ccnl_rule
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.service.pension_fund import (
    CAPABILITY,
    NOT_ENROLLED,
    resolve_terms,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.service.pension_fund import (
        PensionContribution,
        PensionFundTerms,
    )

_NOT_IN_BUNDLE = "not_in_bundle"


def pension_terms(ctx: RunContext) -> PensionFundTerms | None:
    """Return the rates of the fund the worker is enrolled in.

    Returns:
        ``None`` when the worker is not enrolled.
    """
    enrolment = ctx.request.pension_fund
    if enrolment is None:
        return None
    contract = ctx.contract
    return resolve_terms(
        contract.ccnl,
        enrolment,
        ctx.worker_category,
        contract.tctx.competence,
        contract.year_rules.complementary_pension,
    )


def _inputs(pension: PensionContribution) -> dict[str, Decimal | str]:
    terms = pension.terms
    minimum = terms.employee_min_rate
    return {
        "fund_code": terms.fund.code,
        "base": pension.base,
        "employer_rate": terms.employer_rate,
        "employee_rate": terms.employee_rate,
        "employee_min_rate": _NOT_IN_BUNDLE if minimum is None else minimum,
        "employer": pension.employer,
        "employee": pension.employee,
        "solidarity": pension.solidarity,
        "deductible": pension.deductible,
        "deduction_cap": terms.rules.deduction_cap,
        "tfr_to_fund": str(terms.tfr_to_fund).lower(),
    }


def pension_decision(
    ccnl: CCNL, pension: PensionContribution | None, year: int
) -> CalculationDecision | None:
    """Return the decision recording the pension fund contributions of the run.

    Args:
        ccnl: The applicable CCNL.
        pension: Contributions of the run, ``None`` when not enrolled.
        year: Competence year, the rule version when the CCNL has no ruleset.

    Returns:
        A decision with reason ``enrolled`` and the employer and employee
        contributions as amount; with reason ``not_enrolled`` when the
        worker is not enrolled in a fund the CCNL has; ``None`` when the
        CCNL has no fund.
    """
    rule, version = _ccnl_rule(ccnl, year)
    if pension is None:
        if not ccnl.parameters.employer_funds:
            return None
        return CalculationDecision(
            capability=CAPABILITY,
            status=CalculationStatus.FINAL,
            reason_code=NOT_ENROLLED,
            rule=rule,
            rule_version=version,
            inputs={"funds": ",".join(f.code for f in ccnl.parameters.employer_funds)},
        )
    provenance = pension.terms.rate_period.provenance or pension.terms.fund.provenance
    return CalculationDecision(
        capability=CAPABILITY,
        status=CalculationStatus.FINAL,
        reason_code="enrolled",
        rule=f"{rule}:employer_funds[{pension.terms.fund.code}]",
        rule_version=version,
        inputs=_inputs(pension),
        source=None if provenance is None else provenance.location,
        amount=pension.employer + pension.employee,
    )
