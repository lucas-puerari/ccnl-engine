"""A seasonal apprentice with a term earns no increment of the operai agricoli.

Allegato 10 (PDF p. 124) allows apprentices 'anche a tempo determinato' in
seasonal cycles; art. 54 grants the increments to 'gli operai a tempo
indeterminato'.  Area1, March 2026, 30 months: a permanent apprentice is
paid the 12.50 increment of the biennium, a fixed-term one is not.
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
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import Apprentice, EmploymentPeriod
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


@pytest.mark.parametrize(("fixed_term", "amount"), [(False, "12.50"), (True, "0")])
def test_the_increment_follows_the_term(fixed_term: bool, amount: str) -> None:
    """The permanent apprentice is paid the increment; the seasonal one not."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="operai-agricoli-florovivaisti",
                level_code="Area1",
                seniority=new_hire(2023),
                roles=frozenset(),
                contract_type=Apprentice(months_elapsed=30, fixed_term=fixed_term),
                employment_period=EmploymentPeriod(date(2023, 9, 1)),
                category=WorkerCategory.OPERAIO,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )
    (decision,) = (d for d in result.decisions if d.capability == "seniority")
    assert decision.amount == Decimal(amount)


def test_the_term_is_a_bool() -> None:
    """A term is stated or not."""
    with pytest.raises(InvalidInputError):
        Apprentice(months_elapsed=1, fixed_term="yes")  # type: ignore[arg-type]
