"""CCNL data file loaders."""

from __future__ import annotations

import importlib.resources
from typing import TYPE_CHECKING

from ccnl_engine.models.ccnl import CCNL, TaxSector
from ccnl_engine.tax.models import (
    InpsRates,
    YearRules,
    _InpsEmployerTier,
    _YearRulesRaw,
)

if TYPE_CHECKING:
    from decimal import Decimal


def load_ccnl(filename: str) -> CCNL:
    """Load and validate a CCNL data file from the package bundle."""
    raw = (
        importlib.resources.files("ccnl_engine.data")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )
    return CCNL.model_validate_json(raw)


def load_year_rules(
    year: int,
    sector: TaxSector,
    num_employees: int,
) -> YearRules:
    """Load and validate tax year rules, resolving employer INPS rate by headcount."""
    filename = f"{year}-{sector.value}.json"
    raw_text = (
        importlib.resources.files("ccnl_engine.tax.data")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )
    raw = _YearRulesRaw.model_validate_json(raw_text)
    employer_rate = _resolve_employer_tier(raw.inps.employer_tiers, num_employees)
    return YearRules(
        year=raw.year,
        irpef_brackets=raw.irpef_brackets,
        work_deduction_breakpoints=raw.work_deduction_breakpoints,
        fixed_term_additional_rate=raw.fixed_term_additional_rate,
        inps=InpsRates(
            employee_rate=raw.inps.employee_rate,
            employer_rate=employer_rate,
            ceiling=raw.inps.ceiling,
        ),
        tfr=raw.tfr,
        notes=raw.notes,
    )


def _resolve_employer_tier(
    tiers: list[_InpsEmployerTier],
    num_employees: int,
) -> Decimal:
    sorted_tiers = sorted(
        tiers,
        key=lambda t: (t.max_employees is None, t.max_employees or 0),
    )
    for tier in sorted_tiers:
        if tier.max_employees is None or num_employees <= tier.max_employees:
            return tier.rate
    msg = (
        f"No employer-rate tier covers {num_employees} employees. "
        "Check that the tax data file has an open tier (max_employees: null)."
    )
    raise ValueError(msg)
