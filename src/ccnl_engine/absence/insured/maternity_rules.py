"""CCNL maternity integration periods."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.absence.insured.maternity_holiday import MaternityHoliday
from ccnl_engine.provenance.source.rule.models import RuleProvenance

type Share = Annotated[Decimal, Field(gt=Decimal(0), le=Decimal(1))]


class MaternityRules(BaseModel):
    """What a CCNL adds to the INPS maternity indemnity.

    Attributes:
        integration_rate: Share of the pay the employer tops the indemnity
            up to; ``None`` for a CCNL that tops up the holidays only.
        integration_days: Days of the leave, from its first day, the
            top-up is due for (five months: 150).
        next_integration_rate: Target share after the first integration period.
        next_integration_days: Length of that following period in calendar days.
        parental_sixth_month: Whether the following period also covers parental
            leave immediately after the compulsory maternity leave.
        net_basis: Whether the measure is of the net pay (the INPS share,
            free of contributions, is grossed up by the worker's INPS rate).
        holiday: The target of a national holiday in the compulsory leave
            (Studi art. 110 c. 8: "in modo da raggiungere complessivamente il
            100%"), net of the INPS share and of the top-up of the day.
        paternity_holiday: The same target in a compulsory paternity leave.
        parental_holiday: The holiday target during optional (parental) leave.
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    integration_rate: Share | None = None
    integration_days: int | None = Field(default=None, ge=1)
    next_integration_rate: Share | None = None
    next_integration_days: int | None = Field(default=None, ge=1)
    parental_sixth_month: bool = False
    net_basis: bool = False
    holiday: MaternityHoliday | None = None
    paternity_holiday: MaternityHoliday | None = None
    parental_holiday: MaternityHoliday | None = None
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_next_period(self) -> Self:
        if (self.next_integration_rate is None) != (self.next_integration_days is None):
            msg = "the following maternity period requires a rate and days"
            raise ValueError(msg)
        if self.next_integration_rate is not None and (
            self.integration_rate is None or self.integration_days is None
        ):
            msg = "the following maternity period requires a first period"
            raise ValueError(msg)
        if self.parental_sixth_month and self.next_integration_rate is None:
            msg = "parental sixth month requires a following maternity period"
            raise ValueError(msg)
        return self
