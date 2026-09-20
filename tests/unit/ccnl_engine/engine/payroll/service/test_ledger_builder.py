"""Unit tests for ledger_builder.post_earnings."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.payroll.domain.bundle import make_bundle
from ccnl_engine.engine.payroll.domain.calculation import Calculation
from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger
from ccnl_engine.engine.payroll.service.gross import GrossPay
from ccnl_engine.engine.payroll.service.ledger_builder import post_earnings
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual
from ccnl_engine.engine.payroll.service.types import MonthlyPayChain
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _DATE,
    _RULES,
    _allowance,
    _build_ccnl,
    _req,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL

_DEFAULT_CCNL = _build_ccnl()
_CCNL_WITH_ALLOWANCE = _build_ccnl(**{
    "levels.2.fixed_allowances": [_allowance("edr", "10.33")]
})
_CCNL_TWO_ALLOWANCES = _build_ccnl(**{
    "levels.2.fixed_allowances": [
        _allowance("edr", "10.33"),
        _allowance("ind", "50.00"),
    ]
})

_KIND_ALLOWANCE = "fixed_allowance_earning"


def _calc(
    level_code: str = "4",
    seniority_count: int | None = None,
    ccnl: CCNL = _DEFAULT_CCNL,
) -> Calculation:
    """Run estimate_annual and return the Calculation.

    Returns:
        The resulting :class:`Calculation`.
    """
    bundle = make_bundle(ccnl, _RULES, None)
    return estimate_annual(
        _req(level_code=level_code, seniority_count=seniority_count),
        bundle=bundle,
    )


class TestPostEarningsBaseSalary:
    """post_earnings posts base salary as a GROSS_EARNINGS entry."""

    def test_base_salary_entry_exists(self) -> None:
        """A base_salary_earning entry is posted for non-zero base."""
        calc = _calc()
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert "base_salary_earning" in kinds

    def test_base_salary_amount_matches(self) -> None:
        """The base salary entry amount matches the chain.base value."""
        calc = _calc()
        base_entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == "base_salary_earning"
        )
        assert base_entry.amount == Decimal("1000.00")

    def test_base_salary_account(self) -> None:
        """Base salary is posted to the GROSS_EARNINGS account."""
        calc = _calc()
        base_entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == "base_salary_earning"
        )
        assert base_entry.account == AccountKind.GROSS_EARNINGS

    def test_base_salary_competence_period(self) -> None:
        """Competence period matches the as_of date."""
        calc = _calc()
        base_entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == "base_salary_earning"
        )
        assert base_entry.competence_period.year == _DATE.year
        assert base_entry.competence_period.month == _DATE.month

    def test_base_salary_entry_id_format(self) -> None:
        """entry_id follows the base_salary_{year}_{month:02d} pattern."""
        calc = _calc()
        base_entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == "base_salary_earning"
        )
        assert base_entry.entry_id == f"base_salary_{_DATE.year}_{_DATE.month:02d}"


class TestPostEarningsSeniority:
    """post_earnings posts seniority only when the amount is non-zero."""

    def test_no_seniority_entry_when_zero(self) -> None:
        """seniority_earning is absent when count=0 (no increment applies)."""
        calc = _calc(seniority_count=0)
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert "seniority_earning" not in kinds

    def test_seniority_entry_present_when_nonzero(self) -> None:
        """seniority_earning is posted when at least one increment applies."""
        calc = _calc(seniority_count=1)
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert "seniority_earning" in kinds

    def test_seniority_amount_matches(self) -> None:
        """Seniority entry amount equals one increment of 20.00."""
        calc = _calc(seniority_count=1)
        sen_entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == "seniority_earning"
        )
        assert sen_entry.amount == Decimal("20.00")

    def test_seniority_account(self) -> None:
        """Seniority is posted to GROSS_EARNINGS."""
        calc = _calc(seniority_count=1)
        sen_entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == "seniority_earning"
        )
        assert sen_entry.account == AccountKind.GROSS_EARNINGS

    def test_seniority_note_records_count(self) -> None:
        """Note field records the seniority count."""
        calc = _calc(seniority_count=2)
        sen_entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == "seniority_earning"
        )
        assert "count=2" in sen_entry.note

    def test_level_without_seniority_has_no_entry(self) -> None:
        """Level with no seniority increments produces no seniority_earning."""
        calc = _calc(level_code="3")
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert "seniority_earning" not in kinds


class TestPostEarningsAllowances:
    """post_earnings posts one fixed_allowance_earning per non-zero allowance."""

    def test_no_allowance_entries_when_none(self) -> None:
        """No fixed_allowance_earning when the level has no allowances."""
        calc = _calc()
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert _KIND_ALLOWANCE not in kinds

    def test_single_allowance_produces_one_entry(self) -> None:
        """One allowance yields exactly one fixed_allowance_earning."""
        calc = _calc(ccnl=_CCNL_WITH_ALLOWANCE)
        allowance_entries = [
            e for e in calc.ledger_entries if e.pay_item_kind == _KIND_ALLOWANCE
        ]
        assert len(allowance_entries) == 1

    def test_allowance_amount_matches(self) -> None:
        """Allowance entry amount equals the configured monthly value."""
        calc = _calc(ccnl=_CCNL_WITH_ALLOWANCE)
        entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == _KIND_ALLOWANCE
        )
        assert entry.amount == Decimal("10.33")

    def test_allowance_account(self) -> None:
        """Allowance is posted to GROSS_EARNINGS."""
        calc = _calc(ccnl=_CCNL_WITH_ALLOWANCE)
        entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == _KIND_ALLOWANCE
        )
        assert entry.account == AccountKind.GROSS_EARNINGS

    def test_allowance_note_contains_code(self) -> None:
        """Note field stores the allowance code."""
        calc = _calc(ccnl=_CCNL_WITH_ALLOWANCE)
        entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == _KIND_ALLOWANCE
        )
        assert entry.note == "edr"

    def test_two_allowances_produce_two_entries(self) -> None:
        """Two allowances yield exactly two fixed_allowance_earning entries."""
        calc = _calc(ccnl=_CCNL_TWO_ALLOWANCES)
        allowance_entries = [
            e for e in calc.ledger_entries if e.pay_item_kind == _KIND_ALLOWANCE
        ]
        assert len(allowance_entries) == 2
        notes = {e.note for e in allowance_entries}
        assert notes == {"edr", "ind"}

    def test_allowance_entry_id_contains_code(self) -> None:
        """entry_id includes the allowance code."""
        calc = _calc(ccnl=_CCNL_WITH_ALLOWANCE)
        entry = next(
            e for e in calc.ledger_entries if e.pay_item_kind == _KIND_ALLOWANCE
        )
        assert "edr" in entry.entry_id


class TestLedgerEntriesOnCalculation:
    """ledger_entries is populated on Calculation and defaults to empty."""

    def test_ledger_entries_is_tuple(self) -> None:
        """ledger_entries is always a tuple."""
        calc = _calc()
        assert isinstance(calc.ledger_entries, tuple)

    def test_all_earnings_entries_have_gross_earnings_account(self) -> None:
        """All GROSS_EARNINGS entries are posted to the GROSS_EARNINGS account."""
        calc = _calc(ccnl=_CCNL_WITH_ALLOWANCE, seniority_count=1)
        earnings = [
            e for e in calc.ledger_entries if e.account == AccountKind.GROSS_EARNINGS
        ]
        assert all(e.account == AccountKind.GROSS_EARNINGS for e in earnings)
        assert len(earnings) >= 1

    def test_base_only_produces_one_gross_earnings_entry(self) -> None:
        """Level 3 with no seniority and no allowances: 1 GROSS_EARNINGS entry."""
        calc = _calc(level_code="3", seniority_count=0)
        earnings = [
            e for e in calc.ledger_entries if e.account == AccountKind.GROSS_EARNINGS
        ]
        assert len(earnings) == 1

    @pytest.mark.parametrize(
        ("level", "seniority_count", "has_allowance", "expected_count"),
        [
            ("4", 0, False, 1),
            ("4", 1, False, 2),
            ("4", 0, True, 2),
            ("4", 1, True, 3),
        ],
    )
    def test_gross_earnings_entry_count(
        self,
        level: str,
        seniority_count: int,
        has_allowance: bool,
        expected_count: int,
    ) -> None:
        """GROSS_EARNINGS entry count matches base + seniority + allowances."""
        ccnl = _CCNL_WITH_ALLOWANCE if has_allowance else _DEFAULT_CCNL
        calc = _calc(level_code=level, seniority_count=seniority_count, ccnl=ccnl)
        earnings = [
            e for e in calc.ledger_entries if e.account == AccountKind.GROSS_EARNINGS
        ]
        assert len(earnings) == expected_count

    def test_from_dict_round_trip_has_empty_ledger(self) -> None:
        """Calculation.from_dict round-trip produces an empty ledger_entries tuple."""
        calc = _calc()
        restored = Calculation.from_dict(calc.to_dict())
        assert restored.ledger_entries == ()


class TestPostEarningsZeroAmounts:
    """post_earnings skips entries whose amount is zero."""

    def _zero_chain_gross(self) -> GrossPay:
        """Build a GrossPay where chain.base and chain.seniority are zero.

        Returns:
            A :class:`GrossPay` with all monetary chain components at zero.
        """
        zero_chain = MonthlyPayChain(
            base=Decimal(0),
            seniority=Decimal(0),
            allowances=(),
        )
        level = _DEFAULT_CCNL.level_by_code("4")
        return GrossPay(
            level=level,
            worker_category=None,
            count=0,
            chain_full_time=zero_chain,
            chain=zero_chain,
            apprenticeship_pct=None,
            under_level_code=None,
            ad_personam=Decimal(0),
            scaled_second_level=(),
            second_level_monthly_total=Decimal(0),
            additional_months=Decimal(12),
            hourly_divisor=Decimal(168),
            gross_monthly=Decimal(0),
            gross_annual=Decimal(0),
            contribution_base=Decimal(0),
            tfr_base=Decimal(0),
        )

    def test_zero_base_produces_no_entry(self) -> None:
        """When chain.base is zero, no base_salary_earning entry is posted."""
        ledger = Ledger()
        post_earnings(self._zero_chain_gross(), _DATE, ledger)
        assert ledger.entries() == ()
