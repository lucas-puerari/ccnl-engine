"""Coverage notes and work-rules container models."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.contract.domain.absence import AbsenceRules
from ccnl_engine.contract.domain.identity._enums import NoteKind
from ccnl_engine.contract.domain.sickness import SicknessRules
from ccnl_engine.contract.domain.working_time import LeaveRules, TimeSupplements


class CoverageNote(BaseModel):
    """A structured note attached to a CCNL coverage block.

    ``capability`` names the capability of the registry the note limits for
    this CCNL.  A ``missing`` note documents data the engine supports but
    the file lacks, so it must name the capability it leaves partial; the
    capability coverage of the CCNL derives from it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: NoteKind
    text: str
    capability: str | None = None

    @model_validator(mode="after")
    def _missing_names_capability(self) -> Self:
        if self.kind is NoteKind.MISSING and not self.capability:
            msg = "a 'missing' coverage note must name the capability it limits"
            raise ValueError(msg)
        return self


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
    (``ccnl_engine.payroll.service.capability_coverage``).  For human-review
    confidence and traceability use :class:`CCNLVerification`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    notes: tuple[CoverageNote, ...]
