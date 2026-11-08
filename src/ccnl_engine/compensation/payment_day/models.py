"""Contractual calendar day for an extra payment."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance


class PaymentDay(BaseModel):
    """Calendar day on which the CCNL pays an extra month.

    Attributes:
        month: Month of the payment, 1-12.
        day: Day of the month, 1-28 so that every month has it.
        provenance: Source of the clause; ``missing`` is not allowed, a
            day without a source is left out of the data instead.

    Raises:
        ValueError: When the provenance is ``missing``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=28)
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_source(self) -> Self:
        if self.provenance.status is ProvenanceStatus.MISSING:
            msg = "a stored payment day needs a source; omit it when missing"
            raise ValueError(msg)
        return self
