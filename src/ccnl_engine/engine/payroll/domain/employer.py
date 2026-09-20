"""Employer domain type."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.contract.domain.ccnl import SupplementaryAllowance
from ccnl_engine.engine.primitives.domain.primitives import StrictDecimal

_ZERO: Decimal = Decimal(0)


class Employer(BaseModel):
    """Employer-side inputs for payroll computation.

    Attributes:
        num_employees: Employer headcount. Required — used to select the
            INPS contribution tier. Must be ``>= 1``.
        second_level_allowances: Allowances from a territorial or company
            second-level agreement (*contrattazione di secondo livello*).
            Each item is scaled by ``part_time_ratio``; whether the
            apprenticeship percentage also applies is controlled per-item
            by ``apprenticeship_pct_relevant``. Mutually exclusive with
            :attr:`~ccnl_engine.engine.payroll.domain.employee.Agreement\
.ral_override`.
        inail_rate: Caller-supplied INAIL tariff rate (e.g. ``Decimal("0.015")``
            for 1.5%). When set, the engine computes the INAIL employer
            contribution as ``gross_annual * inail_rate`` and adds it to
            ``employer_cost_annual``. Must be ``>= 0``. ``None`` means INAIL
            is not modelled (reported as ``not_computed`` in the scope).
            The INAIL massimale and minimale retributivi are not applied;
            the caller is responsible for providing the correct net rate.
        inps_employer_exemption_annual: Caller-declared annual INPS employer
            contribution exemption (e.g. Esonero contributivo, Decontribuzione
            Sud). When set, the engine subtracts this amount from
            ``employer_cost_annual``, capped at ``inps_employer_annual``
            (cannot exceed the contribution itself). Must be ``>= 0``.
            ``None`` means no exemption is applied.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    num_employees: int = Field(ge=1)
    second_level_allowances: tuple[SupplementaryAllowance, ...] = ()
    inail_rate: StrictDecimal | None = None
    inps_employer_exemption_annual: StrictDecimal | None = None

    @model_validator(mode="after")
    def _check_rates(self) -> Employer:
        if self.inail_rate is not None and self.inail_rate < _ZERO:
            msg = f"inail_rate must be >= 0, got {self.inail_rate}"
            raise ValueError(msg)
        if (
            self.inps_employer_exemption_annual is not None
            and self.inps_employer_exemption_annual < _ZERO
        ):
            msg = (
                "inps_employer_exemption_annual must be >= 0, "
                f"got {self.inps_employer_exemption_annual}"
            )
            raise ValueError(msg)
        return self
