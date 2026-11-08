"""The elemento perequativo: a yearly amount for the workers paid only the CCNL."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["EqualisationElement"]


class EqualisationElement(BaseModel):
    """A yearly amount owed to the workers of a firm without second-level pay.

    The worker in service on 1 January of a year, in a firm without
    second-level bargaining with economic content, is owed it with the pay
    of :attr:`paid_in_month` of that year, for the months served in the year
    before; the pay above the CCNL received in that year reduces it, down
    to nothing.  It is all-inclusive: out of the TFR base and of the extra
    months, of the competence of the year it is paid in (metalmeccanici
    Federmeccanica Art. 13, Unionmeccanica-Confapi Art. 48).

    Attributes:
        code: Identifier of the element in the CCNL.
        yearly: Amount of a whole year of service, in EUR.
        paid_in_month: Month of the regular run that pays it, 1-12.
        month_min_days: Days of service that make a month of the year
            before ("la frazione di mese superiore a 15 giorni", 16).
        yearly_by_level: Amount by level code, in place of :attr:`yearly`
            (Turismo art. 13 c. 10: A and B 186, 1-3 158...).
        paid_in_year: The only year it is paid in, ``None`` for every year.
        in_service_month_before: Whether it is owed to the worker in service
            in the month before its month with at least six months of
            service, and never at a termination (Turismo art. 13 c. 5),
            instead of the worker in service on 1 January.
        part_time_proportional: Whether a part-time worker is owed it in
            proportion to the hours (Turismo art. 13 c. 6).
        individual_excludes: Whether any individual element of the worker
            closes it instead of reducing it (Uniontessile art. 12 bis: "che
            non percepiscono altri trattamenti economici individuali").
        settled_on_termination: Whether a termination run before its month
            pays it with the final settlement; ``False`` pays it only in the
            regular run of its month.
        provenance: The clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str = Field(min_length=1)
    yearly: Decimal | None = Field(default=None, gt=0)
    yearly_by_level: dict[str, Decimal] = Field(default_factory=dict)
    paid_in_year: int | None = None
    in_service_month_before: bool = False
    part_time_proportional: bool = False
    individual_excludes: bool = False
    settled_on_termination: bool = True
    paid_in_month: int = Field(ge=1, le=12)
    month_min_days: int = Field(default=16, ge=1, le=31)
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _one_amount(self) -> Self:
        if (self.yearly is None) == (not self.yearly_by_level):
            msg = f"element {self.code}: set yearly or yearly_by_level, not both"
            raise ValueError(msg)
        return self
