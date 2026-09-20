"""IVS ceiling warning logic for payroll coverage evaluation."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, assert_never

from ccnl_engine.engine.payroll.domain.employee import (
    SeniorityByCount,
    SeniorityByDate,
    SeniorityByMonths,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
    from ccnl_engine.engine.payroll.domain.annual_input import AnnualEstimateInput

_IVS_CEILING_THRESHOLD = date(1996, 1, 1)


def _ivs_date_msg(hire_date: date) -> str | None:
    """Warning when an explicit hire date is on or after the IVS threshold.

    Returns:
        Warning string, or ``None`` when hire date is before the threshold.
    """
    if hire_date < _IVS_CEILING_THRESHOLD:
        return None
    return (
        f"hire date {hire_date} is on or after "
        f"{_IVS_CEILING_THRESHOLD}: contributions are overstated; "
        "consider setting ivs_ceiling_applies=True"
    )


def _ivs_months_msg(months: int, as_of: date) -> str | None:
    """Warning when implied hire date (from months of service) is post-threshold.

    Returns:
        Warning string, or ``None`` when the implied hire predates the threshold.
    """
    months_since_threshold = (as_of.year - _IVS_CEILING_THRESHOLD.year) * 12 + (
        as_of.month - _IVS_CEILING_THRESHOLD.month
    )
    if months > months_since_threshold:
        return None  # implied hire date is before the threshold
    return (
        f"seniority of {months} months implies hire on or after "
        f"{_IVS_CEILING_THRESHOLD}: contributions are overstated; "
        "consider setting ivs_ceiling_applies=True"
    )


def _ivs_ceiling_warning(
    scenario: _InternalScenario | AnnualEstimateInput,
    as_of: date,
    contribution_base: Decimal,
    ivs_ceiling: Decimal | None,
) -> str | None:
    """Return a warning when a post-1996 hire has ivs_ceiling_applies=False.

    Workers hired on or after 1996-01-01 are subject to the INPS IVS
    contribution ceiling.  When the ceiling is skipped, the engine uses a
    higher contribution base, so computed contributions are overstated.

    When ``ivs_ceiling`` is known and the contribution base does not exceed
    it, the ceiling would have no effect, so no warning is emitted.

    Covers all three seniority input types:

    - ``SeniorityByDate``: compare the explicit hire date to the threshold.
    - ``SeniorityByMonths``: derive an implied hire date from *as_of* and
      the stored months count; warn when the implied date is on or after
      the threshold.
    - ``SeniorityByCount``: hire date is unknowable; always warn so the
      caller can make an explicit choice.

    Returns:
        A warning string, or ``None`` when no warning is warranted.
    """
    if scenario.employee.ivs_ceiling_applies:
        return None
    if ivs_ceiling is not None and contribution_base <= ivs_ceiling:
        return None
    seniority = scenario.employee.seniority
    if seniority is None:
        return (
            (
                "seniority is None: IVS ceiling applicability cannot be "
                "determined; if the worker was hired on or after "
                f"{_IVS_CEILING_THRESHOLD}, contributions are overstated. "
                "Set ivs_ceiling_applies=True to apply the IVS ceiling."
            )
            if ivs_ceiling is not None
            else None
        )
    if isinstance(seniority, SeniorityByDate):
        return _ivs_date_msg(seniority.value)
    if isinstance(seniority, SeniorityByMonths):
        return _ivs_months_msg(seniority.value, as_of)
    if isinstance(seniority, SeniorityByCount):
        return (
            "SeniorityByCount used without ivs_ceiling_applies: "
            f"if hired on or after {_IVS_CEILING_THRESHOLD}, "
            "contributions are overstated; "
            "consider setting ivs_ceiling_applies=True"
        )
    assert_never(seniority)  # pragma: no cover
