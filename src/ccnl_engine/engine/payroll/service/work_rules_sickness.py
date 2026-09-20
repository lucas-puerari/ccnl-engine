"""Sickness handler: INPS indemnity and company integration."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import OutOfScopeError
from ccnl_engine.engine.payroll.service.sickness import compute_sickness

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
    from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates

_ZERO = Decimal(0)


@dataclass(frozen=True)
class _SicknessResult:
    sick_days: Decimal
    carenza_days: Decimal
    inps_indemnity: Decimal
    company_integration: Decimal
    present: bool


def _run_wr_sickness(
    scenario: _InternalScenario,
    ccnl: CCNL,
    sick_pay_rates: InpsSickPayRates | None,
    gross_monthly: Decimal,
) -> _SicknessResult:
    """Run the work-rules sickness block.

    Returns:
        :class:`_SicknessResult` with zero amounts when sick input is absent
        or ``sick_days == 0``.

    Raises:
        OutOfScopeError: If sick_days > 0 but the CCNL has no sickness schema.
        RuntimeError: If ``work_rules`` or ``sickness_rules`` is ``None``
            despite ``present=True``, or if ``sick_pay_rates`` is ``None``
            when sickness computation is attempted (indicates a caller bug).
    """
    sick_input = scenario.sick_input
    present = ccnl.work_rules is not None and ccnl.work_rules.sickness_rules is not None
    if sick_input is None or sick_input.sick_days == _ZERO:
        return _SicknessResult(
            sick_days=_ZERO,
            carenza_days=_ZERO,
            inps_indemnity=_ZERO,
            company_integration=_ZERO,
            present=present,
        )
    if present:
        work_rules_sk = ccnl.work_rules
        if (  # pragma: no cover
            work_rules_sk is None or work_rules_sk.sickness_rules is None
        ):
            msg = "sickness_rules is None despite present=True"
            raise RuntimeError(msg)
        if sick_pay_rates is None:  # pragma: no cover
            msg = "sick_pay_rates is None despite sick_days > 0"
            raise RuntimeError(msg)
        sick_days, carenza, inps_indemnity, company_integration = compute_sickness(
            sick_input=sick_input,
            sickness_rules=work_rules_sk.sickness_rules,
            sick_pay_rates=sick_pay_rates,
            gross_monthly=gross_monthly,
        )
        return _SicknessResult(
            sick_days=sick_days,
            carenza_days=carenza,
            inps_indemnity=inps_indemnity,
            company_integration=company_integration,
            present=True,
        )
    msg = "sick_input requested but not modelled for this CCNL"
    raise OutOfScopeError(msg, feature="sickness", reason="no_schema")
