"""The totals of a result that a limitation or a blocker leaves unreliable.

They sit with the limitations, the lower of their two users, so that
:mod:`ccnl_engine.limitation.models` names them without importing the
assurance of a result (:mod:`ccnl_engine.assurance.models`).
"""

from __future__ import annotations

from enum import StrEnum

__all__ = ["ALL_TOTALS", "ResultTotal"]


class ResultTotal(StrEnum):
    """A total of a result that a blocker leaves unreliable.

    Attributes:
        NET_PAY: The net pay of the worker.
        EMPLOYER_COST: The employer cost of the result.
    """

    NET_PAY = "net_pay"
    EMPLOYER_COST = "employer_cost"


#: Both totals: what a blocker leaves unreliable unless it states otherwise.
ALL_TOTALS: frozenset[ResultTotal] = frozenset(ResultTotal)
