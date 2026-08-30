"""CCNL data file loaders.

Provides :func:`load_ccnl` and :func:`load_year_rules` for loading validated
data from the package's bundled JSON files.

File layout
-----------
- ``ccnl_engine/data/*.json`` — CCNL contract data files (one per CCNL).
- ``ccnl_engine/tax/data/<year>-<sector>.json`` — statutory tax and
  contribution parameters, one file per (year, INPS sector) pair.

Both directories are included in the wheel via ``setuptools.package-data`` in
``pyproject.toml``.
"""

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
    """Load and validate a CCNL data file from the package bundle.

    Args:
        filename: JSON filename without directory, e.g.
            ``"commercio-confcommercio.json"``.

    Returns:
        A fully-validated :class:`~ccnl_engine.models.ccnl.CCNL` instance.

    Raises:
        FileNotFoundError: If *filename* does not exist in the bundle.
        pydantic.ValidationError: If the JSON does not conform to the schema.
    """
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
    """Load and validate tax year rules, resolving employer INPS rate by size.

    Reads ``tax/data/<year>-<sector>.json`` from the package bundle, then
    resolves the employer-rate tier table against *num_employees* to produce a
    flat :class:`~ccnl_engine.tax.models.YearRules` ready for use by
    :func:`~ccnl_engine.engine.compute.compute`.

    Args:
        year: Four-digit fiscal year, e.g. ``2026``.
        sector: INPS sector for this CCNL (see
            :class:`~ccnl_engine.models.ccnl.TaxSector`).
        num_employees: Number of employees in the company; used to select the
            correct employer-rate tier (e.g. ``≤15``, ``≤50``, unlimited).

    Returns:
        A fully-validated :class:`~ccnl_engine.tax.models.YearRules` instance
        with a flat, resolved ``inps.employer_rate``.

    Raises:
        FileNotFoundError: If no data file exists for the given year/sector.
        pydantic.ValidationError: If the JSON does not conform to the schema.
        ValueError: If *num_employees* does not match any tier in the file.
    """
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
    """Return the employer rate for *num_employees* from an ordered tier list.

    Tiers are evaluated in ascending order of ``max_employees``; the first
    tier whose ``max_employees`` is ``None`` (open) or ``>= num_employees``
    is selected.

    Args:
        tiers: Tier list from the raw JSON file.
        num_employees: Actual employee headcount.

    Returns:
        The resolved employer contribution rate as a :class:`~decimal.Decimal`.

    Raises:
        ValueError: If no tier covers *num_employees* (malformed file).
    """
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
