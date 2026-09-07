"""Extraction-trace models for the provenance chain.

An :class:`ExtractionTrace` records how a rule was turned into a domain-model
value and who verified it.  ``verified_by``/``verified_at`` stay ``None``
until a human curator reviews an extraction, mirroring the existing
``human_reviewed: false`` convention on CCNL data files.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.metadata.domain.rules import VerificationStatus


class ExtractionMethod(StrEnum):
    """How a rule was extracted into the domain model."""

    AI_ASSISTED = "ai_assisted"
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
        result: The derived rule value.
    """

    model_config = ConfigDict(extra="forbid")

    description: str
    inputs: dict[str, Decimal | str]
    result: Decimal


class ExtractionTrace(BaseModel):
    """Metadata about how one rule was extracted and verified.

    Attributes:
        method: How the value was extracted (see :class:`ExtractionMethod`).
        model: AI/LLM model used for ``ai_assisted`` extractions.
        extraction_timestamp: When the extraction was performed.
        verified_by: Identifier of the human curator who reviewed the
            extraction; ``None`` until reviewed.
        verified_at: When the human curator approved it; ``None`` until then.
        verification_status: Confidence level (defaults to ``unverified``).
        effective_from: First date the extracted value applies.
        effective_until: Last date it applies; ``None`` when open-ended.
        back_calculation: Steps of a ``back_calculation`` extraction.
    """

    model_config = ConfigDict(extra="forbid")

    method: ExtractionMethod
    model: str | None = None
    extraction_timestamp: datetime
    verified_by: str | None = None
    verified_at: datetime | None = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    effective_from: date
    effective_until: date | None = None
    back_calculation: list[BackCalculationStep] | None = Field(
        default=None,
        validate_default=True,
    )

    @model_validator(mode="after")
    def _check_back_calculation(self) -> Self:
        if self.back_calculation and self.method != ExtractionMethod.BACK_CALCULATION:
            msg = "back_calculation steps require method='back_calculation'"
            raise ValueError(msg)
        return self
