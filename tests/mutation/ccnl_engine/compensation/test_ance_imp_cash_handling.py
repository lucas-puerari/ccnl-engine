"""Art. 50: cash handling with liability for errors."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.rules import _level_chain

_CCNL = load_ccnl("edilizia-ance-impiegati")
_ROLE = frozenset({"cash_handler_with_error_liability"})


@pytest.mark.parametrize(
    ("level", "month", "expected"),
    [
        ("1", date(2025, 2, 1), "126.42"),
        ("1", date(2026, 3, 1), "130.42"),
        ("1", date(2027, 3, 1), "134.42"),
        ("3", date(2025, 2, 1), "152.54"),
        ("3", date(2026, 3, 1), "157.74"),
        ("3", date(2027, 3, 1), "162.94"),
        ("7", date(2025, 2, 1), "213.48"),
        ("7", date(2026, 3, 1), "221.48"),
        ("7", date(2027, 3, 1), "229.48"),
    ],
)
def test_cash_handler_receives_eight_percent_of_only_minimum_and_contingenza(
    level: str, month: date, expected: str
) -> None:
    """Level 3 in March 2026: (1452.56 + 519.16) * .08 = EUR 157.74."""
    chain = _level_chain(
        _CCNL, _CCNL.level_by_code(level), 0, _ROLE, month, is_apprentice=False
    )
    assert {a.code: amount for a, amount in chain.allowances}[
        "CASH_HANDLING"
    ] == Decimal(expected)


def test_cash_percentage_ignores_individual_pay() -> None:
    """Adding EUR 100 individual pay keeps the March 2026 allowance at EUR 157.74."""
    level = _CCNL.level_by_code("3")
    personal = level.fixed_allowances[0].model_copy(
        update={
            "code": "PERSONAL",
            "individual": True,
            "monthly": level.fixed_allowances[0].monthly.model_copy(
                update={
                    "periods": (
                        level
                        .fixed_allowances[0]
                        .monthly.periods[0]
                        .model_copy(update={"value": Decimal(100)}),
                    )
                }
            ),
        }
    )
    with_personal = level.model_copy(
        update={"fixed_allowances": (*level.fixed_allowances, personal)}
    )
    chain = _level_chain(
        _CCNL, with_personal, 0, _ROLE, date(2026, 3, 1), is_apprentice=False
    )
    assert {a.code: value for a, value in chain.allowances}["CASH_HANDLING"] == Decimal(
        "157.74"
    )


def test_only_attested_cash_handlers_are_paid() -> None:
    """Without the liability-bearing role, the EUR 157.74 is not paid."""
    chain = _level_chain(
        _CCNL,
        _CCNL.level_by_code("3"),
        0,
        frozenset(),
        date(2026, 3, 1),
        is_apprentice=False,
    )
    assert "CASH_HANDLING" not in {a.code for a, _ in chain.allowances}
