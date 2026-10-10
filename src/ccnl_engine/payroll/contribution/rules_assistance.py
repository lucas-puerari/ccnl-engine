"""Contractual assistance contribution of one run, charged per paid hour."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.errors import MissingRequiredFactError
from ccnl_engine.payroll.amount.policies_rounding import money

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.provenance.source.models_chain import RuleProvenance

__all__ = ["CAPABILITY", "AssistanceContribution", "AssistanceTerms", "run_assistance"]

#: Catalog capability of the contribution.
CAPABILITY = "assistance_contribution"


@dataclass(frozen=True)
class AssistanceTerms:
    """Rates per paid hour the CCNL charges on the competence date.

    Attributes:
        employee_per_hour: Worker share per paid hour, in EUR.
        employer_per_hour: Employer share per paid hour, in EUR.
        provenance: Source of the clause.
    """

    employee_per_hour: Decimal
    employer_per_hour: Decimal
    provenance: RuleProvenance


@dataclass(frozen=True)
class AssistanceContribution:
    """The contribution of one run.

    Attributes:
        terms: Rates it was charged at.
        hours: Paid hours it was charged on.
        employee: Worker share, withheld from the pay.
        employer: Employer share, part of the employer cost.
    """

    terms: AssistanceTerms
    hours: Decimal
    employee: Decimal
    employer: Decimal


def run_assistance(
    terms: AssistanceTerms | None, hours: Decimal | None
) -> AssistanceContribution | None:
    """Return the contribution of the run on its paid hours.

    The hours are those the INPS contributions of the run are paid on: the
    CCNL lavoro domestico collects the contribution with them (art. 54
    c. 1).  A run is charged on the hours it states, a tredicesima run too.

    Args:
        terms: Rates of the CCNL, ``None`` when it charges no contribution.
        hours: Contributable hours of the run, ``None`` when not stated.

    Returns:
        ``None`` when the CCNL charges no contribution.

    Raises:
        MissingRequiredFactError: When the CCNL charges one and the request
            states no contributable hours.
    """
    if terms is None:
        return None
    if hours is None:
        msg = (
            "the CCNL charges its assistance contribution per paid hour: "
            "set PeriodFacts.contributable_hours"
        )
        raise MissingRequiredFactError(msg, feature=CAPABILITY)
    return AssistanceContribution(
        terms=terms,
        hours=hours,
        employee=money(terms.employee_per_hour * hours),
        employer=money(terms.employer_per_hour * hours),
    )
