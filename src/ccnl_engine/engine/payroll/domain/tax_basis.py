"""Tax-basis types: AnnualizedAssumption and TaxPeriod."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


class AnnualizedAssumption(BaseModel):
    """Full-year fiscal assumption for annual estimate computations.

    Used by :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_annual` to indicate that all fiscal formulas (Art. 13
    work-income deduction, ulteriore detrazione, trattamento integrativo)
    are applied at 365/365, i.e. a full calendar year is assumed.

    Attributes:
        type: Discriminator literal ``"annualized"``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["annualized"] = "annualized"


class TaxPeriod(BaseModel):
    """Actual work-period data required for period payroll fiscal pro-rata.

    When provided, fiscal formulas are scaled by
    ``eligible_work_days / 365`` instead of assuming a full year.
    Required when calling
    :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_period_effects`.

    ``eligible_work_days`` counts calendar days in the **tax year** for
    which the worker is employed, not days in the pay period alone.  For
    a worker hired on 1 March, the correct value for the March payslip is
    ``(31 Dec - 1 Mar).days + 1 = 306``, not ``31``.

    Attributes:
        type: Discriminator literal ``"tax_period"``.
        start: First day of employment in the tax year (inclusive).
        end: Last day of employment in the tax year (inclusive).
        eligible_work_days: Calendar days in the tax year the worker is
            employed.  Must be ``>= 1`` and ``<= (end - start).days + 1``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["tax_period"] = "tax_period"
    start: date
    end: date
    eligible_work_days: int

    @model_validator(mode="after")
    def _check(self) -> TaxPeriod:
        if self.start > self.end:
            msg = f"TaxPeriod.start {self.start} is after end {self.end}"
            raise ValueError(msg)
        max_days = (self.end - self.start).days + 1
        if self.eligible_work_days < 1:
            msg = f"eligible_work_days must be >= 1, got {self.eligible_work_days}"
            raise ValueError(msg)
        if self.eligible_work_days > max_days:
            msg = (
                f"eligible_work_days {self.eligible_work_days} exceeds "
                f"period span {max_days} days ({self.start} to {self.end})"
            )
            raise ValueError(msg)
        return self
