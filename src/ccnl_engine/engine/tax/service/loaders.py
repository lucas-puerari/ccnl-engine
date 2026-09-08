"""Tax year rules loader (reads the Knowledge Base bundle)."""

from __future__ import annotations

import importlib.resources
import json
from typing import TYPE_CHECKING, Any, Protocol

from ccnl_engine.engine.io.bundled import read_bundled
from ccnl_engine.engine.metadata import RulesetIdentity, source_hash
from ccnl_engine.engine.tax.domain.rules import (
    ApprenticeRates,
    ApprenticeRawRates,
    InpsRates,
    InpsRawRates,
    YearRules,
    YearRulesRaw,
)
from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates, SickPayBand

if TYPE_CHECKING:
    from collections.abc import Sequence
    from decimal import Decimal
    from importlib.abc import Traversable

    from ccnl_engine.engine.contract.domain.ccnl import TaxSector


class _Tier(Protocol):
    max_employees: int | None
    rate: Decimal
    ivs_rate: Decimal


def load_year_rules(
    year: int,
    sector: TaxSector,
    num_employees: int,
) -> YearRules:
    """Load and validate tax year rules, resolving INPS rates by headcount.

    INPS contribution rates are tiered by company size. This function selects
    the correct tier for ``num_employees`` and returns a flat ``YearRules``
    with the resolved rates — callers do not need to handle tier logic.

    The IRPEF/TFR block comes from ``ccnl_engine/knowledge/tax/data/``; the
    INPS contribution block (aliquote, apprentice, domestic) comes from
    ``ccnl_engine/knowledge/inps/data/``. Both are merged and validated
    against :class:`~ccnl_engine.engine.tax.domain.rules.YearRulesRaw` before
    resolving tiers.

    Args:
        year: Tax year (e.g. ``2026``). Matching data files must exist in the
            package bundle.
        sector: INPS sector classification, taken from ``CCNL.meta.tax_sector``.
        num_employees: Headcount used to select the INPS contribution-rate tier.
            Use the employer's total headcount, not just the contract's.

    Returns:
        A ``YearRules`` instance with INPS rates already resolved for the given
        headcount. The ``inps`` field is ``None`` for domestic-work sectors,
        which use ``domestic_contributions`` instead.
    """
    tax_raw = read_tax_rules_raw(year, sector)
    inps_raw = read_inps_rules_raw(year, sector)
    inps_sources = inps_raw.pop("sources", [])
    inps_extraction = inps_raw.pop("extraction", None)
    raw = {**tax_raw, **inps_raw}
    raw["inps_sources"] = inps_sources
    raw["inps_extraction"] = inps_extraction
    rules = YearRulesRaw.model_validate(raw)
    inps = _resolve_inps(rules.inps, num_employees)
    apprentice = (
        _resolve_apprentice(rules.apprentice, num_employees)
        if rules.apprentice is not None
        else None
    )
    return YearRules(
        year=rules.year,
        ruleset=_as_ruleset(tax_raw),
        inps_ruleset=_as_ruleset(inps_raw),
        irpef_brackets=rules.irpef_brackets,
        work_deduction_breakpoints=rules.work_deduction_breakpoints,
        fixed_term_additional_rate=rules.fixed_term_additional_rate,
        inps=inps,
        apprentice=apprentice,
        domestic_contributions=rules.domestic_contributions,
        tfr=rules.tfr,
        trattamento_integrativo=rules.trattamento_integrativo,
        notes=rules.notes,
        sources=rules.sources,
        extraction=rules.extraction,
        inps_sources=rules.inps_sources,
        inps_extraction=rules.inps_extraction,
    )


