"""INPS and apprentice contribution rate models: tiers, bounds and lookups."""

from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.payroll.service._contributions_apprentice import (
    apprentice_employer_rate,
)
from ccnl_engine.payroll.service._contributions_rates import inps_employer_rate
from ccnl_engine.tax.domain.contribution_rules import ApprenticeRates, InpsRates
from ccnl_engine.tax.domain.contribution_tiers import (
    ApprenticeRawRates,
    InpsEmployeeTier,
    InpsEmployerTier,
    InpsRawRates,
)

_VALID_APPRENTICE: dict[str, Any] = {
    "employee_rate": "0.0584",
    "employee_ivs_rate": "0.0584",
    "employer_rate_months_0_11": "0.0311",
    "employer_ivs_rate_months_0_11": "0.0150",
    "employer_rate_months_12_23": "0.0461",
    "employer_ivs_rate_months_12_23": "0.0300",
    "employer_rate_after": "0.1161",
    "employer_ivs_rate_after": "0.1000",
}


class TestInpsTiers:
    """Unit tests for InpsEmployeeTier and InpsEmployerTier ivs_rate validator."""

    def test_employee_tier_ivs_rate_exceeds_rate_raises(self) -> None:
        """ivs_rate > rate must raise ValidationError."""
        with pytest.raises(ValidationError, match="ivs_rate"):
            InpsEmployeeTier(
                max_employees=None, rate=Decimal("0.09"), ivs_rate=Decimal("0.10")
            )

    def test_employer_tier_ivs_rate_exceeds_rate_raises(self) -> None:
        """ivs_rate > rate must raise ValidationError."""
        with pytest.raises(ValidationError, match="ivs_rate"):
            InpsEmployerTier(
                max_employees=None, rate=Decimal("0.28"), ivs_rate=Decimal("0.30")
            )

    def test_employer_tier_category_rate_below_ivs_rate_raises(self) -> None:
        """rate_by_category value < ivs_rate must raise ValidationError."""
        with pytest.raises(ValidationError, match="rate_by_category"):
            InpsEmployerTier(
                max_employees=None,
                rate=Decimal("0.2693"),
                ivs_rate=Decimal("0.2381"),
                rate_by_category={WorkerCategory.IMPIEGATO: Decimal("0.20")},
            )


class TestInpsRates:
    """Unit tests for InpsRates construction."""

    def test_uncapped(self) -> None:
        """ceiling=None (no cap) is accepted."""
        r = InpsRates(
            employee_rate=Decimal("0.0919"),
            employee_ivs_rate=Decimal("0.0919"),
            employer_rate=Decimal("0.2898"),
            employer_ivs_rate=Decimal("0.2381"),
            ceiling=None,
        )
        assert r.ceiling is None

    def test_with_ceiling(self) -> None:
        """A finite ceiling is accepted."""
        r = InpsRates(
            employee_rate=Decimal("0.09"),
            employee_ivs_rate=Decimal("0.09"),
            employer_rate=Decimal("0.28"),
            employer_ivs_rate=Decimal("0.2381"),
            ceiling=Decimal(105014),
        )
        assert r.ceiling == Decimal(105014)

    def test_employer_rate_for_category(self) -> None:
        """Category override applies only to listed categories."""
        r = InpsRates(
            employee_rate=Decimal("0.0919"),
            employee_ivs_rate=Decimal("0.0919"),
            employer_rate=Decimal("0.2693"),
            employer_ivs_rate=Decimal("0.2381"),
            ceiling=None,
            employer_rate_by_category={WorkerCategory.IMPIEGATO: Decimal("0.2471")},
        )
        assert inps_employer_rate(r, None) == Decimal("0.2693")
        assert inps_employer_rate(r, WorkerCategory.OPERAIO) == Decimal("0.2693")
        assert inps_employer_rate(r, WorkerCategory.IMPIEGATO) == Decimal("0.2471")


