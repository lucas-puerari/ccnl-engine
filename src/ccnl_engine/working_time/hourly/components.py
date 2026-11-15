"""Monthly pay components of a derived hourly base."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.provenance.source.rule.models import ProvenanceStatus
from ccnl_engine.working_time.supplement.models import HourlyBaseMethod

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.compensation.models import Level
    from ccnl_engine.provenance.source.rule.models import RuleProvenance
    from ccnl_engine.working_time.models import TimeSupplements


def base_record(
    supplements: TimeSupplements | None, level: Level | None
) -> RuleProvenance | None:
    """Return the record of the hourly base of ``level``.

    Returns:
        The level's own record, else the CCNL's, ``None`` without either.
    """
    if level is not None and level.hourly_base_provenance is not None:
        return level.hourly_base_provenance
    return None if supplements is None else supplements.hourly_base_provenance


def derives_hourly_base(ccnl: CCNL) -> bool:
    """Return whether the engine derives the hourly base of every level of ``ccnl``.

    A percentage supplement computes nothing without it: the event then
    needs the amount from the caller.

    Returns:
        Whether each level has a verified record of its hourly base and the
        CCNL or the level an hourly divisor.
    """
    work = ccnl.work_rules
    supplements = None if work is None else work.time_supplements
    divisor = bool(ccnl.parameters.hourly_divisor.periods)
    for level in ccnl.levels:
        record = base_record(supplements, level)
        if record is None or record.status is not ProvenanceStatus.VERIFIED:
            return False
        if not divisor and level.hourly_divisor is None:
            return False
    return True


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
            if (not a.in_kind or a.in_global_pay)
            and not a.individual
            and a.code not in excluded
        )
    return tuple(found)


def individual(chain: MonthlyPayChain) -> tuple[tuple[str, Decimal], ...]:
    """Return the individual elements of the worker in ``chain``.

    Returns:
        Each element and its full-time monthly amount.
    """
    return tuple((a.code, v) for a, v in chain.allowances if a.individual)


def cash_pay(chain: MonthlyPayChain) -> Decimal:
    """Return the monthly retribuzione di fatto of ``chain``.

    Returns:
        The minimo, the seniority and the cash allowances of the CCNL.
    """
    parts = components(chain, HourlyBaseMethod.GROSS_INCL_ALLOWANCES, ())
    return sum((v for _, v in parts), Decimal(0))


def rateo(
    parts: tuple[tuple[str, Decimal], ...], payments: int | None
) -> tuple[tuple[str, Decimal], ...]:
    """Return the rateo of the further monthly payments the base includes.

    Returns:
        ``("rateo", monthly * (payments - 12) / 12)``; nothing without
        ``payments``.
    """
    if payments is None:
        return ()
    monthly = sum((v for _, v in parts), Decimal(0))
    return (("rateo", monthly * (payments - 12) / 12),)
