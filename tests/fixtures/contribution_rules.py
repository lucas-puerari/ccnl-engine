"""Minimal INPS year rules and the contributions of a first run on them.

Unit tests of the contribution service build their rules here: standard
and apprentice rates of an industrial employer with a configurable IVS
ceiling.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.contributions import resolve_contributions
from tests.helpers import make_year_rules

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
    from ccnl_engine.payroll.domain.employment import (
        Apprentice,
        FixedTerm,
        Permanent,
    )
    from ccnl_engine.tax.domain.ruleset import YearRules

__all__ = ["first_run_contributions", "inps_year_rules"]


def inps_year_rules(ceiling: str | None = None) -> YearRules:
    """Build minimal YearRules with configurable INPS ceiling.

    Returns:
        A YearRules instance with the specified ceiling value.
    """
    return make_year_rules(
        inps={
            "employee_rate": "0.0919",
            "employee_ivs_rate": "0.0919",
            "employer_rate": "0.2898",
            "employer_ivs_rate": "0.2381",
            "ceiling": ceiling,
            "employer_rate_by_category": {"impiegato": "0.2471"},
        },
        apprentice={
            "employee_rate": "0.0584",
            "employee_ivs_rate": "0.0584",
            "employer_rate_months_0_11": "0.0311",
            "employer_ivs_rate_months_0_11": "0.0150",
            "employer_rate_months_12_23": "0.0461",
            "employer_ivs_rate_months_12_23": "0.0300",
            "employer_rate_after": "0.1161",
            "employer_ivs_rate_after": "0.1000",
        },
    )


def first_run_contributions(
    base: Decimal,
    rules: YearRules,
    contract: Permanent | FixedTerm | Apprentice,
    category: WorkerCategory | None,
    *,
    ytd_inps_base: Decimal = Decimal(0),
    ivs_ceiling_applies: bool = True,
) -> ContributionBreakdown:
    """Resolve contributions, first run of the year and massimale applied.

    Returns:
        The breakdown of ``resolve_contributions``.
    """
    return resolve_contributions(
        base,
        rules,
        contract,
        category,
        ytd_inps_base=ytd_inps_base,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
