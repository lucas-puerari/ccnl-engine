"""Fixed monthly social-cooperative elements require an attested role.

Legacoopsociali consolidated text, PDF pp. 84, 93, 109-111, sha256
3ed1d09098959f8b7fb50da86d4f6f1bf3a22023bf1d8852614899ed88919440.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WorkerCategory
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()


def _month(
    year: int, month: int, roles: frozenset[str], level: str = "D2"
) -> dict[str, Decimal]:
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year, month),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_id="cooperative-sociali",
                level_code=level,
                category=WorkerCategory.IMPIEGATO,
                seniority=new_hire(2025),
                roles=roles,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2025, 1, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )
    return {item.item_id: item.amount for item in result.pay_items}


def test_february_2026_fixed_elements_are_paid_only_to_eligible_roles() -> None:
    """D2 1727.83 + nurse 154.94 + stay 77.47 + assignment 50 + cash 30.99 = 2041.23."""
    roles = frozenset({
        "infermiere",
        "reperibilita_struttura",
        "affiancamento_inserimento",
        "maneggio_denaro",
    })
    items = _month(2026, 2, roles)
    bare = _month(2026, 2, frozenset())
    for code, amount in (
        ("IND_PROF_INFERMIERE", Decimal("154.94")),
        ("IND_REPERIBILITA_STRUTTURA", Decimal("77.47")),
        ("IND_AFFIANCAMENTO", Decimal("50.00")),
        ("IND_CASSA", Decimal("30.99")),
    ):
        assert [value for key, value in items.items() if code in key] == [amount]
        assert not any(code in key for key in bare)
    assert sum(
        (
            value
            for key, value in items.items()
            if any(
                code in key
                for code in (
                    "IND_PROF_INFERMIERE",
                    "IND_REPERIBILITA_STRUTTURA",
                    "IND_AFFIANCAMENTO",
                    "IND_CASSA",
                )
            )
        ),
        Decimal("1727.83"),
    ) == Decimal("2041.23")


def test_educator_etdr_expires_in_2026() -> None:
    """The D1 ETDR of 82 in September 2025 is zero from January 2026."""
    assert not any(
        "ETDR_EDUCATORE" in key
        for key in _month(2026, 1, frozenset({"educatore_etdr"}), "D1")
    )
