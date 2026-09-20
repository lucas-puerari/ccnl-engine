"""Structural annual payroll input: AnnualEstimateInput."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.bilateral_funds import BilateralFundInput
from ccnl_engine.engine.payroll.domain.employee import Employee
from ccnl_engine.engine.payroll.domain.employment import Employment
from ccnl_engine.engine.payroll.domain.family import FamilyComposition


class AnnualEstimateInput(BaseModel):
    """Structural payroll scenario without period-specific events.

    Use :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_annual` to compute annual gross-to-net figures, or
    :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_period_effects` together with a :class:`~ccnl_engine.engine\
.payroll.domain.period_input.PeriodPayrollInput` to include
    the month's variable events in the result fields.

    Compared to the legacy :class:`~ccnl_engine.engine.payroll.domain\
.scenario.PayrollScenario`, this class holds only
    the structural fields that describe *who the worker is* and *what the
    employment relationship is*.  Period-specific events (overtime, absences,
    sick leave, fringe benefits, bonuses) live in
    :class:`~ccnl_engine.engine.payroll.domain.period_input.PeriodPayrollInput`.

    Attributes:
        employee: Worker-side inputs.
        employment: Employment relationship inputs.
        family: Optional family composition for Art. 12 TUIR deductions.
        art15_deductions: Optional Art. 15 TUIR oneri detraibili.
        bilateral_funds: Bilateral fund contributions (fondi bilaterali).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    employee: Employee
    employment: Employment
    family: FamilyComposition | None = None
    art15_deductions: Art15Deductions | None = None
    bilateral_funds: tuple[BilateralFundInput, ...] = ()
