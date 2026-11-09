"""Hourly holiday supplements and the annual legacy individual payment."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance


class LegacyHolidayPayment(BaseModel):
    """Two distinct former-worker clauses, each with its own source.

    ``holiday_hours`` applies to each weekday holiday and to Epiphany on a
    weekend in January. ``annual_hours`` is paid only in December to workers
    in service under the former Special Discipline Part One at 2008-12-31.
    The hourly rate is the Art. 38 monthly pay divided by the CCNL divisor.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    holiday_hours: Decimal = Field(gt=0)
    annual_hours: Decimal = Field(gt=0)
    holiday_provenance: RuleProvenance
    annual_provenance: RuleProvenance
