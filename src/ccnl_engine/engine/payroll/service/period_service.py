"""Period payroll services: compute_period, compute_year, compute_period_payroll."""

from __future__ import annotations

import warnings
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.engine.payroll.domain.fiscal_ytd import FiscalYTD
from ccnl_engine.engine.payroll.domain.payroll_result import PeriodPayroll
from ccnl_engine.engine.payroll.domain.payroll_state import PayrollState
from ccnl_engine.engine.payroll.domain.period import PayrollPeriod, YTDState
from ccnl_engine.engine.payroll.domain.period_payroll import (
    PeriodId,
    PeriodPayrollRequest,
    PeriodPayrollResult,
)
from ccnl_engine.engine.payroll.domain.scenario import PeriodPayrollInput
from ccnl_engine.engine.payroll.service.pipeline import _annual_to_scenario, compute
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.engine.payroll.domain.bundle import PayrollBundle
    from ccnl_engine.engine.payroll.domain.calculation import Calculation
    from ccnl_engine.engine.payroll.domain.scenario import AnnualEstimateInput

_ZERO = Decimal(0)


def _accrue_ytd(ytd: YTDState, calc: Calculation) -> YTDState:
    """Return a new YTDState with one month's contribution appended.

    The engine produces annualized figures; dividing by 12 gives the
    per-period share that accumulates in the YTD totals.

    Returns:
        A new :class:`~ccnl_engine.engine.payroll.domain.period.YTDState`
        with the monthly share of *calc* added to *ytd*.
    """
    twelve = Decimal(12)
    r = calc.result
    return YTDState(
        taxable_income=ytd.taxable_income + r.taxes.taxable_income / twelve,
        irpef_withheld=ytd.irpef_withheld + r.taxes.irpef_net / twelve,
        inps_employee=ytd.inps_employee + r.contributions.inps_employee_annual / twelve,
    )


def compute_period(
    scenario: AnnualEstimateInput,
    period: PayrollPeriod,
    bundle: PayrollBundle | None = None,
    *,
    repo: KnowledgeRepository | None = None,
) -> Calculation:
    """Compute payroll for a single month of competence.

    .. deprecated::
        This function divides annual figures by 12 and does not compute a real
        period payroll.  The YTD state does not alter the calculation.  It will
        be replaced by a period-first engine in a future release.

    Args:
        scenario: The annual payroll scenario (structural fields only).
        period: The month descriptor including YTD state and period events.
        bundle: Optional pre-loaded knowledge bundle.  When ``None``,
            rulesets are loaded on demand.
        repo: Optional knowledge repository.  When ``None``,
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is used.

    Returns:
        A :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        for the specified month.
    """
    warnings.warn(
        "compute_period() produces annualized figures divided by 12, not a real "
        "period payroll. It will be replaced in a future release.",
        DeprecationWarning,
        stacklevel=2,
    )
    updated = scenario.model_copy(
        update={
            "employment": scenario.employment.model_copy(
                update={"as_of": date(period.year, period.month, 1)}
            )
        }
    )
    return compute(
        _annual_to_scenario(updated, period.events),
        bundle,
        _period=period.events,
        repo=repo,
    )


def compute_year(
    scenario: AnnualEstimateInput,
    year: int,
    *,
    bundle: PayrollBundle | None = None,
    month_events: list[PeriodPayrollInput] | None = None,
    repo: KnowledgeRepository | None = None,
) -> list[Calculation]:
    """Compute payroll for all twelve months of *year*.

    .. deprecated::
        Each month is computed by dividing annual figures — not by a real
        period-first engine.  The year total does not equal the sum of
        independent period results.  Will be replaced in a future release.

    Args:
        scenario: The annual payroll scenario (structural fields only).
        year: The calendar year to compute (e.g. ``2026``).
        bundle: Optional pre-loaded knowledge bundle shared across all twelve
            calls.  When ``None``, rulesets are loaded on demand.
        month_events: List of exactly twelve :class:`~ccnl_engine.PeriodPayrollInput`
            instances, one per month January-December.  When ``None``, every
            month uses a default :class:`~ccnl_engine.PeriodPayrollInput` (no special
            events).
        repo: Optional knowledge repository.  When ``None``,
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is used.

    Returns:
        A list of twelve
        :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        instances, one per month in calendar order.

    Raises:
        InvalidInputError: When *month_events* is provided but does not
            contain exactly 12 entries.
    """
    warnings.warn(
        "compute_year() divides annual figures across months rather than "
        "computing each period independently. It will be replaced in a future release.",
        DeprecationWarning,
        stacklevel=2,
    )
    from ccnl_engine.engine.errors import InvalidInputError  # noqa: PLC0415

    events: list[PeriodPayrollInput] = (
        month_events
        if month_events is not None
        else [PeriodPayrollInput() for _ in range(12)]
    )
    if len(events) != 12:
        msg = f"month_events must have exactly 12 entries, got {len(events)}"
        raise InvalidInputError(msg, feature="payroll_period")
    results: list[Calculation] = []
    ytd = YTDState()
    for i, ev in enumerate(events):
        month = i + 1
        period = PayrollPeriod(year=year, month=month, events=ev, ytd=ytd)
        calc = compute_period(scenario, period, bundle, repo=repo)
        ytd = _accrue_ytd(ytd, calc)
        results.append(calc)
    return results


