"""IRPEF withheld on one run: family deductions, the pay period and conguaglio."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.models_decision import (
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.family.services import resolve_family
from ccnl_engine.payroll.period.services_shared import _ZERO
from ccnl_engine.payroll.taxation.services_tax_computation import (
    TaxResolution,
    compute_tax,
)
from ccnl_engine.payroll.withholding.rules_period import PayPeriod

if TYPE_CHECKING:
    from ccnl_engine.payroll.amount.types import _AmountsInput
    from ccnl_engine.payroll.family.services import RunFamily
    from ccnl_engine.payroll.taxation.services_taxable import _Taxable


@dataclass(frozen=True)
class _Irpef:
    """IRPEF of the run with the family deductions it was computed with.

    Attributes:
        tax: Tax computation, recovery plan and decisions of the run.
        family: Art. 12 TUIR deductions of the run, ``None`` without a
            family composition.
    """

    tax: TaxResolution
    family: RunFamily | None


#: Other income can only raise the reddito complessivo of L. 207/2024 art. 1
#: c. 6, so it matters only while the ulteriore detrazione is due.
ULTERIORE_INCOME_UNKNOWN = CalculationIssue(
    code="ulteriore_income_unknown",
    message=(
        "ulteriore_detrazione: the reddito complessivo of L. 207/2024 art. 1 "
        "c. 6 includes the income beyond this employment, which the run does "
        "not know: state it in PeriodInput.current_year (zero included); the "
        "amount shown is computed on this employment alone"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="current_year",
)


def ulteriore_issues(inp: _AmountsInput, irpef: _Irpef) -> tuple[CalculationIssue, ...]:
    """Return the missing income beyond this employment of a due ulteriore.

    Returns:
        :data:`ULTERIORE_INCOME_UNKNOWN` while the ulteriore detrazione is
        due and ``current_year`` of the tax year is not stated, else nothing.
    """
    due = any(
        c.name == "ulteriore_detrazione" and c.amount > _ZERO
        for c in irpef.tax.computation.components
    )
    facts = inp.current_year
    if not due or (facts is not None and facts.tax_year == inp.rules.year):
        return ()
    return (ULTERIORE_INCOME_UNKNOWN,)


def _external_income(inp: _AmountsInput) -> Decimal:
    """Return the reddito complessivo of the tax year beyond this employment.

    Returns:
        The income beyond this employment the somma esente counts, the
        exempt share of the impatriati and researcher regimes included (L.
        207/2024 art. 1 c. 9); zero without the facts of the tax year: the
        somma esente is then computed on this employment alone and flagged
        (c. 4).
    """
    facts = inp.current_year
    if facts is None or facts.tax_year != inp.rules.year:
        return _ZERO
    return facts.somma_esente_income


def _pay_period(
    inp: _AmountsInput, taxable: _Taxable, family: RunFamily | None
) -> PayPeriod:
    """Return the pay of the run as art. 23 c. 2 DPR 600/1973 withholds it.

    The deductions of the period are those of a regular month: the days of
    the month over the days of employment in the year for art. 13 TUIR and
    the ulteriore detrazione, the dependents of the month for art. 12 TUIR.
    A tredicesima, a quattordicesima or an adjustment run takes none
    (``period_days`` is zero).

    Returns:
        The taxable of lett. a) and b), the day share and the art. 12
        deductions of the month.
    """
    days = inp.eligible_work_days
    share = Decimal(inp.period_days) / days if days > 0 else _ZERO
    month_family = (
        _ZERO
        if family is None or not inp.period_days
        else family.deductions.of_month(inp.run_month)
    )
    return PayPeriod(
        regular_taxable=taxable.period - taxable.separate,
        separate_taxable=taxable.separate,
        day_share=share,
        family=month_family,
    )


def withhold_irpef(inp: _AmountsInput, taxable: _Taxable) -> _Irpef:
    """Return the IRPEF of the run.

    The annual deductions are measured on the projected annual taxable
    income; the run withholds on its pay period, the last slot settles the
    year (art. 23 c. 2-3 DPR 600/1973).

    Returns:
        The tax resolution and the family deductions it used.
    """
    projected = taxable.projected
    family = resolve_family(
        inp.family_composition,
        inp.family_deduction_rules,
        inp.current_year,
        projected,
        conguaglio=inp.conguaglio,
    )
    opening = inp.opening
    # Net credit = recognized minus already recovered; prevents re-recovering credits
    # that have already been clawed back in previous periods (D.L. 3/2020, art. 1 c. 3).
    net_credit_ytd = opening.trattamento.recognized - opening.trattamento.recovered
    tax = compute_tax(
        projected,
        inp.rules,
        opening_irpef_withheld=opening.tax.irpef + inp.deferred_irpef,
        opening_tratt_ytd=net_credit_ytd,
        remaining_slots=inp.withholding.remaining,
        family_deductions=_ZERO if family is None else family.deductions.total,
        recovery_plan=inp.recovery_plan,
        eligible_work_days=inp.eligible_work_days,
        period=_pay_period(inp, taxable, family),
        carried_shortfall=opening.shortfall.irpef,
        ulteriore_account=opening.ulteriore_detrazione,
        run=inp.installment_run,
        ulteriore_plan=inp.ulteriore_plan,
        foreign_taxes=inp.foreign_taxes if inp.conguaglio else (),
        fixed_term=inp.fixed_term_in_year,
        external_income=_external_income(inp),
    )
    return _Irpef(tax=tax, family=family)
