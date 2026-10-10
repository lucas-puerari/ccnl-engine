"""Coverage notes and work-rules container models."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.contract.absence.models import AbsenceRules
from ccnl_engine.contract.identity.types import NoteKind
from ccnl_engine.contract.sickness.models import SicknessRules
from ccnl_engine.contract.working_time.models import LeaveRules, TimeSupplements
from ccnl_engine.knowledge.limitation.models import (
    ModelLimitation,
    MonetaryImpact,
    NoteLimitation,
)


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
