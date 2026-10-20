"""Health and bilateral funds a CCNL owes for every worker, or their element.

Many CCNLs oblige the employer to pay a health fund (Fondo Est, FAST,
mètaSalute, Cadiprof) or a bilateral body (EBT, EBNT, Ebipro) for every
worker, and grant the worker of an employer that does not an elemento
distinto della retribuzione instead.  The employer states which funds it
pays (``EmployerProfile.contractual_funds``); the CCNL gives the amounts.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["ContractualFund", "FundAmount"]


class FundAmount(BaseModel):
    """A monthly amount: fixed, a rate of the minimo, or both.

    Attributes:
        monthly: Fixed amount a month, in EUR.
        rate: Fraction of the monthly minimo the run pays (paga base and
            contingenza, as the CCNL table gives them).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    monthly: TimeSeries | None = None
    rate: TimeSeries | None = None

    @model_validator(mode="after")
    def _check_some(self) -> Self:
        if self.monthly is None and self.rate is None:
            msg = "a fund amount needs a monthly amount or a rate"
            raise ValueError(msg)
        return self


class ContractualFund(BaseModel):
    """A fund the CCNL owes for every worker it covers.

    Attributes:
        code: Stable code the employer names in
            ``EmployerProfile.contractual_funds`` (e.g. ``"fondo_est"``).
        description: Name and article of the fund.
        categories: Worker categories it covers, ``None`` for all.
        levels: Level codes it covers, ``None`` for all.
        permanent_only: Whether only permanent workers are covered.
        employer: Employer share a month.
        employee: Worker share a month, withheld from the pay.
        extra_months: Whether the shares are due on the extra months too.
        employee_deductible: Whether the worker share leaves the IRPEF base
            (a health fund of TUIR art. 51 c. 2 lett. a).
        solidarity_rate: INPS solidarity contribution the employer owes on
            its share (10% for a health fund, L. 166/1991 art. 9-bis).
        alternative: Elemento distinto the worker is owed when the employer
            does not pay the fund, ``None`` when the CCNL grants none.
        alternative_extra_months: Whether the element is paid on the extra
            months too (e.g. "per 14 mensilità").
        alternative_tfr: Whether the element enters the TFR base.
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    description: str
    categories: frozenset[WorkerCategory] | None = None
    levels: frozenset[str] | None = None
    permanent_only: bool = False
    employer: FundAmount
    employee: FundAmount | None = None
    extra_months: bool = False
    employee_deductible: bool = False
    solidarity_rate: Decimal = Field(default=Decimal(0), ge=0, lt=1)
    alternative: FundAmount | None = None
    alternative_extra_months: bool = False
    alternative_tfr: bool = False
    provenance: RuleProvenance
