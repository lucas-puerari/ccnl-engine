"""CIGS contribution of the craft firms of an indotto.

D.Lgs. 148/2015 art. 20 c. 1 lett. b brings under the cassa integrazione
straordinaria the "imprese artigiane che procedono alla sospensione dei
lavoratori in conseguenza di sospensioni o riduzioni dell'attività
dell'impresa che esercita l'influsso gestionale prevalente", with more than
fifteen employees on average; art. 23 c. 1 charges them 0.90%, 0.60% to the
employer and 0.30% to the worker.  Whether a craft firm works in such an
indotto is known to it only:
:attr:`~ccnl_engine.employer.inputs.EmployerProfile.cigs_indotto` states it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.types import NonNegativeRate

if TYPE_CHECKING:
    from ccnl_engine.contribution.rate.models import InpsRates

__all__ = ["CigsIndotto", "with_cigs_indotto"]


class CigsIndotto(BaseModel):
    """The CIGS rate of a craft firm of an indotto.

    Attributes:
        more_than_employees: Headcount the firm must exceed.
        employer_rate: Employer share.
        employee_rate: Worker share.
        provenance: Where the rate is read from.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    more_than_employees: int = Field(ge=0)
    employer_rate: NonNegativeRate
    employee_rate: NonNegativeRate
    provenance: RuleProvenance | None = None


def with_cigs_indotto(
    rates: InpsRates, indotto: bool | None, headcount: int
) -> InpsRates:
    """Return ``rates`` for a craft firm in or out of an indotto.

    Args:
        rates: Rates resolved for the headcount of the employer.
        indotto: Whether the firm works in the indotto of art. 20 c. 1
            lett. b; ``None`` when unknown.
        headcount: Headcount of the employer.

    Returns:
        ``rates`` when the rule does not apply; with it, the employee,
        employer and category rates raised by its shares; with the fact
        unknown, ``rates`` flagged ``cigs_indotto_open``, for a
        ``missing_fact`` issue.
    """
    rule = rates.cigs_indotto
    if rule is None or headcount <= rule.more_than_employees or indotto is False:
        return rates
    if indotto is None:
        return rates.model_copy(update={"cigs_indotto_open": True})
    by_category = {
        category: rate + rule.employer_rate
        for category, rate in rates.employer_rate_by_category.items()
    }
    return rates.model_copy(
        update={
            "employee_rate": rates.employee_rate + rule.employee_rate,
            "employer_rate": rates.employer_rate + rule.employer_rate,
            "employer_rate_by_category": by_category,
        }
    )
