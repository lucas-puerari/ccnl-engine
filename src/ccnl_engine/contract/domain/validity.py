"""Validity period and time series primitives."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.shared.domain.errors import MissingRuleError
from ccnl_engine.shared.domain.primitives import validate_open_sequence


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


class SeriesGapError(ValueError):
    """Raised by :meth:`TimeSeries.value_at` on a date the series has no value.

    The date precedes the first period, or falls in a gap period.  It stays
    a ``ValueError`` so that Pydantic validators reading a series keep
    working; a run translates it into
    :class:`~ccnl_engine.shared.domain.errors.MissingRuleError` with
    :func:`rule_scope`.

    Attributes:
        day: The date that was queried.
        gap_kind: Kind of the gap period, ``None`` before the series starts.
        resumes_on: First date with a value after ``day``, ``None`` when the
            gap is open-ended.
    """

    def __init__(
        self, day: date, gap_kind: SalaryGapKind | None, resumes_on: date | None
    ) -> None:
        """Initialise with the queried date, the gap kind and the next value."""
        self.day = day
        self.gap_kind = gap_kind
        self.resumes_on = resumes_on
        super().__init__(self.detail)

    @property
    def detail(self) -> str:
        """Why the series has no value on :attr:`day`."""
        if self.gap_kind is None:
            return f"the rule starts on {self.resumes_on}"
        until = "further notice" if self.resumes_on is None else self.resumes_on
        return f"the bundle declares a {self.gap_kind.value} gap until {until}"

    @property
    def remediation(self) -> str:
        """What the caller can do about the missing value."""
        if self.resumes_on is None:
            return "Update the knowledge bundle with the values of this period."
        return (
            f"Compute a period from {self.resumes_on}, or update the knowledge "
            "bundle with the values before that date."
        )

    def missing_rule(
        self, *, ruleset: str | None, feature: str | None
    ) -> MissingRuleError:
        """Return the public error of the gap for the rule of a run.

        Returns:
            A :class:`MissingRuleError` carrying the date, the gap kind, the
            ruleset, the feature and the remediation.
        """
        return MissingRuleError(
            self.detail,
            as_of=self.day,
            gap_kind=None if self.gap_kind is None else self.gap_kind.value,
            feature=feature,
            ruleset=ruleset,
            remediation=self.remediation,
        )


@contextmanager
def rule_scope(
    *, ruleset: str | None = None, feature: str | None = None
) -> Iterator[None]:
    """Raise a series gap met within as a :class:`MissingRuleError`.

    Scopes nest: an inner scope names the feature, an outer one the
    ruleset; a value already set by an inner scope is kept.

    Raises:
        MissingRuleError: When a :class:`SeriesGapError` or a
            ``MissingRuleError`` is raised within the scope.
    """
    try:
        yield
    except SeriesGapError as gap:
        raise gap.missing_rule(ruleset=ruleset, feature=feature) from gap
    except MissingRuleError as error:
        raise MissingRuleError(
            error.detail,
            as_of=error.as_of,
            gap_kind=error.gap_kind,
            feature=error.feature or feature,
            ruleset=error.ruleset or ruleset,
            remediation=error.remediation,
        ) from error


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

    model_config = ConfigDict(extra="forbid", frozen=True)

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

    model_config = ConfigDict(extra="forbid", frozen=True)

    periods: tuple[ValidityPeriod, ...]

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
            SeriesGapError: If the date precedes the series or falls in a gap
                period.
        """
        period = self.period_at(day)
        if period is None:
            raise SeriesGapError(day, None, self.periods[0].valid_from)
        if period.value is None:
            raise SeriesGapError(day, period.gap_kind, period.valid_until)
        return period.value

    def applies_on(self, day: date) -> bool:
        """Return whether the rule of the series is in force on day.

        Returns:
            ``False`` in a ``not_applicable`` gap period, ``True`` otherwise.
        """
        period = self.period_at(day)
        return period is None or period.gap_kind is not SalaryGapKind.NOT_APPLICABLE
