"""Coverage, notes, and work-rules container models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.contract.domain.absence import AbsenceRules
from ccnl_engine.engine.contract.domain.identity._enums import (
    CoverageStatus,
    NoteKind,
    WorkRuleFeature,
)
from ccnl_engine.engine.contract.domain.sickness import SicknessRules
from ccnl_engine.engine.contract.domain.working_time import LeaveRules, TimeSupplements
from ccnl_engine.engine.primitives import FrozenDict


class CoverageNote(BaseModel):
    """A structured note attached to a CCNL coverage block.

    Replaces the legacy string-prefix convention (``SIMPLIFICATION: …``,
    ``MISSING: …``, etc.) with a typed ``kind`` field.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: NoteKind
    text: str


class CCNLWorkRules(BaseModel):
    """Container for work rules attached to a CCNL data file."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    time_supplements: TimeSupplements | None = None
    absence_rules: AbsenceRules | None = None
    leave_rules: LeaveRules | None = None
    sickness_rules: SicknessRules | None = None


class CCNLCoverage(BaseModel):
    """Declares implementation completeness for a CCNL data file.

    Measures *what* the engine implements, not how trustworthy the values are.
    For human-review confidence and traceability use :class:`CCNLVerification`.

    * **Coverage** (``gross`` / ``net`` / ``work_rules``): what the engine
      implements for this contract — ``implemented``, ``partial``, or
      ``out_of_scope``.

      - L1 — Gross: base salary, seniority, fixed allowances, additional
        months, hourly rate.
      - L2 — Net: INPS contributions, TFR, IRPEF, regional/municipal surtax.
      - Work rules — Extended: overtime, sick/injury leave, performance bonuses,
        welfare/benefits. Defaults to ``not_implemented``.

    ``work_rules`` is the scalar summary status (for backward compat with the
    coverage matrix). ``work_rules_features`` is the authoritative per-feature
    dict; it drives the computed work-rules rollup and the per-feature coverage
    table.

    A ``missing`` note documents data the engine supports but the file lacks,
    and is only allowed while at least one of gross / net is ``partial``
    or any work_rules feature is ``partial``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    gross: CoverageStatus
    net: CoverageStatus
    work_rules: CoverageStatus = CoverageStatus.NOT_IMPLEMENTED
    work_rules_features: Mapping[WorkRuleFeature, CoverageStatus] = Field(
        default_factory=dict
    )
    notes: tuple[CoverageNote, ...]

    @model_validator(mode="after")
    def _check_notes(self) -> Self:
        has_missing = any(n.kind == NoteKind.MISSING for n in self.notes)
        any_wr_partial = any(
            v == CoverageStatus.PARTIAL for v in self.work_rules_features.values()
        )
        if (
            has_missing
            and "partial" not in {self.gross, self.net}
            and not any_wr_partial
        ):
            msg = (
                "coverage has 'missing' notes but neither gross nor net "
                "is 'partial' and no work_rules feature is 'partial'"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _freeze_dicts(self) -> Self:
        object.__setattr__(  # noqa: PLC2801
            self,
            "work_rules_features",
            FrozenDict(self.work_rules_features),
        )
        return self
