"""Year-to-date progressive state for period payroll computation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

_ZERO = Decimal(0)


@dataclass(frozen=True)
class PayrollState:
    """All YTD progressives needed to compute a payroll period.

    Fields represent cumulative amounts from January 1 through the end of
    the most recently closed period.  The opening state for January is a
    zero-valued instance (see :meth:`zero`).

    Gross earnings
    --------------
    gross_annual_ytd
        Sum of all gross earnings (base salary, seniority, allowances,
        supplements, bonuses, fringe benefit taxable) posted to the ledger
        through the last closed period.

    Contributions
    -------------
    inps_employee_annual_ytd
        Employee INPS contributions withheld YTD.
    inps_employer_annual_ytd
        Employer INPS contributions accrued YTD.
    inail_employer_annual_ytd
        Employer INAIL contributions accrued YTD.

    Taxable income and IRPEF
    ------------------------
    taxable_income_ytd
        Imponibile fiscale (taxable base) accrued YTD.
    irpef_gross_ytd
        IRPEF lorda (before deductions) accrued YTD.
    irpef_withheld_ytd
        Net IRPEF actually withheld YTD (after all deductions and credits).

    Deductions and credits
    ----------------------
    work_income_deduction_ytd
        Detrazione per redditi da lavoro dipendente used YTD.
    fam_deductions_ytd
        Family deductions (spouse, children, dependants) used YTD.
    art15_deductions_ytd
        Art. 15 TUIR additional deductions used YTD.
    trattamento_integrativo_ytd
        Trattamento integrativo (tax credit) accrued YTD.

    Surtaxes
    --------
    addizionale_regionale_ytd
        Regional surtax withheld YTD.
    addizionale_comunale_ytd
        Municipal surtax withheld YTD (including advance payments).

    TFR
    ---
    tfr_annual_ytd
        TFR quota accrued YTD.

    Leave (ferie)
    -------------
    leave_accrued_days_ytd
        Leave days accrued YTD.
    leave_taken_days_ytd
        Leave days taken YTD.
    leave_balance_days
        Current leave balance (accrued minus taken YTD).

    Sickness (malattia)
    -------------------
    sick_days_ytd
        Calendar days of sickness absence YTD.
    """

    gross_annual_ytd: Decimal
    inps_employee_annual_ytd: Decimal
    inps_employer_annual_ytd: Decimal
    inail_employer_annual_ytd: Decimal
    taxable_income_ytd: Decimal
    irpef_gross_ytd: Decimal
    irpef_withheld_ytd: Decimal
    work_income_deduction_ytd: Decimal
    fam_deductions_ytd: Decimal
    art15_deductions_ytd: Decimal
    trattamento_integrativo_ytd: Decimal
    addizionale_regionale_ytd: Decimal
    addizionale_comunale_ytd: Decimal
    tfr_annual_ytd: Decimal
    leave_accrued_days_ytd: Decimal
    leave_taken_days_ytd: Decimal
    leave_balance_days: Decimal
    sick_days_ytd: Decimal

    @classmethod
    def zero(cls) -> PayrollState:
        """Return the opening state for January (all progressives at zero).

        Returns:
            A :class:`PayrollState` with every field set to zero.
        """
        return cls(
            gross_annual_ytd=_ZERO,
            inps_employee_annual_ytd=_ZERO,
            inps_employer_annual_ytd=_ZERO,
            inail_employer_annual_ytd=_ZERO,
            taxable_income_ytd=_ZERO,
            irpef_gross_ytd=_ZERO,
            irpef_withheld_ytd=_ZERO,
            work_income_deduction_ytd=_ZERO,
            fam_deductions_ytd=_ZERO,
            art15_deductions_ytd=_ZERO,
            trattamento_integrativo_ytd=_ZERO,
            addizionale_regionale_ytd=_ZERO,
            addizionale_comunale_ytd=_ZERO,
            tfr_annual_ytd=_ZERO,
            leave_accrued_days_ytd=_ZERO,
            leave_taken_days_ytd=_ZERO,
            leave_balance_days=_ZERO,
            sick_days_ytd=_ZERO,
        )
