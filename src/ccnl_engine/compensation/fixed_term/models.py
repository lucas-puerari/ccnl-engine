"""Pay of the fixed-term workers a CCNL pays by the hour with a percentage.

CCNL operai agricoli e florovivaisti, art. 50: the operaio a tempo
determinato (OTD) is paid the salario contrattuale of the hours worked and
a terzo elemento of 30.44% on it, "quale corrispettivo" of the festività,
the ferie and the tredicesima and quattordicesima mensilità of the operai
a tempo indeterminato.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.compensation.hourly.models import HourlyPay
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["FixedTermPay"]


class FixedTermPay(BaseModel):
    """The pay of the fixed-term workers of some categories.

    A fixed-term worker of :attr:`categories` is paid by
    :attr:`hourly_pay`, with :attr:`additional_months` monthly payments and
    no leave accrued: the percentages of :attr:`hourly_pay` stand for the
    extra months and the ferie.

    Attributes:
        categories: Worker categories the rule covers.
        hourly_pay: Pay by the hour worked and its percentages.
        additional_months: Monthly payments a year (12: no extra month).
        tfr_rate: Share of the TFR pay accrued as TFR, in place of the
            divisor of art. 2120 c.c. (OTD: 'pari all'8,63 per cento
            calcolato sul salario contrattuale'); ``None`` keeps the divisor.
        overtime_tfr_rate: TFR on the ordinary pay of the non-occasional
            overtime hours (OTD: 'elevata al 10 per cento').
        seasonal_only: The rule covers only the seasonal fixed terms
            (``FixedTerm.naspi_exclusion`` seasonal): Ortofrutticoli art. 72,
            the 'personale assunto con contratto a tempo determinato
            stagionale'.
        percentages_on_overtime: Whether the percentages also apply to the
            overtime hours (OTD art. 44: 'anche per le ore straordinarie');
            false when the CCNL excludes them (Ortofrutticoli art. 72: 'con
            esclusione di tutte le ore di lavoro straordinario').
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    categories: tuple[WorkerCategory, ...] = Field(min_length=1)
    hourly_pay: HourlyPay
    additional_months: TimeSeries
    tfr_rate: TimeSeries | None = None
    overtime_tfr_rate: TimeSeries | None = None
    seasonal_only: bool = False
    percentages_on_overtime: bool = True
    provenance: RuleProvenance
