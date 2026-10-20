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
    """A monthly amount: fixed, yearly, a rate of the minimo, or a sum.

    Attributes:
        monthly: Fixed amount a month, in EUR.
        annual: Fixed amount a year, in EUR, charged a twelfth a month.
        rate: Fraction of the monthly minimo the run pays (paga base and
            contingenza, as the CCNL table gives them), with the allowances
            the fund names in ``rate_allowances``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    monthly: TimeSeries | None = None
    annual: TimeSeries | None = None
    rate: TimeSeries | None = None

    @model_validator(mode="after")
    def _check_some(self) -> Self:
        if self.monthly is None and self.annual is None and self.rate is None:
            msg = "a fund amount needs a monthly or annual amount or a rate"
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
        group: Funds that are alternative ways to meet the same obligation
            (e.g. the EBM contribution of a firm with or without an internal
            RLS) share a group: the employer names the one it pays; naming
            none owes the element of the first fund of the group once.
        rate_allowances: Codes of the fixed allowances of the level a rate
            reads besides the base salary: the contingenza of a CCNL whose
            table lists it apart from the paga base (Commercio Art. 23,
            "paga base e contingenza").
        employer: Employer share a month.
        reduced_employer: Employer share of a part-timer working at most
            ``reduced_up_to_weekly_hours`` a week, when the fund sets one.
        reduced_up_to_weekly_hours: Weekly hours up to which the reduced
            share applies.
        employee: Worker share a month, withheld from the pay.
        extra_months: Whether the shares are due on the extra months too.
        employee_deductible: Whether the worker share leaves the IRPEF base
            (a health fund of TUIR art. 51 c. 2 lett. a).
        solidarity_rate: INPS solidarity contribution the employer owes on
            its share (10% for a health fund, L. 166/1991 art. 9-bis).
        alternative: Elemento distinto the worker is owed when the employer
            does not pay the fund, ``None`` when the CCNL grants none.
        alternative_in: Code of the fund whose element also stands for this
            one, when the CCNL owes a single element for several funds
            (Studi professionali Art. 13: 43 EUR for CADIPROF and EBIPRO).
        alternative_extra_months: Whether the element is paid on the extra
            months too (e.g. "per 14 mensilità").
        alternative_tfr: Whether the element enters the TFR base.
        alternative_scaled: Whether the element follows the minimo of the
            run (part time, partial month) like the pay it belongs to;
            false when the CCNL owes it in full ("non riproporzionato").
        charged_in_month: Month of the year the yearly amounts are charged
            whole, by year (a value 1-12 from each ``valid_from``); ``None``
            charges them a twelfth a month.
        welfare: Whether the employer amount is a welfare benefit made
            available to the worker (goods and services, outside the pay)
            rather than a contribution to a fund.
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    description: str
    categories: frozenset[WorkerCategory] | None = None
    levels: frozenset[str] | None = None
    permanent_only: bool = False
    group: str | None = None
    rate_allowances: frozenset[str] = frozenset()
    employer: FundAmount
    reduced_employer: FundAmount | None = None
    reduced_up_to_weekly_hours: Decimal | None = Field(default=None, gt=0)
    employee: FundAmount | None = None
    extra_months: bool = False
    employee_deductible: bool = False
    solidarity_rate: Decimal = Field(default=Decimal(0), ge=0, lt=1)
    alternative: FundAmount | None = None
    alternative_in: str | None = None
    alternative_extra_months: bool = False
    alternative_tfr: bool = False
    alternative_scaled: bool = True
    charged_in_month: TimeSeries | None = None
    welfare: bool = False
    provenance: RuleProvenance
