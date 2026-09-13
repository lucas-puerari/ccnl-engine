"""Domain models for scenario-level bilateral fund contributions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

_ZERO: Decimal = Decimal(0)


@dataclass(frozen=True)
class FlatMonthlyFund:
    """Fixed monthly bilateral fund contribution.

    Both employee and employer amounts are fixed monthly figures, annualised
    by multiplying by 12 regardless of the number of additional salary months.

    Attributes:
        employee_monthly: Monthly employee contribution. Must be >= 0.
        employer_monthly: Monthly employer contribution. Must be >= 0.
    """

    employee_monthly: Decimal
    employer_monthly: Decimal

    def __post_init__(self) -> None:
        """Validate that monthly amounts are non-negative.

        Raises:
            ValueError: If any amount is negative.
        """
        if self.employee_monthly < _ZERO:
            msg = f"employee_monthly must be >= 0, got {self.employee_monthly}"
            raise ValueError(msg)
        if self.employer_monthly < _ZERO:
            msg = f"employer_monthly must be >= 0, got {self.employer_monthly}"
            raise ValueError(msg)


@dataclass(frozen=True)
class RateFund:
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

    employee_rate: Decimal
    employer_rate: Decimal
    base: Literal["tfr_base", "gross_annual"]

    def __post_init__(self) -> None:
        """Validate that rates are non-negative.

        Raises:
            ValueError: If any rate is negative.
        """
        if self.employee_rate < _ZERO:
            msg = f"employee_rate must be >= 0, got {self.employee_rate}"
            raise ValueError(msg)
        if self.employer_rate < _ZERO:
            msg = f"employer_rate must be >= 0, got {self.employer_rate}"
            raise ValueError(msg)


#: Union type for any bilateral fund contribution input.
BilateralFundInput = FlatMonthlyFund | RateFund
