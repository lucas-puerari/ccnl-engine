"""Wheel smoke test: import the engine and run one end-to-end scenario.

This script is intentionally dependency-minimal so it can run in a clean
virtual environment that has only the installed wheel (no dev extras).
It exercises the public API surface and exits non-zero on any failure.
"""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    Agreement,
    AnnualPayrollScenario,
    Employee,
    Employer,
    Employment,
    Permanent,
    RalOverride,
    SeniorityByDate,
    estimate_annual,
    get_ccnl,
    list_ccnls,
)


def main() -> int:
    """Run the smoke test; return 0 on success, 1 on failure.

    Returns:
        0 when the end-to-end scenario produces a positive net_annual;
        1 on any exception or unexpected result.
    """
    scenario = AnnualPayrollScenario(
        employee=Employee(
            level_code="II",
            seniority=SeniorityByDate(value=date(2020, 1, 1)),
            weekly_hours=Decimal(40),
            agreement=Agreement(ral_override=RalOverride(value=Decimal(30000))),
        ),
        employment=Employment(
            ccnl="agenti-immobiliari-fiaip.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
    try:
        result = estimate_annual(scenario)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: estimate_annual() raised {type(exc).__name__}: {exc}")
        return 1

    net = result.result.net_annual
    if net <= Decimal(0):
        print(f"FAIL: net_annual is {net!r}, expected > 0")
        return 1

    print(f"OK: net_annual={net}")

    ccnls = list_ccnls()
    if len(ccnls) != 125:
        print(f"FAIL: list_ccnls() returned {len(ccnls)} items, expected 125")
        return 1

    slug = ccnls[0].ccnl_id
    by_slug = get_ccnl(slug)
    by_code = get_ccnl(by_slug.cnel_code)
    if by_slug != by_code:
        print("FAIL: get_ccnl by slug and by CNEL code returned different results")
        return 1

    print(f"OK: list_ccnls()={len(ccnls)}, get_ccnl resolved '{slug}' and CNEL code")
    return 0


if __name__ == "__main__":
    sys.exit(main())
