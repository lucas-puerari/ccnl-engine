"""Seniority cohort and promotion helpers for pay chains."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.models import CCNL


def _cohort_rules(ccnl: CCNL, hired_on: date | None) -> CCNL:
    """Return the CCNL whose apprentice increment is the one of the worker.

    Returns:
        ``ccnl`` with the cohort amount as the apprentice amount when the
        worker was hired by the cohort day; ``ccnl`` itself otherwise.
    """
    rules = ccnl.parameters.seniority_increments
    cohort = rules.apprentice_cohort
    if cohort is None or hired_on is None or hired_on > cohort.in_service_on:
        return ccnl
    kept = rules.model_copy(update={"apprentice_amount": cohort.amount})
    parameters = ccnl.parameters.model_copy(update={"seniority_increments": kept})
    return ccnl.model_copy(update={"parameters": parameters})


def _reprices_at_next(ccnl: CCNL) -> bool:
    """Return whether the CCNL reprices the increments at the next one.

    Returns:
        ``True`` when its seniority rules state so; a CCNL without the
        clause reprices them at once.
    """
    rule = ccnl.parameters.seniority_increments.on_promotion
    return rule is not None and rule.at_next_increment
