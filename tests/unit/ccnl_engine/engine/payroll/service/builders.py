"""Shared test helpers for engine/compute tests."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from ccnl_engine.engine.contract.domain.ccnl import CCNL, LevelCategory
from ccnl_engine.engine.payroll.domain.employee import (
    ContractPosition,
    DestinationRalOverride,
    Employee,
    RalOverride,
    SalaryOverrides,
    SeniorityByCount,
    SeniorityByMonths,
    WorkArrangement,
)
from ccnl_engine.engine.payroll.domain.employment import (
    Employment,
    FixedTerm,
    Permanent,
)
from tests.helpers import TEST_PROV, make_ccnl_dict, make_year_rules

_DATE = date(2026, 6, 1)
_D = Decimal
_RULES = make_year_rules()
_PERMANENT = Permanent()
_FIXED_TERM = FixedTerm()


def _series(value: str) -> dict[str, Any]:
    return {
        "periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": value}]
    }


def _allowance(code: str, monthly: str, **extra: object) -> dict[str, Any]:
    return {
        "code": code,
        "description": code,
        "monthly": _series(monthly),
        "provenance": TEST_PROV,
        **extra,
    }


def _build_ccnl(app_type: str = "percentage", /, **mutations: object) -> CCNL:
    """Build a CCNL from the shared dict, applying dotted-path mutations.

    Returns:
        A validated CCNL instance with the requested mutations applied.
    """
    data = make_ccnl_dict(app_type=app_type)
    for path, value in mutations.items():
        node: Any = data
        keys = path.split(".")
        for key in keys[:-1]:
            node = node[int(key)] if key.isdigit() else node[key]
        last = keys[-1]
        if last.isdigit():
            node[int(last)] = value
        else:
            node[last] = value
    return CCNL.model_validate(data)


def _req(
    level_code: str = "4",
    as_of: date = _DATE,
    employment: Employment = _PERMANENT,
    part_time_pct: Decimal = Decimal(1),
    seniority_count: int | None = None,
    seniority_months: int | None = None,
    negotiated_ral: Decimal | None = None,
    negotiated_destination_ral: Decimal | None = None,
    roles: frozenset[str] = frozenset(),
    ad_personam_monthly: Decimal = Decimal(0),
    category: LevelCategory | None = None,
) -> Employee:
    """Build an Employee with test defaults; override any field via kwargs.

    Returns:
        An Employee with the given overrides applied.
    """
    seniority: SeniorityByCount | SeniorityByMonths | None = None
    if seniority_count is not None:
        seniority = SeniorityByCount(seniority_count)
    elif seniority_months is not None:
        seniority = SeniorityByMonths(seniority_months)

    ral_override: RalOverride | DestinationRalOverride | None = None
    if negotiated_ral is not None:
        ral_override = RalOverride(negotiated_ral)
    elif negotiated_destination_ral is not None:
        ral_override = DestinationRalOverride(negotiated_destination_ral)

    agreement: SalaryOverrides | None = None
    if ral_override is not None or ad_personam_monthly != Decimal(0):
        agreement = SalaryOverrides(
            ral_override=ral_override,
            ad_personam_monthly=ad_personam_monthly,
        )

    return Employee(
        position=ContractPosition(
            level_code=level_code,
            as_of=as_of,
            employment=employment,
            category=category,
            roles=roles,
        ),
        arrangement=WorkArrangement(
            part_time_pct=part_time_pct,
            seniority=seniority,
        ),
        agreement=agreement,
    )
