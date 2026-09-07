"""Tests for Payslip.to_dict / to_json / from_dict / from_json."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    ContractPosition,
    Employee,
    FiscalSimplification,
    Permanent,
    TaxSector,
    WorkArrangement,
    compute,
    load_ccnl,
    load_year_rules,
)
from ccnl_engine.engine.payroll.domain.payslip import Payslip


@pytest.fixture(scope="module")
def payslip() -> Payslip:
    """Return a representative Payslip via a real compute() call.

    Returns:
        A Payslip for CCNL Commercio level 4, 2026, permanent full-time.
    """
    ccnl = load_ccnl("commercio-confcommercio.json")
    rules = load_year_rules(2026, TaxSector.TERZIARIO, 50)
    return compute(
        ccnl,
        rules,
        Employee(
            position=ContractPosition(
                level_code="4",
                as_of=date(2026, 1, 1),
                employment=Permanent(),
            ),
            arrangement=WorkArrangement(),
        ),
    )


@pytest.fixture(scope="module")
def payslip_domestic() -> Payslip:
    """Return a Payslip for lavoro domestico (employer_withholds_irpef=False).

    Returns:
        A Payslip for CCNL Lavoro Domestico level C, 2026, full-time 40h.
    """
    ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
    rules = load_year_rules(2026, TaxSector.LAVORO_DOMESTICO, 1)
    return compute(
        ccnl,
        rules,
        Employee(
            position=ContractPosition(
                level_code="C",
                as_of=date(2026, 1, 1),
                employment=Permanent(),
            ),
            arrangement=WorkArrangement(weekly_hours=Decimal(40)),
        ),
    )


class TestToDict:
    """Unit tests for Payslip.to_dict()."""

    def test_decimal_fields_are_strings(self, payslip: Payslip) -> None:
        """Decimal fields are serialised as strings."""
        d = payslip.to_dict()
        assert isinstance(d["net_annual"], str)
        assert isinstance(d["gross_monthly"], str)

    def test_date_is_iso_string(self, payslip: Payslip) -> None:
        """The as_of date is serialised as an ISO-8601 string."""
        d = payslip.to_dict()
        assert d["as_of"] == "2026-01-01"

    def test_fiscal_simplifications_is_sorted_list(self, payslip: Payslip) -> None:
        """fiscal_simplifications is a sorted list of valid enum value strings."""
        d = payslip.to_dict()
        flist = d["fiscal_simplifications"]
        assert isinstance(flist, list)
        assert flist == sorted(flist)
        for v in flist:
            FiscalSimplification(v)  # raises ValueError if invalid

    def test_none_field_preserved(self, payslip: Payslip) -> None:
        """None values are preserved as None."""
        d = payslip.to_dict()
        assert d["apprenticeship_pct"] is None
        assert d["apprenticeship_under_level_code"] is None

    def test_bool_field_preserved(
        self, payslip: Payslip, payslip_domestic: Payslip
    ) -> None:
        """Bool fields keep their Python bool type."""
        assert payslip.to_dict()["employer_withholds_irpef"] is True
        assert payslip_domestic.to_dict()["employer_withholds_irpef"] is False

    def test_int_fields_preserved(self, payslip: Payslip) -> None:
        """Integer fields remain int."""
        d = payslip.to_dict()
        assert isinstance(d["year"], int)
        assert isinstance(d["seniority_count"], int)


class TestToJson:
    """Unit tests for Payslip.to_json()."""

    def test_returns_valid_json(self, payslip: Payslip) -> None:
        """to_json() returns a parseable JSON string with the expected keys."""
        raw = payslip.to_json()
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)
        assert "net_annual" in parsed


class TestFromDict:
    """Unit tests for Payslip.from_dict()."""

    def test_round_trip_standard(self, payslip: Payslip) -> None:
        """from_dict(to_dict(p)) == p for a standard permanent payslip."""
        assert Payslip.from_dict(payslip.to_dict()) == payslip

    def test_round_trip_domestic(self, payslip_domestic: Payslip) -> None:
        """Round-trip for domestic payslip: withholds=False, ti>0."""
        assert Payslip.from_dict(payslip_domestic.to_dict()) == payslip_domestic

    def test_decimal_fields_restored(self, payslip: Payslip) -> None:
        """Decimal fields come back as Decimal with the same value."""
        restored = Payslip.from_dict(payslip.to_dict())
        assert isinstance(restored.net_annual, Decimal)
        assert restored.net_annual == payslip.net_annual

    def test_date_field_restored(self, payslip: Payslip) -> None:
        """The as_of field comes back as a date object."""
        restored = Payslip.from_dict(payslip.to_dict())
        assert isinstance(restored.as_of, date)
        assert restored.as_of == payslip.as_of

    def test_frozenset_field_restored(self, payslip: Payslip) -> None:
        """fiscal_simplifications comes back as a frozenset."""
        restored = Payslip.from_dict(payslip.to_dict())
        assert isinstance(restored.fiscal_simplifications, frozenset)
        assert restored.fiscal_simplifications == payslip.fiscal_simplifications

    def test_none_decimal_field_restored(self, payslip: Payslip) -> None:
        """apprenticeship_pct (Decimal | None) is restored as None for permanent."""
        assert payslip.apprenticeship_pct is None
        restored = Payslip.from_dict(payslip.to_dict())
        assert restored.apprenticeship_pct is None

    def test_optional_decimal_coerced_when_present(self, payslip: Payslip) -> None:
        """apprenticeship_pct is coerced to Decimal when a non-None value is given."""
        d = payslip.to_dict()
        d["apprenticeship_pct"] = "0.80"
        restored = Payslip.from_dict(d)
        assert restored.apprenticeship_pct == Decimal("0.80")

    def test_missing_key_raises(self, payslip: Payslip) -> None:
        """ValueError is raised when a required field is absent."""
        d = payslip.to_dict()
        del d["net_annual"]
        with pytest.raises(ValueError, match="Missing field"):
            Payslip.from_dict(d)


class TestFromJson:
    """Unit tests for Payslip.from_json()."""

    def test_round_trip(self, payslip: Payslip) -> None:
        """from_json(to_json(p)) == p."""
        assert Payslip.from_json(payslip.to_json()) == payslip

    def test_invalid_json_raises(self) -> None:
        """JSONDecodeError is raised for unparseable input."""
        with pytest.raises(json.JSONDecodeError):
            Payslip.from_json("not json")
