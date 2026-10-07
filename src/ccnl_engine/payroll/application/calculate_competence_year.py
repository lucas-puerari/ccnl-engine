"""Every run of one competence year, across the tax years that pay them."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.close_tax_year import close_tax_year
from ccnl_engine.payroll.application.withholding._plan import standard_payments
from ccnl_engine.payroll.application.year._calendar import standard_calendar
from ccnl_engine.payroll.application.year._payments import (
    PreparedYear,
    check_opening,
    prepare_year,
    tax_year_payments,
    tax_year_schedule,
)
from ccnl_engine.payroll.application.year._sequence import Engine, compute_payments
from ccnl_engine.payroll.application.year_result import CompetenceYearResult
from ccnl_engine.payroll.domain.engine_mode import EngineMode
from ccnl_engine.payroll.domain.withholding_schedule import WithholdingSlot
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.application.year._payments import PlannedPayment
    from ccnl_engine.payroll.domain.competence_year_plan import CompetenceYearPlan
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.policy import PolicyResolver

__all__ = ["calculate_competence_year"]

_PATH = "CompetenceYearPlan.opening_state"
_ONE = Decimal(1)


def calculate_competence_year(
    plan: CompetenceYearPlan,
    *,
    repo: KnowledgeRepository | None = None,
    resolver: PolicyResolver | None = None,
    bundle_version: str | None = None,
    mode: EngineMode = EngineMode.SIMULATION,
) -> CompetenceYearResult:
    """Compute every run of a competence year, in payment order.

    The runs follow from the effective calendar (the CCNL standard one or
    ``plan.calendar_override``) and the employment period: a regular run
    for each month with at least one employed day, an extra-month run only
    when its payment month is such a month.  A partly employed month pays
    the daily quotas of its employed days under the CCNL partial-month
    rule, and is not payable when the CCNL defines none (see
    :mod:`~ccnl_engine.payroll.domain.proration`).  Extra months accrue per
    qualifying month of their window; an absence with ``suspends_accrual``
    in any entry of ``plan.periods`` removes its days from every window,
    and the ratei of an extra month not paid before the termination are
    paid on the last regular run.

    A run whose competence date has no base salary of the level in the
    bundle (the pay tables start later in the year, or a declared gap) is
    not computed: it is listed in ``uncovered_runs`` with its
    :class:`~ccnl_engine.shared.domain.errors.MissingRuleError`, adds a
    ``run_not_computed`` blocker, and the other runs are computed on a
    withholding schedule without it.  The extra months still accrue over
    the employed months the year left out, since the worker was employed
    in them.  ``ContractSummary.validity`` tells the dates in advance.

    Each run is paid on its date in the plan, which sets its tax year.  The
    runs paid in the competence year are computed on the schedule of the
    payments of that tax year (those closed in the opening state, then
    these), so the conguaglio falls on the last of them; that tax year is
    then closed with
    :func:`~ccnl_engine.payroll.application.close_tax_year.close_tax_year`.
    The runs paid in a later tax year (December paid after 12 January)
    open it, on a schedule that projects the CCNL standard runs of that
    year after them.  A run the opening state already closed with the same
    payment is not computed again.  A run paid after the first payment of
    the next tax year belongs in
    :func:`~ccnl_engine.payroll.application.calculate_tax_year\
.calculate_tax_year`, which orders it among the runs of that year.

    Args:
        plan: Employment, employer, facts and payment dates of the runs, and
            the opening state.
        repo: Knowledge repository; the bundled one when ``None``.
        resolver: Pre-loaded policy resolver, or ``None``.
        bundle_version: Knowledge-bundle version propagated to each result.
        mode: Payability policy of every run.

    Returns:
        One result per run computed, in payment order, and the state that
        opens the next competence year (``next_opening_state``).

    Errors: :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`
    when the calendar override, the employment period or the payment dates
    are rejected, or the opening state is of another tax year, holds totals
    of unidentified payments or closed a run of the year with another
    payment; :class:`~ccnl_engine.shared.domain.errors.MissingRuleError`
    when no run of the year has a base salary.
    """
    effective_repo = repo if repo is not None else BundledKnowledgeRepository()
    prepared = prepare_year(plan, effective_repo)
    tax_years = sorted({p.payment.tax_year for p in prepared.payments})
    state = plan.opening_state
    first = tax_years[0] if state is None or state.tax_year is None else state.tax_year
    opening = check_opening(state, first, _PATH)
    engine = Engine(effective_repo, resolver, bundle_version, mode)
    results: list[PeriodResult] = []
    current = opening
    for tax_year in tax_years:
        current = _open_tax_year(current, tax_year, prepared)
        if current.tax_year is not None and current.tax_year > tax_year:
            continue
        pending = tax_year_payments((prepared,), tax_year, current)
        if not pending:
            continue
        projected = () if tax_year == plan.year else _projection(prepared, pending)
        schedule = tax_year_schedule(tax_year, current, pending, projected)
        computed = compute_payments(pending, schedule, current, engine)
        results.extend(computed)
        current = computed[-1].closing_state
    return CompetenceYearResult(
        tuple(results),
        opening,
        bundle_version=bundle_version,
        year=plan.year,
        calendar=prepared.calendar,
        calendar_override=plan.calendar_override,
        uncovered_runs=prepared.uncovered,
    )


def _open_tax_year(
    state: PeriodState, tax_year: int, prepared: PreparedYear
) -> PeriodState:
    """Return ``state`` moved to ``tax_year``, closing the years before it.

    Returns:
        ``state`` when it is of ``tax_year`` or of no year; otherwise the
        state after :func:`close_tax_year` up to ``tax_year``.

    Raises:
        InvalidInputError: When ``state`` is of a tax year after
            ``tax_year`` but a run of the plan paid in ``tax_year`` is not
            closed in it.
    """
    if state.tax_year is not None and state.tax_year > tax_year:
        settled = set(state.accrual.competence_runs)
        missing = [
            p.payment
            for p in prepared.payments
            if p.payment.tax_year == tax_year and p.payment.run_id not in settled
        ]
        if missing:
            msg = (
                f"the opening state is of tax year {state.tax_year}, but "
                f"payment '{missing[0]}' of tax year {tax_year} is not closed"
            )
            raise InvalidInputError(msg, field=_PATH, feature="tax_year")
        return state
    while state.tax_year is not None and state.tax_year < tax_year:
        state = close_tax_year(state)
    return state


def _projection(
    prepared: PreparedYear, pending: tuple[PlannedPayment, ...]
) -> tuple[WithholdingSlot, ...]:
    """Return the standard runs of a later tax year after the late payments.

    Returns:
        One slot per run of the CCNL standard calendar of the tax year of
        ``pending``, in a month of the employment, paid on the plan's day.
    """
    last = pending[-1].payment.run_id
    tax_year = pending[0].payment.tax_year
    as_of = date(last.year, last.month, 1)
    calendar = standard_calendar(prepared.ccnl, tax_year, as_of)
    fractions = {e.kind.value: e.max_fraction for e in calendar.extra_months}
    payments = standard_payments(
        calendar,
        exclude=frozenset(),
        employment=prepared.plan.employment.employment_period,
        day=prepared.plan.payment_day,
    )
    return tuple(
        WithholdingSlot(p, fractions.get(p.run_id.kind.value, _ONE)) for p in payments
    )
