"""FiscalYTD: accumulated fiscal amounts from closed periods in the tax year."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

_ZERO = Decimal(0)


@dataclass(frozen=True)
class FiscalYTD:
    """Fiscal year-to-date accumulators for period payroll chaining.

    Each field holds the cumulative fiscal amount from January 1 through
    the end of the most recently closed period.  Pass :meth:`zero` as the
    opening value for the first period of a tax year.

    Attributes:
        taxable_income_ytd: Imponibile fiscale accrued YTD.
        irpef_gross_ytd: IRPEF lorda (before deductions) accrued YTD.
        irpef_withheld_ytd: Net IRPEF actually withheld YTD (after credits).
        work_income_deduction_ytd: Detrazione per redditi di lavoro used YTD.
        fam_deductions_ytd: Family deductions (spouse, children) used YTD.
        art15_deductions_ytd: Art. 15 TUIR additional deductions used YTD.
        trattamento_integrativo_ytd: Tax credit (trattamento integrativo) YTD.
        addizionale_regionale_ytd: Regional surtax withheld YTD.
        addizionale_comunale_ytd: Municipal surtax withheld YTD.
    """

    taxable_income_ytd: Decimal
    irpef_gross_ytd: Decimal
    irpef_withheld_ytd: Decimal
    work_income_deduction_ytd: Decimal
    fam_deductions_ytd: Decimal
    art15_deductions_ytd: Decimal
    trattamento_integrativo_ytd: Decimal
    addizionale_regionale_ytd: Decimal
    addizionale_comunale_ytd: Decimal

    @classmethod
    def zero(cls) -> FiscalYTD:
        """Return the opening FiscalYTD for January (all accumulators at zero).

        Returns:
            A :class:`FiscalYTD` with every field set to zero.
        """
        return cls(
            taxable_income_ytd=_ZERO,
            irpef_gross_ytd=_ZERO,
            irpef_withheld_ytd=_ZERO,
            work_income_deduction_ytd=_ZERO,
            fam_deductions_ytd=_ZERO,
            art15_deductions_ytd=_ZERO,
            trattamento_integrativo_ytd=_ZERO,
            addizionale_regionale_ytd=_ZERO,
            addizionale_comunale_ytd=_ZERO,
        )
