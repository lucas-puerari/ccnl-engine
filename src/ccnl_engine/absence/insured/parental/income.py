"""The income condition of the parental leave beyond the indemnified months.

Art. 34 c. 3 D.Lgs. 151/2001 pays the further months 30% "a condizione che
il reddito individuale dell'interessato sia inferiore a 2,5 volte l'importo
del trattamento minimo di pensione": the income is a fact of the parent
(``individual_income``) and the minimum a figure of the INPS circular of the
year (``ParentalRates.minimum_pension_yearly``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus, IssueCause

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from datetime import date
    from decimal import Decimal

__all__ = ["INCOME_UNKNOWN", "income_check"]

#: Issue of a further month whose parent's income is not stated.
INCOME_UNKNOWN = "parental_income_unknown"


def income_check(
    rates: Mapping[date, Decimal | None],
    days: Iterable[date],
    income: Decimal | None,
    capability: str,
) -> tuple[CalculationIssue | None, bool]:
    """Tell what a day without a rate needs.

    Returns:
        A missing-fact issue when a day of ``days`` has no rate and the
        income is not stated, and whether the rate is missing for the
        year's minimum instead (the limitation of unpublished data).
    """
    if all(rates[day] is not None for day in days):
        return None, False
    if income is not None:
        return None, True
    issue = CalculationIssue(
        code=INCOME_UNKNOWN,
        message=(
            "the parental leave runs past the indemnified months: state the "
            "parent's individual_income of the year (art. 34 c. 3 D.Lgs. "
            "151/2001: 30% below 2.5 times the trattamento minimo)"
        ),
        status=CalculationStatus.INCOMPLETE,
        capability=capability,
        fact="individual_income",
        cause=IssueCause.FACT,
    )
    return issue, False
