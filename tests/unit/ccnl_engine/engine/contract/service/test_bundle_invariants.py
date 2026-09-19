"""Parametric bundle invariant tests over all 125 bundled CCNL data files.

Each test class runs once per CCNL and verifies a structural or data-quality
invariant not already enforced by Pydantic validators at parse time.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.contract.service.discovery import list_ccnls
from ccnl_engine.engine.contract.service.loaders import load_ccnl

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL

# Load all CCNLs once at collection time; load_ccnl is cached so this is cheap.
_ALL_CCNL: list[CCNL] = [load_ccnl(ci.ccnl_id + ".json") for ci in list_ccnls()]

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# Salary table range: EUR 100-10000 per month.
_SALARY_MIN = Decimal(100)
_SALARY_MAX = Decimal(10000)

# Hourly divisor: valid Italian CCNL range 100-250 hours per month.
_DIVISOR_MIN = Decimal(100)
_DIVISOR_MAX = Decimal(250)

# Additional months: Italian CCNL always adds 1-4 extra months (13th-16th).
_MONTHS_MIN = Decimal(12)
_MONTHS_MAX = Decimal(16)


class TestBundleSize:
    """The bundle must contain the expected number of CCNL files."""

    def test_bundle_contains_125_ccnl(self) -> None:
        """Exactly 125 CCNL data files must be present in the bundle."""
        assert len(_ALL_CCNL) == 125


@pytest.mark.parametrize("ccnl", _ALL_CCNL, ids=lambda c: c.meta.ccnl_id)
class TestRulesetIdentity:
    """Ruleset identity must be complete and carry a valid SHA-256 hash."""

    def test_ruleset_present(self, ccnl: CCNL) -> None:
        """Every CCNL must carry a non-None ruleset identity."""
        assert ccnl.ruleset is not None

    def test_ruleset_hash_is_sha256(self, ccnl: CCNL) -> None:
        """source_hash must be a 64-character lowercase hex SHA-256 digest."""
        assert ccnl.ruleset is not None
        assert _SHA256_RE.match(ccnl.ruleset.source_hash) is not None

    def test_ruleset_id_contains_ccnl_id(self, ccnl: CCNL) -> None:
        """ruleset.id must embed the contract's ccnl_id slug."""
        assert ccnl.ruleset is not None
        assert ccnl.meta.ccnl_id in ccnl.ruleset.id


@pytest.mark.parametrize("ccnl", _ALL_CCNL, ids=lambda c: c.meta.ccnl_id)
class TestLevelStructure:
    """Level codes and orders must be unique; salary series must be well-formed."""

    def test_level_codes_unique(self, ccnl: CCNL) -> None:
        """Level codes must be unique within a CCNL."""
        codes = [lv.code for lv in ccnl.levels]
        assert len(codes) == len(set(codes))

    def test_level_orders_unique(self, ccnl: CCNL) -> None:
        """Level order values must be unique within a CCNL."""
        orders = [lv.order for lv in ccnl.levels]
        assert len(orders) == len(set(orders))

    def test_base_salary_last_period_open_ended(self, ccnl: CCNL) -> None:
        """The last base_salary period of each level must be open-ended."""
        for lv in ccnl.levels:
            assert lv.base_salary.periods[-1].valid_until is None

    def test_base_salary_has_no_gaps(self, ccnl: CCNL) -> None:
        """Base salary periods must not be gap periods."""
        for lv in ccnl.levels:
            for p in lv.base_salary.periods:
                assert not p.is_gap, f"level {lv.code}: unexpected gap {p.gap_kind}"

    def test_base_salary_values_positive(self, ccnl: CCNL) -> None:
        """All base salary values must be strictly positive."""
        for lv in ccnl.levels:
            for p in lv.base_salary.periods:
                assert p.value is not None
                assert p.value > Decimal(0), f"level {lv.code}: {p.value}"

    def test_base_salary_values_in_range(self, ccnl: CCNL) -> None:
        """Base salary values must be within 100-10000 EUR per month."""
        for lv in ccnl.levels:
            for p in lv.base_salary.periods:
                assert p.value is not None
                assert _SALARY_MIN <= p.value <= _SALARY_MAX, (
                    f"level {lv.code}: {p.value} not in [{_SALARY_MIN}, {_SALARY_MAX}]"
                )


@pytest.mark.parametrize("ccnl", _ALL_CCNL, ids=lambda c: c.meta.ccnl_id)
class TestParameters:
    """Contract parameters must be within expected ranges."""

    def test_hourly_divisor_has_no_gaps(self, ccnl: CCNL) -> None:
        """Hourly divisor periods must not be gap periods."""
        for p in ccnl.parameters.hourly_divisor.periods:
            assert not p.is_gap, f"unexpected gap {p.gap_kind}"

    def test_hourly_divisor_in_range(self, ccnl: CCNL) -> None:
        """Hourly divisor must be within 100-250 hours per month."""
        for p in ccnl.parameters.hourly_divisor.periods:
            assert p.value is not None
            assert _DIVISOR_MIN < p.value < _DIVISOR_MAX, (
                f"hourly_divisor {p.value} not in ({_DIVISOR_MIN}, {_DIVISOR_MAX})"
            )

    def test_additional_months_has_no_gaps(self, ccnl: CCNL) -> None:
        """Additional months periods must not be gap periods."""
        for p in ccnl.parameters.additional_months.periods:
            assert not p.is_gap, f"unexpected gap {p.gap_kind}"

    def test_additional_months_in_range(self, ccnl: CCNL) -> None:
        """Additional months must be within 12-16 (13th-16th month payments)."""
        for p in ccnl.parameters.additional_months.periods:
            assert p.value is not None
            assert _MONTHS_MIN <= p.value <= _MONTHS_MAX, (
                f"additional_months {p.value} not in [{_MONTHS_MIN}, {_MONTHS_MAX}]"
            )
