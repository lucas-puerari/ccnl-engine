"""CCNL, level, dates and yearly rules of one run.

The tax rules are those of the tax year of the payment; the INPS rules are
those of the competence year of the run (:func:`with_competence_contributions`).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.compensation.provincial_element.services import (
    without_replaced_elements,
)
from ccnl_engine.contribution.cigs.models import with_cigs_indotto
from ccnl_engine.contribution.fis.models import with_fis_reduction
from ccnl_engine.contribution.zone.models import with_zone_reduction
from ccnl_engine.employment.context.models import (
    EffectiveDateContext,
    TemporalContext,
)
from ccnl_engine.errors import InvalidInputError, UnknownLevelError

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL, TaxSector
    from ccnl_engine.capability.registry.models import CapabilityCatalog
    from ccnl_engine.compensation.models import Level
    from ccnl_engine.employment.fact.inputs import WeeklyHours
    from ccnl_engine.period.ports import KnowledgeRepository
    from ccnl_engine.period.requests import PeriodCalculationRequest
    from ccnl_engine.sector.models import YearRules

__all__ = [
    "RunContract",
    "load_contract",
    "with_competence_contributions",
    "with_employer_sector",
]

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
    """CCNL, level, dates and yearly rules of a run.

    ``provincial_unknown`` holds the national elements of the level left out
    because the employer does not state whether a provincial element
    replaces them (:mod:`._provincial`).  ``sector_unknown`` holds the INPS
    sectors of a CCNL applied in more than one when the employer does not
    state its own: the run reads the sector of the CCNL.
    """

    ccnl: CCNL
    level: Level
    tctx: TemporalContext
    date_ctx: EffectiveDateContext
    year_rules: YearRules
    catalog: CapabilityCatalog
    provincial_unknown: tuple[str, ...] = ()
    sector_unknown: tuple[TaxSector, ...] = ()


def with_employer_sector(
    ccnl: CCNL, stated: TaxSector | None
) -> tuple[CCNL, tuple[TaxSector, ...]]:
    """Return the CCNL read in the INPS sector of the employer.

    A CCNL applied by employers of more than one INPS sector
    (``CCNLMeta.inps_sectors``) is read in the sector the employer states,
    so every rule that follows the sector (INPS rates, sickness cover, the
    Fondo Tesoreria) follows the classification of the employer.

    Returns:
        The CCNL, with ``tax_sector`` the stated sector, and the sectors
        left open when the CCNL lists several and none is stated.

    Raises:
        InvalidInputError: When the stated sector is not one the CCNL lists.
    """
    meta = ccnl.meta
    allowed = meta.inps_sectors or frozenset({meta.tax_sector})
    if stated is None:
        open_sectors = () if len(allowed) == 1 else tuple(sorted(allowed))
        return ccnl, open_sectors
    if stated not in allowed:
        msg = (
            f"EmployerProfile.inps_sector is {stated}, but the employers of "
            f"{meta.ccnl_id} are classified in {', '.join(sorted(allowed))}"
        )
        raise InvalidInputError(
            msg,
            field="EmployerProfile.inps_sector",
            feature="inps_employer",
            ruleset=meta.ccnl_id,
        )
    if stated is meta.tax_sector:
        return ccnl, ()
    sector_meta = meta.model_copy(update={"tax_sector": stated})
    return ccnl.model_copy(update={"meta": sector_meta}), ()


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
    ccnl = flat_pay_divisor(repo.load_ccnl(request.ccnl_slug), request.weekly_hours)
    ccnl, sector_unknown = with_employer_sector(ccnl, request.employer.inps_sector)
    tctx = TemporalContext.from_period(
        period_id.year, period_id.month, request.payment_date
    )
    ccnl, provincial_unknown = without_replaced_elements(
        ccnl,
        request.level_code,
        request.employer.provincial_pay_element,
        tctx.competence,
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
    if year_rules.inps is not None:
        inps = with_cigs_indotto(
            with_zone_reduction(
                with_fis_reduction(
                    year_rules.inps.for_public_fund(ccnl.meta.public_pension_fund),
                    request.employer.fis_reduction,
                    headcount,
                ),
                request.employer.agricultural_zone,
            ),
            request.employer.cigs_indotto,
            headcount,
        )
        year_rules = year_rules.model_copy(update={"inps": inps})
    catalog = repo.load_capability_catalog(tctx.fiscal_year)
    return RunContract(
        ccnl,
        level,
        tctx,
        date_ctx,
        year_rules,
        catalog,
        provincial_unknown,
        sector_unknown,
    )


#: Weeks of a month: a weekly schedule times 52 / 12 is its monthly hours.
_WEEKS_PER_MONTH = Decimal(52) / Decimal(12)
_CENT = Decimal("0.01")


def flat_pay_divisor(ccnl: CCNL, weekly_hours: WeeklyHours | None) -> CCNL:
    """Return ``ccnl`` with the hourly divisor of the hours actually worked.

    A regime that pays its minimum whatever the hours up to a ceiling
    (``flat_pay_max_weekly_hours``, CCNL lavoro domestico art. 14 c. 2) has
    an hourly rate of the monthly pay over the hours of the employment, not
    over those of the ceiling: the divisor becomes ``weekly_hours x 52 / 12``
    for the INPS hourly bracket, the overtime and the proration alike.

    Returns:
        ``ccnl`` unchanged outside such a regime or without weekly hours.
    """
    params = ccnl.parameters
    if params.flat_pay_max_weekly_hours is None or weekly_hours is None:
        return ccnl
    hours = (Decimal(weekly_hours.value) * _WEEKS_PER_MONTH).quantize(_CENT)
    periods = tuple(
        p.model_copy(update={"value": hours}) for p in params.hourly_divisor.periods
    )
    divisor = params.hourly_divisor.model_copy(update={"periods": periods})
    update = {"parameters": params.model_copy(update={"hourly_divisor": divisor})}
    return ccnl.model_copy(update=update)


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
        :class:`~ccnl_engine.errors.UnsupportedTaxYearError`.
    """
    if rules.year == competence_year:
        return rules
    source = repo.load_year_rules(competence_year, sector, headcount)
    return rules.model_copy(
        update={name: getattr(source, name) for name in _CONTRIBUTION_FIELDS}
    )
