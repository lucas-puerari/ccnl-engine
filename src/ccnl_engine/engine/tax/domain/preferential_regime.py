"""Preferential tax regimes: statutory substitute taxes on selected pay items.

A preferential regime replaces ordinary IRPEF and its surtaxes with a flat
substitute tax on the pay items it covers, for the tax years it is in force
and for the workers who meet its requirements.  Each regime is data: its
parameters are read from the versioned tax bundle.
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.metadata import RulesetIdentity  # noqa: TC001
from ccnl_engine.engine.provenance.domain.source import SourceLocation  # noqa: TC001

__all__ = ["EmploymentSector", "PreferentialTaxRegime"]


class EmploymentSector(StrEnum):
    """Whether the worker is employed in the private or the public sector.

    Attributes:
        PRIVATE: Employer outside the public administrations.
        PUBLIC: Public administration employer (D.Lgs. 165/2001 art. 1 c. 2).
    """

    PRIVATE = "private"
    PUBLIC = "public"


class PreferentialTaxRegime(BaseModel):
    """A statutory substitute tax on selected pay items.

    Attributes:
        regime_id: Stable lower snake case identifier, e.g. ``"rinnovo"``.
        eligible_kinds: Pay item kinds the regime covers, e.g.
            ``{"contract_renewal_earning"}``.
        valid_from_year: First tax year the regime is in force.
        valid_until_year: Last tax year the regime is in force.
        flat_tax_rate: Substitute rate replacing IRPEF and its surtaxes.
        annual_cap: Largest amount per tax year that may take the substitute
            rate; the excess is taxed as ordinary income.  ``None`` when the
            regime has no cap.
        income_ceiling: Largest employment income of
            ``income_reference_year`` that keeps the worker eligible (the
            ceiling itself is eligible).  ``None`` when the regime has no
            income requirement.
        income_reference_year: Tax year whose employment income is compared
            with ``income_ceiling``.  Required with ``income_ceiling``.
        required_sector: Sector the worker must be employed in, or ``None``
            when every sector qualifies.
        waivable: Whether the worker may renounce the regime in writing and
            keep the ordinary taxation.
        source: Normative source of the regime: document, section and quote.
        ruleset: Provenance of the data file the regime was read from.

    Raises:
        ValueError: When the validity years are reversed, or when exactly
            one of ``income_ceiling`` and ``income_reference_year`` is set.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    regime_id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    eligible_kinds: frozenset[str] = Field(min_length=1)
    valid_from_year: int
    valid_until_year: int
    flat_tax_rate: Decimal = Field(gt=Decimal(0), lt=Decimal(1))
    annual_cap: Decimal | None = Field(default=None, gt=Decimal(0))
    income_ceiling: Decimal | None = Field(default=None, gt=Decimal(0))
    income_reference_year: int | None = None
    required_sector: EmploymentSector | None = None
    waivable: bool = True
    source: SourceLocation
    ruleset: RulesetIdentity | None = None

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if self.valid_from_year > self.valid_until_year:
            msg = (
                f"valid_from_year {self.valid_from_year} is after "
                f"valid_until_year {self.valid_until_year}"
            )
            raise ValueError(msg)
        if (self.income_ceiling is None) != (self.income_reference_year is None):
            msg = "income_ceiling and income_reference_year must be set together"
            raise ValueError(msg)
        return self

    def in_force(self, tax_year: int) -> bool:
        """Return whether the regime applies to payments of ``tax_year``.

        Returns:
            ``True`` when ``tax_year`` lies within the validity years.
        """
        return self.valid_from_year <= tax_year <= self.valid_until_year
