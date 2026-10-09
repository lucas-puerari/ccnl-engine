"""Pension fund contributions of one run and their effect on the taxable."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.fund_contribution import FundContributionBase
from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.service.pension_fund import (
    contractual_only,
    contribute,
    upcoming_adjustment,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.service.pension_fund import PensionContribution

_ZERO = Decimal(0)
#: A fund with a young member rate needs the enrolment to state it.
YOUNG_MEMBER_UNKNOWN = CalculationIssue(
    code="pension_fund_young_member_unknown",
    message=(
        "the fund has a higher employer rate for members enrolled young "
        "(Cometa: after 5 February 2021, before turning 35) and the enrolment "
        "does not state it: the amounts shown use the base rate; state "
        "PensionFundEnrolment.young_member"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="young_member",
)


def run_pension(inp: _AmountsInput) -> PensionContribution | None:
    """Return the fund contributions of the run, on the base of the fund.

    The base is the one the fund names: the INPS base of the run, the TFR
    base (the recurring gross, the benefits in kind and the events entering
    the TFR, e.g. Fon.Te.) or the contractual minimum (Cometa).  An employee
    rate above the minimum is computed on the base the fund sets for it,
    when it sets one (Cometa: the TFR base).

    The contractual contribution of the CCNL is added to the employer part,
    and is the whole contribution of a worker not enrolled voluntarily.

    Returns:
        ``None`` when the worker is not enrolled and owes no contractual
        contribution.
    """
    deducted = inp.opening.earnings.pension_deducted
    if inp.pension is None:
        if inp.contractual_fund.amount == _ZERO:
            return None
        rules = inp.rules.complementary_pension
        return contractual_only(inp.contractual_fund.amount, rules, deducted)
    terms = inp.pension
    bases = {
        FundContributionBase.INPS_BASE: inp.monthly_gross + inp.event_inps_base,
        FundContributionBase.TFR_BASE: inp.monthly_gross
        + inp.in_kind
        + inp.event_tfr_base,
        FundContributionBase.CONTRACTUAL_MINIMUM: terms.minimum_base,
    }
    fund = terms.fund
    base = bases[fund.contribution_base]
    above = fund.employee_base_above_minimum
    minimum = terms.employee_min_rate
    chosen_more = minimum is not None and terms.employee_rate > minimum
    employee_base = bases[above] if above is not None and chosen_more else None
    return contribute(terms, base, deducted, inp.contractual_fund.amount, employee_base)


def projected_adjustment(
    inp: _AmountsInput, pension: PensionContribution | None
) -> Decimal:
    """Return the taxable change of the fund on the slots still to come.

    The recurring gross still to come is taken as their INPS base, as the
    projection of the employee INPS does.  A contractual contribution alone
    stays within the cap: the projection leaves it out.

    Returns:
        Zero when the worker is not enrolled.
    """
    if pension is None or pension.terms is None:
        return _ZERO
    deducted = inp.opening.earnings.pension_deducted + pension.deductible
    return upcoming_adjustment(pension.terms, inp.upcoming_gross, deducted)
