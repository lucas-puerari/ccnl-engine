"""Standard INPS rate selection (permanent and fixed-term contracts)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.payroll.service._contributions_apprentice import (
    apprentice_employer_ivs_rate,
    apprentice_employer_rate,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.payroll.domain.employment import Contract as Employment
    from ccnl_engine.tax.domain.contribution_rules import InpsRates
    from ccnl_engine.tax.domain.ruleset import YearRules


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


def resolve_rates(
    rules: YearRules, employment: Employment, category: WorkerCategory | None
) -> ContributionRates:
    """Resolve INPS rates for an employment type and worker category.

    Apprentices use the statutory reduced rates (L. 296/2006 art. 1 c. 773,
    headcount already resolved in ``rules.apprentice``).  The NASpI
    *addizionale* (Art. 2 c. 28 L. 92/2012) is **not** applied to apprentices:
    apprendistato is explicitly exempt under Art. 2 c. 29 of the same law, so
    the ``Apprentice`` branch returns before the ``FixedTerm`` check — this is
    intentional, not an oversight.  Fixed-term non-apprentice contracts add the
    addizionale to the employer rate only; the IVS rate is unchanged because
    the addizionale is a non-IVS component (NASpI fund).

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
    employer_rate = inps_employer_rate(rules.inps, category)
    # NASpI addizionale is not IVS; keep ivs_rate unchanged.
    employer_ivs_rate = rules.inps.employer_ivs_rate
    if isinstance(employment, FixedTerm):
        employer_rate += rules.fixed_term_additional_rate
    return ContributionRates(
        employee_rate=rules.inps.employee_rate,
        employee_ivs_rate=rules.inps.employee_ivs_rate,
        employer_rate=employer_rate,
        employer_ivs_rate=employer_ivs_rate,
    )
