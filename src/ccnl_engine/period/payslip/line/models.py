"""One line of the payslip of a run."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.extra_month.progress.models import ExtraMonthProgress
from ccnl_engine.pay_item.voce.rules import VoceUnit

__all__ = ["PayslipLine", "Progressives"]


@dataclass(frozen=True, slots=True)
class PayslipLine:
    """A line of the payslip: a voce, its quantity and its two columns.

    Attributes:
        voce: The provider's code of the voce when its mapping names the
            engine code, else the engine code.
        engine_code: The engine code of the voce.
        description: What the line pays or withholds.
        quantity: Quantity in :attr:`unit`, ``None`` for a statutory line
            (contributions, taxes) that has no pay item.
        unit: Unit of :attr:`quantity`, ``None`` with it.
        rate: Amount per unit, ``None`` when it has no quantity.
        earning: Amount in the competenze column, zero otherwise.
        deduction: Amount in the trattenute column, zero otherwise.
    """

    voce: str
    engine_code: str
    description: str
    quantity: Decimal | None
    unit: VoceUnit | None
    rate: Decimal | None
    earning: Decimal
    deduction: Decimal


@dataclass(frozen=True, slots=True)
class Progressives:
    """The progressivi a payslip prints, after the run.

    Attributes:
        tax_year: Tax year of the cash amounts, ``None`` before any payment.
        gross: Gross paid in the tax year.
        taxable: IRPEF taxable income of the tax year.
        inps_employee: Employee INPS contributions of the tax year.
        irpef: IRPEF withheld in the tax year.
        surtax: Regional and municipal surtax withheld in the tax year.
        inps_base: INPS base of the runs of this employment of the
            competence year of the run.
        tfr_accrued: TFR the runs of the competence year accrued with the
            employer, the run's own included; ``None`` for a year whose
            quotas an import left unknown.
        extra_months: Ratei maturati of each extra month by the end of the
            month of the run.
    """

    tax_year: int | None
    gross: Decimal
    taxable: Decimal
    inps_employee: Decimal
    irpef: Decimal
    surtax: Decimal
    inps_base: Decimal
    tfr_accrued: Decimal | None = None
    extra_months: tuple[ExtraMonthProgress, ...] = ()
