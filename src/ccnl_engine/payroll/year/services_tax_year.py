"""Every payment cashed in one tax year, whatever its competence year."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.assurance.policies_engine_mode import EngineMode
from ccnl_engine.payroll.period.repositories import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.year.results import TaxYearResult
from ccnl_engine.payroll.year.services_payment import (
    check_opening,
    prepare_year,
    tax_year_payments,
    tax_year_schedule,
)
from ccnl_engine.payroll.year.services_sequence import Engine, compute_payments

if TYPE_CHECKING:
    from ccnl_engine.payroll.amount.policies import PolicyResolver
    from ccnl_engine.payroll.period.ports import KnowledgeRepository
    from ccnl_engine.payroll.period.results import PeriodResult
    from ccnl_engine.payroll.taxation.inputs_current_year import CurrentYearTaxFacts
    from ccnl_engine.payroll.year.inputs_competence_plan import CompetenceYearPlan
    from ccnl_engine.payroll.year.inputs_tax_plan import TaxYearPlan

__all__ = ["calculate_tax_year"]


def calculate_tax_year(
    plan: TaxYearPlan,
    *,
    repo: KnowledgeRepository | None = None,
    resolver: PolicyResolver | None = None,
    bundle_version: str | None = None,
    mode: EngineMode = EngineMode.SIMULATION,
) -> TaxYearResult:
    """Compute every payment of a tax year, in payment order.

    The payments are the runs of ``plan.competence_years`` attributed to
    ``plan.tax_year`` by their payment date (TUIR art. 51 c. 1), after
    those already closed in ``plan.opening_state``.  Every payment is
    computed on the withholding schedule of all of them, so the IRPEF
    projection counts the payments actually made in the year and the
    conguaglio falls on the last one, whether a late payment of an
    earlier competence year comes before, among or after the runs of the
    year.  A payment the opening state already closed is not computed
    again: resuming an interrupted plan on the state it reached gives the
    same closing state as one uninterrupted pass.  A run of the tax year
    whose competence date has no base salary of its level is not computed
    and is listed in ``uncovered_runs``, as in
    :func:`~ccnl_engine.payroll.year.services_competence\
.calculate_competence_year`; when no run of a competence year has a base
    salary, :class:`~ccnl_engine.errors.MissingRuleError` of
    its first run is raised.

    Args:
        plan: The tax year, its competence years and its opening state.
        repo: Knowledge repository; the bundled one when ``None``.
        resolver: Pre-loaded policy resolver, or ``None``.
        bundle_version: Knowledge-bundle version propagated to each result.
        mode: Payability policy of every payment.

    Returns:
        One result per payment computed, the payments of the tax year and
        the closing state, whose ``conguaglio`` names the last payment.

    Raises:
        InvalidInputError: When the opening state is of another tax year or
            holds totals of unidentified payments, a planned run is closed
            with another payment, no run of the plans is paid in the tax
            year, or a competence year is rejected (calendar override,
            employment, payment dates).
    """
    effective_repo = repo if repo is not None else BundledKnowledgeRepository()
    tax_year = plan.tax_year
    opening = check_opening(plan.opening_state, tax_year, "TaxYearPlan.opening_state")
    years = tuple(
        prepare_year(_with_current_year(p, plan.current_year), effective_repo)
        for p in plan.competence_years
    )
    pending = tax_year_payments(years, tax_year, opening)
    if not pending and not opening.cash.payments:
        msg = (
            f"no run of the competence years {[p.year for p in plan.competence_years]}"
            f" is paid in tax year {tax_year}"
        )
        raise InvalidInputError(msg, field="TaxYearPlan", feature="tax_year")
    results: tuple[PeriodResult, ...] = ()
    if pending:
        results = compute_payments(
            pending,
            tax_year_schedule(tax_year, opening, pending),
            opening,
            Engine(effective_repo, resolver, bundle_version, mode),
        )
    return TaxYearResult(
        results,
        opening,
        mode=mode,
        bundle_version=bundle_version,
        tax_year=tax_year,
        payments=(*opening.cash.payments, *(p.payment for p in pending)),
        uncovered_runs=tuple(
            u for y in years for u in y.uncovered if u.payment.tax_year == tax_year
        ),
    )


def _with_current_year(
    plan: CompetenceYearPlan, current_year: CurrentYearTaxFacts | None
) -> CompetenceYearPlan:
    """Return ``plan`` reading the current-year facts of the tax year.

    Returns:
        ``plan`` unchanged when the tax year plan carries no facts.
    """
    if current_year is None:
        return plan
    return replace(plan, current_year=current_year)
