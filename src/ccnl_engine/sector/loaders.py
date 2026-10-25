"""Annual tax rules assembler: merges tax and INPS raw data into YearRules."""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from ccnl_engine.contribution.headcount.rules import (
    _resolve_apprentice,
    _resolve_inps,
)
from ccnl_engine.contribution.rate.models import ApprenticeRates, InpsRates
from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.irpef.work_deduction.loaders import load_work_deduction_rules
from ccnl_engine.sector.models import YearRules, YearRulesRaw
from ccnl_engine.sector.raw.loaders import (
    _as_ruleset,
    read_inps_rules_raw,
    read_tax_rules_raw,
)
from ccnl_engine.severance.loaders import (
    load_tfr_revaluation_rules,
    load_tfr_settlement_rules,
)
from ccnl_engine.tax_credit.somma_esente.loaders import load_somma_esente_rules

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.agreement.facade import TaxSector
    from ccnl_engine.provenance.ruleset.models import RulesetIdentity


def load_year_rules(
    year: int,
    sector: TaxSector,
    num_employees: int,
) -> YearRules:
    """Load and validate tax year rules, resolving INPS rates by headcount.

    INPS contribution rates are tiered by company size. This function selects
    the correct tier for ``num_employees`` and returns a flat ``YearRules``
    with the resolved rates -- callers do not need to handle tier logic.

    The IRPEF/TFR block comes from
    ``knowledge/sector/<year>/<sector>.json``, with the TFR
    revaluation and the somma esente of the year from their national files;
    the INPS contribution block (aliquote, apprentice, domestic) comes from
    ``knowledge/contribution/<year>/<sector>.json``.  Both are
    merged and validated
    against :class:`~ccnl_engine.sector.models.YearRulesRaw` before
    resolving tiers.

    The rules are frozen and cached: every call for the same arguments
    returns the same object, and a caller that needs other values builds
    them with ``model_copy(update=...)``.

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
    raw, _, _ = _raw_rules(year, sector)
    inps = _resolve_inps(raw.inps, num_employees, raw.apprentice)
    apprentice = (
        None
        if raw.apprentice is None
        else _resolve_apprentice(raw.apprentice, num_employees)
    )
    return _assembled(
        year,
        sector,
        None if inps is None else inps.model_dump_json(),
        None if apprentice is None else apprentice.model_dump_json(),
    )


def _clear_year_rules() -> None:
    """Forget the parsed and the assembled year rules (tests patch the files)."""
    _raw_rules.cache_clear()
    _assembled.cache_clear()


@cache
def _raw_rules(
    year: int, sector: TaxSector
) -> tuple[YearRulesRaw, RulesetIdentity | None, RulesetIdentity | None]:
    """Parse and validate the tax and INPS files of a year and sector, once.

    A tax or INPS file whose year or sector does not match the request
    raises ``DataIntegrityError``.

    Returns:
        The merged raw rules with the ruleset of the tax and of the INPS file.
    """
    tax_raw = read_tax_rules_raw(year, sector)
    _check_identity("tax", tax_raw, year, sector)
    inps_raw = read_inps_rules_raw(year, sector)
    _check_identity("inps", inps_raw, year, sector)
    inps_sources = inps_raw.pop("sources", [])
    inps_extraction = inps_raw.pop("extraction", None)
    raw = {**tax_raw, **inps_raw}
    raw["inps_sources"] = inps_sources
    raw["inps_extraction"] = inps_extraction
    return (
        YearRulesRaw.model_validate(raw),
        _as_ruleset(tax_raw),
        _as_ruleset(inps_raw),
    )


@cache
def _assembled(
    year: int, sector: TaxSector, inps_json: str | None, apprentice_json: str | None
) -> YearRules:
    """Build the year rules once per set of resolved INPS rates.

    The key is the rates the headcount resolves to, not the headcount: the
    cache holds one entry per tier the files define, however many
    headcounts the employers have.

    Returns:
        The frozen year rules, shared by every headcount of the same tier.
    """
    rules, tax_ruleset, inps_ruleset = _raw_rules(year, sector)
    return YearRules(
        year=rules.year,
        ruleset=tax_ruleset,
        inps_ruleset=inps_ruleset,
        irpef_brackets=tuple(rules.irpef_brackets),
        irpef_brackets_provenance=rules.irpef_brackets_provenance,
        fixed_term_additional_rate=rules.fixed_term_additional_rate,
        fixed_term_renewal_increment=rules.fixed_term_renewal_increment,
        fixed_term_exempt_categories=rules.fixed_term_exempt_categories,
        fixed_term_additional_rate_provenance=(
            rules.fixed_term_additional_rate_provenance
        ),
        inps=None if inps_json is None else InpsRates.model_validate_json(inps_json),
        apprentice=None
        if apprentice_json is None
        else ApprenticeRates.model_validate_json(apprentice_json),
        domestic_contributions=rules.domestic_contributions,
        tfr=rules.tfr,
        tfr_revaluation=load_tfr_revaluation_rules(year),
        tfr_settlement=load_tfr_settlement_rules(year),
        trattamento_integrativo=rules.trattamento_integrativo,
        ulteriore_detrazione=rules.ulteriore_detrazione,
        somma_esente=load_somma_esente_rules(year),
        sterilizzazione_detrazioni=rules.sterilizzazione_detrazioni,
        work_deduction=load_work_deduction_rules(year),
        complementary_pension=rules.complementary_pension,
        notes=tuple(rules.notes),
        sources=tuple(rules.sources),
        extraction=rules.extraction,
        inps_sources=tuple(rules.inps_sources),
        inps_extraction=rules.inps_extraction,
    )


def _check_identity(
    kind: str, raw: Mapping[str, object], year: int, sector: TaxSector
) -> None:
    """Reject a data file whose year or sector is not the one requested.

    Raises:
        DataIntegrityError: If the file's year or sector does not match.
    """
    name = f"{kind}-{year}-{sector.value}.json"
    if raw.get("year") != year:
        msg = f"{name} year={raw.get('year')!r} does not match requested year={year!r}"
        raise DataIntegrityError(msg)
    if raw.get("sector") != sector.value:
        msg = (
            f"{name} sector={raw.get('sector')!r} "
            f"does not match requested sector={sector.value!r}"
        )
        raise DataIntegrityError(msg)
