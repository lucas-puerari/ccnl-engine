"""Monthly pay chain of a run: level or apprentice chain, part-time scaling."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.apprenticeship.rules import _apprentice_chain
from ccnl_engine.compensation.element.rules import _level_chain
from ccnl_engine.compensation.element.types import ApprenticeshipScaling
from ccnl_engine.employment.inputs import Apprentice, FixedTerm, Permanent
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.seniority.repricing.rules import (
    earned_seniority,
    promoted_seniority,
)
from ccnl_engine.seniority.rules import _resolve_seniority_count

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.compensation.models import Level
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.seniority.inputs import SeniorityFact


def _seniority_count(
    ccnl: CCNL,
    level: Level,
    seniority_months: int | None,
    worker_category: WorkerCategory | None,
) -> int:
    """Return the seniority increments matured by the worker.

    Returns:
        Zero when the seniority is not declared.
    """
    if seniority_months is None:
        return 0
    return _resolve_seniority_count(
        ccnl.parameters.seniority_increments,
        level.code,
        None,
        seniority_months,
        worker_category=worker_category,
    )


#: Variant of the CCNL limitation a part-time scaling of the pay traverses.
PART_TIME_VARIANT = "part_time_scaling"


def _part_time(
    ccnl: CCNL,
    chain: MonthlyPayChain,
    weekly_hours: Decimal | None,
    full_time_weekly_hours: Decimal | None,
) -> MonthlyPayChain:
    """Scale ``chain`` to the part-time ratio of the weekly hours.

    A regime with ``flat_pay_max_weekly_hours`` pays the chain in full up to
    that ceiling.  A scaled chain records the :data:`PART_TIME_VARIANT`
    path of its CCNL, which a CCNL whose text gives no proportioning rule
    declares as a limitation.

    Returns:
        ``chain`` unchanged unless ``weekly_hours < full_time_weekly_hours``.

    Raises:
        InvalidInputError: When the weekly hours exceed the ceiling of a
            flat-pay regime.
    """
    ceiling = ccnl.parameters.flat_pay_max_weekly_hours
    if ceiling is not None:
        if weekly_hours is not None and weekly_hours > ceiling:
            msg = (
                f"CCNL {ccnl.meta.ccnl_id} pays its minimum up to {ceiling} "
                f"weekly hours; the employment states {weekly_hours}"
            )
            raise InvalidInputError(
                msg, field="Employment.weekly_hours", feature="employment_facts"
            )
        return chain
    # Both values are positive: WeeklyHours validates them on construction.
    if (
        full_time_weekly_hours is not None
        and weekly_hours is not None
        and weekly_hours < full_time_weekly_hours
    ):
        scaled = chain.scaled_for_part_time(weekly_hours / full_time_weekly_hours)
        path = f"{ccnl.meta.ccnl_id}/{PART_TIME_VARIANT}"
        return replace(scaled, limitations=(*scaled.limitations, path))
    return chain


def _resolve_chain(
    ccnl: CCNL,
    level: Level,
    contract_type: Permanent | FixedTerm | Apprentice,
    as_of: date,
    *,
    seniority_months: int | None = None,
    roles: frozenset[str] = frozenset(),
    worker_category: WorkerCategory | None = None,
    weekly_hours: Decimal | None = None,
    full_time_weekly_hours: Decimal | None = None,
    hired_on: date | None = None,
    seniority: SeniorityFact | None = None,
) -> tuple[MonthlyPayChain, ApprenticeshipScaling | None]:
    """Resolve the elementary pay chain for the period.

    For a percentage apprenticeship the percentage reduces the base salary,
    the seniority and the allowances flagged ``apprenticeship_pct_relevant``;
    the other allowances are paid in full.  Part-time scaling then applies
    when ``weekly_hours < full_time_weekly_hours``.  An allowance of a
    cohort in service on a day (``in_service_on``) is kept only when
    ``hired_on`` is known and not later.  A qualified worker whose
    ``seniority`` states the increments earned is paid them as stated plus
    the increments matured since (:func:`earned_seniority`); one whose
    ``seniority`` states a promotion, under a CCNL that reprices the earlier
    increments at the next one, is paid them at the level before it until
    then (:func:`promoted_seniority`).

    Returns:
        :class:`~ccnl_engine.compensation.element.types.MonthlyPayChain` with each
        component rounded and ready for pay-item emission, and the
        apprenticeship scaling applied, ``None`` unless the worker is on a
        percentage apprenticeship track.
    """
    with rule_scope(ruleset=ccnl.meta.ccnl_id):
        chain, scaling = _contract_chain(
            ccnl,
            level,
            contract_type,
            as_of,
            seniority_months=seniority_months,
            roles=roles,
            worker_category=worker_category,
            hired_on=hired_on,
        )
        if (
            seniority is not None
            and seniority.earned is not None
            and seniority_months is not None
            and not isinstance(contract_type, Apprentice)
        ):
            with rule_scope(feature="seniority"):
                stated = earned_seniority(
                    ccnl.parameters.seniority_increments,
                    level.code,
                    seniority.earned,
                    seniority.months,
                    seniority_months,
                    as_of,
                    worker_category=worker_category,
                )
            chain = replace(chain, seniority=stated)
        elif (
            seniority is not None
            and seniority.promotion is not None
            and seniority_months is not None
            and _reprices_at_next(ccnl)
            and not isinstance(contract_type, Apprentice)
        ):
            promotion = seniority.promotion
            with rule_scope(feature="seniority"):
                stated = promoted_seniority(
                    ccnl.parameters.seniority_increments,
                    level.code,
                    promotion.from_level,
                    seniority.months_at(promotion.effective_on),
                    seniority_months,
                    as_of,
                    worker_category=worker_category,
                )
            chain = replace(chain, seniority=stated)
    chain = chain.for_hire_date(hired_on)
    return _part_time(ccnl, chain, weekly_hours, full_time_weekly_hours), scaling


def _contract_chain(
    ccnl: CCNL,
    level: Level,
    contract_type: Permanent | FixedTerm | Apprentice,
    as_of: date,
    *,
    seniority_months: int | None,
    roles: frozenset[str],
    worker_category: WorkerCategory | None,
    hired_on: date | None,
) -> tuple[MonthlyPayChain, ApprenticeshipScaling | None]:
    """Return the level or apprentice chain of the contract, full time.

    An apprentice hired by the day of the CCNL apprentice cohort is paid
    the increment of the cohort.

    Returns:
        The chain and the apprenticeship scaling, as :func:`_resolve_chain`.
    """
    count = _seniority_count(ccnl, level, seniority_months, worker_category)
    scaling: ApprenticeshipScaling | None = None
    if isinstance(contract_type, Apprentice):
        ccnl = _cohort_rules(ccnl, hired_on)
        chain, pct, _ = _apprentice_chain(
            ccnl,
            level,
            contract_type,
            count,
            roles,
            as_of,
            worker_category=worker_category,
            seniority_months=seniority_months,
        )
        if pct is not None:
            scaling = ApprenticeshipScaling.of(chain, pct)
            chain = chain.scaled_for_apprenticeship(pct)
    else:
        chain = _level_chain(
            ccnl,
            level,
            count,
            roles,
            as_of,
            is_apprentice=False,
            worker_category=worker_category,
            seniority_months=seniority_months,
        )
    return chain, scaling


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
