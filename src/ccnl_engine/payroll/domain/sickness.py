"""SicknessCase domain model: one sick-leave episode for a payroll period."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.shared.domain.errors import InvalidInputError, OutOfScopeError
from ccnl_engine.shared.domain.validation import (
    require_date,
    require_decimal,
    require_int,
)

if TYPE_CHECKING:
    from datetime import date

_ZERO = Decimal(0)
_ONE = Decimal(1)
_FEATURE = "sickness"


@dataclass(frozen=True)
class SicknessCase:
    """Full sick-leave episode entering a single period-first payroll calculation.

    The caller supplies the episode interval and per-day rates; the engine
    derives absence deduction, INPS indemnity, and employer integration.

    Attributes:
        episode_start: First calendar day of the sickness episode.
            Used to document the episode; may precede the competence period
            when the illness started in a prior month.
        episode_end: Last calendar day of the sickness episode.
            May fall in a later month for multi-period episodes.
        working_days: Working days within this competence period that are
            affected by the sick leave.  Must be >= 1.
        waiting_period_days: Carenza (waiting period) days at the start of
            the episode.  Must be >= 0 and <= working_days.  Days with
            carenza receive employer integration only at
            ``carenza_integration_rate``, not the INPS indemnity path.
        gross_daily: Gross daily reference salary in EUR.  The absence
            deduction equals ``gross_daily * working_days``.
        inps_daily_rate: INPS indemnity rate applied on indemnifiable days
            (after carenza).  Between 0 and 1 inclusive.  Use ``0`` when
            INPS does not cover this episode (e.g. domestic workers).
        integration_rate: Target fraction of ``gross_daily`` the worker should
            receive during INPS-covered days (CCNL integration rate).  Must
            be between 0 and 1 inclusive.  The employer pays the difference
            above the INPS indemnity.
        carenza_integration_rate: Fraction of ``gross_daily`` the employer
            covers during carenza days.  Between 0 and 1 inclusive.
            Defaults to 0 (no employer coverage during carenza).
        cumulative_sick_days_ytd: Total sick days accumulated in prior
            periods this tax year.  When > 0, tier-based integration is
            required; the engine raises :class:`OutOfScopeError` for this
            case (seniority/tier tracking not yet implemented).
    """

    episode_start: date
    episode_end: date
    working_days: int
    waiting_period_days: int
    gross_daily: Decimal
    inps_daily_rate: Decimal
    integration_rate: Decimal
    carenza_integration_rate: Decimal = _ZERO
    cumulative_sick_days_ytd: int = 0

    def __post_init__(self) -> None:  # noqa: D105
        self._check_days()
        require_decimal(
            self.gross_daily,
            "SicknessCase.gross_daily",
            feature=_FEATURE,
            minimum=_ZERO,
        )
        for name in ("inps_daily_rate", "integration_rate", "carenza_integration_rate"):
            require_decimal(
                getattr(self, name),
                f"SicknessCase.{name}",
                feature=_FEATURE,
                minimum=_ZERO,
                maximum=_ONE,
            )
        self._check_cumulative_days()

    def _check_days(self) -> None:
        """Validate the episode dates, working days and carenza days.

        Raises:
            InvalidInputError: When the episode ends before it starts, or the
                day counts are out of range.
        """
        require_date(self.episode_start, "SicknessCase.episode_start", feature=_FEATURE)
        require_date(self.episode_end, "SicknessCase.episode_end", feature=_FEATURE)
        require_int(
            self.working_days, "SicknessCase.working_days", feature=_FEATURE, minimum=1
        )
        require_int(
            self.waiting_period_days,
            "SicknessCase.waiting_period_days",
            feature=_FEATURE,
            minimum=0,
        )
        if self.episode_end < self.episode_start:
            msg = (
                f"SicknessCase.episode_end ({self.episode_end}) must not precede "
                f"episode_start ({self.episode_start})"
            )
            raise InvalidInputError(
                msg, field="SicknessCase.episode_end", feature=_FEATURE
            )
        if self.waiting_period_days > self.working_days:
            msg = (
                f"SicknessCase.waiting_period_days ({self.waiting_period_days}) "
                f"must not exceed working_days ({self.working_days})"
            )
            raise InvalidInputError(
                msg, field="SicknessCase.waiting_period_days", feature=_FEATURE
            )

    def _check_cumulative_days(self) -> None:
        """Validate the sick days of earlier periods; tiers are out of scope.

        Raises:
            OutOfScopeError: When it is positive.
        """
        require_int(
            self.cumulative_sick_days_ytd,
            "SicknessCase.cumulative_sick_days_ytd",
            feature=_FEATURE,
            minimum=0,
        )
        if self.cumulative_sick_days_ytd > 0:
            msg = (
                "Tier-based sickness integration (cumulative_sick_days_ytd > 0) "
                "is not yet implemented; compute the integration_rate from the "
                "applicable CCNL tier and pass cumulative_sick_days_ytd=0."
            )
            raise OutOfScopeError(
                msg,
                feature="sickness",
                reason="cumulative_tiers_not_implemented",
                remediation=(
                    "Pass the applicable integration_rate directly and set "
                    "cumulative_sick_days_ytd=0."
                ),
            )

    @property
    def spans_multiple_months(self) -> bool:
        """True when the episode crosses a calendar-month boundary.

        Returns:
            Whether ``episode_start`` and ``episode_end`` fall in different
            months (possibly different years).
        """
        return (
            self.episode_start.year != self.episode_end.year
            or self.episode_start.month != self.episode_end.month
        )

    @property
    def indemnifiable_days(self) -> int:
        """Working days covered by INPS indemnity (after carenza).

        Returns:
            ``max(0, working_days - waiting_period_days)``.
        """
        return max(0, self.working_days - self.waiting_period_days)
