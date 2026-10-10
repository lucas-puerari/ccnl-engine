"""Reduced FIS rate of the smallest employers.

D.Lgs. 148/2015 art. 29 c. 8 sets the rate of the fondo di integrazione
salariale at 0.50% for the employers with on average up to five employees
in the semester before; c. 8-bis, from 1 January 2025, cuts it by 40% for
those who have not applied for the assegno di integrazione salariale for at
least twenty-four months.  Art. 33 c. 1 splits the rate two thirds to the
employer and one third to the worker, so the cut lowers both shares.
Whether the employer has applied is known to it only:
:attr:`~ccnl_engine.payroll.employment.inputs_employer.EmployerProfile.fis_reduction`
states it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.primitives import NonNegativeRate  # noqa: TC001
from ccnl_engine.provenance.source.models_chain import RuleProvenance  # noqa: TC001

if TYPE_CHECKING:
    from ccnl_engine.tax.contribution.models import InpsRates

__all__ = ["FisReduction", "with_fis_reduction"]


class FisReduction(BaseModel):
    """The cut of the FIS rate of art. 29 c. 8-bis D.Lgs. 148/2015.

    Attributes:
        max_employees: Largest headcount the cut applies to.
        employer_rate: Cut of the employer share of the FIS rate.
        employee_rate: Cut of the worker share of the FIS rate.
        provenance: Where the cut is read from.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_employees: int = Field(ge=1)
    employer_rate: NonNegativeRate
    employee_rate: NonNegativeRate
    provenance: RuleProvenance | None = None


def with_fis_reduction(
    rates: InpsRates, reduced: bool | None, headcount: int
) -> InpsRates:
    """Return ``rates`` for an employer that has or has not the cut.

    Args:
        rates: Rates resolved for the headcount of the employer.
        reduced: Whether the employer has the cut; ``None`` when unknown.
        headcount: Headcount of the employer.

    Returns:
        ``rates`` without a cut that applies; with it, the employee, employer
        and category rates lowered by its shares; with the fact unknown,
        ``rates`` flagged ``fis_reduction_open``, for a ``missing_fact``
        issue.
    """
    cut = rates.fis_reduction
    if cut is None or headcount > cut.max_employees or reduced is False:
        return rates
    if reduced is None:
        return rates.model_copy(update={"fis_reduction_open": True})
    by_category = {
        category: rate - cut.employer_rate
        for category, rate in rates.employer_rate_by_category.items()
    }
    return rates.model_copy(
        update={
            "employee_rate": rates.employee_rate - cut.employee_rate,
            "employer_rate": rates.employer_rate - cut.employer_rate,
            "employer_rate_by_category": by_category,
        }
    )
