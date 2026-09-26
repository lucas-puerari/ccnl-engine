"""Extraction-trace models for the provenance chain.

An :class:`ExtractionTrace` records how a rule was turned into a domain-model
value and who verified it.  ``verified_by``/``verified_at`` stay ``None``
until a human curator reviews an extraction, mirroring the existing
``human_reviewed: false`` convention on CCNL data files.
"""

from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.domain.ruleset_identity import VerificationStatus
from ccnl_engine.shared.domain.primitives import FrozenDict


class ExtractionMethod(StrEnum):
    """How a rule was extracted into the domain model."""

    AI = "ai"
    MANUAL = "manual"
    BACK_CALCULATION = "back_calculation"
    IMPORT = "import"


class BackCalculationStep(BaseModel):
    """One step of a back-calculation used to derive a rule.

    E.g. reconstructing a conglobated seniority amount across seniority
    levels: the step records the formula inputs and the result.

    Attributes:
        description: What this step computes.
        inputs: Named formula inputs (the base and the derived amount).
            Read-only: the mapping is frozen after construction.
        result: The derived rule value.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    description: str
    inputs: Mapping[str, Decimal | str] = Field(default_factory=dict)
    result: Decimal

    @model_validator(mode="after")
    def _freeze_inputs(self) -> Self:
        object.__setattr__(self, "inputs", FrozenDict(self.inputs))  # noqa: PLC2801
        return self


class ExtractionTrace(BaseModel):
    """Metadata about how one rule was extracted and verified.

    Attributes:
        method: How the value was extracted (see :class:`ExtractionMethod`).
        model: AI/LLM model used for ``ai`` extractions.
        extraction_timestamp: When the extraction was performed.
        verified_by: Identifier of the human curator who reviewed the
            extraction; ``None`` until reviewed.
        verified_at: When the human curator approved it; ``None`` until then.
        verification_status: Confidence level (defaults to ``unverified``).
        effective_from: First date the extracted value applies.
        effective_until: Last date it applies; ``None`` when open-ended.
        back_calculation: Steps of a ``back_calculation`` extraction.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    method: ExtractionMethod
    model: str | None = None
    extraction_timestamp: datetime
    verified_by: str | None = None
    verified_at: datetime | None = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    effective_from: date
    effective_until: date | None = None
    back_calculation: tuple[BackCalculationStep, ...] | None = Field(
        default=None,
        validate_default=True,
    )

    @model_validator(mode="after")
    def _check_ai_model(self) -> Self:
        if self.method is ExtractionMethod.AI and self.model is None:
            msg = "method='ai' requires a model identifier; set model=<model-id>"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_back_calculation(self) -> Self:
        if self.back_calculation and self.method != ExtractionMethod.BACK_CALCULATION:
            msg = "back_calculation steps require method='back_calculation'"
            raise ValueError(msg)
        return self
