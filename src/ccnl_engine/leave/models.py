"""Paid leave rules of a CCNL: ferie, ROL and ex festività, and their payout.

The ferie days of a year (:class:`LeaveRules`) are read by every CCNL file.
A CCNL whose text was read for the accrual also states how the days accrue
month by month (:class:`FerieAccrual`), the hours of each permit bucket
(:class:`PermitRules`) and the basis of the indemnity for the leave left
at the end of the employment (:class:`LeaveTermination`); a CCNL without
them accrues nothing and pays no residual leave (fail closed).
"""

from __future__ import annotations

from datetime import date  # noqa: TC003
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.leave.permit.models import PermitRules  # noqa: TC001
from ccnl_engine.leave.types import LeaveBucket, MonthCredit
from ccnl_engine.provenance.source.rule.models import RuleProvenance  # noqa: TC001

__all__ = [
    "FerieAccrual",
    "LeaveEntitlementTier",
    "LeaveRules",
    "LeaveTermination",
]

_ZERO = Decimal(0)
_ONE = Decimal(1)


class LeaveEntitlementTier(BaseModel):
    """One seniority-gated leave entitlement tier.

    When ``service_months_min`` months of service have elapsed, the worker
    is entitled to ``annual_days`` paid leave days per year. Tiers are
    evaluated in descending order of ``service_months_min``; the first
    matching tier wins. Use :class:`LeaveRules.default_annual_days` as
    the fallback when no tier matches or seniority is unknown.
    ``valid_from`` and ``valid_until`` (exclusive) bound the dates a tier is
    in force (Funzioni Centrali: the 26 days of the first three years end
    on 31 December 2026); ``None`` leaves that side open.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    service_months_min: int = Field(default=0, ge=0)
    annual_days: Decimal = Field(gt=Decimal(0))
    valid_from: date | None = None
    valid_until: date | None = None

    def in_force(self, day: date) -> bool:
        """Return whether the tier applies on ``day``.

        Returns:
            ``True`` from ``valid_from`` up to ``valid_until`` (exclusive).
        """
        after = self.valid_from is None or self.valid_from <= day
        return after and (self.valid_until is None or day < self.valid_until)


class FerieAccrual(BaseModel):
    """How the ferie days of the year accrue month by month.

    Attributes:
        month_credit: Which months accrue a twelfth of the days; ``None``
            when the text does not say how a month fraction counts: a month
            served in part accrues nothing and the accrual is not exact.
        provenance: Source of the twelfths and of the month rule.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    month_credit: MonthCredit | None = None
    provenance: RuleProvenance | None = None


class LeaveTermination(BaseModel):
    """Basis of the indemnity for the leave left at the end of the employment.

    Attributes:
        ferie_divisor: Divisor of the monthly pay that gives the indemnity
            of one day of ferie (Commercio Art. 159: twenty-six).
        permits_hourly: Whether the hours of the permit buckets left are
            paid at the hourly quota of the monthly pay (the monthly pay
            over the hourly divisor of the CCNL).  ``False`` when the text
            read gives no basis for them: they are not paid.
        provenance: Source of the basis.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    ferie_divisor: Decimal = Field(gt=_ZERO)
    permits_hourly: bool
    provenance: RuleProvenance | None = None


class LeaveRules(BaseModel):
    """Layer 3 rules for paid leave (ferie and permessi).

    ``default_annual_days`` is the contractual entitlement when no
    seniority-gated tier matches or when seniority is unknown.
    ``entitlement_tiers`` (optional) list tiers in any order; the engine
    selects the one with the highest ``service_months_min`` that the
    worker has satisfied.  ``ferie_accrual``, ``permits`` and
    ``termination`` are stated for a CCNL whose accrual was read; a CCNL
    without them accrues no leave.

    ``provenance`` links this rule to its CCNL article.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    default_annual_days: Decimal = Field(gt=Decimal(0))
    entitlement_tiers: tuple[LeaveEntitlementTier, ...] = Field(default=())
    provenance: RuleProvenance | None = None
    ferie_accrual: FerieAccrual | None = None
    permits: tuple[PermitRules, ...] = ()
    termination: LeaveTermination | None = None

    @model_validator(mode="after")
    def _distinct_buckets(self) -> Self:
        buckets = [p.bucket for p in self.permits]
        pooled = any(p.includes_ex_festivita for p in self.permits)
        if len(set(buckets)) != len(buckets) or (
            pooled and LeaveBucket.EX_FESTIVITA in buckets
        ):
            msg = (
                "permits need distinct buckets, and no ex_festivita bucket "
                f"beside a rol pool that includes it; got {buckets}"
            )
            raise ValueError(msg)
        return self

    @property
    def buckets(self) -> frozenset[LeaveBucket]:
        """Buckets the CCNL accrues: ferie with an accrual, and the permits."""
        ferie = {LeaveBucket.FERIE} if self.ferie_accrual is not None else set()
        return frozenset(ferie | {p.bucket for p in self.permits})

    def annual_days(self, service_months: int | None, day: date) -> Decimal:
        """Return the leave days of a year for a worker on ``day``.

        Returns:
            The days of the tier in force on ``day`` with the highest
            ``service_months_min`` the worker reached, else
            ``default_annual_days``.
        """
        if service_months is None:
            return self.default_annual_days
        tiers = [
            t
            for t in self.entitlement_tiers
            if t.in_force(day) and t.service_months_min <= service_months
        ]
        if not tiers:
            return self.default_annual_days
        return max(tiers, key=lambda t: t.service_months_min).annual_days

    def days_depend_on_seniority(self, day: date) -> bool:
        """Return whether the days of a year on ``day`` depend on the seniority.

        Returns:
            ``True`` when two tiers in force, or a tier and the default,
            grant different days.
        """
        days = {t.annual_days for t in self.entitlement_tiers if t.in_force(day)}
        return len(days | {self.default_annual_days}) > 1
