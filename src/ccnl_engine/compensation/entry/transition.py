"""Resolve a time-limited entry classification to its target level."""

from datetime import date

from ccnl_engine.agreement.facade import CCNL
from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.compensation.models import Level
from ccnl_engine.employment.inputs import Apprentice
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource


def require_effective_salary(
    ccnl: CCNL,
    level: Level,
    contract_type: object,
    as_of: date,
    started_on: date | None,
) -> Level:
    """Preflight the mandatory transition and return the level actually paid.

    Returns:
        Effective level with a salary on ``as_of``.
    """
    effective = transitioned_level(ccnl, level, contract_type, as_of, started_on)
    with rule_scope(ruleset=ccnl.meta.ccnl_id, feature="base_salary"):
        effective.base_salary.value_at(as_of)
    return effective


def transitioned_level(
    ccnl: CCNL, level: Level, contract_type: object, as_of: date, hired_on: date | None
) -> Level:
    """Return the target level when tenure or a mandatory cutoff has passed.

    Returns:
        The effective level for this month's pay.

    Raises:
        InvalidInputError: If an apprentice needs distinct progression rules.
    """
    target = level.transition_to
    if target is None:
        return level
    if level.transition_by is not None and as_of >= level.transition_by:
        return ccnl.level_by_code(target)
    if isinstance(contract_type, Apprentice):
        msg = "entry-level apprenticeship requires its own progression"
        raise InvalidInputError(
            msg, field="Employment.level_code", feature="base_salary"
        )
    if level.transition_after_months is None:
        return level
    if hired_on is None:
        return level  # The missing-fact issue blocks the provisional minimum.
    elapsed = SeniorityFact.since(
        hired_on, SenioritySource.EMPLOYER_RECORDS
    ).months_in_month(as_of.year, as_of.month)
    return (
        ccnl.level_by_code(target)
        if elapsed >= level.transition_after_months
        else level
    )
