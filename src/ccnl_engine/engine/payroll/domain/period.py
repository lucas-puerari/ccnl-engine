"""PayrollPeriod — month-of-competence descriptor for payroll computation."""

from __future__ import annotations

import dataclasses
from decimal import Decimal
from typing import Literal

from ccnl_engine.engine.payroll.domain.scenario import PeriodPayrollInput

_ZERO = Decimal(0)


@dataclasses.dataclass(frozen=True)
class YTDState:
    """Year-to-date progressive totals accumulated from prior closed periods.

    Carries the cumulative fiscal and contributive figures that have already
    been computed for earlier months in the same tax year.  Pass these into
    :class:`PayrollPeriod` so that :func:`~ccnl_engine.compute_period` and
    :func:`~ccnl_engine.compute_year` can produce deterministic, reproducible
    results independent of call order.

    Attributes:
        taxable_income: Cumulative IRPEF taxable income from prior periods.
        irpef_withheld: Cumulative IRPEF net withheld from prior periods.
        inps_employee: Cumulative employee INPS contributions from prior
            periods.
    """

    taxable_income: Decimal = _ZERO
    irpef_withheld: Decimal = _ZERO
    inps_employee: Decimal = _ZERO


@dataclasses.dataclass(frozen=True)
class PayrollPeriod:
    """A month-of-competence descriptor for a payroll computation.

    Groups the calendar month, period-specific payroll events, and the
    year-to-date progressive state accumulated from prior periods into a
    single immutable value.

    Pass to :func:`~ccnl_engine.compute_period` for a deterministic
    single-period calculation.  Build a sequence of twelve and pass to
    :func:`~ccnl_engine.compute_year` to aggregate a full payroll year.

    Attributes:
        year: Calendar year of competence (e.g. ``2026``).
        month: Month of competence, 1-12.
        events: Period-specific variable events (overtime, absences, bonuses).
            Defaults to a standard month with no special events.
        ytd: Year-to-date progressive totals from prior closed periods.
            Defaults to zero (i.e. January is the first period).
        status: ``"open"`` while the period is still editable;
            ``"closed"`` once it has been definitively processed.
    """

    year: int
    month: int
    events: PeriodPayrollInput = dataclasses.field(default_factory=PeriodPayrollInput)
    ytd: YTDState = dataclasses.field(default_factory=YTDState)
    status: Literal["open", "closed"] = "open"
