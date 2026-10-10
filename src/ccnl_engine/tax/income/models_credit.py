"""Tax credit and bonus rule models (trattamento integrativo, somma esente, etc.)."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.primitives import PercentageRate
from ccnl_engine.provenance.ruleset.models import RulesetIdentity
from ccnl_engine.provenance.source.models_chain import RuleProvenance


class TrattamentoIntegrativoRules(BaseModel):
    """Parameters for the trattamento integrativo (Art. 1 D.L. 3/2020).

    The bonus depends on the reddito complessivo (RC), c. 1:

    - RC <= ``threshold_mid``, first period: ``max_amount`` if IRPEF lorda
      exceeds the art. 13 c. 1 TUIR deduction less 75 EUR for the days of
      work, else 0.
    - ``threshold_mid`` < RC <= ``threshold_upper``, second and third
      periods: min(``max_amount``, deductions listed - IRPEF lorda) when the
      deductions listed (art. 12 and art. 13 c. 1 TUIR, among others)
      exceed IRPEF lorda, else 0.
    - RC > ``threshold_upper``: 0.
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

    The ``rate`` applies to the whole employment income (not a marginal
    slice) when the employment income annualised to the whole year falls
    within this band (i.e. does not exceed ``up_to``).  Bands are ordered
    ascending by ``up_to``.

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

    The rules are statutory and the same for every sector: the bundle
    keeps them in their own year file, whose identity is ``ruleset``.

    ``bands`` must be non-empty and strictly ascending by ``up_to``.
    """

    model_config = ConfigDict(extra="forbid")

    bands: list[SommaEsenteBand] = Field(min_length=1)
    provenance: RuleProvenance | None = None
    ruleset: RulesetIdentity | None = None

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