def compute_period_payroll(
    request: PeriodPayrollRequest,
    bundle: PayrollBundle | None = None,
    *,
    repo: KnowledgeRepository | None = None,
) -> PeriodPayrollResult:
    """Compute a single payroll period with YTD-based conguaglio IRPEF.

    .. deprecated::
        This function divides annual figures by the number of pay periods and
        does not perform real period-based payroll computation.  The YTD
        ``irpef_withheld_ytd`` is injected into the annual formula but does not
        drive a genuine conguaglio: changing it does not alter the period net.
        Variable events (overtime, bonus, fringe) may update the closing state
        without entering the net or employer cost.  Do not rely on this function
        for cedolino production.  It will be replaced in a future release.

    Args:
        request: Period payroll request: structural scenario, period events,
            and the YTD opening state accumulated from all prior periods.
        bundle: Optional pre-loaded knowledge bundle.  When ``None``,
            rulesets are loaded on demand.
        repo: Optional knowledge repository.  When ``None``,
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is used.

    Returns:
        A :class:`~PeriodPayrollResult` with the opening and closing YTD
        states, the key period figures, and all ledger entries.
    """
    warnings.warn(
        "compute_period_payroll() divides annual figures and does not compute a real "
        "cedolino. The YTD state does not drive conguaglio. "
        "It will be replaced in a future release.",
        DeprecationWarning,
        stacklevel=2,
    )
    opening = request.opening_state
    if request.period_id is not None:
        period_id: PeriodId | None = request.period_id
        as_of = date(request.period_id.year, request.period_id.month, 1)
    else:
        warnings.warn(
            "PeriodPayrollRequest.period_id is None; period inferred from "
            "structural.employment.as_of. Set period_id to silence this warning.",
            DeprecationWarning,
            stacklevel=2,
        )
        period_id = None
        as_of = request.structural.employment.as_of
    if bundle is not None:
        ccnl = bundle.ccnl
    else:
        effective_repo = repo if repo is not None else BundledKnowledgeRepository()
        ccnl = effective_repo.load_ccnl(request.structural.employment.ccnl)
    additional_months = ccnl.parameters.additional_months.value_at(as_of)
    multiplier = Decimal(1 + request.period.extra_monthly_payments)
    twelve = Decimal(12)
    eleven = Decimal(11)
    scenario = _annual_to_scenario(request.structural, request.period)
    if opening.irpef_withheld_ytd != _ZERO:
        scenario = scenario.model_copy(
            update={"prior_period_irpef_withheld": opening.irpef_withheld_ytd}
        )
    calc = compute(scenario, bundle, repo=repo)
    r = calc.result
    base_gross = money(r.earnings.gross_annual / additional_months)
    period_gross = money(base_gross * multiplier)
    reg_annual = r.taxes.addizionale_regionale_annual
    com_annual = r.taxes.addizionale_comunale_annual
    if request.period.is_addizionali_settlement:
        period_addizionale_reg = money(reg_annual - opening.addizionale_regionale_ytd)
        period_addizionale_com = money(com_annual - opening.addizionale_comunale_ytd)
    else:
        period_addizionale_reg = money(reg_annual / eleven)
        period_addizionale_com = money(com_annual / eleven)
    engine_addizionale_period = money(
        (reg_annual + com_annual) / additional_months * multiplier
    )
    period_net = money(
        r.net_monthly * multiplier
        + engine_addizionale_period
        - period_addizionale_reg
        - period_addizionale_com
    )
    period_employer_cost = money(
        (r.employer_cost.employer_cost_annual / additional_months) * multiplier
    )
    period_leave_accrued = (
        r.leave_accrued_days_monthly if isinstance(r, PeriodPayroll) else _ZERO
    )
    period_leave_taken = (
        r.leave_taken_days_monthly if isinstance(r, PeriodPayroll) else _ZERO
    )
    period_sick = r.sick_days_monthly if isinstance(r, PeriodPayroll) else _ZERO
    new_leave_accrued = opening.leave_accrued_days_ytd + period_leave_accrued
    new_leave_taken = opening.leave_taken_days_ytd + period_leave_taken
    closing = PayrollState(
        gross_annual_ytd=opening.gross_annual_ytd + period_gross,
        inps_employee_annual_ytd=(
            opening.inps_employee_annual_ytd
            + money(
                r.contributions.inps_employee_annual / additional_months * multiplier
            )
        ),
        inps_employer_annual_ytd=(
            opening.inps_employer_annual_ytd
            + money(
                r.contributions.inps_employer_annual / additional_months * multiplier
            )
        ),
        inail_employer_annual_ytd=(
            opening.inail_employer_annual_ytd
            + money(
                r.contributions.inail_employer_annual / additional_months * multiplier
            )
        ),
        taxable_income_ytd=(
            opening.taxable_income_ytd
            + money(r.taxes.taxable_income / additional_months * multiplier)
        ),
        irpef_gross_ytd=(
            opening.irpef_gross_ytd
            + money(r.taxes.irpef_gross / additional_months * multiplier)
        ),
        irpef_withheld_ytd=(
            opening.irpef_withheld_ytd
            + money(r.taxes.irpef_net / additional_months * multiplier)
        ),
        work_income_deduction_ytd=(
            opening.work_income_deduction_ytd
            + money(r.taxes.work_income_deduction / twelve)
        ),
        fam_deductions_ytd=(
            opening.fam_deductions_ytd + money(r.taxes.family_deduction_annual / twelve)
        ),
        art15_deductions_ytd=(
            opening.art15_deductions_ytd
            + money(r.taxes.art15_deduction_annual / twelve)
        ),
        trattamento_integrativo_ytd=(
            opening.trattamento_integrativo_ytd
            + money(r.taxes.trattamento_integrativo / twelve)
        ),
        addizionale_regionale_ytd=(
            opening.addizionale_regionale_ytd + period_addizionale_reg
        ),
        addizionale_comunale_ytd=(
            opening.addizionale_comunale_ytd + period_addizionale_com
        ),
        tfr_annual_ytd=(
            opening.tfr_annual_ytd
            + money(r.contributions.tfr_annual / additional_months * multiplier)
        ),
        leave_accrued_days_ytd=new_leave_accrued,
        leave_taken_days_ytd=new_leave_taken,
        leave_balance_days=new_leave_accrued - new_leave_taken,
        sick_days_ytd=opening.sick_days_ytd + period_sick,
    )
    fiscal_ytd = FiscalYTD(
        taxable_income_ytd=closing.taxable_income_ytd,
        irpef_gross_ytd=closing.irpef_gross_ytd,
        irpef_withheld_ytd=closing.irpef_withheld_ytd,
        work_income_deduction_ytd=closing.work_income_deduction_ytd,
        fam_deductions_ytd=closing.fam_deductions_ytd,
        art15_deductions_ytd=closing.art15_deductions_ytd,
        trattamento_integrativo_ytd=closing.trattamento_integrativo_ytd,
        addizionale_regionale_ytd=closing.addizionale_regionale_ytd,
        addizionale_comunale_ytd=closing.addizionale_comunale_ytd,
    )
    return PeriodPayrollResult(
        opening_state=opening,
        closing_state=closing,
        period_gross=period_gross,
        period_net=period_net,
        period_employer_cost=period_employer_cost,
        fiscal_ytd=fiscal_ytd,
        ledger_entries=calc.ledger_entries,
        period_id=period_id,
    )
