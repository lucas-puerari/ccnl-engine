"""Tests for _posting_service.post()."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application._posting_service import post
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry, PostingIntent
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod

_CP = CompetencePeriod(year=2026, month=1)
_DATE = date(2026, 1, 28)
_D = Decimal
_DEFAULT_AMOUNT = _D("1000")


def _intent(
    entry_id: str,
    source_item_id: str = "item_1",
    pay_item_kind: str = "base_salary_earning",
    account: AccountKind = AccountKind.CASH_EARNINGS,
    amount: Decimal = _DEFAULT_AMOUNT,
    policy_decision_id: str | None = "pol_001",
    note: str = "",
) -> PostingIntent:
    return PostingIntent(
        entry_id=entry_id,
        source_item_id=source_item_id,
        pay_item_kind=pay_item_kind,
        account=account,
        amount=amount,
        policy_decision_id=policy_decision_id,
        note=note,
    )


class TestPost:
    """post() converts PostingIntent tuples to LedgerEntry tuples."""

    def test_empty_intents_returns_empty_tuple(self) -> None:
        """Empty input produces empty output."""
        result = post((), _CP, _DATE)
        assert result == ()

    def test_single_intent_produces_single_entry(self) -> None:
        """One intent produces one entry with all fields mapped correctly."""
        intent = _intent("cash_001", amount=_D("500"), policy_decision_id="p1")
        (entry,) = post((intent,), _CP, _DATE)

        assert isinstance(entry, LedgerEntry)
        assert entry.entry_id == "cash_001"
        assert entry.competence_period == _CP
        assert entry.payment_date == _DATE
        assert entry.pay_item_id == "item_1"
        assert entry.pay_item_kind == "base_salary_earning"
        assert entry.account == AccountKind.CASH_EARNINGS
        assert entry.amount == _D("500")
        assert entry.source_item_id == "item_1"
        assert entry.policy_decision_id == "p1"
        assert not entry.note

    def test_multiple_intents_preserve_order(self) -> None:
        """Output order matches input order."""
        intents = (
            _intent("e1", amount=_D("100")),
            _intent("e2", amount=_D("200")),
            _intent("e3", amount=_D("300")),
        )
        entries = post(intents, _CP, _DATE)
        assert len(entries) == 3
        assert [e.entry_id for e in entries] == ["e1", "e2", "e3"]
        assert [e.amount for e in entries] == [_D("100"), _D("200"), _D("300")]

    def test_period_and_date_applied_uniformly(self) -> None:
        """All entries share the same cp and payment_date."""
        intents = (_intent("a"), _intent("b"))
        entries = post(intents, _CP, _DATE)
        for entry in entries:
            assert entry.competence_period == _CP
            assert entry.payment_date == _DATE

    def test_none_policy_decision_id(self) -> None:
        """None policy_decision_id passes through."""
        intent = _intent("x", policy_decision_id=None)
        (entry,) = post((intent,), _CP, _DATE)
        assert entry.policy_decision_id is None

    def test_note_field_passes_through(self) -> None:
        """Non-empty note is preserved."""
        intent = _intent("y", note="test note")
        (entry,) = post((intent,), _CP, _DATE)
        assert entry.note == "test note"

    def test_duplicate_entry_id_raises(self) -> None:
        """Duplicate entry_id in the batch raises ValueError."""
        intents = (_intent("dup"), _intent("dup"))
        with pytest.raises(ValueError, match="Duplicate entry_id"):
            post(intents, _CP, _DATE)

    def test_duplicate_detected_before_second_occurrence(self) -> None:
        """First occurrence passes; error raised on the duplicate."""
        intents = (_intent("a"), _intent("b"), _intent("a"))
        with pytest.raises(ValueError, match="'a'"):
            post(intents, _CP, _DATE)


class TestPostingIntent:
    """PostingIntent is a frozen value object."""

    def test_fields_accessible(self) -> None:
        """All fields are readable after construction."""
        intent = _intent("eid", source_item_id="sid", amount=_D("42"))
        assert intent.entry_id == "eid"
        assert intent.source_item_id == "sid"
        assert intent.amount == _D("42")
        assert intent.account == AccountKind.CASH_EARNINGS

    def test_default_policy_id_is_none(self) -> None:
        """policy_decision_id defaults to None when omitted."""
        intent = PostingIntent(
            entry_id="e",
            source_item_id="s",
            pay_item_kind="k",
            account=AccountKind.CASH_EARNINGS,
            amount=_D(0),
        )
        assert intent.policy_decision_id is None

    def test_equality(self) -> None:
        """Two intents with same fields are equal."""
        a = _intent("e")
        b = _intent("e")
        assert a == b
