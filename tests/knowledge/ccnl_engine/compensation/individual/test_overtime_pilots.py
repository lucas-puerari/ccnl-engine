"""Hand oracle: two weekday overtime hours with a 200 EUR superminimo.

March 2026, the worker of ``test_pilots`` (hired 1 January 2025, the
superminimo stated at 200 EUR on 1 January 2026, not yet absorbed): two
weekday overtime hours on 10 March at the CCNL hourly base.  Each CCNL says
whether the superminimo enters the hourly base (work_rules.time_supplements
.individual_elements):

| CCNL | Monthly base / divisor | Multiplier | Superminimo in | Without | With |
|---|---|---:|---|---:|---:|
| chimica (art. 15 punto 1) | 2360.26 / 175 | 1.10 | both | 29.67 | 32.19 |
| turismo (art. 148) | 1660.69 / 172 | 1.30 | neither | 25.10 | 25.10 |
| FIPE (art. 157) | 1757.14 / 172 | 1.30 | neither | 26.56 | 26.56 |
| terziario (art. 149) | 1781.68 / 168 | 1.15 | hour only | 24.39 | 26.77 |
| confapi (art. 38) | 2195.87 / 173 | 1.20 | both | 30.46 | 33.24 |
| federmeccanica (art. 3) | 2158.26 / 173 | 1.25 | both | 31.19 | 34.08 |
| studi (artt. 95, 135) | 1722.01 / 170 | 1.15 | both | 23.30 | 26.00 |
| commercio (art. 149) | 1781.68 / 168 | 1.15 | hour only | 24.39 | 26.77 |

Without: 2 x multiplier x base / divisor.  With, included: 2 x multiplier x
(base + 200) / divisor, e.g. chimica 2 x 1.10 x 2560.26 / 175 = 32.19.
With, hour only (Commercio and Terziario art. 149: the hour at the
retribuzione di fatto, the 15% on the normale retribuzione): 2 x (1981.68
/ 168 + 0.15 x 1781.68 / 168) = 2 x (11.7957 + 1.5908) = 26.77.
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
from ccnl_engine.events import OvertimeEvent, OvertimeKind
from ccnl_engine.inputs import (
    EmploymentPeriod,
    IndividualElement,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.pay_item.facade import OvertimeEarning

_HIRED = date(2025, 1, 1)
_SUPERMINIMO = IndividualElement(
    "superminimo", Decimal(200), absorbable=True, as_of=date(2026, 1, 1)
)
_OVERTIME = OvertimeEvent(date(2026, 3, 10), Decimal(2), kind=OvertimeKind.WEEKDAY)


def _overtime(ccnl_id: str, level: str, *, with_element: bool) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
                individual_elements=(_SUPERMINIMO,) if with_element else (),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=(_OVERTIME,)),
        )
    )
    return sum(
        (i.amount for i in result.pay_items if isinstance(i, OvertimeEarning)),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("ccnl_id", "level", "without", "with_"),
    [
        ("chimica-farmaceutica-federchimica", "D1", "29.67", "32.19"),
        ("turismo-federalberghi", "4", "25.10", "25.10"),
        ("pubblici-esercizi-fipe-angem", "3", "26.56", "26.56"),
        ("terziario-confesercenti", "IV", "24.39", "26.77"),
        ("metalmeccanico-confapi", "5", "30.46", "33.24"),
        ("metalmeccanico-federmeccanica", "C3", "31.19", "34.08"),
        ("studi-professionali-confprofessioni", "3S", "23.30", "26.00"),
        ("commercio-confcommercio", "4", "24.39", "26.77"),
    ],
)
def test_overtime_counts_the_superminimo_as_the_ccnl_says(
    ccnl_id: str, level: str, without: str, with_: str
) -> None:
    """The superminimo raises the overtime only where the CCNL counts it."""
    assert _overtime(ccnl_id, level, with_element=False) == Decimal(without)
    assert _overtime(ccnl_id, level, with_element=True) == Decimal(with_)
