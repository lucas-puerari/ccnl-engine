"""Domain types for period and year payroll computation."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.engine.payroll.domain.payroll_state import PayrollState
    from ccnl_engine.engine.payroll.domain.scenario import (
        AnnualEstimateInput,
        PeriodPayrollInput,
    )

_ZERO = Decimal(0)
_MONTHS_PER_YEAR = 12


@dataclass(frozen=True)
class PeriodId:
    """Identifies a single payroll period by calendar year and month.

    Use this instead of relying on ``structural.employment.as_of`` to
    identify the competence period.  Both :class:`PeriodPayrollRequest`
    and :class:`PeriodPayrollResult` carry a ``period_id`` so consumers can
    match requests to results without parsing dates.

    Attributes:
        year: Calendar year (e.g. ``2026``).
        month: Month of competence, 1-12.
    """

    year: int
    month: int

    def __post_init__(self) -> None:
        """Validate year and month ranges.

        Raises:
            ValueError: When ``month`` is outside 1-12 or ``year`` is zero.
        """
        if not (1 <= self.month <= 12):
            msg = f"month must be 1-12, got {self.month}"
            raise ValueError(msg)
        if self.year <= 0:
            msg = f"year must be positive, got {self.year}"
            raise ValueError(msg)


@dataclass(frozen=True)
class PeriodPayrollRequest:
    """Input for a single payroll period with YTD opening state.

    Combines the structural annual scenario with period-specific events and
    the year-to-date progressive state accumulated from prior closed periods.
    Pass :meth:`~PayrollState.zero` as ``opening_state`` for January.

    Attributes:
        structural: Structural annual scenario (worker, employment, contract).
        period: Period-specific events (overtime, absences, sick leave, etc.).
        opening_state: YTD progressive state entering this period. Pass
            :meth:`~PayrollState.zero` for the first period of the year.
        period_id: Explicit competence period.  When ``None``, the period is
            inferred from ``structural.employment.as_of``; a
            :class:`DeprecationWarning` is emitted by the service at call
            time.  Set this field to silence the warning.
        payment_date: Intended payment date.  When ``None`` and
            ``period_id`` is set, defaults to the last day of the competence
            month.  No default is derived when both are ``None``.
        idempotency_key: Optional caller-supplied key to prevent duplicate
            period closures.  The engine records but does not enforce
            uniqueness; enforcement is the caller's responsibility.
    """

    structural: AnnualEstimateInput
    period: PeriodPayrollInput
    opening_state: PayrollState
    period_id: PeriodId | None = None
    payment_date: date | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True)
class PeriodPayrollResult:
    """Result of a single payroll period computation.

    Captures the opening and closing YTD states alongside the key period
    figures (gross, net, employer cost) and the full ledger for the period.
    The closing state may be passed as the opening state of the next period.

    Attributes:
        opening_state: YTD state at the start of this period (passed in).
        closing_state: YTD state after closing this period. Feed this into
            the next :class:`PeriodPayrollRequest` as ``opening_state``.
        period_gross: Gross earnings for this period only.
        period_net: Net pay for this period only.
        period_employer_cost: Total employer cost for this period only.
        ledger_entries: All ledger entries posted for this period.
        period_id: The competence period that was closed.  ``None`` when the
            result was produced from a request without an explicit
            ``period_id``.
    """

    opening_state: PayrollState
    closing_state: PayrollState
    period_gross: Decimal
    period_net: Decimal
    period_employer_cost: Decimal
    ledger_entries: tuple[LedgerEntry, ...] = field(default_factory=tuple)
    period_id: PeriodId | None = None


@dataclass(frozen=True)
class PayrollYearRequest:
    """Input for a full-year payroll computation orchestrated by period.

    Chains twelve :class:`PeriodPayrollRequest` calls using
    :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.compute_period_payroll`, threading the closing YTD state of each period
    into the next.  The structural scenario's ``as_of`` date is overridden
    per month.

    Attributes:
        structural: Structural annual scenario (worker, employment, contract).
        year: Calendar year to compute (e.g. ``2026``).
        month_periods: Exactly twelve :class:`PeriodPayrollInput` instances,
            one per month in calendar order (index 0 = January).  When
            omitted, every month uses a default :class:`PeriodPayrollInput`.
        opening_state: YTD state at the start of January. Pass
            :meth:`~PayrollState.zero` (or omit) to start a fresh year.
    """

    structural: AnnualEstimateInput
    year: int
    month_periods: tuple[PeriodPayrollInput, ...]
    opening_state: PayrollState

    def __post_init__(self) -> None:
        """Validate that month_periods contains exactly 12 entries.

        Raises:
            ValueError: When ``month_periods`` does not have exactly 12 items.
        """
        if len(self.month_periods) != _MONTHS_PER_YEAR:
            msg = (
                f"month_periods must have exactly {_MONTHS_PER_YEAR} entries, "
                f"got {len(self.month_periods)}"
            )
            raise ValueError(msg)


@dataclass(frozen=True)
class PayrollYearResult:
    """Result of a full-year payroll computation.

    Contains one :class:`PeriodPayrollResult` per month in calendar order.
    The :attr:`closing_state` is the YTD state after December and can be
    passed as the ``opening_state`` of the next year's
    :class:`PayrollYearRequest`.

    Attributes:
        periods: Twelve period results, one per month (index 0 = January).
        closing_state: Final YTD state after December; equals
            ``periods[-1].closing_state``.
    """

    periods: tuple[PeriodPayrollResult, ...]
    closing_state: PayrollState


@dataclass(frozen=True)
class AnnualPayrollSummary:
    """Annual payroll summary derived from aggregating period results.

    Produced by :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.summarize_payroll_year`.  All monetary totals are the sum of the
    corresponding per-period figures.  The :attr:`closing_state` is the
    final YTD progressive state after December and mirrors
    :attr:`PayrollYearResult.closing_state`.

    Attributes:
        total_gross: Sum of :attr:`PeriodPayrollResult.period_gross`
            across all twelve periods.
        total_net: Sum of :attr:`PeriodPayrollResult.period_net`
            across all twelve periods.
        total_employer_cost: Sum of
            :attr:`PeriodPayrollResult.period_employer_cost` across all
            twelve periods.
        closing_state: Final YTD state after December.
        ledger_entries: All ledger entries from every period, concatenated
            in calendar order (January first, December last).
    """

    total_gross: Decimal
    total_net: Decimal
    total_employer_cost: Decimal
    closing_state: PayrollState
    ledger_entries: tuple[LedgerEntry, ...]
