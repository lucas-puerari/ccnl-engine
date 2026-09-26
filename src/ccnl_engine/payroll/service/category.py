"""Worker category resolution for one employment on one CCNL level."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.category import parse_worker_category
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.contract.domain.compensation import Level
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.domain.employment import SeniorityMonths

_FEATURE = "worker_category"


def resolve_worker_category(
    ccnl: CCNL,
    level: Level,
    declared: WorkerCategory | str | None,
    *,
    seniority: SeniorityMonths | None,
) -> WorkerCategory | None:
    """Return the worker category used for pay and contributions.

    Args:
        ccnl: The applicable CCNL.
        level: The worker's level within ``ccnl``.
        declared: Category declared on the employment, or ``None``.
        seniority: Months of service; seniority increments are resolved
            only when given, so only then can they require a category.

    Returns:
        The declared category, or the level's category when the level fixes
        it; ``None`` when neither gives one and none is needed.

    Raises:
        InvalidInputError: When the declared category is unknown or differs
            from the one the level fixes, or when the category is needed to
            price seniority increments and none is available.
    """
    category = parse_worker_category(declared)
    if level.category is not None:
        if category is not None and category != level.category:
            msg = (
                f"category {category.value!r} is not admitted by level "
                f"{level.code!r} of {ccnl.meta.ccnl_id}, which is reserved to "
                f"category {level.category.value!r}"
            )
            raise InvalidInputError(msg, feature=_FEATURE)
        # The level admits a single category, so it fixes the category
        # unambiguously even when the employment does not declare it.
        return level.category
    if (
        category is None
        and seniority is not None
        and ccnl.parameters.seniority_increments.requires_category(level.code)
    ):
        msg = (
            f"worker category is required for level {level.code!r} of "
            f"{ccnl.meta.ccnl_id}: seniority increments differ by category"
        )
        remediation = "Set Employment.category (e.g. operaio or impiegato)."
        raise InvalidInputError(msg, feature=_FEATURE, remediation=remediation)
    return category
