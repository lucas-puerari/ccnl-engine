"""The entry pay of the Studi professionali (Art. 56, p. 40).

"un salario di ingresso pari alla retribuzione fino a due livelli
immediatamente inferiori per i primi 9 mesi dalla data di assunzione, e di un
livello per i successivi 6 mesi rispetto a quello di inquadramento [...] non è
applicabile ai lavoratori inquadrati al V livello". Levels by order: 5, 4,
4S, 3, 3S, 2, 1, Q.
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.entry.rules import entry_level
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)

_STUDI = load_ccnl("studi-professionali-confprofessioni")
_HIRED = date(2025, 1, 1)


def _paid(level: str, as_of: date, *, chosen: bool = True) -> str:
    return entry_level(_STUDI, _STUDI.level_by_code(level), chosen, _HIRED, as_of).code


@pytest.mark.parametrize(
    ("level", "as_of", "paid"),
    [
        ("3", date(2025, 9, 1), "4"),
        ("3", date(2025, 10, 1), "4S"),
        ("3", date(2026, 3, 1), "4S"),
        ("3", date(2026, 4, 1), "3"),
        ("4S", date(2025, 3, 1), "5"),
        ("4", date(2025, 3, 1), "5"),
    ],
)
def test_two_levels_below_then_one(level: str, as_of: date, paid: str) -> None:
    """Months 0-8 two below, 9-14 one below, then the level; never below 5."""
    assert _paid(level, as_of) == paid


def test_without_the_entry_pay_the_level_is_paid() -> None:
    """An ordinary hire."""
    assert _paid("3", date(2025, 3, 1), chosen=False) == "3"


@pytest.mark.parametrize(
    ("ccnl_id", "level", "hired", "match"),
    [
        ("studi-professionali-confprofessioni", "5", _HIRED, "excludes level 5"),
        ("studi-professionali-confprofessioni", "3", None, "employment_period"),
        ("commercio-confcommercio", "3", _HIRED, "has no entry pay"),
    ],
)
def test_an_entry_pay_that_cannot_apply_raises(
    ccnl_id: str, level: str, hired: date | None, match: str
) -> None:
    """Level V, an unknown hire date, a CCNL without the institute."""
    ccnl = load_ccnl(ccnl_id)
    with pytest.raises(InvalidInputError, match=match) as raised:
        entry_level(ccnl, ccnl.level_by_code(level), True, hired, date(2025, 3, 1))
    assert (raised.value.field, raised.value.feature) == (
        "Permanent.entry_pay",
        "base_salary",
    )


def test_a_run_pays_the_lower_level() -> None:
    """Level 3 hired January 2026, March 2026: the minimum of level 4."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="studi-professionali-confprofessioni",
                level_code="3",
                contract_type=Permanent(entry_pay=True),
                employment_period=EmploymentPeriod(date(2026, 1, 1), None),
                seniority=SeniorityFact.since(
                    date(2026, 1, 1), SenioritySource.EMPLOYER_RECORDS
                ),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(5)),
        )
    )
    (base,) = [
        i.amount for i in result.pay_items if i.item_id.startswith("base_salary")
    ]
    four = _STUDI.level_by_code("4").base_salary.value_at(date(2026, 3, 1))
    assert base == four
