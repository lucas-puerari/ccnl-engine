"""Social security contribution calculations.

IVS ceiling split: when the ceiling applies and the INPS rules carry a non-null
``ceiling``, only the IVS portion of each INPS rate is capped at the massimale
annuo della base contributiva (Art. 2 c. 18 L. 335/1995); the remainder
(NASpI, CUAF, CIG, etc.) is applied to the full base.  The ceiling is enforced
via ``ytd_inps_base``: only the portion of ``period_inps_base`` fitting within
the remaining headroom attracts IVS contributions.  Whether it applies is
derived by the caller from the worker's contribution history (first enrolment
from 1 Jan 1996, or the contributory option of Art. 1 c. 23); this module
never assumes it.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.contribution.additional_ivs.rules import (
    AdditionalIvsPosition,
    additional_ivs,
)
from ccnl_engine.contribution.rate.rules import resolve_rates
from ccnl_engine.contribution.results import (
    ContributionBreakdown,
    ContributionComponent,
)
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.contribution.rate.rules import ContributionRates
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.employment.inputs import Apprentice, FixedTerm, Permanent
    from ccnl_engine.sector.models import YearRules

_ZERO = Decimal(0)
#: Sectors whose employers declare each worker in the <DenunciaIndividuale>
#: of the UniEmens flow, one contribution at the whole rate.  The public
#: administrations declare each fund apart (ListaPosPA) and the farm
#: workers go through the DMAG: their rates stay rounded one by one.
_DENUNCIA_INDIVIDUALE = frozenset({
    TaxSector.INDUSTRIA,
    TaxSector.TERZIARIO,
    TaxSector.EDILIZIA,
    TaxSector.CREDITO,
    TaxSector.ARTIGIANATO,
})
_NO_POSITION = AdditionalIvsPosition()


def _side(
    side: str,
    rate: Decimal,
    ivs_rate: Decimal,
    ivs_base: Decimal,
    full_base: Decimal,
) -> tuple[Decimal, list[ContributionComponent]]:
    """Split one side's contribution into its IVS and non-IVS parts.

    The IVS part applies ``ivs_rate`` to the capped ``ivs_base``; the rest of
    ``rate`` applies to the full base.

    Returns:
        The side's total and its components ``ivs_<side>`` and
        ``non_ivs_<side>``, each only when its rate is positive.
    """
    non_ivs_rate = rate - ivs_rate
    ivs = money(ivs_base * ivs_rate)
    non_ivs = money(full_base * non_ivs_rate)
    components: list[ContributionComponent] = []
    if ivs_rate > _ZERO:
        components.append(
            ContributionComponent(
                name=f"ivs_{side}", base=ivs_base, rate=ivs_rate, amount=ivs
            )
        )
    if non_ivs_rate > _ZERO:
        components.append(
            ContributionComponent(
                name=f"non_ivs_{side}",
                base=full_base,
                rate=non_ivs_rate,
                amount=non_ivs,
            )
        )
    return ivs + non_ivs, components


def _employer_share(
    employee: Decimal,
    employer_items: list[ContributionComponent],
    rates: ContributionRates,
    ivs_base: Decimal,
    full_base: Decimal,
) -> tuple[Decimal, list[ContributionComponent]]:
    """Return the employer share of the contribution INPS charges on the run.

    INPS charges one contribution per worker and month: "Importo della
    contribuzione calcolata sull'imponibile previdenziale del mese corrente
    [...] con arrotondamento ai centesimi" (Documento tecnico UniEmens,
    <Contributo> of <DatiRetributivi>), at the whole rate of the worker, the
    NASpI surcharge of a fixed term included (INPS circ. 140/2012 p. 6: no
    exposure of its own).  The part of the base above the IVS massimale is
    declared apart, with the minor contributions only.  The employer pays
    that contribution less the share it withholds from the employee, so the
    non-IVS employer component takes the rounding of the whole.

    Returns:
        The employer share and its components, the non-IVS one (or the IVS
        one without it) adjusted to the share.
    """
    rate = rates.employee_rate + rates.employer_rate
    ivs_rate = rates.employee_ivs_rate + rates.employer_ivs_rate
    total = money(ivs_base * rate) + money((full_base - ivs_base) * (rate - ivs_rate))
    share = total - employee
    if not employer_items:
        return _ZERO, employer_items
    *kept, last = employer_items
    rest = sum((c.amount for c in kept), _ZERO)
    return share, [*kept, replace(last, amount=share - rest)]


def whole_rate_addition(
    breakdown: ContributionBreakdown, rules: YearRules, base: Decimal, rate: Decimal
) -> Decimal:
    """Return what a further employer rate on ``base`` adds to the contribution.

    In a sector whose employers declare one contribution per worker at the
    whole rate (:data:`_DENUNCIA_INDIVIDUALE`), a further rate INPS charges in
    the same <Contributo> (the additional sickness contribution of the
    pubblici esercizi) joins the single rounding: the addition is the whole
    contribution with it less the whole contribution without it.  Elsewhere
    it is ``base * rate`` to cents.

    Returns:
        The amount the further rate adds.
    """
    if rules.sector not in _DENUNCIA_INDIVIDUALE:
        return money(base * rate)
    named = {c.name: c for c in breakdown.components}
    ivs = [named[n] for n in ("ivs_employee", "ivs_employer") if n in named]
    other = [named[n] for n in ("non_ivs_employee", "non_ivs_employer") if n in named]
    ivs_rate = sum((c.rate for c in ivs), _ZERO)
    other_rate = sum((c.rate for c in other), _ZERO)
    ivs_base = max((c.base for c in ivs), default=base)
    excess = base - ivs_base

    def whole(extra: Decimal) -> Decimal:
        return money(ivs_base * (ivs_rate + other_rate + extra)) + money(
            excess * (other_rate + extra)
        )

    return whole(rate) - whole(_ZERO)


def _additional(
    rules: YearRules,
    period_inps_base: Decimal,
    ytd_inps_base: Decimal,
    ceiling: Decimal | None,
    position: AdditionalIvsPosition,
) -> ContributionComponent | None:
    """Return the additional 1% IVS of the run, if the rules model it.

    Returns:
        The component of :func:`additional_ivs`, ``None`` without a rule.
    """
    rule = None if rules.inps is None else rules.inps.employee_additional
    if rule is None:
        return None
    return additional_ivs(
        rule,
        period_inps_base,
        ytd_base=ytd_inps_base,
        ceiling=ceiling,
        position=position,
    )


def resolve_contributions(
    period_inps_base: Decimal,
    rules: YearRules,
    contract_type: Permanent | FixedTerm | Apprentice,
    category: WorkerCategory | None,
    *,
    ytd_inps_base: Decimal,
    ivs_ceiling_applies: bool,
    additional: AdditionalIvsPosition = _NO_POSITION,
) -> ContributionBreakdown:
    """Compute INPS contributions with per-component breakdown and IVS ceiling.

    The IVS portion of both employee and employer contributions is capped at
    the massimale (Art. 2 c. 18 L. 335/1995) when it applies and a ceiling is
    configured.  The ceiling is enforced across the year via ``ytd_inps_base``:
    only the portion of ``period_inps_base`` that fits within the remaining
    headroom (``ceiling - ytd_inps_base``) attracts IVS contributions; the
    non-IVS components (NASpI, CUAF, CIG) are applied to the full base.

    Args:
        period_inps_base: Gross INPS-liable base for this period.
        rules: Year-specific tax and contribution rules.
        contract_type: Employment type (Permanent, FixedTerm, Apprentice).
        category: Level category for employer rate lookup, or None.
        ytd_inps_base: INPS base of the competence year before the run,
            all employers (``RunContext.ytd_inps_base``, from the accrual
            state). Used to enforce the annual IVS ceiling across periods.
        ivs_ceiling_applies: Whether the massimale applies to the worker.
            When False all contributions are applied to the full base.
        additional: Position of the run toward the additional 1% IVS
            (:mod:`~ccnl_engine.contribution.additional_ivs.rules`); by default
            the first run of its month, settling nothing.

    Returns:
        :class:`~ccnl_engine.contribution.results.ContributionBreakdown`
        with employee/employer totals and per-component trace.
    """
    rates = resolve_rates(rules, contract_type, category)
    ceiling = (
        rules.inps.ceiling if (rules.inps is not None and ivs_ceiling_applies) else None
    )

    # IVS-eligible base for this period: capped at remaining ceiling headroom.
    if ceiling is not None:
        ivs_base = max(_ZERO, min(period_inps_base, ceiling - ytd_inps_base))
    else:
        ivs_base = period_inps_base

    employee_total, employee_items = _side(
        "employee",
        rates.employee_rate,
        rates.employee_ivs_rate,
        ivs_base,
        period_inps_base,
    )
    _, employer_items = _side(
        "employer",
        rates.employer_rate,
        rates.employer_ivs_rate,
        ivs_base,
        period_inps_base,
    )
    employer_total = sum((c.amount for c in employer_items), _ZERO)
    if rules.sector in _DENUNCIA_INDIVIDUALE:
        employer_total, employer_items = _employer_share(
            employee_total, employer_items, rates, ivs_base, period_inps_base
        )
    components = [*employee_items, *employer_items]

    add_comp = _additional(rules, period_inps_base, ytd_inps_base, ceiling, additional)
    if add_comp is not None:
        employee_total += add_comp.amount
        components.append(add_comp)

    return ContributionBreakdown(
        employee=employee_total,
        employer=employer_total,
        components=tuple(components),
    )
