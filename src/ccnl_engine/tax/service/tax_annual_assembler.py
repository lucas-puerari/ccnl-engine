"""Annual tax rules assembler: merges tax and INPS raw data into YearRules."""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from ccnl_engine.shared.domain.errors import DataIntegrityError
from ccnl_engine.tax.domain.ruleset import YearRules, YearRulesRaw
from ccnl_engine.tax.service.tax_resource_reader import (
    _as_ruleset,
    read_inps_rules_raw,
    read_tax_rules_raw,
)
from ccnl_engine.tax.service.tax_tier_resolver import (
    _resolve_apprentice,
    _resolve_inps,
)

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import TaxSector


def load_year_rules(
    year: int,
    sector: TaxSector,
    num_employees: int,
) -> YearRules:
    """Load and validate tax year rules, resolving INPS rates by headcount.

    INPS contribution rates are tiered by company size. This function selects
    the correct tier for ``num_employees`` and returns a flat ``YearRules``
    with the resolved rates -- callers do not need to handle tier logic.

    The IRPEF/TFR block comes from ``ccnl_engine/knowledge/tax/data/``; the
    INPS contribution block (aliquote, apprentice, domestic) comes from
    ``ccnl_engine/knowledge/inps/data/``. Both are merged and validated
    against :class:`~ccnl_engine.tax.domain.ruleset.YearRulesRaw` before
    resolving tiers.

    Each call returns an independent deep copy of the cached rules object, so
    callers may freely mutate nested fields (e.g. ``irpef_brackets``) without
    contaminating subsequent loads.

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
    return _load_year_rules_cached(year, sector, num_employees).model_copy(deep=True)


@cache
def _load_year_rules_cached(
    year: int,
    sector: TaxSector,
    num_employees: int,
) -> YearRules:
    """Parse, validate and cache tax rules for the given arguments (internal use only).

    Callers must use :func:`load_year_rules`, which returns a deep copy so
    each caller gets an independent object that may be mutated freely.

    Returns:
        The shared :class:`~ccnl_engine.tax.domain.ruleset.YearRules`
        object stored in the cache.

    Raises:
        DataIntegrityError: If the tax or INPS file's year/sector doesn't match.
    """
    tax_raw = read_tax_rules_raw(year, sector)
    if tax_raw.get("year") != year:
        msg = (
            f"tax-{year}-{sector.value}.json year={tax_raw.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)
    if tax_raw.get("sector") != sector.value:
        msg = (
            f"tax-{year}-{sector.value}.json sector={tax_raw.get('sector')!r} "
            f"does not match requested sector={sector.value!r}"
        )
        raise DataIntegrityError(msg)
    inps_raw = read_inps_rules_raw(year, sector)
    if inps_raw.get("year") != year:
        msg = (
            f"inps-{year}-{sector.value}.json year={inps_raw.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)
    if inps_raw.get("sector") != sector.value:
        msg = (
            f"inps-{year}-{sector.value}.json sector={inps_raw.get('sector')!r} "
            f"does not match requested sector={sector.value!r}"
        )
        raise DataIntegrityError(msg)
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
        fixed_term_additional_rate=rules.fixed_term_additional_rate,
        inps=inps,
        apprentice=apprentice,
        domestic_contributions=rules.domestic_contributions,
        tfr=rules.tfr,
        trattamento_integrativo=rules.trattamento_integrativo,
        ulteriore_detrazione=rules.ulteriore_detrazione,
        somma_esente=rules.somma_esente,
        sterilizzazione_detrazioni=rules.sterilizzazione_detrazioni,
        work_deduction=rules.work_deduction,
        notes=rules.notes,
        sources=rules.sources,
        extraction=rules.extraction,
        inps_sources=rules.inps_sources,
        inps_extraction=rules.inps_extraction,
    )
