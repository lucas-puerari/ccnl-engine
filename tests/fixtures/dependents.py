"""Dependants with every condition of art. 12 TUIR stated.

A test that is not about an unknown condition builds its dependant here:
resident under c. 2-bis, no own income (within the limit of c. 2),
cohabiting when an ascendant (c. 1 lett. d), the whole deduction to the
worker when a child or an ascendant, and dependent over the whole tax year
(the interval open at both ends).  Each field can be overridden.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.inputs import Dependent, DependentRelationship

if TYPE_CHECKING:
    from datetime import date

__all__ = ["declared_dependent"]


def declared_dependent(
    relationship: DependentRelationship,
    *,
    birth_date: date | None = None,
    disabled: bool = False,
    own_income: Decimal | None = Decimal(0),
    allocation_pct: Decimal | None = None,
    cohabiting: bool | None = None,
    residency_eligibility: bool | None = True,
    dependent_from: date | None = None,
    dependent_until: date | None = None,
) -> Dependent:
    """Return a dependant whose conditions are all stated.

    ``allocation_pct`` and ``cohabiting`` left ``None`` are stated as the
    whole share and as cohabiting where art. 12 reads them: a share for a
    child or an ascendant, cohabitation for an ascendant.

    Returns:
        The dependant.
    """
    spouse = relationship is DependentRelationship.SPOUSE
    ascendant = relationship is DependentRelationship.ASCENDANT
    if allocation_pct is None and not spouse:
        allocation_pct = Decimal(100)
    if cohabiting is None and ascendant:
        cohabiting = True
    return Dependent(
        relationship,
        birth_date=birth_date,
        disabled=disabled,
        own_income=own_income,
        allocation_pct=allocation_pct,
        cohabiting=cohabiting,
        residency_eligibility=residency_eligibility,
        dependent_from=dependent_from,
        dependent_until=dependent_until,
    )
