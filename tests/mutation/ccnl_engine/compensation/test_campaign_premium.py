"""The premio di campagna of the Alimentari, Art. 51 ter (PDF p. 120).

FLAI text of the CCNL 2023-2027 (sha256
11792ad3df71999684bae85fea8aaf1e3d492d477043eecc78545b5f41db842c): "un
premio di campagna per i soli lavoratori stagionali addetti ai processi di
lavorazione e trasformazione del pomodoro e piselli freschi", by level from
142.57 (1S) to 61.99 (6) a month; a full month of July 2026 pays the whole
amount.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.inputs import EmploymentPeriod, FixedTerm, WorkerCategory
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()


def _premium(level: str, roles: frozenset[str]) -> list[Decimal]:
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=7),
            payment_date=date(2026, 7, 31),
            employment=Employment(
                ccnl_id="alimentari-federalimentare",
                level_code=level,
                category=WorkerCategory.OPERAIO,
                seniority=new_hire(),
                roles=roles,
                contract_type=FixedTerm(),
                employment_period=EmploymentPeriod(date(2026, 7, 1), date(2026, 9, 30)),
            ),
            employer=EmployerProfile(headcount=Headcount(80)),
            facts=PeriodFacts(regione="IT-72", comune_belfiore="F839"),
        )
    )
    assert not [b for b in result.blockers if "roles" in b.detail]
    return [i.amount for i in result.pay_items if "PREMIO_CAMPAGNA" in i.item_id]


@pytest.mark.parametrize(
    ("level", "amount"), [("2", "102.28"), ("3A", "89.88"), ("6", "61.99")]
)
def test_the_seasonal_campaign_worker_takes_the_premium(
    level: str, amount: str
) -> None:
    """The amount of the level to the role, nothing without it."""
    assert _premium(level, frozenset({"stagionale_campagna"})) == [Decimal(amount)]
    assert _premium(level, frozenset()) == []
