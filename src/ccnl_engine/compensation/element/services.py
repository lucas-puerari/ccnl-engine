"""Monthly pay chain of a run: level or apprentice chain, part-time scaling."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.apprenticeship.dual.rules import dual_chain
from ccnl_engine.apprenticeship.rules import _apprentice_chain
from ccnl_engine.compensation.element.rules import _level_chain
from ccnl_engine.compensation.element.seniority_helpers import (
    _cohort_rules,
    _reprices_at_next,
)
from ccnl_engine.compensation.element.types import ApprenticeshipScaling
from ccnl_engine.compensation.entry.rules import entry_level
from ccnl_engine.compensation.entry.transition import (
    require_preserved_seniority,
    transitioned_level,
)
from ccnl_engine.employment.apprentice.inputs import ApprenticeshipProgramme
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

_DUAL = frozenset({
    ApprenticeshipProgramme.FIRST_LEVEL,
    ApprenticeshipProgramme.THIRD_LEVEL,
})


def _seniority_count(
    ccnl: CCNL,
    level: Level,
    seniority_months: int | None,
    worker_category: WorkerCategory | None,
    contract_type: Permanent | FixedTerm | Apprentice,
) -> int:
    """Return the seniority increments matured by the worker.

    Returns:
        Zero when the seniority is not declared.
    """
    if seniority_months is None or (
        ccnl.parameters.seniority_increments.permanent_only
        and isinstance(contract_type, FixedTerm)
    ):
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
    increment_months: int | None = None,
    roles: frozenset[str] = frozenset(),
    worker_category: WorkerCategory | None = None,
    weekly_hours: Decimal | None = None,
    full_time_weekly_hours: Decimal | None = None,
    hired_on: date | None = None,
    level_started_on: date | None = None,
    seniority: SeniorityFact | None = None,
    career_months: int | None = None,
) -> tuple[MonthlyPayChain, ApprenticeshipScaling | None]:
    """Resolve the elementary pay chain for the period.

    Apprentice percentages reduce base, seniority and relevant allowances;
    other allowances stay whole. Part-time scaling then applies
    when ``weekly_hours < full_time_weekly_hours``. An ``in_service_on``
    allowance requires a known eligible hire date, a ``below_weekly_hours``
    one a stated shorter schedule. Stated earned steps
    persist (:func:`earned_seniority`); promotion under a repricing CCNL
    retains old steps until the next one (:func:`promoted_seniority`).

    Returns:
        :class:`~ccnl_engine.compensation.element.types.MonthlyPayChain` with each
        component rounded, and optional apprenticeship scaling.
    """
    with rule_scope(ruleset=ccnl.meta.ccnl_id):
        require_preserved_seniority(
            ccnl,
            level,
            contract_type,
            as_of,
            level_started_on,
            hired_on,
            seniority_months,
            earned=seniority.earned if seniority else None,
        )
        chain, scaling = _contract_chain(
            ccnl,
            level,
            contract_type,
            as_of,
            seniority_months=seniority_months,
            increment_months=(
                seniority_months if increment_months is None else increment_months
            ),
            roles=roles,
            worker_category=worker_category,
            hired_on=hired_on,
            level_started_on=level_started_on,
            career_months=career_months,
        )
        level = transitioned_level(
            ccnl, level, contract_type, as_of, level_started_on, hired_on=hired_on
        )
        eligible_for_seniority = not isinstance(contract_type, Apprentice) and not (
            ccnl.parameters.seniority_increments.permanent_only
            and isinstance(contract_type, FixedTerm)
        )
        if (
            seniority is not None
            and seniority.earned is not None
            and seniority_months is not None
            and eligible_for_seniority
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
                    roles=roles,
                )
            chain = replace(chain, seniority=stated)
        elif (
            seniority is not None
            and seniority.promotion is not None
            and seniority_months is not None
            and _reprices_at_next(ccnl)
            and eligible_for_seniority
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
                    roles=roles,
                )
            chain = replace(chain, seniority=stated)
    chain = chain.for_hire_date(hired_on).for_weekly_hours(weekly_hours)
    return _part_time(ccnl, chain, weekly_hours, full_time_weekly_hours), scaling


def _contract_chain(
    ccnl: CCNL,
    level: Level,
    contract_type: Permanent | FixedTerm | Apprentice,
    as_of: date,
    *,
    seniority_months: int | None,
    increment_months: int | None,
    roles: frozenset[str],
    worker_category: WorkerCategory | None,
    hired_on: date | None,
    level_started_on: date | None = None,
    career_months: int | None = None,
) -> tuple[MonthlyPayChain, ApprenticeshipScaling | None]:
    """Return the level or apprentice chain of the contract, full time.

    An apprentice hired by the day of the CCNL apprentice cohort is paid
    the increment of the cohort.

    Returns:
        The chain and the apprenticeship scaling, as :func:`_resolve_chain`.
    """
    level = transitioned_level(
        ccnl, level, contract_type, as_of, level_started_on, hired_on=hired_on
    )
    count = _seniority_count(
        ccnl, level, increment_months, worker_category, contract_type
    )
    scaling: ApprenticeshipScaling | None = None
    if isinstance(contract_type, Apprentice) and contract_type.programme in _DUAL:
        chain = dual_chain(
            ccnl,
            level,
            contract_type,
            count,
            roles,
            as_of,
            worker_category=worker_category,
            seniority_months=seniority_months,
        )
    elif isinstance(contract_type, Apprentice):
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
            scaled = ccnl.parameters.seniority_increments.apprentice_pct_scaled
            scaling = ApprenticeshipScaling.of(chain, pct, seniority_scaled=scaled)
            chain = chain.scaled_for_apprenticeship(pct, seniority_scaled=scaled)
    else:
        chosen = isinstance(contract_type, Permanent) and contract_type.entry_pay
        chain = _level_chain(
            ccnl,
            entry_level(ccnl, level, chosen, hired_on, as_of),
            count,
            roles,
            as_of,
            is_apprentice=False,
            worker_category=worker_category,
            seniority_months=seniority_months,
            increment_months=increment_months,
            career_months=career_months,
        )
    return chain, scaling
