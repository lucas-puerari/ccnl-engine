"""The age from which a CCNL counts the service of its seniority increments."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["SeniorityAge"]


class SeniorityAge(BaseModel):
    """The increments count only the service after an age.

    Turismo Art. 158 c. 2: "L'anzianità utile ai fini della maturazione del
    primo scatto di anzianità è: - quella maturata successivamente al
    compimento del diciottesimo anno di età per il personale assunto a
    partire dal 1° giugno 1986".

    Attributes:
        age: Years of age from which the service counts.
        hired_from: First hire date the rule applies to.
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    age: int = Field(ge=1)
    hired_from: date
    provenance: RuleProvenance | None = None
