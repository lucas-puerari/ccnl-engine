"""The work injury of the Studi professionali (Art. 123, p. 66).

"l'intera retribuzione per la giornata in cui avviene l'infortunio e una
indennità pari al 60% [...] per i tre giorni successivi"; then "una
integrazione dell'indennità corrisposta dall'INAIL, fino a raggiungere il
75%". Level 4, injured 2 March 2026 to the end of the month: the carenza is
3 x 60% x 1595.42 / 26 = 110.45, and the INAIL share is topped up.
"""

from __future__ import annotations

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
from ccnl_engine.events import WorkInjuryEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)

_HIRED = date(2025, 1, 1)


def test_the_inail_share_is_topped_up_after_the_carenza() -> None:
    """60% for the three carenza days, then an integration line."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="studi-professionali-confprofessioni",
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(10)),
            facts=PeriodFacts(
                events=(WorkInjuryEvent(date(2026, 3, 2), date(2026, 3, 31)),)
            ),
        )
    )
    lines = {i.item_id.rsplit("_", 1)[-1]: i.amount for i in result.pay_items}

    assert lines["crnz"] == Decimal("110.45")
    assert lines["intg"] > 0
