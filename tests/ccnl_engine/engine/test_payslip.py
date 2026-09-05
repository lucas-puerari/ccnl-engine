"""Tests for Payslip.to_dict / to_json / from_dict / from_json."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    FiscalSimplification,
    Permanent,
    TaxSector,
    compute,
    load_ccnl,
    load_year_rules,
)
from ccnl_engine.engine.compute import Scenario
from ccnl_engine.engine.payslip import Payslip


def _payslip() -> Payslip:
    """Return a representative Payslip via a real compute() call.

    Returns:
        A Payslip for CCNL Commercio level 4, 2026, permanent full-time.
    """
    ccnl = load_ccnl("commercio-confcommercio.json")
    rules = load_year_rules(2026, TaxSector.TERZIARIO, 50)
    scenario = Scenario(
        level_code="4",
        as_of=date(2026, 1, 1),
        employment=Permanent(),
        num_employees=50,
    )
    return compute(ccnl, rules, scenario)


def _payslip_domestic() -> Payslip:
    """Return a Payslip for lavoro domestico (employer_withholds_irpef=False).

    Returns:
        A Payslip for CCNL Lavoro Domestico level C, 2026, full-time 40h.
    """
    ccnl = load_ccnl("lavoro-domestico-non-convivente.json")
    rules = load_year_rules(2026, TaxSector.LAVORO_DOMESTICO, 1)
    scenario = Scenario(
        level_code="C",
        as_of=date(2026, 1, 1),
        employment=Permanent(),
        num_employees=1,
        weekly_hours=Decimal(40),
    )
    return compute(ccnl, rules, scenario)


class TestToDict:
    """Unit tests for Payslip.to_dict()."""

    def test_decimal_fields_are_strings(self) -> None:
        """Decimal fields are serialised as strings."""
        d = _payslip().to_dict()
        assert isinstance(d["net_annual"], str)
        assert isinstance(d["gross_monthly"], str)

    def test_date_is_iso_string(self) -> None:
        """The as_of date is serialised as an ISO-8601 string."""
        d = _payslip().to_dict()
        assert d["as_of"] == "2026-01-01"

    def test_fiscal_simplifications_is_sorted_list(self) -> None:
        """fiscal_simplifications is a sorted list of valid enum value strings."""
        d = _payslip().to_dict()
        flist = d["fiscal_simplifications"]
        assert isinstance(flist, list)
        assert flist == sorted(flist)
        for v in flist:
            FiscalSimplification(v)  # raises ValueError if invalid

    def test_none_field_preserved(self) -> None:
        """None values are preserved as None."""
        d = _payslip().to_dict()
        assert d["apprenticeship_pct"] is None
        assert d["apprenticeship_under_level_code"] is None

    def test_bool_field_preserved(self) -> None:
        """Bool fields keep their Python bool type."""
        d = _payslip().to_dict()
        assert d["employer_withholds_irpef"] is True
        d2 = _payslip_domestic().to_dict()
        assert d2["employer_withholds_irpef"] is False

    def test_int_fields_preserved(self) -> None:
        """Integer fields remain int."""
        d = _payslip().to_dict()
        assert isinstance(d["year"], int)
        assert isinstance(d["seniority_count"], int)


class TestToJson:
    """Unit tests for Payslip.to_json()."""

    def test_returns_valid_json(self) -> None:
        """to_json() returns a parseable JSON string with the expected keys."""
        raw = _payslip().to_json()
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)
        assert "net_annual" in parsed

    def test_round_trip_via_json_string(self) -> None:
        """from_json(to_json(p)) == p."""
        original = _payslip()
        restored = Payslip.from_json(original.to_json())
        assert restored == original


class TestFromDict:
    """Unit tests for Payslip.from_dict()."""

    def test_round_trip_standard(self) -> None:
        """from_dict(to_dict(p)) == p for a standard permanent payslip."""
        original = _payslip()
        restored = Payslip.from_dict(original.to_dict())
        assert restored == original

    def test_round_trip_domestic(self) -> None:
        """Round-trip for domestic payslip: withholds=False, ti>0."""
        original = _payslip_domestic()
        restored = Payslip.from_dict(original.to_dict())
        assert restored == original

    def test_decimal_fields_restored(self) -> None:
        """Decimal fields come back as Decimal with the same value."""
        original = _payslip()
        restored = Payslip.from_dict(original.to_dict())
        assert isinstance(restored.net_annual, Decimal)
        assert restored.net_annual == original.net_annual

    def test_date_field_restored(self) -> None:
        """The as_of field comes back as a date object."""
        original = _payslip()
        restored = Payslip.from_dict(original.to_dict())
        assert isinstance(restored.as_of, date)
        assert restored.as_of == original.as_of

    def test_frozenset_field_restored(self) -> None:
        """fiscal_simplifications comes back as a frozenset."""
        original = _payslip()
        restored = Payslip.from_dict(original.to_dict())
        assert isinstance(restored.fiscal_simplifications, frozenset)
        assert restored.fiscal_simplifications == original.fiscal_simplifications

    def test_none_decimal_field_restored(self) -> None:
        """apprenticeship_pct (Decimal | None) is restored as None for permanent."""
        original = _payslip()
        assert original.apprenticeship_pct is None
        restored = Payslip.from_dict(original.to_dict())
        assert restored.apprenticeship_pct is None

    def test_missing_key_raises(self) -> None:
        """KeyError is raised when a required field is absent."""
        d = _payslip().to_dict()
        del d["net_annual"]
        with pytest.raises(KeyError):
            Payslip.from_dict(d)


class TestFromJson:
    """Unit tests for Payslip.from_json()."""

    def test_round_trip(self) -> None:
        """from_json(to_json(p)) == p."""
        original = _payslip()
        assert Payslip.from_json(original.to_json()) == original

    def test_invalid_json_raises(self) -> None:
        """JSONDecodeError is raised for unparseable input."""
        with pytest.raises(json.JSONDecodeError):
            Payslip.from_json("not json")
