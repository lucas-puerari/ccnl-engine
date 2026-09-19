"""Absence rule models for CCNL contracts."""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from ccnl_engine.engine.provenance.domain.chain import RuleProvenance


class DailyDivisorMethod(StrEnum):
    """How the daily rate is derived for absence deductions.

    * ``by_26``: ``gross_monthly / 26`` — the standard industria divisor.
    * ``by_30``: ``gross_monthly / 30`` — the PA calendar-month divisor.
    * ``by_hourly``: ``hourly_rate * daily_hours`` — for contracts that
      specify a daily working-hours figure.
    """

    BY_26 = "by_26"
    BY_30 = "by_30"
    BY_HOURLY = "by_hourly"


class AbsenceRules(BaseModel):
    """Layer 3 rules for unpaid-absence (assenza non retribuita) deductions.

    ``daily_divisor_method`` controls how the daily rate is computed:

    * ``by_26``: ``gross_monthly / 26`` (standard industria divisore).
    * ``by_30``: ``gross_monthly / 30`` (PA calendar-month convention).
    * ``by_hourly``: ``hourly_rate * daily_hours`` — ``daily_hours`` must
      be provided.

    ``provenance`` links this rule to its source CCNL article.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    daily_divisor_method: DailyDivisorMethod = DailyDivisorMethod.BY_26
    daily_hours: Decimal | None = None
    provenance: RuleProvenance | None = None
