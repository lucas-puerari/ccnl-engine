"""PeriodPayroll — annual estimate enriched with period-specific L3 event amounts."""

from __future__ import annotations

import dataclasses
import json
import typing
from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.annual_result import (
    AnnualEstimate,
    _decode_field,
)
from ccnl_engine.engine.payroll.domain.components import _has_default

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.scenario import PeriodPayrollInput

_ZERO = Decimal(0)


@dataclass(frozen=True, kw_only=True)
class PeriodPayroll(AnnualEstimate):
    """Period-specific payroll: annual estimate enriched with L3 event amounts.

    Extends :class:`AnnualEstimate` with the period-specific inputs and
    informational breakdown fields.  The L3 amounts (absence deductions,
    overtime supplements, sick-pay indemnities, fringe benefits, etc.) do
    **not** flow into ``net_annual`` or ``employer_cost`` in this version —
    those remain annualised structural estimates.

    Attributes:
        pay_period: The period-specific events that were merged into the
            structural scenario.
        base_monthly_full_time: Full-time equivalent base monthly pay before
            part-time scaling.
        overtime_supplement_monthly: Estimated monthly overtime supplement.
        night_supplement_monthly: Estimated monthly night-shift supplement.
        holiday_supplement_monthly: Estimated monthly holiday supplement.
        time_supplements_monthly: Sum of all time-based supplements.
        time_supplements_annual_projection: Annualised projection of
            ``time_supplements_monthly``.
        absence_deduction_monthly: Pay reduction for unpaid absence days.
        effective_gross_monthly: Gross monthly adjusted for absence deduction.
        leave_accrued_days_monthly: Leave days accrued in this period.
        leave_taken_days_monthly: Leave days consumed in this period.
        leave_balance_days: Remaining leave balance after this period.
        sick_days_monthly: Total sick-leave days in this period.
        sick_carenza_days_monthly: Unpaid waiting-period sick days.
        sick_inps_indemnity_monthly: INPS sick-pay indemnity for this period.
        sick_company_integration_monthly: Employer top-up on INPS indemnity.
        fringe_benefit_annual: Total fringe-benefit amount (informational).
        fringe_benefit_threshold_annual: Applicable tax-free threshold.
        fringe_benefit_taxable_annual: Taxable fringe-benefit amount.
        welfare_annual: Welfare contribution amount (tax-exempt).
        bonus_annual: Total bonus / PdR amount (informational).
        bonus_pdr_flat_tax_annual: PdR flat-tax amount.
        bonus_ordinary_taxable_annual: Ordinary taxable bonus portion.
    """

    pay_period: PeriodPayrollInput

    base_monthly_full_time: Decimal = field(default=_ZERO)
    overtime_supplement_monthly: Decimal = field(default=_ZERO)
    night_supplement_monthly: Decimal = field(default=_ZERO)
    holiday_supplement_monthly: Decimal = field(default=_ZERO)
    time_supplements_monthly: Decimal = field(default=_ZERO)
    time_supplements_annual_projection: Decimal = field(default=_ZERO)
    absence_deduction_monthly: Decimal = field(default=_ZERO)
    effective_gross_monthly: Decimal = field(default=_ZERO)
    leave_accrued_days_monthly: Decimal = field(default=_ZERO)
    leave_taken_days_monthly: Decimal = field(default=_ZERO)
    leave_balance_days: Decimal = field(default=_ZERO)
    sick_days_monthly: Decimal = field(default=_ZERO)
    sick_carenza_days_monthly: Decimal = field(default=_ZERO)
    sick_inps_indemnity_monthly: Decimal = field(default=_ZERO)
    sick_company_integration_monthly: Decimal = field(default=_ZERO)
    fringe_benefit_annual: Decimal = field(default=_ZERO)
    fringe_benefit_threshold_annual: Decimal = field(default=_ZERO)
    fringe_benefit_taxable_annual: Decimal = field(default=_ZERO)
    welfare_annual: Decimal = field(default=_ZERO)
    bonus_annual: Decimal = field(default=_ZERO)
    bonus_pdr_flat_tax_annual: Decimal = field(default=_ZERO)
    bonus_ordinary_taxable_annual: Decimal = field(default=_ZERO)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> PeriodPayroll:
        """Reconstruct from a ``to_dict()`` dict.

        Args:
            data: A dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`PeriodPayroll` with all fields restored.

        Raises:
            TypeError: If *data* contains unexpected keys.
            ValueError: If a required field is absent from *data*.
        """
        from ccnl_engine.engine.payroll.domain.scenario import (  # noqa: PLC0415
            PeriodPayrollInput,
        )

        allowed = frozenset(f.name for f in dataclasses.fields(cls))
        extra = set(data) - allowed
        if extra:
            msg = f"PeriodPayroll.from_dict: unexpected keys: {sorted(extra)}"
            raise TypeError(msg)
        hints = typing.get_type_hints(
            cls, localns={"PeriodPayrollInput": PeriodPayrollInput}
        )
        extra_decoders: dict[str, object] = {
            "pay_period": PeriodPayrollInput.model_validate
        }
        kwargs: dict[str, object] = {}
        for f in dataclasses.fields(cls):
            if f.name not in data:
                if _has_default(f):
                    continue
                msg = f"Missing field: {f.name!r}"
                raise ValueError(msg) from None
            kwargs[f.name] = _decode_field(
                f.name, data[f.name], hints[f.name], extra_decoders
            )
        return cls(**kwargs)  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, raw: str) -> PeriodPayroll:
        """Reconstruct from a JSON string.

        Args:
            raw: A JSON string as returned by :meth:`to_json`.

        Returns:
            A new :class:`PeriodPayroll` equal to the original.
        """
        return cls.from_dict(json.loads(raw))
