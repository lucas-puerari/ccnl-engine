"""Ordinary contribution of the bilateral solidarity fund of a CCNL.

D.Lgs. 148/2015 art. 26 has the sectors outside the CIGO and CIGS set up a
solidarity fund at INPS by collective agreement; the decree of each fund
sets its ordinary contribution on the INPS taxable pay, split between the
employer and the worker.  The fund belongs to the CCNL, not to the INPS
sector: in credito the bancari ABI and the BCC have funds of their own.

A fund comes in one of two shapes.  A fund of a sector whose INPS rates
hold no wage-integration share (the credito) charges one rate on top of
them, to the workers its decree covers.  A fund of a sector that would
otherwise be in the FIS (the Fondo di solidarietà bilaterale per le
attività professionali) charges a rate by headcount in place of the FIS and
CIGS shares of the sector rates, to every worker the sector rates apply to.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.types import PercentageRate

if TYPE_CHECKING:
    from ccnl_engine.sector.models import YearRules

__all__ = ["SolidarityFund", "SolidarityTier", "with_solidarity_tiers"]


class SolidarityTier(BaseModel):
    """Ordinary contribution of a fund for employers up to a headcount.

    Attributes:
        max_employees: Largest average headcount of the tier; ``None`` is
            the open tier.
        employer_rate: Share the employer pays.
        employee_rate: Share the worker pays, withheld from the pay.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_employees: int | None = Field(default=None, ge=1)
    employer_rate: PercentageRate
    employee_rate: PercentageRate


class SolidarityFund(BaseModel):
    """Ordinary contribution of a solidarity fund on the INPS base.

    Attributes:
        code: Short name of the fund.
        employer_rate: Share of a fund on top of the sector rates the
            employer pays, charged to the permanent workers.
        employee_rate: Share of that fund the worker pays.
        wage_integration_tiers: Rates by headcount of a fund in place of
            the wage-integration shares (FIS, CIGS) of the sector rates:
            the tier of the employer replaces those shares in the INPS rates
            of every worker, apprentices and fixed terms included.
        provenance: Source of the rates and of the workers they cover.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    employer_rate: PercentageRate | None = None
    employee_rate: PercentageRate | None = None
    wage_integration_tiers: tuple[SolidarityTier, ...] = ()
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_shape(self) -> Self:
        flat = self.employer_rate is not None and self.employee_rate is not None
        partial = (self.employer_rate is None) != (self.employee_rate is None)
        tiered = bool(self.wage_integration_tiers)
        if partial or flat == tiered:
            msg = (
                "a solidarity fund has either an employer and an employee rate "
                "or wage_integration_tiers"
            )
            raise ValueError(msg)
        open_tiers = sum(t.max_employees is None for t in self.wage_integration_tiers)
        if tiered and open_tiers != 1:
            msg = "wage_integration_tiers need exactly one open tier"
            raise ValueError(msg)
        return self

    def tier(self, headcount: int) -> SolidarityTier:
        """Return the tier of an employer of ``headcount`` employees.

        Returns:
            The narrowest tier whose ``max_employees`` covers the headcount,
            else the open tier.
        """
        bounded = sorted(
            (t for t in self.wage_integration_tiers if t.max_employees is not None),
            key=lambda t: t.max_employees or 0,
        )
        for tier in bounded:
            if tier.max_employees is not None and headcount <= tier.max_employees:
                return tier
        return next(t for t in self.wage_integration_tiers if t.max_employees is None)


def with_solidarity_tiers(
    rules: YearRules, fund: SolidarityFund | None, headcount: int
) -> YearRules:
    """Return ``rules`` with the fund's tier in place of the FIS and CIGS shares.

    The shares of the sector rates and the tier of the fund are both
    unreduced: the cut of art. 29 c. 8-bis D.Lgs. 148/2015 that
    ``EmployerProfile.fis_reduction`` applies to the rates is the cut the
    fund grants too (INPS circ. 5/2025 p. 3: 0.50% down to 0.30% for the
    Fondo delle attività professionali), so it stays right after the swap.

    Returns:
        ``rules`` unchanged without a tiered fund or INPS rates; else the
        employee, employer and apprentice rates moved by the tier less the
        wage-integration shares of the headcount.
    """
    if fund is None or not fund.wage_integration_tiers or rules.inps is None:
        return rules
    tier = fund.tier(headcount)
    inps = rules.inps
    employer = tier.employer_rate - inps.wage_integration_employer_rate
    employee = tier.employee_rate - inps.wage_integration_employee_rate
    swapped = inps.model_copy(
        update={
            "employee_rate": inps.employee_rate + employee,
            "employer_rate": inps.employer_rate + employer,
            "employer_rate_by_category": {
                category: rate + employer
                for category, rate in inps.employer_rate_by_category.items()
            },
            "wage_integration_employer_rate": tier.employer_rate,
            "wage_integration_employee_rate": tier.employee_rate,
        }
    )
    apprentice = rules.apprentice
    if apprentice is not None:
        apprentice = apprentice.model_copy(
            update={
                "employee_rate": apprentice.employee_rate + employee,
                "employer_rate_months_0_11": apprentice.employer_rate_months_0_11
                + employer,
                "employer_rate_months_12_23": apprentice.employer_rate_months_12_23
                + employer,
                "employer_rate_after": apprentice.employer_rate_after + employer,
            }
        )
    return rules.model_copy(update={"inps": swapped, "apprentice": apprentice})
