"""Tax credit and bonus rule models (trattamento integrativo, somma esente, etc.)."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.primitives.domain.primitives import PercentageRate
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance


class TrattamentoIntegrativoRules(BaseModel):
    """Parameters for the trattamento integrativo (Art. 1 D.L. 3/2020).

    The bonus is computed on gross annual income (RAL) as follows:

    - RAL <= ``threshold_mid``: ``max_amount`` if IRPEF lorda > detrazioni lavoro,
      else 0.
    - ``threshold_mid`` < RAL <= ``threshold_upper``:
      max(0, ``max_amount`` * (``threshold_upper`` - RAL)
      / (``threshold_upper`` - ``threshold_mid``)).
    - RAL > ``threshold_upper``: 0.
    """

    model_config = ConfigDict(extra="forbid")

    threshold_mid: Decimal
    threshold_upper: Decimal
    max_amount: Decimal
    provenance: RuleProvenance | None = None


class UlterioreDetrazioneRules(BaseModel):
    """Ulteriore detrazione del lavoro dipendente (Art. 1 c. 6 L. 207/2024).

    Three zones by reddito complessivo (``rc``):

    - ``rc <= threshold_low``: zero.
    - ``threshold_low < rc <= threshold_mid``: ``max_amount`` (flat).
    - ``threshold_mid < rc <= threshold_high``:
      ``max_amount * (threshold_high - rc) / (threshold_high - threshold_mid)``
      (tapering to zero at the upper boundary).
    - ``rc > threshold_high``: zero.

    Pro-rating to the actual work period is the caller's responsibility.
    """

    model_config = ConfigDict(extra="forbid")

    threshold_low: Decimal
    threshold_mid: Decimal
    threshold_high: Decimal
    max_amount: Decimal
    provenance: RuleProvenance | None = None


class SommaEsenteBand(BaseModel):
    """One income band for the somma esente schedule.

    The ``rate`` applies to the full reddito complessivo (not a marginal
    slice) when the income falls within this band (i.e. does not exceed
    ``up_to``).  Bands are ordered ascending by ``up_to``.

    ``rate`` must be in [0, 1]; negative bonus rates are economically
    impossible.
    """

    model_config = ConfigDict(extra="forbid")

    up_to: Decimal
    rate: PercentageRate


class SommaEsenteRules(BaseModel):
    """Somma esente L. 207/2024 for low-income workers.

    A flat-rate bonus added to net pay when reddito complessivo does not
    exceed the last band's ``up_to`` threshold (art. 1 c. 4).  The rate is
    that of the first band whose ``up_to`` covers the employment income
    annualised to the whole year (c. 5), the last band's above them all;
    it is applied to the whole employment income of the year (not just
    the marginal slice).

    Band cut points in the knowledge bundle are unverified reconstructions
    from available examples and are flagged in the JSON ``notes`` array.

    ``bands`` must be non-empty and strictly ascending by ``up_to``.
    """

    model_config = ConfigDict(extra="forbid")

    bands: list[SommaEsenteBand] = Field(min_length=1)
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_bands_order(self) -> Self:
        for i, band in enumerate(self.bands[:-1]):
            nxt = self.bands[i + 1]
            if nxt.up_to <= band.up_to:
                msg = (
                    f"SommaEsenteRules.bands must be strictly ascending "
                    f"by up_to: bands[{i}].up_to={band.up_to} >= "
                    f"bands[{i + 1}].up_to={nxt.up_to}"
                )
                raise ValueError(msg)
        return self
