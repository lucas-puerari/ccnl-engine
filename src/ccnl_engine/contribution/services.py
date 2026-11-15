"""INPS contributions and TFR accrual of one run."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contribution.domestic.services import (
    compute_domestic_breakdown,
)
from ccnl_engine.contribution.rate.rules import resolve_rates
from ccnl_engine.contribution.rules import resolve_contributions
from ccnl_engine.contribution.sick_pay_supplement.services import (
    with_sick_pay_supplement,
)
from ccnl_engine.contribution.tfr.services import ivs_employer_base
from ccnl_engine.decision.models import (
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.end_of_service.services import (
    end_of_service_employee_rate,
    with_enam,
    with_end_of_service,
    with_life_insurance,
    with_public_credit,
)
from ccnl_engine.fund.solidarity.services import (
    with_solidarity_fund,
)
from ccnl_engine.pay_item.rounding.policies import contribution_base
from ccnl_engine.pay_item.services import _ZERO

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.amount.types import _AmountsInput
    from ccnl_engine.contribution.results import ContributionBreakdown

#: An employer of up to five employees in the FIS must say whether its rate
#: is cut (D.Lgs. 148/2015 art. 29 c. 8-bis).
FIS_REDUCTION_UNKNOWN = CalculationIssue(
    code="fis_reduction_unknown",
    capability="inps_employer",
    message=(
        "an employer of the fondo di integrazione salariale with up to five "
        "employees pays 40% less FIS when it has not applied for the assegno "
        "di integrazione salariale for twenty-four months (D.Lgs. 148/2015 "
        "art. 29 c. 8-bis); the amounts shown charge the full rate; state "
        "EmployerProfile.fis_reduction"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="fis_reduction",
)

#: A craft firm above fifteen employees must say whether it owes the CIGS.
CIGS_INDOTTO_UNKNOWN = CalculationIssue(
    code="cigs_indotto_unknown",
    capability="inps_employer",
    message=(
        "a craft firm with more than fifteen employees in the indotto of a firm "
        "with the prevailing management influence owes the CIGS contribution "
        "of 0.90%, 0.30% of it the worker's (D.Lgs. 148/2015 art. 20 c. 1 "
        "lett. b, art. 23 c. 1); the amounts shown charge none; state "
        "EmployerProfile.cigs_indotto"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="cigs_indotto",
)

#: An agricultural employer must say the zone its contributions are cut in.
AGRICULTURAL_ZONE_UNKNOWN = CalculationIssue(
    code="agricultural_zone_unknown",
    capability="inps_employer",
    message=(
        "an agricultural employer of a zona svantaggiata pays 68% less "
        "employer contributions, of a zona particolarmente svantaggiata 75% "
        "less (INPS circ. 43/2026 par. 7); the amounts shown charge the full "
        "rates; state EmployerProfile.agricultural_zone"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="agricultural_zone",
)


def _raised(inp: _AmountsInput, base: Decimal) -> Decimal:
    """Return ``base`` raised to the minimum INPS base of the run.

    Returns:
        ``base``, or the minimum when one is determined and higher, rounded
        to the whole euro (:func:`contribution_base`).
    """
    minimum = inp.inps_minimum
    whole_euro = inp.rules.inps is None or inp.rules.inps.base_whole_euro
    return contribution_base(
        base if minimum is None else max(base, minimum), whole_euro=whole_euro
    )


def _ordinary_breakdown(inp: _AmountsInput, base: Decimal) -> ContributionBreakdown:
    """Return the ordinary INPS breakdown of ``base`` for the run.

    Returns:
        The breakdown with the YTD INPS base, the IVS ceiling and the
        additional 1% IVS position of the run.
    """
    return resolve_contributions(
        base,
        inp.rules,
        inp.contract_type,
        inp.category,
        ytd_inps_base=inp.ytd_inps_base,
        ivs_ceiling_applies=inp.ivs_ceiling_applies,
        additional=inp.additional_ivs,
    )


def run_contributions(inp: _AmountsInput) -> tuple[ContributionBreakdown, Decimal]:
    """Return the INPS breakdown of the run and the employee rate for IRPEF.

    Domestic CCNLs have no ordinary INPS rules: their flat per-hour
    contributions apply and no employee rate is projected on the slots
    still to come.  The tredicesima of a domestic worker is spread over
    the hours of the year in the effective hourly pay that bands them
    (:func:`~ccnl_engine.contribution.domestic.services._domestic_hourly_rate`),
    so its own run charges no hours.

    Returns:
        ``(breakdown, employee_rate)``.
    """
    if inp.rules.inps is not None:
        base = _raised(inp, inp.monthly_gross + inp.event_inps_base)
        breakdown = with_end_of_service(inp, _ordinary_breakdown(inp, base))
        # The pension base of the credit and ASV contributions stops at the
        # IVS massimale, like the IVS share itself.
        pension_base = ivs_employer_base(breakdown)
        breakdown, credit = with_public_credit(inp, breakdown, pension_base)
        breakdown, life = with_life_insurance(inp, breakdown, pension_base)
        breakdown, enam = with_enam(inp, breakdown)
        breakdown, fund = with_solidarity_fund(inp, breakdown)
        breakdown = with_sick_pay_supplement(inp, breakdown, base)
        rates = resolve_rates(inp.rules, inp.contract_type, inp.category)
        public = end_of_service_employee_rate(inp) + credit + life + enam
        employee = rates.employee_rate + public + fund
        return breakdown, employee
    breakdown = compute_domestic_breakdown(
        inp.rules,
        inp.weekly_hours,
        _ZERO if inp.additional_month else inp.contributable_hours,
        inp.domestic_hourly_rate,
        inp.contract_type,
    )
    return breakdown, _ZERO
