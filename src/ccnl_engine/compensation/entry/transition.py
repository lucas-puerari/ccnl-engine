"""Resolve a time-limited entry classification to its target level."""

from datetime import date

from ccnl_engine.agreement.facade import CCNL
from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.compensation.models import Level
from ccnl_engine.employment.inputs import Apprentice
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.seniority.inputs import (
    EarnedIncrements,
    SeniorityFact,
    SenioritySource,
)


def require_effective_salary(
    ccnl: CCNL,
    level: Level,
    contract_type: object,
    as_of: date,
    started_on: date | None,
    hired_on: date | None = None,
    seniority: SeniorityFact | None = None,
) -> Level:
    """Preflight the mandatory transition and return the level actually paid.

    Returns:
        Effective level with a salary on ``as_of``.
    """
    require_preserved_seniority(
        ccnl,
        level,
        contract_type,
        as_of,
        started_on,
        hired_on,
        seniority.months_in_month(as_of.year, as_of.month) if seniority else None,
        earned=seniority.earned if seniority else None,
    )
    effective = transitioned_level(
        ccnl, level, contract_type, as_of, started_on, hired_on=hired_on
    )
    with rule_scope(ruleset=ccnl.meta.ccnl_id, feature="base_salary"):
        effective.base_salary.value_at(as_of)
    return effective


def require_preserved_seniority(
    ccnl: CCNL,
    level: Level,
    contract_type: object,
    as_of: date,
    started_on: date | None,
    hired_on: date | None,
    months: int | None,
    *,
    earned: EarnedIncrements | None = None,
) -> None:
    """Refuse promotions that would reprice previously matured junior steps.

    Raises:
        InvalidInputError: If prior-level step amounts cannot be preserved.
    """
    if (
        level.transition_to is not None
        and months is not None
        and months >= 24
        and earned is None
        and transitioned_level(
            ccnl, level, contract_type, as_of, started_on, hired_on=hired_on
        ).code
        != level.code
    ):
        msg = (
            "junior promotion with matured seniority steps needs preserved "
            "prior-level increments and unfinished biennium"
        )
        raise InvalidInputError(msg, field="Employment.seniority", feature="seniority")


def transitioned_level(
    ccnl: CCNL,
    level: Level,
    contract_type: object,
    as_of: date,
    started_on: date | None,
    *,
    hired_on: date | None = None,
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
    wait = level.transition_after_months
    if level.transition_hire_bands:
        if hired_on is None:
            msg = "hire date is required to select the junior transition cohort"
            raise InvalidInputError(
                msg,
                field="Employment.employment_period",
                feature="base_salary",
            )
        bands = sorted(level.transition_hire_bands, key=lambda band: band.hired_from)
        matching = [band for band in bands if hired_on >= band.hired_from]
        if not matching:
            msg = "pre-2018 junior classification requires verified 2017 level history"
            raise InvalidInputError(
                msg,
                field="Employment.level_started_on",
                feature="base_salary",
            )
        wait = matching[-1].after_months
    if wait is None or started_on is None:
        return level  # The missing-fact issue blocks the provisional minimum.
    elapsed = SeniorityFact.since(
        started_on, SenioritySource.EMPLOYER_RECORDS
    ).months_in_month(as_of.year, as_of.month)
    return ccnl.level_by_code(target) if elapsed >= wait else level
