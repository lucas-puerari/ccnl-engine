"""Decision of the pension fund contributions of one run.

Enrolment is voluntary (D.Lgs. 252/2005 art. 1 c. 2), so it is a fact of
the employment: :class:`~ccnl_engine.payroll.domain.pension_fund\
.PensionFundEnrolment` or :class:`~ccnl_engine.payroll.domain.pension_fund\
.NoPensionFund`.  An enrolment left unknown leaves the contributions
undetermined on a CCNL whose funds the bundle holds, and on every CCNL of
the private sectors and the public administration whose negotiated fund it
does not hold (domestic work has none): the decision is incomplete and an
issue names the fact.  The engine does not infer the destination of the TFR of a
worker who expressed no choice (art. 8 c. 7).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.payroll.application.period._contractual_fund import contractual_run
from ccnl_engine.payroll.application.period._erc import erc_of
from ccnl_engine.payroll.application.period._run_decisions import _ccnl_rule
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.employment import Apprentice
from ccnl_engine.payroll.domain.events import SickLeaveEvent, SicknessEpisode
from ccnl_engine.payroll.domain.pension_fund import PensionFundEnrolment
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
#: Sectors whose CCNLs have no negotiated pension fund.
_NO_NEGOTIATED_FUND = frozenset({TaxSector.LAVORO_DOMESTICO})
#: Reason code of a run whose enrolment in a fund of the CCNL is unknown.
REQUIRED_FACT_MISSING = "required_fact_missing"
#: Reason code of a run that owes only the contractual contribution.
CONTRACTUAL_ONLY = "contractual_only"
FACT = "pension_fund"
#: Variant of the CCNL limitation a fund due on the pay of the month
#: traverses on a month paid in part.
PAID_MONTH_VARIANT = "fund_paid_month"


def pension_terms(ctx: RunContext) -> PensionFundTerms | None:
    """Return the rates of the fund the worker is enrolled in.

    Returns:
        ``None`` when the worker is not enrolled or the enrolment is
        unknown.
    """
    enrolment = ctx.request.pension_fund
    if not isinstance(enrolment, PensionFundEnrolment):
        return None
    contract = ctx.contract
    return resolve_terms(
        contract.ccnl,
        enrolment,
        ctx.worker_category,
        contract.tctx.competence,
        contract.year_rules.complementary_pension,
        apprentice=isinstance(ctx.request.contract_type, Apprentice),
        minimum_base=ctx.chain.base,
        erc_amount=erc_of(ctx),
    )


def _inputs(pension: PensionContribution) -> dict[str, Decimal | str]:
    terms = pension.terms
    if terms is None:
        return {
            "contractual": pension.contractual,
            "employer": pension.employer,
            "solidarity": pension.solidarity,
            "deductible": pension.deductible,
        }
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
        "tfr_to_fund": "notional"
        if terms.tfr_to_fund and terms.tfr_notional
        else str(terms.tfr_to_fund).lower(),
        "contractual": pension.contractual,
        "contribution_base": str(terms.fund.contribution_base),
    }


def enrolment_unknown(ctx: RunContext) -> bool:
    """Return whether the run cannot tell whether the worker is enrolled.

    Returns:
        True when the enrolment is not stated, unless the CCNL has no
        negotiated fund and the bundle holds none.
    """
    ccnl = ctx.contract.ccnl
    return ctx.request.pension_fund is None and (
        bool(ccnl.parameters.employer_funds)
        or ccnl.meta.tax_sector not in _NO_NEGOTIATED_FUND
    )


def paid_month_paths(ctx: RunContext, event_inps_base: Decimal) -> frozenset[str]:
    """Return the limitation path of a fund due on the pay of the month.

    Previambiente art. 65 c. 8: no contribution "in caso di assenza non
    retribuita per il mese"; with a paid absence it "è commisurato alla
    retribuzione corrisposta".  A month without pay owes none; a month
    paid in part (an unpaid absence, sickness, a partial month) traverses
    :data:`PAID_MONTH_VARIANT`, a rule the engine does not compute.

    Returns:
        The path when the worker is enrolled in such a fund and the regular
        run pays part of its month, else nothing.
    """
    terms = pension_terms(ctx)
    paid = ctx.monthly_gross + event_inps_base
    if terms is None or not terms.fund.paid_month_only or paid <= 0:
        return frozenset()
    sick = any(
        isinstance(e, (SickLeaveEvent, SicknessEpisode)) for e in ctx.request.events
    )
    if not (sick or event_inps_base < 0 or ctx.proration.partial):
        return frozenset()
    return frozenset({f"{ctx.contract.ccnl.meta.ccnl_id}/{PAID_MONTH_VARIANT}"})


def pension_unresolved(ctx: RunContext) -> bool:
    """Return whether the run cannot determine its fund contributions.

    Returns:
        True when the enrolment is unknown (:func:`enrolment_unknown`) or a
        fact of the contractual contribution is missing.
    """
    return enrolment_unknown(ctx) or contractual_run(ctx).issue is not None


def pension_fund_issue(ctx: RunContext) -> CalculationIssue | None:
    """Return the missing-fact issue of an unknown enrolment.

    Returns:
        An incomplete issue naming ``pension_fund``, or ``None``.
    """
    if not enrolment_unknown(ctx):
        return None
    funds = ", ".join(f.code for f in ctx.contract.ccnl.parameters.employer_funds)
    held = f"pension funds ({funds})" if funds else "a negotiated pension fund"
    return CalculationIssue(
        code="pension_fund_enrolment_unknown",
        message=(
            f"the CCNL has {held} and the enrolment of the worker is not "
            "stated: the fund contributions and the destination of the TFR "
            "are undetermined, the amounts shown leave them out; state "
            "Employment.pension_fund (NoPensionFund when not enrolled)"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=FACT,
    )


def pension_decision(
    ccnl: CCNL, pension: PensionContribution | None, year: int, *, unknown: bool
) -> CalculationDecision | None:
    """Return the decision recording the pension fund contributions of the run.

    Args:
        ccnl: The applicable CCNL.
        pension: Contributions of the run, ``None`` when not enrolled.
        year: Competence year, the rule version when the CCNL has no ruleset.
        unknown: Whether the enrolment is unknown (see
            :func:`enrolment_unknown`).

    Returns:
        A decision with reason ``enrolled`` and the employer and employee
        contributions as amount; with reason ``not_enrolled`` when the
        worker is stated not enrolled in a fund the CCNL has; with reason
        ``contractual_only`` and its amount when the worker, not enrolled,
        is owed the contractual contribution of the CCNL; an incomplete
        one with reason ``required_fact_missing`` when the enrolment is
        unknown; ``None`` when the CCNL has no fund.
    """
    rule, version = _ccnl_rule(ccnl, year)
    funds = ",".join(f.code for f in ccnl.parameters.employer_funds)
    contractual = ccnl.parameters.contractual_fund_contribution
    if unknown:
        return CalculationDecision(
            capability=CAPABILITY,
            status=CalculationStatus.INCOMPLETE,
            reason_code=REQUIRED_FACT_MISSING,
            rule=rule,
            rule_version=version,
            inputs={"funds": funds}
            | ({} if pension is None else {"contractual": pension.contractual}),
        )
    if pension is None:
        if not funds:
            return None
        return CalculationDecision(
            capability=CAPABILITY,
            status=CalculationStatus.FINAL,
            reason_code=NOT_ENROLLED,
            rule=rule,
            rule_version=version,
            inputs={"funds": funds},
        )
    terms = pension.terms
    if terms is None:
        return CalculationDecision(
            capability=CAPABILITY,
            status=CalculationStatus.FINAL,
            reason_code=CONTRACTUAL_ONLY,
            rule=f"{rule}:contractual_fund_contribution",
            rule_version=version,
            inputs=_inputs(pension),
            source=None if contractual is None else contractual.provenance.location,
            amount=pension.employer,
        )
    provenance = terms.rate_period.provenance or terms.fund.provenance
    return CalculationDecision(
        capability=CAPABILITY,
        status=CalculationStatus.FINAL,
        reason_code="enrolled",
        rule=f"{rule}:employer_funds[{terms.fund.code}]",
        rule_version=version,
        inputs=_inputs(pension),
        source=None if provenance is None else provenance.location,
        amount=pension.employer + pension.employee,
    )
