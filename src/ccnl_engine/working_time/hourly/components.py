"""Monthly pay components of a derived hourly base."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.working_time.supplement.models import HourlyBaseMethod

if TYPE_CHECKING:
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.compensation.models import Level


def level_method(level: Level | None, default: HourlyBaseMethod) -> HourlyBaseMethod:
    """Select sourced level pay elements, or the contract's existing method.

    Returns:
        The verified level method, or the contract's method.
    """
    if (
        level is not None
        and level.hourly_base_method is not None
        and level.hourly_base_provenance is not None
    ):
        return level.hourly_base_method
    return default


def week_mismatch(
    level: Level | None, expected: Decimal | None, stated: Decimal | None
) -> bool:
    """Whether the contract divisor belongs to a different full-time week.

    Returns:
        Whether the stated week mismatches the contract week and no level
        divisor overrides it.
    """
    return (
        (level is None or level.hourly_divisor is None)
        and expected is not None
        and stated is not None
        and stated != expected
    )


def components(
    chain: MonthlyPayChain, method: HourlyBaseMethod, excluded: tuple[str, ...]
) -> tuple[tuple[str, Decimal], ...]:
    """Return the monthly pay elements ``method`` names, from ``chain``.

    Returns:
        The base salary, then the seniority, then each cash allowance not
        ``excluded``, as far as the method reaches.
    """
    found: list[tuple[str, Decimal]] = [("base_salary", chain.base)]
    if method is HourlyBaseMethod.MINIMO_TABELLARE:
        return tuple(found)
    if method is HourlyBaseMethod.MINIMO_E_CONTINGENZA:
        found.extend(
            (a.code, v)
            for a, v in chain.allowances
            if a.code == "CONTINGENZA" and not a.in_kind and not a.individual
        )
        return tuple(found)
    found.append(("seniority", chain.seniority))
    if method is HourlyBaseMethod.GROSS_INCL_ALLOWANCES:
        found.extend(
            (a.code, v)
            for a, v in chain.allowances
            if not a.in_kind and not a.individual and a.code not in excluded
        )
    return tuple(found)


def individual(chain: MonthlyPayChain) -> tuple[tuple[str, Decimal], ...]:
    """Return the individual elements of the worker in ``chain``.

    Returns:
        Each element and its full-time monthly amount.
    """
    return tuple((a.code, v) for a, v in chain.allowances if a.individual)
