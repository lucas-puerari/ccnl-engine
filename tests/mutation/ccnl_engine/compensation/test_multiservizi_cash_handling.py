"""Art. 24 cash-handling allowance on tabellare for a qualifying role."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.rules import _level_chain

_CCNL = load_ccnl("multiservizi-anip")
_MONTH = date(2025, 7, 1)
_ROLE = frozenset({"maneggio_denaro"})


@pytest.mark.parametrize(
    ("level", "expected"),
    [
        ("1", "21.45"),
        ("2", "23.38"),
        ("2par115", "24.66"),
        ("3", "25.31"),
        ("4par125", "26.81"),
        ("4", "27.45"),
        ("5", "30.02"),
        ("6", "37.32"),
        ("7", "43.11"),
        ("Q", "47.18"),
    ],
)
def test_qualifying_cash_handler_month(level: str, expected: str) -> None:
    """July 2025 level 2: EUR 779.21 tabellare * 3% = EUR 23.38."""
    chain = _level_chain(
        _CCNL, _CCNL.level_by_code(level), 0, _ROLE, _MONTH, is_apprentice=False
    )
    assert {a.code: amount for a, amount in chain.allowances}[
        "CASH_HANDLING"
    ] == Decimal(expected)


def test_no_cash_handling_duty_no_payment() -> None:
    """July 2025 level 2: without the role, EUR 23.38 becomes EUR 0."""
    chain = _level_chain(
        _CCNL,
        _CCNL.level_by_code("2"),
        0,
        frozenset(),
        _MONTH,
        is_apprentice=False,
    )
    assert "CASH_HANDLING" not in {a.code for a, _ in chain.allowances}


def test_cash_allowance_excludes_personal_elements() -> None:
    """July 2025 level 2: even with EUR 100 personal, 779.21 * 3% = 23.38."""
    level = _CCNL.level_by_code("2")
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
    amended = level.model_copy(
        update={"fixed_allowances": (*level.fixed_allowances, personal)}
    )
    chain = _level_chain(_CCNL, amended, 0, _ROLE, _MONTH, is_apprentice=False)
    assert {a.code: amount for a, amount in chain.allowances}[
        "CASH_HANDLING"
    ] == Decimal("23.38")
