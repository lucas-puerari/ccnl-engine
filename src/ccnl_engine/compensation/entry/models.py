"""The entry pay of a CCNL: a new hire paid below the level for some months."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.apprenticeship.models import UnderClassificationPeriod
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["EntryPay", "TransitionHireBand"]


class TransitionHireBand(BaseModel):
    """Minimum hire date and level tenure for an entry-level promotion."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    hired_from: date
    after_months: int = Field(gt=0)


class EntryPay(BaseModel):
    """A permanent hire the employer may pay below the level for some months.

    Studi professionali Art. 56: the over 50 and the long-term unemployed
    hired "a tempo indeterminato" may be paid "un salario di ingresso pari
    alla retribuzione fino a due livelli immediatamente inferiori per i primi
    9 mesi dalla data di assunzione, e di un livello per i successivi 6 mesi".

    Attributes:
        periods: Months from the hire and the levels below of each, in
            order; the last ends when the entry pay ends.
        excluded_levels: Levels the entry pay is not applicable to.
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    periods: tuple[UnderClassificationPeriod, ...] = Field(min_length=1)
    excluded_levels: tuple[str, ...] = ()
    provenance: RuleProvenance | None = None