class TestApprenticeRates:
    """Unit tests for ApprenticeRates.employer_rate_at() and ivs_rate validators."""

    def test_rate_steps(self) -> None:
        """Employer rate steps at month 12 and month 24."""
        r = ApprenticeRates.model_validate(_VALID_APPRENTICE)
        assert apprentice_employer_rate(r, 0) == Decimal("0.0311")
        assert apprentice_employer_rate(r, 11) == Decimal("0.0311")
        assert apprentice_employer_rate(r, 12) == Decimal("0.0461")
        assert apprentice_employer_rate(r, 23) == Decimal("0.0461")
        assert apprentice_employer_rate(r, 24) == Decimal("0.1161")

    def test_ivs_rate_exceeds_total_raises(self) -> None:
        """Any ivs_rate above its paired total rate must raise ValidationError."""
        with pytest.raises(ValidationError, match=r"ivs_rate.*must not exceed"):
            ApprenticeRates.model_validate({
                **_VALID_APPRENTICE,
                "employer_ivs_rate_after": "0.20",
            })


class TestApprenticeRawRates:
    """ivs_rate validators on ApprenticeRawRates (raw JSON model)."""

    _VALID_RAW: dict[str, Any] = {
        "employee_rate": "0.0584",
        "employee_ivs_rate": "0.0584",
        "employer_rate": "0.1161",
        "employer_ivs_rate": "0.1000",
        "small_firm_max_employees": 9,
        "small_firm_employer_rate_months_0_11": "0.0311",
        "small_firm_employer_ivs_rate_months_0_11": "0.0150",
        "small_firm_employer_rate_months_12_23": "0.0461",
        "small_firm_employer_ivs_rate_months_12_23": "0.0300",
    }

    def test_ivs_rate_exceeds_total_raises(self) -> None:
        """employer_ivs_rate above employer_rate must raise ValidationError."""
        with pytest.raises(ValidationError, match=r"ivs_rate.*must not exceed"):
            ApprenticeRawRates.model_validate({
                **self._VALID_RAW,
                "employer_ivs_rate": "0.20",  # exceeds employer_rate 0.1161
            })


class TestInpsRatesNegativeConstraints:
    """InpsRates and related models must reject negative rates and ceilings."""

    def test_negative_employee_rate_raises(self) -> None:
        """employee_rate < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRates(
                employee_rate=Decimal("-0.1"),
                employee_ivs_rate=Decimal("-0.2"),
                employer_rate=Decimal("-0.1"),
                employer_ivs_rate=Decimal("-0.2"),
                ceiling=None,
            )

    def test_negative_ceiling_raises(self) -> None:
        """Ceiling < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRates(
                employee_rate=Decimal("0.0919"),
                employee_ivs_rate=Decimal("0.0919"),
                employer_rate=Decimal("0.2898"),
                employer_ivs_rate=Decimal("0.2381"),
                ceiling=Decimal(-1),
            )

    def test_zero_ceiling_raises(self) -> None:
        """Ceiling = 0 must raise ValidationError (must be strictly positive)."""
        with pytest.raises(ValidationError):
            InpsRates(
                employee_rate=Decimal("0.0919"),
                employee_ivs_rate=Decimal("0.0919"),
                employer_rate=Decimal("0.2898"),
                employer_ivs_rate=Decimal("0.2381"),
                ceiling=Decimal(0),
            )


class TestInpsRawRatesEmptyTiers:
    """InpsRawRates rejects empty employee_tiers or employer_tiers."""

    _OPEN_EMPLOYEE_TIER: dict[str, Any] = {
        "max_employees": None,
        "rate": "0.0919",
        "ivs_rate": "0.0919",
    }
    _OPEN_EMPLOYER_TIER: dict[str, Any] = {
        "max_employees": None,
        "rate": "0.2898",
        "ivs_rate": "0.2381",
    }

    def test_empty_employee_tiers_raises(self) -> None:
        """Empty employee_tiers must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRawRates.model_validate({
                "employee_tiers": [],
                "employer_tiers": [self._OPEN_EMPLOYER_TIER],
                "ceiling": None,
            })

    def test_empty_employer_tiers_raises(self) -> None:
        """Empty employer_tiers must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRawRates.model_validate({
                "employee_tiers": [self._OPEN_EMPLOYEE_TIER],
                "employer_tiers": [],
                "ceiling": None,
            })

    def test_non_empty_tiers_accepted(self) -> None:
        """Non-empty tiers are accepted."""
        raw = InpsRawRates.model_validate({
            "employee_tiers": [self._OPEN_EMPLOYEE_TIER],
            "employer_tiers": [self._OPEN_EMPLOYER_TIER],
            "ceiling": None,
        })
        assert len(raw.employee_tiers) == 1
        assert len(raw.employer_tiers) == 1


