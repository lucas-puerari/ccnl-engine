"""Rules a CCNL sets apart for the employers of a sub-sector.

Pubblici esercizi FIPE, special parts of the stabilimenti balneari (artt.
245, 250) and of the alberghi diurni (art. 266): their own sickness
supplement and, for the balneari non impiegati, a 44-hour week paid over
190 hours.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.sickness.integration.models import SicknessRules

__all__ = ["SubsectorRules"]


class SubsectorRules(BaseModel):
    """The rules of a sub-sector that replace the CCNL's.

    Attributes:
        sickness_rules: Sickness rules of the sub-sector, ``None`` to keep
            the CCNL's.
        hourly_divisor_by_category: Hourly divisor of the workers of a
            category, in place of the CCNL's.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    sickness_rules: SicknessRules | None = None
    hourly_divisor_by_category: dict[WorkerCategory, TimeSeries] = Field(
        default_factory=dict
    )
