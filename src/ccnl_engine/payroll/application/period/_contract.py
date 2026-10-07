"""CCNL, level, dates and yearly rules of one run.

The tax rules are those of the tax year of the payment; the INPS rules are
those of the competence year of the run (:func:`with_competence_contributions`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.validity import rule_scope
from ccnl_engine.payroll.domain.employment_context import (
    EffectiveDateContext,
    TemporalContext,
)
from ccnl_engine.shared.domain.errors import UnknownLevelError

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.compensation import Level
    from ccnl_engine.contract.domain.identity import CCNL, TaxSector
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.domain.capability_catalog import CapabilityCatalog
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
    from ccnl_engine.tax.domain.ruleset import YearRules

__all__ = ["RunContract", "load_contract", "with_competence_contributions"]

#: Fields of :class:`YearRules` that follow competence: the INPS
#: contributions and the TFR revaluation at 31 December of the year.
_CONTRIBUTION_FIELDS = (
    "inps_ruleset",
    "inps",
    "apprentice",
    "domestic_contributions",
    "fixed_term_additional_rate",
    "fixed_term_renewal_increment",
    "fixed_term_exempt_categories",
    "fixed_term_additional_rate_provenance",
    "inps_sources",
    "inps_extraction",
    "tfr_revaluation",
)


@dataclass(frozen=True)
class RunContract:
    """CCNL, level, dates and yearly rules of a run."""

    ccnl: CCNL
    level: Level
    tctx: TemporalContext
    date_ctx: EffectiveDateContext
    year_rules: YearRules
    catalog: CapabilityCatalog


def load_contract(
    request: PeriodCalculationRequest, repo: KnowledgeRepository
) -> RunContract:
    """Load the CCNL, level and yearly rules of the run.

    Returns:
        The contract of the run.

    Raises:
        UnknownLevelError: When the CCNL has no level ``request.level_code``.
    """
    period_id = request.period_id
    ccnl = repo.load_ccnl(request.ccnl_slug)
    tctx = TemporalContext.from_period(
        period_id.year, period_id.month, request.payment_date
    )
    try:
        level = ccnl.level_by_code(request.level_code)
    except ValueError:
        raise UnknownLevelError(request.level_code, ccnl.meta.ccnl_id) from None
    # The base salary of the level is the first rule every run reads.
    with rule_scope(ruleset=ccnl.meta.ccnl_id, feature="base_salary"):
        level.base_salary.value_at(tctx.competence)
    date_ctx = EffectiveDateContext.from_period(
        period_id.year, period_id.month, tctx.payment
    )
    sector, headcount = ccnl.meta.tax_sector, request.employer.headcount.value
    year_rules = with_competence_contributions(
        repo,
        repo.load_year_rules(tctx.fiscal_year, sector, headcount),
        period_id.year,
        sector,
        headcount,
    )
    catalog = repo.load_capability_catalog(tctx.fiscal_year)
    return RunContract(ccnl, level, tctx, date_ctx, year_rules, catalog)


def with_competence_contributions(
    repo: KnowledgeRepository,
    rules: YearRules,
    competence_year: int,
    sector: TaxSector,
    headcount: int,
) -> YearRules:
    """Return ``rules`` with the INPS and TFR revaluation rules of competence.

    INPS contributions follow competence: a December paid on 13 January is
    contributed in the December denuncia, at the rates and under the
    massimale of its own year (INPS circ. 237/2016 par. 2.1 and 3.1).  The
    TFR revaluation is that of 31 December of the competence year (art.
    2120 c. 4 c.c.).  The IRPEF rules stay those of the tax year of the
    payment.

    Returns:
        ``rules`` when they are of ``competence_year``; otherwise a copy
        whose contribution fields come from the rules of that year.  A
        competence year without bundled rules raises
        :class:`~ccnl_engine.shared.domain.errors.UnsupportedTaxYearError`.
    """
    if rules.year == competence_year:
        return rules
    source = repo.load_year_rules(competence_year, sector, headcount)
    return rules.model_copy(
        update={name: getattr(source, name) for name in _CONTRIBUTION_FIELDS}
    )
