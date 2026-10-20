"""Hand oracle: a 200 EUR absorbable superminimo on the eight pilot CCNLs.

The worker is hired on 1 January 2025 at the middle level; the superminimo
is stated at 200 EUR on 1 January 2026 and absorbed by the increases of the
minimo tabellare to December 2026.  The increases are read from the tables
of each CCNL (minimo in force on 1 January 2026, then on 1 December 2026):

| CCNL | Level | 1 Jan 2026 | 1 Dec 2026 | Superminimo |
|---|---|---:|---:|---:|
| chimica-farmaceutica-federchimica | D1 | 2360.26 | 2420.26 | 140.00 |
| turismo-federalberghi | 4 | 1660.69 | 1695.69 | 165.00 |
| pubblici-esercizi-fipe-angem | 3 | 1757.14 | 1800.73 | 156.41 |
| terziario-confesercenti | IV | 1781.68 | 1816.68 | 165.00 |
| metalmeccanico-confapi | 5 | 2195.87 | 2245.87 | 150.00 |
| metalmeccanico-federmeccanica | C3 | 2158.26 | 2211.43 | 146.83 |
| studi-professionali-confprofessioni | 3S | 1722.01 | 1742.20 | 179.81 |
| commercio-confcommercio | 4 | 1257.46 | 1292.46 | 165.00 |

The December run pays it on top of the pay without it, the tredicesima
pays it once (a full year of service), and the TFR of the month accrues
its 1/13.5 less the additional 0.50% IVS deducted from the quota (L.
297/1982 art. 3 c. 15-16).
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
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    IndividualElement,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.results import AccountKind

_HIRED = date(2025, 1, 1)
_SUPERMINIMO = IndividualElement(
    "superminimo", Decimal(200), absorbable=True, as_of=date(2026, 1, 1)
)
_PILOTS = [
    ("chimica-farmaceutica-federchimica", "D1", "140.00"),
    ("turismo-federalberghi", "4", "165.00"),
    ("pubblici-esercizi-fipe-angem", "3", "156.41"),
    ("terziario-confesercenti", "IV", "165.00"),
    ("metalmeccanico-confapi", "5", "150.00"),
    ("metalmeccanico-federmeccanica", "C3", "146.83"),
    ("studi-professionali-confprofessioni", "3S", "179.81"),
    ("commercio-confcommercio", "4", "165.00"),
]


def _run(
    ccnl_id: str, level: str, run: PayrollRun, *, with_element: bool
) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(2026, 12, 18),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                roles=frozenset(),
                individual_elements=(_SUPERMINIMO,) if with_element else (),
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), provincial_pay_element=False
            ),
        )
    )


def _tfr(result: PeriodResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account is AccountKind.TFR_ACCRUAL
        ),
        Decimal(0),
    )


def _difference(
    ccnl_id: str, level: str, run: PayrollRun
) -> tuple[PeriodResult, Decimal, Decimal]:
    with_it = _run(ccnl_id, level, run, with_element=True)
    without = _run(ccnl_id, level, run, with_element=False)
    tfr = _tfr(with_it) - _tfr(without)
    return with_it, with_it.period_gross - without.period_gross, tfr


@pytest.mark.parametrize(("ccnl_id", "level", "expected"), _PILOTS)
def test_the_december_run_pays_the_absorbed_superminimo(
    ccnl_id: str, level: str, expected: str
) -> None:
    """The gross rises by the superminimo left after the increases."""
    result, gross, tfr = _difference(ccnl_id, level, PayrollRun.regular(2026, 12))

    assert gross == Decimal(expected)
    element = Decimal(expected)
    quota = element / Decimal("13.5") - element * Decimal("0.005")
    assert abs(tfr - quota) <= Decimal("0.01")
    (decision,) = [
        d for d in result.decisions if d.reason_code.startswith("individual_element")
    ]
    assert decision.reason_code == "individual_element_absorbed"
    assert decision.amount == Decimal(expected)


@pytest.mark.parametrize(("ccnl_id", "level", "expected"), _PILOTS)
def test_the_tredicesima_pays_it_once(ccnl_id: str, level: str, expected: str) -> None:
    """A full year of service: the tredicesima is a whole month of it."""
    _, gross, _ = _difference(ccnl_id, level, PayrollRun.thirteenth(2026, 12))

    assert gross == Decimal(expected)
