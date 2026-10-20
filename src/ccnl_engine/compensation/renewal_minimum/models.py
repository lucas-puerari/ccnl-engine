"""The renewals of a CCNL that raised its minimo tabellare."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
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
        minimum_before: Full-time minimo before the renewal by level code,
            when it is not the table in force the day before the first
            tranche: the bundle has no such table, or the first tranche
            also pays the last tranche of an earlier renewal (Chimica 2025
            p. 46).  A renewal that lists it leaves the levels it omits
            unmeasured.
        minimum_before_source: Where :attr:`minimum_before` is read,
            required with it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    signed_on: date
    tables_from: date
    source: SourceLocation
    minimum_before: dict[str, Decimal] = {}
    minimum_before_source: SourceLocation | None = None

    @model_validator(mode="after")
    def _check_quote(self) -> Self:
        if self.source.quote is None:
            msg = "a renewal must quote its first tranche"
            raise ValueError(msg)
        if bool(self.minimum_before) != (self.minimum_before_source is not None):
            msg = "minimum_before and minimum_before_source go together"
            raise ValueError(msg)
        if any(v <= 0 for v in self.minimum_before.values()):
            msg = "a minimum_before value must be above zero"
            raise ValueError(msg)
        return self
