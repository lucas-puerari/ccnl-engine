"""Shared test helpers for engine/compute tests."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from ccnl_engine.engine.contract.domain.ccnl import (
    CCNL,
    LevelCategory,
    SupplementaryAllowance,
)
from ccnl_engine.engine.payroll.domain.employee import (
    DestinationRalOverride,
    RalOverride,
    SeniorityByCount,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PayrollScenario,
)
from tests.helpers import TEST_PROV, make_ccnl_dict, make_year_rules

_DATE = date(2026, 6, 1)
_D = Decimal
_RULES = make_year_rules()
_PERMANENT = Permanent()
_FIXED_TERM = FixedTerm()
_CCNL_FILENAME = "test.json"


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
    contract: Permanent | FixedTerm | Apprentice = _PERMANENT,
    num_employees: int = 50,
    part_time_pct: Decimal = Decimal(1),
    seniority_count: int | None = None,
    seniority_months: int | None = None,
    negotiated_ral: Decimal | None = None,
    negotiated_destination_ral: Decimal | None = None,
    roles: frozenset[str] = frozenset(),
    ad_personam_monthly: Decimal = Decimal(0),
    category: LevelCategory | None = None,
    second_level_allowances: tuple[SupplementaryAllowance, ...] = (),
    jurisdiction: Jurisdiction | None = None,
    ivs_ceiling_applies: bool = False,
    weekly_hours: Decimal | None = None,
) -> PayrollScenario:
    """Build a PayrollScenario with test defaults; override any field via kwargs.

    Returns:
        A PayrollScenario with the given overrides applied.
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

    agreement: Agreement | None = None
    if ral_override is not None or ad_personam_monthly != Decimal(0):
        agreement = Agreement(
            ral_override=ral_override,
            ad_personam_monthly=ad_personam_monthly,
        )

    return PayrollScenario(
        employee=Employee(
            level_code=level_code,
            seniority=seniority,
            part_time_pct=part_time_pct,
            weekly_hours=weekly_hours,
            category=category,
            roles=roles,
            ivs_ceiling_applies=ivs_ceiling_applies,
            jurisdiction=jurisdiction,
            agreement=agreement,
        ),
        employment=Employment(
            ccnl=_CCNL_FILENAME,
            contract=contract,
            employer=Employer(
                num_employees=num_employees,
                second_level_allowances=second_level_allowances,
            ),
            date=as_of,
        ),
    )
