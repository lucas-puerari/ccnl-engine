"""Read the applicability facts of the capability registry from a request.

An applicability fact decides whether a required capability applies (see
:mod:`~ccnl_engine.payroll.capability.rules_requirement`).  Each one the registry
names needs a reader here, keyed by the path the registry uses; a fact is
absent when the request left it to its default, ``None``.
:func:`~ccnl_engine.payroll.capability.services_registry\
.validate_registry` rejects a registry naming a fact without a reader.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from ccnl_engine.payroll.period.requests import PeriodCalculationRequest

__all__ = ["FACT_READERS", "absent_facts"]

#: Reader of each applicability fact, keyed by its registry path.
FACT_READERS: Mapping[str, Callable[[PeriodCalculationRequest], object]] = {
    "facts.regione": lambda request: request.regione,
    "facts.comune_belfiore": lambda request: request.comune_belfiore,
    "facts.family_composition": lambda request: request.family_composition,
}


def absent_facts(request: PeriodCalculationRequest) -> frozenset[str]:
    """Return the applicability facts *request* left to their default.

    Returns:
        The registry path of every readable fact whose value is ``None``.
    """
    return frozenset(
        fact for fact, read in FACT_READERS.items() if read(request) is None
    )
