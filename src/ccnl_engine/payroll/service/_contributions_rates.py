"""Standard INPS rate selection (permanent and fixed-term contracts)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.employment import Apprentice
from ccnl_engine.payroll.service._contributions_apprentice import (
    apprentice_employer_ivs_rate,
    apprentice_employer_rate,
)
from ccnl_engine.payroll.service.naspi_surcharge import naspi_surcharge

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.contract.employment.models_category import WorkerCategory
    from ccnl_engine.payroll.domain.employment import Contract as Employment
    from ccnl_engine.tax.annual.models import YearRules
    from ccnl_engine.tax.contribution.models import InpsRates


@dataclass(frozen=True)
class ContributionRates:
    """Employee and employer INPS rates resolved for one scenario."""

    employee_rate: Decimal
    employee_ivs_rate: Decimal
    employer_rate: Decimal
    employer_ivs_rate: Decimal


def inps_employer_rate(rates: InpsRates, category: WorkerCategory | None) -> Decimal:
    """Return the employer rate applicable to a worker category.

    Returns:
        The employer contribution rate for the given worker category.
    """
    if category is None:
        return rates.employer_rate
    return rates.employer_rate_by_category.get(category, rates.employer_rate)


CATEGORY_RATE_ASSUMED_CODE = "employer_rate_category_assumed"


def category_rate_issue(
    rules: YearRules, employment: Employment, category: WorkerCategory | None
) -> CalculationIssue | None:
    """Return the issue of an employer rate chosen without a worker category.

    When a sector sets employer rates by category (e.g. artigianato:
    impiegati and quadri 24.71%) and the worker has no category, the
    general tier rate applies, which is the rate of the operai.  The result
    is provisional until the category is declared.

    Returns:
        A provisional issue, or ``None`` when the rate did not depend on a
        missing category (apprentices use their statutory rates).
    """
    inps = rules.inps
    if (
        inps is None
        or category is not None
        or not inps.employer_rate_by_category
        or isinstance(employment, Apprentice)
    ):
        return None
    categories = ", ".join(sorted(c.value for c in inps.employer_rate_by_category))
    return CalculationIssue(
        code=CATEGORY_RATE_ASSUMED_CODE,
        message=(
            "inps_employer: the level fixes no worker category and none was "
            f"declared, so the general employer rate {inps.employer_rate} "
            f"applies instead of the rate for {categories}; declare the "
            "category of the employment"
        ),
        status=CalculationStatus.PROVISIONAL,
    )


def resolve_rates(
    rules: YearRules, employment: Employment, category: WorkerCategory | None
) -> ContributionRates:
    """Resolve INPS rates for an employment type and worker category.

    Apprentices use the statutory reduced rates (L. 296/2006 art. 1 c. 773,
    headcount already resolved in ``rules.apprentice``), without the NASpI
    surcharge (L. 92/2012 art. 2 c. 29 lett. c).  Other contracts add the
    surcharge of :func:`~ccnl_engine.payroll.service.naspi_surcharge\
.naspi_surcharge` to the employer rate only; the IVS rate is unchanged
    because the surcharge is a non-IVS component (NASpI fund).

    Returns:
        ContributionRates with employee and employer rates for the scenario.

    Raises:
        TypeError: If ``rules.inps`` or ``rules.apprentice`` is None (domestic
            model sectors must take the flat-hour path in compute() instead).
    """
    if rules.inps is None or rules.apprentice is None:
        msg = (
            "resolve_rates requires standard INPS rates; "
            "domestic sectors must use the flat-hour path in compute()"
        )
        raise TypeError(msg)
    if isinstance(employment, Apprentice):
        emp_rate = rules.apprentice.employee_rate
        er_rate = apprentice_employer_rate(rules.apprentice, employment.months_elapsed)
        return ContributionRates(
            employee_rate=emp_rate,
            employee_ivs_rate=rules.apprentice.employee_ivs_rate,
            employer_rate=er_rate,
            employer_ivs_rate=apprentice_employer_ivs_rate(
                rules.apprentice, employment.months_elapsed
            ),
        )
    surcharge = naspi_surcharge(rules, employment, category)
    return ContributionRates(
        employee_rate=rules.inps.employee_rate,
        employee_ivs_rate=rules.inps.employee_ivs_rate,
        employer_rate=inps_employer_rate(rules.inps, category) + surcharge.rate,
        employer_ivs_rate=rules.inps.employer_ivs_rate,
    )
