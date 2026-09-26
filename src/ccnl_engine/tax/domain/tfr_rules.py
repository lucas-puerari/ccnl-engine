"""TFR (severance pay) accrual rule models."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.domain.chain import RuleProvenance


class TfrRules(BaseModel):
    """TFR (severance pay) accrual rules (Art. 2120 c.c.)."""

    model_config = ConfigDict(extra="forbid")

    accrual_divisor: Decimal = Field(gt=Decimal(0))
    provenance: RuleProvenance | None = None
