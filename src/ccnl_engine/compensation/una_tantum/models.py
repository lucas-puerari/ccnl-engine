"""The one-off amounts (una tantum) a CCNL renewal pays for its vacancy."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["UnaTantum", "UnaTantumInstallment"]


class UnaTantumInstallment(BaseModel):
    """One payment of an una tantum: its month and its amount by level.

    Attributes:
        paid_in: First day of the month whose regular run pays it.
        amounts: Gross amount by level code, for a full-time worker who
            meets the condition in full.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    paid_in: date
    amounts: dict[str, Decimal]

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.paid_in.day != 1:
            msg = "an installment is paid in a month: paid_in is its first day"
            raise ValueError(msg)
        if not self.amounts or any(v <= 0 for v in self.amounts.values()):
            msg = "an installment has an amount above zero for each level it pays"
            raise ValueError(msg)
        return self


class UnaTantum(BaseModel):
    """An una tantum of a renewal, for the months its contract was vacant.

    The worker in service when an installment is paid is owed it in full
    when hired before :attr:`covers_from`, and a share of it, the months of
    service in the covered period over its months, when hired within it; a
    worker hired after :attr:`covers_until` is owed nothing.  Part-time
    workers are owed it in proportion to their hours.  The share of the
    covered months of earlier years is taxed apart (art. 17 c. 1 lett. b
    TUIR), the rest with the run; it enters the INPS base, not the TFR base.

    Attributes:
        code: Identifier of the una tantum in the CCNL.
        covers_from: First day of the vacancy it pays for.
        covers_until: Last day of the vacancy it pays for.
        month_min_days: Days of service that make a month of the covered
            period (ANAV: "la frazione superiore ai 15 giorni", 16).
        in_service_on: Day the worker must be in service on (the signing
            of the agreement), ``None`` when the text sets none.
        installments: Its payments, in date order.
        provenance: The clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str = Field(min_length=1)
    covers_from: date
    covers_until: date
    month_min_days: int = Field(default=15, ge=1, le=31)
    in_service_on: date | None = None
    installments: tuple[UnaTantumInstallment, ...] = Field(min_length=1)
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.covers_until < self.covers_from:
            msg = "covers_until precedes covers_from"
            raise ValueError(msg)
        days = [i.paid_in for i in self.installments]
        if days != sorted(set(days)) or days[0] <= self.covers_from:
            msg = (
                "installments are paid in order, once a month, after the vacancy starts"
            )
            raise ValueError(msg)
        return self
