"""The renewals of a CCNL that raised its minimo tabellare."""

from __future__ import annotations

from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.provenance.source.models import SourceLocation

__all__ = ["RenewalAgreement"]


class RenewalAgreement(BaseModel):
    """A renewal agreement and the first table of the minimo it set.

    The tables of the minimo record their values, not the agreement that set
    them.  A renewal names the date it was signed and the first day of its
    first tranche: every table from that day on carries its increments, and
    the table in force the day before is the minimo before the renewal.

    Attributes:
        signed_on: Day the agreement was signed (the ipotesi di accordo,
            when the tranches run from it).
        tables_from: First day of the first tranche of the minimo it set.
        source: The agreement: document, page and the quote of the tranche.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    signed_on: date
    tables_from: date
    source: SourceLocation

    @model_validator(mode="after")
    def _check_quote(self) -> Self:
        if self.source.quote is None:
            msg = "a renewal must quote its first tranche"
            raise ValueError(msg)
        return self
