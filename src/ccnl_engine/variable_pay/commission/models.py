"""The levels a CCNL pays partly by sales commission."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["CommissionLevels"]


class CommissionLevels(BaseModel):
    """Levels whose extra months hold the average of the commissions.

    Commercio, protocollo operatori di vendita art. 15: "Per l'Operatore di
    Vendita retribuito anche con provvigione [...] per retribuzione si
    intende la media mensile dei guadagni globali percepiti nei dodici mesi
    precedenti"; art. 220 c. 3: the tredicesima of the commission-paid
    staff "sulla base della media delle provvigioni".

    Attributes:
        levels: The level codes.
        provenance: The CCNL clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    levels: tuple[str, ...] = Field(min_length=1)
    provenance: RuleProvenance
