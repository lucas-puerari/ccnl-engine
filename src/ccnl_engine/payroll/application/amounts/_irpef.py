"""IRPEF withheld on one run: family deductions, one-off pay and conguaglio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application.amounts._family import resolve_family
from ccnl_engine.payroll.application.amounts._taxable import one_off_taxable
from ccnl_engine.payroll.domain.employment import FixedTerm
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR
from ccnl_engine.payroll.service.irpef_net import NetIrpef, net_irpef
from ccnl_engine.payroll.service.tax_computation import TaxResolution, compute_tax

if TYPE_CHECKING:
    from decimal import Decimal

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


def _fixed_term(inp: _AmountsInput) -> bool:
    """Return whether the employment of the run is fixed-term.

    It selects the minimum of the art. 13 deduction (c. 1 lett. a) TUIR).

    Returns:
        True for a :class:`FixedTerm` contract.
    """
    return isinstance(inp.contract_type, FixedTerm)


def _family_deductions(family: RunFamily | None, own_income: Decimal) -> Decimal:
    """Return the annual art. 12 TUIR deductions with ``own_income``.

    Returns:
        Zero without a family composition or its rules.
    """
    return _ZERO if family is None else family.deductions_at(own_income).total


def _without_one_off(
    inp: _AmountsInput,
    taxable: Decimal,
    one_off: Decimal,
    family: RunFamily | None,
) -> NetIrpef | None:
    """Return the net IRPEF of the projection without the one-off pay.

    Returns:
        ``None`` when the run has no one-off taxable income.
    """
    if one_off <= _ZERO:
        return None
    return net_irpef(
        taxable - one_off,
        inp.rules,
        family_deductions=_family_deductions(family, taxable - one_off),
        eligible_work_days=min(inp.eligible_work_days, DAYS_IN_YEAR),
        fixed_term=_fixed_term(inp),
    )


def withhold_irpef(
    inp: _AmountsInput, taxable: _Taxable, inps_employee: Decimal
) -> _Irpef:
    """Return the IRPEF of the run on the projected annual taxable income.

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
    fam_ded = _family_deductions(family, projected)
    one_off = one_off_taxable(inp, taxable, inps_employee)
    without_one_off = _without_one_off(inp, projected, one_off, family)
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
        family_deductions=fam_ded,
        recovery_plan=inp.recovery_plan,
        eligible_work_days=inp.eligible_work_days,
        net_without_one_off=None if without_one_off is None else without_one_off.net,
        carried_shortfall=opening.shortfall.irpef,
        ulteriore_account=opening.ulteriore_detrazione,
        ulteriore_without_one_off=(
            _ZERO if without_one_off is None else without_one_off.ulteriore_effect
        ),
        run=inp.installment_run,
        ulteriore_plan=inp.ulteriore_plan,
        foreign_taxes=inp.foreign_taxes if inp.conguaglio else (),
        fixed_term=_fixed_term(inp),
    )
    return _Irpef(tax=tax, family=family)
