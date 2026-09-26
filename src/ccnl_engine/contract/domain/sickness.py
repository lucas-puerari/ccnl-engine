"""Sickness rule models for CCNL contracts."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.domain.chain import RuleProvenance


class SicknessTier(BaseModel):
    """One month-gated sick-pay integration tier.

    When the total sick days in the episode fall within
    ``[month_from, month_until)`` calendar months (30 days each), the
    ``integration_rate`` applies instead of ``full_pay_integration_rate``.
    Tiers are evaluated in descending order of ``month_from``; the first
    matching tier wins.  Use :attr:`SicknessRules.full_pay_integration_rate`
    as the flat fallback when no tier matches or when cumulative context is
    not available.

    Attributes:
        month_from: First month (1-indexed) in which this tier applies.
        month_until: First month in which this tier no longer applies
            (exclusive upper bound).  ``None`` means open-ended.
        integration_rate: Target fraction of gross daily pay for this tier.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    month_from: int = Field(ge=1)
    month_until: int | None = Field(default=None, ge=2)
    integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))


class SicknessRules(BaseModel):
    """Layer 3 rules for sick leave (malattia ordinaria) integration.

    Defines how the CCNL supplements the statutory INPS indemnity during
    illness.  The engine computes INPS indemnity from the bundled rate
    file; ``carenza_integration_rate`` and ``full_pay_integration_rate``
    determine the company's share on top.

    When ``tiers`` is non-empty and the caller provides the cumulative sick
    days at the start of the period, the engine selects the matching tier's
    ``integration_rate`` instead of ``full_pay_integration_rate``.

    Attributes:
        carenza_integration_rate: Fraction of gross daily pay the company
            covers during the waiting period (days 1-``carenza_days``).
            ``1.0`` = full pay; ``0.0`` = no company coverage.
        full_pay_integration_rate: Target fraction of gross daily pay the
            worker should receive during INPS-covered days.  The company
            pays the difference above the INPS indemnity.  ``1.0`` = 100%
            guaranteed by the CCNL (company tops up to full gross).
            Used as flat fallback when ``tiers`` is empty or cumulative
            context is unavailable.
        tiers: Optional list of month-gated integration tiers for CCNLs
            that reduce the integration rate after several months of
            sickness (e.g. 100% for months 1-9, 90% for months 10-12).
        max_duration_days: Number of calendar days after which sick leave
            exceeds the comporto period.  Days beyond this limit are not
            modelled by the engine.
        provenance: Links this rule to its CCNL article.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    carenza_integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))
    full_pay_integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))
    tiers: tuple[SicknessTier, ...] = Field(default=())
    max_duration_days: int = Field(default=180, ge=1)
    provenance: RuleProvenance | None = None