class TestInpsRatesIvsAndAdditional:
    """InpsRates validators: IVS <= total and paired additional fields."""

    _BASE: dict[str, Any] = {
        "employee_rate": "0.0919",
        "employee_ivs_rate": "0.0919",
        "employer_rate": "0.2898",
        "employer_ivs_rate": "0.2381",
        "ceiling": None,
    }

    def test_employee_ivs_exceeds_employee_rate_raises(self) -> None:
        """employee_ivs_rate > employee_rate must raise ValidationError."""
        with pytest.raises(ValidationError, match="employee_ivs_rate"):
            InpsRates(**{**self._BASE, "employee_ivs_rate": "0.30"})

    def test_employer_ivs_exceeds_employer_rate_raises(self) -> None:
        """employer_ivs_rate > employer_rate must raise ValidationError."""
        with pytest.raises(ValidationError, match="employer_ivs_rate"):
            InpsRates(**{**self._BASE, "employer_ivs_rate": "0.40"})

    def test_additional_rate_without_threshold_raises(self) -> None:
        """employee_additional_rate set without threshold must raise."""
        with pytest.raises(ValidationError, match="both be set or both be absent"):
            InpsRates(**{
                **self._BASE,
                "employee_additional_rate": "0.01",
            })

    def test_additional_threshold_without_rate_raises(self) -> None:
        """employee_additional_threshold set without rate must raise."""
        with pytest.raises(ValidationError, match="both be set or both be absent"):
            InpsRates(**{
                **self._BASE,
                "employee_additional_threshold": "56224",
            })

    def test_negative_additional_threshold_raises(self) -> None:
        """employee_additional_threshold < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRates(**{
                **self._BASE,
                "employee_additional_rate": "0.01",
                "employee_additional_threshold": "-1000",
            })

    def test_valid_with_additional_fields(self) -> None:
        """Valid rate+threshold pair is accepted."""
        r = InpsRates(**{
            **self._BASE,
            "employee_additional_rate": "0.01",
            "employee_additional_threshold": "56224",
        })
        assert r.employee_additional_rate == Decimal("0.01")
        assert r.employee_additional_threshold == Decimal(56224)


class TestInpsRawRatesAdditionalThreshold:
    """InpsRawRates rejects a negative employee_additional_threshold."""

    _TIER: dict[str, Any] = {
        "max_employees": None,
        "rate": "0.0919",
        "ivs_rate": "0.0919",
    }

    def test_negative_threshold_raises(self) -> None:
        """employee_additional_threshold < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRawRates(
                employee_tiers=[InpsEmployeeTier.model_validate(self._TIER)],
                employer_tiers=[
                    InpsEmployerTier.model_validate({
                        **self._TIER,
                        "rate": "0.2898",
                        "ivs_rate": "0.2381",
                    })
                ],
                ceiling=None,
                employee_additional_rate=Decimal("0.01"),
                employee_additional_threshold=Decimal(-1000),
            )

    def test_zero_threshold_accepted(self) -> None:
        """employee_additional_threshold = 0 is on the boundary and accepted."""
        raw = InpsRawRates(
            employee_tiers=[InpsEmployeeTier.model_validate(self._TIER)],
            employer_tiers=[
                InpsEmployerTier.model_validate({
                    **self._TIER,
                    "rate": "0.2898",
                    "ivs_rate": "0.2381",
                })
            ],
            ceiling=None,
            employee_additional_rate=Decimal("0.01"),
            employee_additional_threshold=Decimal(0),
        )
        assert raw.employee_additional_threshold == Decimal(0)
