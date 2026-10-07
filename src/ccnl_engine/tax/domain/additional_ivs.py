"""Rule of the additional 1% IVS charged to the worker (D.L. 384/1992 art. 3-ter).

The contribution is due on the pay above the first pensionable band of the
year, up to the IVS massimale.  INPS charges it month by month on the pay
of the month above the band "rapportato a dodici mesi" (the mensilizzazione
of circ. 7/2010 par. 3), regardless of the annual band, and settles it on
the annual pay at year end or in the month the employment ends (msg.
5327/2015 par. 2.3).  The rule holds both thresholds as the circular of the
year publishes them: the monthly one is rounded there, not derived here.
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.shared.domain.primitives import NonNegativeRate, PositiveCeiling

__all__ = ["AdditionalIvsRule"]


class AdditionalIvsRule(BaseModel):
    """Rate and thresholds of the additional 1% IVS of one year.

    Attributes:
        rate: Rate charged to the worker on the pay above the threshold.
        annual_threshold: First pensionable band of the year, the threshold
            of the year-end settlement.
        monthly_threshold: The band "rapportato a dodici mesi", the
            threshold of each month, as published by INPS.
        provenance: Source of the rate and thresholds.

    Raises:
        ValueError: When the monthly threshold exceeds the annual one.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate: NonNegativeRate
    annual_threshold: PositiveCeiling
    monthly_threshold: PositiveCeiling
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_thresholds(self) -> Self:
        if self.monthly_threshold > self.annual_threshold:
            msg = (
                f"monthly_threshold ({self.monthly_threshold}) must not exceed "
                f"annual_threshold ({self.annual_threshold})"
            )
            raise ValueError(msg)
        return self
