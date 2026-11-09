"""Dated agreement rule for a pre-existing extra month's credit."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from ccnl_engine.provenance.source.rule.models import RuleProvenance


class FourteenthPriorExtraOffset(BaseModel):
    """Offset extra remuneration months already paid at contract entry."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    entry_on: date
    provenance: RuleProvenance
