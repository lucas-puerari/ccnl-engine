"""Take the monthly payments of the worker's category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.employment.category.models import WorkerCategory

__all__ = ["with_category_months"]


def with_category_months(ccnl: CCNL, category: WorkerCategory | None) -> CCNL:
    """Return ``ccnl`` with the monthly payments of the worker's category.

    Edilizia PMI Confapi ANIEM: the operai are paid 13 months, the
    impiegati a tredicesima (art. 63) and a premio annuo (art. 64), 14.

    Returns:
        ``ccnl`` unchanged, or a copy whose ``additional_months`` are those
        of ``category`` in ``additional_months_by_category``.
    """
    months = ccnl.parameters.additional_months_by_category.get(category)  # type: ignore[arg-type]
    if months is None:
        return ccnl
    parameters = ccnl.parameters.model_copy(update={"additional_months": months})
    return ccnl.model_copy(update={"parameters": parameters})
