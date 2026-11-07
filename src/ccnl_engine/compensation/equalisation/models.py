"""The elemento perequativo: a yearly amount for the workers paid only the CCNL."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

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
        provenance: The clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str = Field(min_length=1)
    yearly: Decimal = Field(gt=0)
    paid_in_month: int = Field(ge=1, le=12)
    month_min_days: int = Field(default=16, ge=1, le=31)
    provenance: RuleProvenance
