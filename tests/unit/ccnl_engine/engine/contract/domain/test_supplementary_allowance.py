"""Tests for AgreementKind and SupplementaryAllowance provenance/kind fields."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.engine.contract.domain.ccnl import (
    AgreementKind,
    SupplementaryAllowance,
)


class TestAgreementKind:
    """AgreementKind enum covers company and territorial variants."""

    def test_company_value(self) -> None:
        """COMPANY member serialises to 'company'."""
        assert AgreementKind.COMPANY.value == "company"

    def test_territorial_value(self) -> None:
        """TERRITORIAL member serialises to 'territorial'."""
        assert AgreementKind.TERRITORIAL.value == "territorial"

    def test_round_trip(self) -> None:
        """AgreementKind round-trips from its string value."""
        assert AgreementKind("company") is AgreementKind.COMPANY
        assert AgreementKind("territorial") is AgreementKind.TERRITORIAL

    def test_unknown_value_raises(self) -> None:
        """Unknown string raises ValueError."""
        with pytest.raises(ValueError, match="'national' is not a valid AgreementKind"):
            AgreementKind("national")


class TestSupplementaryAllowanceKindProvenance:
    """kind and provenance fields on SupplementaryAllowance are optional."""

    def test_no_kind_no_provenance_defaults(self) -> None:
        """Existing callers without kind/provenance continue to work."""
        sa = SupplementaryAllowance(
            code="ERT",
            description="Elemento territoriale",
            monthly=Decimal("100.00"),
        )
        assert sa.kind is None
        assert sa.provenance is None

    def test_kind_company(self) -> None:
        """kind=COMPANY is accepted and stored."""
        sa = SupplementaryAllowance(
            code="PDA",
            description="Premio di risultato aziendale",
            monthly=Decimal("200.00"),
            kind=AgreementKind.COMPANY,
        )
        assert sa.kind is AgreementKind.COMPANY

    def test_kind_territorial(self) -> None:
        """kind=TERRITORIAL is accepted and stored."""
        sa = SupplementaryAllowance(
            code="ERT",
            description="Elemento retributivo territoriale",
            monthly=Decimal("80.00"),
            kind=AgreementKind.TERRITORIAL,
        )
        assert sa.kind is AgreementKind.TERRITORIAL

    def test_provenance_is_none_by_default(self) -> None:
        """Provenance defaults to None; the field exists."""
        sa = SupplementaryAllowance(
            code="PDR",
            description="Premio di risultato",
            monthly=Decimal("150.00"),
        )
        assert sa.provenance is None

    def test_provenance_accepted_from_dict(self) -> None:
        """Provenance field accepts a valid provenance dict via model_validate."""
        data = {
            "code": "IND_TER",
            "description": "Indennità territoriale",
            "monthly": "50.00",
            "kind": "territorial",
            "provenance": None,
        }
        sa = SupplementaryAllowance.model_validate(data)
        assert sa.kind is AgreementKind.TERRITORIAL
        assert sa.provenance is None

    def test_json_round_trip_with_kind(self) -> None:
        """Serialise to JSON and back with kind set."""
        sa = SupplementaryAllowance(
            code="ERT",
            description="Elemento territoriale",
            monthly=Decimal("75.00"),
            kind=AgreementKind.TERRITORIAL,
        )
        data = sa.model_dump()
        assert data["kind"] == "territorial"
        reloaded = SupplementaryAllowance.model_validate(data)
        assert reloaded.kind is AgreementKind.TERRITORIAL

    def test_extra_fields_forbidden(self) -> None:
        """extra='forbid' config still rejects unknown fields."""
        with pytest.raises(ValidationError):
            SupplementaryAllowance.model_validate({
                "code": "X",
                "description": "Test",
                "monthly": "100",
                "unknown_field": True,
            })
