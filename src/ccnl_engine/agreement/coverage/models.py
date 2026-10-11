"""Coverage of a CCNL: coverage notes, work rules and rule series in time.

A run reads the base salary of its level on the competence date, then the
other series of the level and of the CCNL on the same date.  Each of them
must therefore cover the dates of the pay table it applies to: from the
first base salary value of the level (of any level, for a CCNL-wide
series).  A range the bundle has no value for is declared with a gap
period (:class:`~ccnl_engine.agreement.validity.rules.SalaryGapKind`),
never left out.

The hourly divisor is not required: a run reads it only for a domestic
CCNL, and the bundle invariants already forbid a gap in it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.absence.models import AbsenceRules
from ccnl_engine.agreement.types import NoteKind
from ccnl_engine.contract.sickness.models import SicknessRules
from ccnl_engine.knowledge.limitation.models import (
    ModelLimitation,
    MonetaryImpact,
    NoteLimitation,
)
from ccnl_engine.working_time.models import LeaveRules, TimeSupplements

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from datetime import date

    from ccnl_engine.agreement.validity.rules import TimeSeries
    from ccnl_engine.compensation.models import CCNLParameters, Level
    from ccnl_engine.seniority.models import SeniorityIncrements


class CoverageNote(BaseModel):
    """A structured note attached to a CCNL coverage block.

    ``capability`` names the capability of the registry the note limits for
    this CCNL.  A ``missing`` note documents data the engine supports but
    the file lacks, so it must name the capability it leaves partial; the
    capability coverage of the CCNL derives from it.

    A ``simplification`` note states its ``monetary_impact``.  When it can
    move an amount (``yes`` or ``unknown``) it must name its capability and
    declare the :class:`~ccnl_engine.knowledge.limitation.models.NoteLimitation`
    the engine records on the runs it concerns: no monetary simplification
    stays free text.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: NoteKind
    text: str
    capability: str | None = None
    monetary_impact: MonetaryImpact | None = None
    limitation: NoteLimitation | None = None

    @model_validator(mode="after")
    def _missing_names_capability(self) -> Self:
        if self.kind is NoteKind.MISSING and not self.capability:
            msg = "a 'missing' coverage note must name the capability it limits"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _simplification_is_typed(self) -> Self:
        simplification = self.kind is NoteKind.SIMPLIFICATION
        if simplification != (self.monetary_impact is not None):
            msg = "exactly the 'simplification' notes state a monetary_impact"
            raise ValueError(msg)
        if self.limitation is not None and not simplification:
            msg = "only a 'simplification' note declares a limitation"
            raise ValueError(msg)
        monetary = simplification and self.monetary_impact is not MonetaryImpact.NO
        if monetary and (self.limitation is None or not self.capability):
            msg = (
                "a simplification with monetary impact "
                f"{self.monetary_impact} must name its capability and "
                f"declare a limitation: {self.text[:60]!r}"
            )
            raise ValueError(msg)
        if self.limitation is not None and not self.capability:
            msg = "a note that declares a limitation must name its capability"
            raise ValueError(msg)
        return self

    def model_limitation(self, ccnl_id: str, source: str) -> ModelLimitation | None:
        """Return the limitation the note declares for the CCNL *ccnl_id*.

        Returns:
            The limitation, ``None`` when the note declares none.
        """
        spec = self.limitation
        if spec is None or self.capability is None or self.monetary_impact is None:
            return None
        return ModelLimitation(
            id=f"{ccnl_id}/{spec.variant}",
            capability=self.capability,
            variant=spec.variant,
            summary=self.text,
            monetary_impact=self.monetary_impact,
            status=spec.status,
            rulesets=(ccnl_id,),
            applies_when=spec.applies_when,
            source=source,
            remediation=spec.remediation,
        )


class CCNLWorkRules(BaseModel):
    """Container for work rules attached to a CCNL data file."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    time_supplements: TimeSupplements | None = None
    absence_rules: AbsenceRules | None = None
    leave_rules: LeaveRules | None = None
    sickness_rules: SicknessRules | None = None


class CCNLCoverage(BaseModel):
    """Notes on what the engine models for a CCNL data file.

    The coverage of each capability is not declared here: it derives from
    the capability registry of the fiscal year and from the ``missing``
    notes, which lower the capability they name to partial for this CCNL
    (``ccnl_engine.payroll.capability.services_coverage``).  For human-review
    confidence and traceability use :class:`CCNLVerification`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    notes: tuple[CoverageNote, ...]

    @model_validator(mode="after")
    def _unique_variants(self) -> Self:
        variants = [n.limitation.variant for n in self.notes if n.limitation]
        duplicates = sorted({v for v in variants if variants.count(v) > 1})
        if duplicates:
            msg = f"limitation variants declared twice: {duplicates}"
            raise ValueError(msg)
        return self


__all__ = ["assert_series_coverage", "required_series"]

#: A series a run reads: its location, the date it must cover from, itself.
type RequiredSeries = tuple[str, date, TimeSeries]


def _pay_table_start(level: Level) -> date | None:
    """Return the first date the base salary of ``level`` has a value.

    Returns:
        The start of its first period with a value, ``None`` without one.
    """
    periods = level.base_salary.periods
    return next((p.valid_from for p in periods if not p.is_gap), None)


def required_series(
    levels: Sequence[Level], parameters: CCNLParameters
) -> Iterator[RequiredSeries]:
    """Yield each series a run reads with the date it must cover from.

    Yields:
        The location of the series in the data file, the first date of the
        pay table it applies to, and the series.
    """
    starts = {level.code: _pay_table_start(level) for level in levels}
    known = [day for day in starts.values() if day is not None]
    if not known:
        return
    start = min(known)
    yield "parameters.additional_months", start, parameters.additional_months
    increments = parameters.seniority_increments
    prefix = "parameters.seniority_increments"
    if increments.apprentice_amount is not None:
        yield f"{prefix}.apprentice_amount", start, increments.apprentice_amount
    for level in levels:
        level_start = starts[level.code]
        if level_start is not None:
            yield from _level_series(level, level_start, increments)


def _level_series(
    level: Level, start: date, increments: SeniorityIncrements
) -> Iterator[RequiredSeries]:
    """Yield the allowance and seniority series of one level.

    Yields:
        Each series of the level with ``start``, the start of its pay table.
    """
    code, prefix = level.code, "parameters.seniority_increments"
    for allowance in level.fixed_allowances:
        path = f"levels[{code}].fixed_allowances[{allowance.code}].monthly"
        yield path, start, allowance.monthly
    if code in increments.amount_by_level:
        yield (
            f"{prefix}.amount_by_level[{code}]",
            start,
            increments.amount_by_level[code],
        )
    for category, amounts in increments.amount_by_level_by_category.items():
        if code in amounts:
            path = f"{prefix}.amount_by_level_by_category[{category}][{code}]"
            yield path, start, amounts[code]
    for i, tier in enumerate(increments.tiers):
        if code in tier.amount_by_level:
            path = f"{prefix}.tiers[{i}].amount_by_level[{code}]"
            yield path, start, tier.amount_by_level[code]


def assert_series_coverage(levels: Sequence[Level], parameters: CCNLParameters) -> None:
    """Reject a series a run reads that starts after its pay table.

    Raises:
        ValueError: If a required series starts after the date it must
            cover from.
    """
    for path, start, series in required_series(levels, parameters):
        first = series.periods[0].valid_from
        if first > start:
            msg = (
                f"{path} starts on {first}, after the pay table it applies to "
                f"({start}): declare the period from {start} with a gap_kind"
            )
            raise ValueError(msg)
