"""Legacy apprentice increment cohorts."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from ccnl_engine.agreement.validity.rules import TimeSeries


class ApprenticeCohort(BaseModel):
    """The apprentice increment kept by the apprentices of an earlier rule.

    Tessile moda artigianato, renewal of 16 July 2024: "Agli apprendisti in
    forza alla data di sottoscrizione del presente accordo di rinnovo
    continua a trovare applicazione la disciplina degli aumenti periodici di
    anzianità vigente alla data di assunzione".

    Attributes:
        in_service_on: Last hire date of the cohort: the day of signature.
        amount: Increment of the cohort, in place of
            :attr:`SeniorityIncrements.apprentice_amount`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    in_service_on: date
    amount: TimeSeries
