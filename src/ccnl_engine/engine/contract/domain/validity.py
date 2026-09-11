"""Validity period and time series primitives."""

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.engine.primitives import validate_open_sequence
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance


class SalaryGapKind(StrEnum):
    """Reason a ValidityPeriod carries no numeric value.

    Use this instead of omitting a period or fabricating a placeholder value
    when salary data is absent for a known date range.

    * ``missing`` — data exists in the CCNL source document but has not been
      extracted yet.  The gap should be filled in a follow-up data update.
    * ``not_applicable`` — the level or rule did not exist / was not in force
      during this period (e.g. a level introduced mid-contract).  No future
      data update is expected.
    * ``unknown`` — no information is available about whether data exists.
      Treat as a data-quality flag requiring investigation.
    """

    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class SalaryGapError(ValueError):
    """Raised by :meth:`TimeSeries.value_at` when the active period is a gap.

    Subclasses :class:`ValueError` so that existing broad ``except ValueError``
    callers continue to work.  Callers that need to distinguish a gap from a
    truly absent series can catch ``SalaryGapError`` specifically.

    Attributes:
        gap_kind: The :class:`SalaryGapKind` declared on the active period.
    """

    def __init__(self, gap_kind: SalaryGapKind, day: date) -> None:
        """Initialise with the gap kind and the queried date.

        Args:
            gap_kind: The :class:`SalaryGapKind` on the active period.
            day: The date that was queried via :meth:`TimeSeries.value_at`.
        """
        self.gap_kind = gap_kind
        super().__init__(f"period at {day} is an explicit gap ({gap_kind.value})")


class ValidityPeriod(BaseModel):
    """A single time-bounded value within a TimeSeries.

    Exactly one of ``value`` or ``gap_kind`` must be supplied.  A period with
    ``gap_kind`` set is a *gap period*: it occupies a date range in the series
    but carries no numeric value.  Use gap periods instead of omitting a range
    or fabricating a placeholder — they document *why* the data is absent.

    ``provenance`` overrides the provenance inherited from the owning domain
    object when the value in this period came from a different source page or
    was extracted differently.  ``None`` means "inherit from the owner".
    Gap periods do not require ``provenance``.
    """

    model_config = ConfigDict(extra="forbid")

    valid_from: date
    valid_until: date | None
    value: Decimal | None = None
    gap_kind: SalaryGapKind | None = None
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_period(self) -> Self:
        if self.valid_until is not None and self.valid_until <= self.valid_from:
            msg = (
                f"valid_until ({self.valid_until}) must be strictly after "
                f"valid_from ({self.valid_from})"
            )
            raise ValueError(msg)
        has_value = self.value is not None
        has_gap = self.gap_kind is not None
        if has_value == has_gap:
            msg = (
                "ValidityPeriod requires exactly one of 'value' or 'gap_kind'; "
                f"got value={self.value!r}, gap_kind={self.gap_kind!r}"
            )
            raise ValueError(msg)
        return self

    @property
    def is_gap(self) -> bool:
        """True when this period carries no numeric value."""
        return self.gap_kind is not None


class TimeSeries(BaseModel):
    """Ordered, contiguous, open-ended sequence of ValidityPeriod objects."""

    model_config = ConfigDict(extra="forbid")

    periods: list[ValidityPeriod]

    @model_validator(mode="after")
    def _check_series(self) -> Self:
        validate_open_sequence(
            self.periods,
            lambda p: p.valid_from,
            lambda p: p.valid_until,
            "TimeSeries periods",
        )
        return self

    def period_at(self, day: date) -> "ValidityPeriod | None":
        """Return the ValidityPeriod active on day, or None if before series start.

        Returns:
            The active period, or ``None`` if *day* precedes the series start.
            The caller must inspect :attr:`ValidityPeriod.is_gap` when the
            result may be a gap period.
        """
        for period in self.periods:
            if period.valid_from <= day and (
                period.valid_until is None or day < period.valid_until
            ):
                return period
        return None

    def value_at(self, day: date) -> Decimal:
        """Return the value in effect on day.

        Returns:
            The Decimal value in effect on the given date.

        Raises:
            SalaryGapError: If the active period is an explicit gap period.
                Subclass of ``ValueError``; callers that only need to skip the
                date can catch ``ValueError`` generically.
            ValueError: If the date precedes the start of the series.
        """
        for period in self.periods:
            if period.valid_from <= day and (
                period.valid_until is None or day < period.valid_until
            ):
                if period.gap_kind is not None:
                    raise SalaryGapError(period.gap_kind, day)
                # XOR invariant: gap_kind is None iff value is not None.
                assert period.value is not None
                return period.value
        msg = f"no value for {day}: series starts on {self.periods[0].valid_from}"
        raise ValueError(msg)
