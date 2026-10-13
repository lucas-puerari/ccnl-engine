"""Pay by the hour of a worker category and the percentages on its hours.

The CCNL edilizia pays the operai by the hour: the monthly elements over the
hourly divisor, for every hour of normal work actually worked (Allegato A),
and on the same hours the percentages of Art. 5 (riposi annui, paid with
the pay) and of Art. 18 (ferie and gratifica natalizia, accrued with the
Cassa Edile net of the withholdings, Allegato D).
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["HourlyPay", "HourlyPercentage", "PercentageSettlement"]

_ZERO = Decimal(0)
_ONE = Decimal(1)


class PercentageSettlement(StrEnum):
    """Who the percentage on the hours worked is paid to.

    Attributes:
        CASH: Paid to the worker with the pay of the period.
        CASSA_EDILE: A gross earning of the worker the employer accrues
            with the Cassa Edile: contributions and taxes are withheld on
            it, then ``net_rate`` of the base is withheld from the pay and
            remitted to the Cassa (CCNL edilizia, Allegato D).
    """

    CASH = "cash"
    CASSA_EDILE = "cassa_edile"


class HourlyPercentage(BaseModel):
    """A percentage of the hourly elements on the hours worked.

    Attributes:
        code: Code of the percentage, unique in the CCNL.
        description: Name of the percentage.
        rate: Share of the base it pays.
        base_allowances: Codes of the fixed allowances that join the base
            salary in its base, as the run pays them by the hour.
        settlement: Who it is paid to.
        net_rate: Share of the base withheld from the pay and accrued with
            the Cassa Edile; set for ``cassa_edile`` alone.
        provenance: Source of the clause.

    Raises:
        ValueError: When a rate is outside [0, 1], ``net_rate`` is set
            against the settlement or exceeds ``rate``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    description: str
    rate: TimeSeries
    base_allowances: tuple[str, ...] = ()
    settlement: PercentageSettlement
    net_rate: TimeSeries | None = None
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_rates(self) -> Self:
        accrued = self.settlement is PercentageSettlement.CASSA_EDILE
        if accrued != (self.net_rate is not None):
            msg = f"percentage {self.code}: net_rate is set for cassa_edile alone"
            raise ValueError(msg)
        for series in (self.rate, self.net_rate):
            for period in () if series is None else series.periods:
                if period.value is not None and not _ZERO <= period.value <= _ONE:
                    msg = f"percentage {self.code}: rates must be within [0, 1]"
                    raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_net_within_gross(self) -> Self:
        for period in () if self.net_rate is None else self.net_rate.periods:
            gross = self.rate.period_at(period.valid_from)
            if period.value is not None and (
                gross is None or gross.value is None or period.value > gross.value
            ):
                msg = f"percentage {self.code}: net_rate exceeds rate"
                raise ValueError(msg)
        return self


class HourlyPay(BaseModel):
    """Worker categories the CCNL pays by the hour.

    A run that posts the monthly pay of such a worker pays the pay chain
    (base salary, seniority and fixed allowances) as its monthly amounts
    over the hourly divisor, times ``PeriodFacts.ordinary_hours_worked``:
    the ferie, the permits and the other hours not worked are not paid as
    days of the month.

    Attributes:
        categories: Worker categories paid by the hour.
        percentages: Percentages of the hourly elements on the same hours.
        provenance: Source of the clause.

    Raises:
        ValueError: When two percentages share a code.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    categories: tuple[WorkerCategory, ...] = Field(min_length=1)
    percentages: tuple[HourlyPercentage, ...] = ()
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_codes(self) -> Self:
        codes = [p.code for p in self.percentages]
        if len(set(codes)) != len(codes):
            msg = f"hourly_pay percentages repeat a code: {codes}"
            raise ValueError(msg)
        return self
