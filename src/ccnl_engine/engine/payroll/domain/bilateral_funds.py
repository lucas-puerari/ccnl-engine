"""Domain models for scenario-level bilateral fund contributions."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.engine.primitives.domain.primitives import StrictDecimal

_ZERO: Decimal = Decimal(0)


class FlatMonthlyFund(BaseModel):
    """Fixed monthly bilateral fund contribution.

    Both employee and employer amounts are fixed monthly figures, annualised
    by multiplying by 12 regardless of the number of additional salary months.

    Attributes:
        employee_monthly: Monthly employee contribution. Must be >= 0.
        employer_monthly: Monthly employer contribution. Must be >= 0.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    employee_monthly: StrictDecimal
    employer_monthly: StrictDecimal

    @model_validator(mode="after")
    def _check_non_negative(self) -> FlatMonthlyFund:
        if self.employee_monthly < _ZERO:
            msg = f"employee_monthly must be >= 0, got {self.employee_monthly}"
            raise ValueError(msg)
        if self.employer_monthly < _ZERO:
            msg = f"employer_monthly must be >= 0, got {self.employer_monthly}"
            raise ValueError(msg)
        return self


class RateFund(BaseModel):
    """Rate-based bilateral fund contribution.

    Contributions are computed as a percentage of an annual base: either
    the TFR computation base (``tfr_base``) or the full annual gross
    (``gross_annual``).

    Attributes:
        employee_rate: Employee contribution rate (e.g. ``Decimal("0.005")``
            for 0.5 %). Must be >= 0.
        employer_rate: Employer contribution rate. Must be >= 0.
        base: The annual amount to which the rates are applied.
            ``"tfr_base"`` uses the TFR computation base (Art. 2120 c.c.);
            ``"gross_annual"`` uses the full annual gross.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    employee_rate: StrictDecimal
    employer_rate: StrictDecimal
    base: Literal["tfr_base", "gross_annual"]

    @model_validator(mode="after")
    def _check_non_negative(self) -> RateFund:
        if self.employee_rate < _ZERO:
            msg = f"employee_rate must be >= 0, got {self.employee_rate}"
            raise ValueError(msg)
        if self.employer_rate < _ZERO:
            msg = f"employer_rate must be >= 0, got {self.employer_rate}"
            raise ValueError(msg)
        return self


#: Union type for any bilateral fund contribution input.
BilateralFundInput = FlatMonthlyFund | RateFund
