"""Unit tests for the preferential tax regime model and its bundled data."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.provenance.domain.source import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.tax.domain.preferential_regime import (
    EmployerActivity,
    EmploymentSector,
    PreferentialTaxRegime,
)
from ccnl_engine.tax.service.tax_optional_loaders import (
    load_variable_pay_rules,
)

_SOURCE = SourceLocation(
    source_document=SourceDocument(
        document_id="l-199-2025", title="L. 199/2025", kind=SourceKind.LEGGE
    ),
    section="art. 1 c. 7",
)


def _regime(**overrides: object) -> PreferentialTaxRegime:
    fields: dict[str, Any] = {
        "regime_id": "rinnovo",
        "eligible_kinds": frozenset({"contract_renewal_earning"}),
        "valid_from_year": 2026,
        "valid_until_year": 2026,
        "flat_tax_rate": Decimal("0.05"),
        "income_ceiling": Decimal(33_000),
        "income_reference_year": 2025,
        "required_sector": EmploymentSector.PRIVATE,
        "source": _SOURCE,
    }
    fields.update(overrides)
    return PreferentialTaxRegime(**fields)


class TestPreferentialTaxRegime:
    """Validation and validity window of the generic regime model."""

    def test_in_force_only_within_validity_years(self) -> None:
        """The regime applies only to the tax years it is in force."""
        regime = _regime(valid_from_year=2026, valid_until_year=2027)

        assert [regime.in_force(y) for y in (2025, 2026, 2027, 2028)] == [
            False,
            True,
            True,
            False,
        ]

    def test_rejects_reversed_validity_years(self) -> None:
        """A validity window ending before it starts is rejected."""
        with pytest.raises(ValidationError, match="is after"):
            _regime(valid_from_year=2027, valid_until_year=2026)

    @pytest.mark.parametrize(
        ("ceiling", "reference_year"),
        [(Decimal(33_000), None), (None, 2025)],
    )
    def test_income_ceiling_needs_reference_year(
        self, ceiling: Decimal | None, reference_year: int | None
    ) -> None:
        """An income ceiling is meaningless without its reference year."""
        with pytest.raises(ValidationError, match="set together"):
            _regime(income_ceiling=ceiling, income_reference_year=reference_year)

    def test_regime_without_income_requirement_is_valid(self) -> None:
        """A regime may have no income requirement at all."""
        regime = _regime(income_ceiling=None, income_reference_year=None)

        assert regime.income_ceiling is None

    @pytest.mark.parametrize(
        ("signed_from", "signed_until"),
        [(date(2024, 1, 1), None), (None, date(2026, 12, 31))],
    )
    def test_signing_window_needs_both_dates(
        self, signed_from: date | None, signed_until: date | None
    ) -> None:
        """A signing window is given by both its dates or not at all."""
        with pytest.raises(ValidationError, match="go together"):
            _regime(
                agreements_signed_from=signed_from,
                agreements_signed_until=signed_until,
            )

    def test_rejects_reversed_signing_window(self) -> None:
        """A signing window ending before it starts is rejected."""
        with pytest.raises(ValidationError, match="is after"):
            _regime(
                agreements_signed_from=date(2026, 1, 1),
                agreements_signed_until=date(2025, 12, 31),
            )

    def test_without_signing_window_every_date_qualifies(self) -> None:
        """A regime without a signing window accepts any signing date."""
        regime = _regime()

        assert not regime.has_signing_window
        assert regime.signed_within_window(date(1990, 1, 1))

    @pytest.mark.parametrize(
        "overrides",
        [
            {"regime_id": "Rinnovo"},
            {"eligible_kinds": frozenset()},
            {"flat_tax_rate": Decimal(0)},
            {"annual_cap": Decimal(0)},
            {"unexpected": True},
        ],
    )
    def test_rejects_invalid_fields(self, overrides: dict[str, Any]) -> None:
        """Malformed ids, empty kinds, zero rate or cap and extras are rejected."""
        with pytest.raises(ValidationError):
            _regime(**overrides)


class TestBundledRinnovoRegime:
    """The bundled data transcribe L. 199/2025 art. 1 c. 7."""

    def test_parameters_match_the_statute(self) -> None:
        """5%, 33,000 EUR on 2025 income, private sector, waivable, no cap."""
        rinnovo = load_variable_pay_rules(2026).rinnovo

        assert rinnovo.flat_tax_rate == Decimal("0.05")
        assert rinnovo.income_ceiling == Decimal(33_000)
        assert rinnovo.income_reference_year == 2025
        assert rinnovo.required_sector is EmploymentSector.PRIVATE
        assert rinnovo.waivable is True
        assert rinnovo.annual_cap is None
        assert (rinnovo.valid_from_year, rinnovo.valid_until_year) == (2026, 2026)
        assert rinnovo.eligible_kinds == {"contract_renewal_earning"}
        assert (rinnovo.agreements_signed_from, rinnovo.agreements_signed_until) == (
            date(2024, 1, 1),
            date(2026, 12, 31),
        )
        assert rinnovo.source.section == "art. 1 c. 7"
        assert rinnovo.ruleset is not None


class TestBundledWorkTimeRegime:
    """The bundled data transcribe L. 199/2025 art. 1 cc. 10-11 and 18."""

    def test_excludes_the_activities_of_comma_18(self) -> None:
        """Food and beverage service, tourism and thermal establishments."""
        regime = load_variable_pay_rules(2026).notte_festivi_turni

        assert regime.excluded_activities == {
            EmployerActivity.FOOD_AND_BEVERAGE_SERVICE,
            EmployerActivity.TOURISM,
            EmployerActivity.THERMAL_ESTABLISHMENT,
        }
        assert not regime.has_signing_window
