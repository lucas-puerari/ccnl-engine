"""IRPEF withheld on one run: family deductions, one-off pay and conguaglio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application.amounts._taxable import one_off_taxable
from ccnl_engine.payroll.service.family_deductions import compute_family_deductions
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR
from ccnl_engine.payroll.service.irpef_net import NetIrpef, net_irpef
from ccnl_engine.payroll.service.tax_computation import TaxResolution, compute_tax

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.amounts._taxable import _Taxable
    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.tax.domain.family import FamilyDeductionRules


@dataclass(frozen=True)
class _Irpef:
    """IRPEF of the run with the family deductions it was computed with.

    Attributes:
        tax: Tax computation, recovery plan and decisions of the run.
        family_deductions: Annual art. 12 TUIR deductions.
        family_rules: Rules the deductions were computed with, ``None``
            without a family composition.
    """

    tax: TaxResolution
    family_deductions: Decimal
    family_rules: FamilyDeductionRules | None


def _family_deductions(
    taxable: Decimal,
    family: FamilyComposition | None,
    rules: FamilyDeductionRules | None,
) -> Decimal:
    """Return the annual art. 12 TUIR deductions on ``taxable``.

    Returns:
        Zero without a family composition or its rules.
    """
    if family is None or rules is None:
        return _ZERO
    return compute_family_deductions(family, taxable, rules)[3]


def _without_one_off(
    inp: _AmountsInput,
    taxable: Decimal,
    one_off: Decimal,
    family_rules: FamilyDeductionRules | None,
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
        family_deductions=_family_deductions(
            taxable - one_off, inp.family_composition, family_rules
        ),
        eligible_work_days=min(inp.eligible_work_days, DAYS_IN_YEAR),
    )


def withhold_irpef(
    inp: _AmountsInput, taxable: _Taxable, inps_employee: Decimal
) -> _Irpef:
    """Return the IRPEF of the run on the projected annual taxable income.

    Returns:
        The tax resolution and the family deductions it used.
    """
    projected = taxable.projected
    family_rules = (
        None if inp.family_composition is None else inp.family_deduction_rules
    )
    fam_ded = _family_deductions(projected, inp.family_composition, family_rules)
    one_off = one_off_taxable(inp, taxable, inps_employee)
    without_one_off = _without_one_off(inp, projected, one_off, family_rules)
    opening = inp.opening
    # Net credit = recognized minus already recovered; prevents re-recovering credits
    # that have already been clawed back in previous periods (D.L. 3/2020, art. 1 c. 3).
    net_credit_ytd = opening.trattamento.recognized - opening.trattamento.recovered
    tax = compute_tax(
        projected,
        inp.rules,
        opening_irpef_withheld=opening.tax.irpef,
        opening_tratt_ytd=net_credit_ytd,
        withholding_schedule=inp.withholding_schedule,
        slots_closed=opening.tax_withholding_periods_closed,
        family_deductions=fam_ded,
        recovery_plan=inp.recovery_plan,
        eligible_work_days=inp.eligible_work_days,
        net_without_one_off=None if without_one_off is None else without_one_off.net,
        carried_shortfall=opening.shortfall.irpef,
        ulteriore_account=opening.ulteriore_detrazione,
        ulteriore_without_one_off=(
            _ZERO if without_one_off is None else without_one_off.ulteriore_effect
        ),
        later_payslips=inp.later_payslips,
    )
    return _Irpef(tax=tax, family_deductions=fam_ded, family_rules=family_rules)
