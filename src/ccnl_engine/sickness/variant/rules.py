"""Take the sickness rules a CCNL sets apart for the worker of the run."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.employment.apprentice.inputs import Apprentice

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.employment.category.models import WorkerCategory

__all__ = ["with_sickness_variant"]


def with_sickness_variant(
    ccnl: CCNL, category: WorkerCategory | None, contract_type: object
) -> CCNL:
    """Return ``ccnl`` with the sickness rules of the worker's kind.

    An apprentice takes ``apprentice_sickness_rules``, else the rules of
    the worker's category in ``sickness_rules_by_category``; a worker of no
    such kind keeps ``sickness_rules``.

    Returns:
        ``ccnl`` unchanged, or a copy whose ``sickness_rules`` are the rules
        of the worker's kind.
    """
    work = ccnl.work_rules
    if work is None:
        return ccnl
    rules = None
    if isinstance(contract_type, Apprentice):
        rules = work.apprentice_sickness_rules
    if rules is None and category is not None:
        rules = work.sickness_rules_by_category.get(category)
    if rules is None:
        return ccnl
    return ccnl.model_copy(
        update={"work_rules": work.model_copy(update={"sickness_rules": rules})}
    )
