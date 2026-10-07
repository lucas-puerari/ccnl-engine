"""IRPEF withheld on one run: family deductions, the pay period and conguaglio."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application.amounts._family import resolve_family
from ccnl_engine.payroll.service.period_withholding import PayPeriod
from ccnl_engine.payroll.service.tax_computation import TaxResolution, compute_tax

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._family import RunFamily
    from ccnl_engine.payroll.application.amounts._taxable import _Taxable
    from ccnl_engine.payroll.application.amounts._types import _AmountsInput


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
    )
    return _Irpef(tax=tax, family=family)
