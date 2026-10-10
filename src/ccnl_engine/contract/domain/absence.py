"""Absence rule models for CCNL contracts."""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from ccnl_engine.provenance.domain.chain import RuleProvenance


class DailyDivisorMethod(StrEnum):
    """How the daily rate is derived for absence deductions.

    * ``by_25``: ``gross_monthly / 25`` — the quota of a CCNL that states
      25 days a month without saying which days of a month are payable:
      a partly employed month and the sick days of a month are not
      computed under it (fail closed).
    * ``by_26``: ``gross_monthly / 26`` — the standard industria divisor.
    * ``by_30``: ``gross_monthly / 30`` — the PA calendar-month divisor.
    * ``by_hourly``: ``hourly_rate * daily_hours`` — for contracts that
      specify a daily working-hours figure.
    """

    BY_25 = "by_25"
    BY_26 = "by_26"
    BY_30 = "by_30"
    BY_HOURLY = "by_hourly"


class AbsenceRules(BaseModel):
    """Layer 3 rules for unpaid-absence (assenza non retribuita) deductions.

    ``daily_divisor_method`` controls how the daily rate is computed:

    * ``by_25``: ``gross_monthly / 25``; the payable days of a month are
      not defined, so partial months and sick days fail closed.
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