def _read_json(pkg: Traversable, filename: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(read_bundled(pkg, filename))
    _verify_ruleset_hash(data, filename)
    return data


def _as_ruleset(raw: dict[str, Any]) -> RulesetIdentity | None:
    """Parse a raw dict's ``ruleset`` block into a :class:`RulesetIdentity`.

    Returns:
        The parsed identity, or ``None`` when the dict carries no ``ruleset``.
    """
    block = raw.get("ruleset")
    if not isinstance(block, dict):
        return None
    return RulesetIdentity.model_validate(block)


def _verify_ruleset_hash(payload: dict[str, Any], filename: str) -> None:
    """Verify a recorded ``ruleset.source_hash`` against the payload.

    The check is skipped when the file carries no ``ruleset`` block or no
    ``source_hash``; a stale hash means the data file was hand-modified after
    the provenance backfill.

    Raises:
        ValueError: If the recomputed hash differs from the recorded one.
    """
    ruleset = payload.get("ruleset")
    if not isinstance(ruleset, dict):
        return
    recorded = ruleset.get("source_hash")
    if not isinstance(recorded, str):
        return
    if source_hash(payload) != recorded:
        msg = (
            f"ruleset source_hash mismatch in {filename}; data file has been "
            "modified without updating its ruleset block."
        )
        raise ValueError(msg)


def read_tax_rules_raw(year: int, sector: TaxSector) -> dict[str, Any]:
    """Read the IRPEF/TFR block of a tax year file as a raw dict.

    Args:
        year: Tax year.
        sector: INPS sector classification.

    Returns:
        The ``knowledge/tax/data/<year>-<sector>.json`` payload.
    """
    filename = f"{year}-{sector.value}.json"
    pkg = importlib.resources.files("ccnl_engine.knowledge.tax.data")
    return _read_json(pkg, filename)


def read_inps_rules_raw(year: int, sector: TaxSector) -> dict[str, Any]:
    """Read the INPS contribution block of a year/sector file as a raw dict.

    Args:
        year: Tax year.
        sector: INPS sector classification.

    Returns:
        The ``knowledge/inps/data/<year>-<sector>.json`` payload.
    """
    filename = f"{year}-{sector.value}.json"
    pkg = importlib.resources.files("ccnl_engine.knowledge.inps.data")
    return _read_json(pkg, filename)


def _resolve_tier[T: _Tier](tiers: list[T], num_employees: int, side: str) -> T:
    _assert_tier_integrity(tiers, side)
    sorted_tiers = sorted(
        tiers,
        key=lambda t: (t.max_employees is None, t.max_employees or 0),
    )
    for tier in sorted_tiers:
        if tier.max_employees is None or num_employees <= tier.max_employees:
            return tier
    msg = (
        f"No {side}-rate tier covers {num_employees} employees. "
        "Check that the tax data file has an open tier (max_employees: null)."
    )
    raise ValueError(msg)


def _assert_tier_integrity(tiers: Sequence[_Tier], side: str) -> None:
    """Raise ValueError if the tier list has structural defects.

    Checks (run on the unsorted input):
    - At most one open tier (max_employees: null); multiple open tiers
      would cause non-deterministic tier selection.
    - No duplicate max_employees values among bounded tiers (would cause
      silent mis-classification depending on sort stability).

    Raises:
        ValueError: if more than one open tier exists, or if any bounded
            max_employees value appears more than once.
    """
    open_count = sum(1 for t in tiers if t.max_employees is None)
    if open_count > 1:
        msg = (
            f"{side}-rate tiers: {open_count} open tiers "
            "(max_employees: null) found; at most one is allowed."
        )
        raise ValueError(msg)
    seen: set[int] = set()
    for tier in tiers:
        if tier.max_employees is None:
            continue
        if tier.max_employees in seen:
            msg = f"{side}-rate tiers: duplicate max_employees={tier.max_employees}."
            raise ValueError(msg)
        seen.add(tier.max_employees)


def _resolve_inps(raw: InpsRawRates | None, num_employees: int) -> InpsRates | None:
    """Resolve INPS tiers by headcount; return None for domestic-model sectors.

    Returns:
        Resolved InpsRates for standard sectors; None when raw is None
        (i.e. the sector uses domestic_contributions instead).
    """
    if raw is None:
        return None
    employer_tier = _resolve_tier(raw.employer_tiers, num_employees, "employer")
    employee_tier = _resolve_tier(raw.employee_tiers, num_employees, "employee")
    return InpsRates(
        employee_rate=employee_tier.rate,
        employee_ivs_rate=employee_tier.ivs_rate,
        employer_rate=employer_tier.rate,
        employer_ivs_rate=employer_tier.ivs_rate,
        ceiling=raw.ceiling,
        employer_rate_by_category=employer_tier.rate_by_category,
    )


def _resolve_apprentice(raw: ApprenticeRawRates, num_employees: int) -> ApprenticeRates:
    small_firm = num_employees <= raw.small_firm_max_employees
    return ApprenticeRates(
        employee_rate=raw.employee_rate,
        employee_ivs_rate=raw.employee_ivs_rate,
        employer_rate_months_0_11=(
            raw.small_firm_employer_rate_months_0_11
            if small_firm
            else raw.employer_rate
        ),
        employer_ivs_rate_months_0_11=(
            raw.small_firm_employer_ivs_rate_months_0_11
            if small_firm
            else raw.employer_ivs_rate
        ),
        employer_rate_months_12_23=(
            raw.small_firm_employer_rate_months_12_23
            if small_firm
            else raw.employer_rate
        ),
        employer_ivs_rate_months_12_23=(
            raw.small_firm_employer_ivs_rate_months_12_23
            if small_firm
            else raw.employer_ivs_rate
        ),
        employer_rate_after=raw.employer_rate,
        employer_ivs_rate_after=raw.employer_ivs_rate,
    )


def load_sick_pay_rates() -> InpsSickPayRates:
    """Load INPS statutory sick-pay indemnity rates from the bundled data file.

    The file ``knowledge/inps/data/sick-pay-rates.json`` is not year- or
    sector-specific: statutory sick-pay rates are cross-sector and change
    only by primary legislation (D.Lgs. 151/2001, artt. 68-71).

    Returns:
        An :class:`~ccnl_engine.engine.tax.domain.sick_pay.InpsSickPayRates`
        with the INPS carenza period, indemnity bands, and provenance.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.inps.data")
    raw = _read_json(pkg, "sick-pay-rates.json")
    bands = [SickPayBand(**b) for b in raw.get("bands", [])]
    return InpsSickPayRates(
        description=raw.get("description", ""),
        carenza_days=int(raw.get("carenza_days", 3)),
        bands=bands,
        ruleset=_as_ruleset(raw),
    )
