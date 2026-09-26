"""Preferential tax regimes: statutory substitute taxes on selected pay items.

A preferential regime replaces ordinary IRPEF and its surtaxes with a flat
substitute tax on the pay items it covers, for the tax years it is in force
and for the workers who meet its requirements.  Each regime is data: its
parameters are read from the versioned tax bundle.
"""

from __future__ import annotations

from datetime import date  # noqa: TC003
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity  # noqa: TC001
from ccnl_engine.engine.provenance.domain.source import SourceLocation  # noqa: TC001

__all__ = [
    "EmployerActivity",
    "EmploymentSector",
    "PreferentialTaxRegime",
    "SubstituteTaxRegime",
]


class EmploymentSector(StrEnum):
    """Whether the worker is employed in the private or the public sector.

    Attributes:
        PRIVATE: Employer outside the public administrations.
        PUBLIC: Public administration employer (D.Lgs. 165/2001 art. 1 c. 2).
    """

    PRIVATE = "private"
    PUBLIC = "public"


class EmployerActivity(StrEnum):
    """Activity of the employer, where a regime excludes some activities.

    L. 199/2025 art. 1 c. 11 excludes from the night, holiday and shift
    substitute tax the activities of c. 18: "esercizi di somministrazione di
    alimenti e bevande, di cui all'articolo 5 della legge 25 agosto 1991,
    n. 287" and "comparto del turismo, ivi inclusi gli stabilimenti
    termali".  Their workers receive the trattamento integrativo speciale of
    c. 18 instead.

    Attributes:
        FOOD_AND_BEVERAGE_SERVICE: Somministrazione di alimenti e bevande
            (L. 287/1991 art. 5).
        TOURISM: Comparto del turismo, other than thermal establishments.
        THERMAL_ESTABLISHMENT: Stabilimenti termali.
        OTHER: Any activity not listed above.
    """

    FOOD_AND_BEVERAGE_SERVICE = "food_and_beverage_service"
    TOURISM = "tourism"
    THERMAL_ESTABLISHMENT = "thermal_establishment"
    OTHER = "other"


class SubstituteTaxRegime(StrEnum):
    """Preferential regimes a worker can renounce in writing.

    Each value is the ``regime_id`` of a bundled
    :class:`PreferentialTaxRegime`.

    Attributes:
        RINNOVO: Contract-renewal increments (L. 199/2025 art. 1 c. 7).
        NOTTE_FESTIVI_TURNI: Night, holiday and shift supplements
            (L. 199/2025 art. 1 cc. 10-11).
    """

    RINNOVO = "rinnovo"
    NOTTE_FESTIVI_TURNI = "notte_festivi_turni"


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
        excluded_activities: Employer activities the regime does not apply
            to.  When not empty, the activity of the employer is a required
            fact.
        agreements_signed_from: First signing date of an agreement whose
            increments qualify, or ``None`` when the regime has no signing
            window.
        agreements_signed_until: Last signing date of a qualifying
            agreement.  Required with ``agreements_signed_from``.
        source: Normative source of the regime: document, section and quote.
        ruleset: Provenance of the data file the regime was read from.

    Raises:
        ValueError: When the validity years or the signing dates are
            reversed, or when exactly one of ``income_ceiling`` and
            ``income_reference_year``, or of the two signing dates, is set.
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
    excluded_activities: frozenset[EmployerActivity] = frozenset()
    agreements_signed_from: date | None = None
    agreements_signed_until: date | None = None
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
        signed_from, signed_until = (
            self.agreements_signed_from,
            self.agreements_signed_until,
        )
        if (signed_from is None) != (signed_until is None):
            msg = "agreements_signed_from and agreements_signed_until go together"
            raise ValueError(msg)
        if signed_from is not None and signed_until is not None:
            _check_signing_order(signed_from, signed_until)
        return self

    @property
    def has_signing_window(self) -> bool:
        """Whether only agreements signed within a window qualify."""
        return self.agreements_signed_from is not None

    def signed_within_window(self, signed_on: date) -> bool:
        """Return whether an agreement signed on ``signed_on`` qualifies.

        Returns:
            ``True`` when the regime has no signing window, or when
            ``signed_on`` lies within it, bounds included.
        """
        signed_from = self.agreements_signed_from
        signed_until = self.agreements_signed_until
        if signed_from is None or signed_until is None:
            return True
        return signed_from <= signed_on <= signed_until

    def in_force(self, tax_year: int) -> bool:
        """Return whether the regime applies to payments of ``tax_year``.

        Returns:
            ``True`` when ``tax_year`` lies within the validity years.
        """
        return self.valid_from_year <= tax_year <= self.valid_until_year


def _check_signing_order(signed_from: date, signed_until: date) -> None:
    """Reject a signing window whose start follows its end.

    Raises:
        ValueError: When ``signed_from`` is after ``signed_until``.
    """
    if signed_from > signed_until:
        msg = (
            f"agreements_signed_from {signed_from} is after "
            f"agreements_signed_until {signed_until}"
        )
        raise ValueError(msg)
