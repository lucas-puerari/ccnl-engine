"""The payslip of a run as lines: the competenze less the trattenute are the net.

March 2026, the middle level of each pilot CCNL, 20 employees, resident in
Milan, 4 overtime hours at a stated 12.50 EUR x 1.25 = 62.50 EUR.
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
    PeriodResult,
)
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    FamilyComposition,
    NoPensionFund,
    PeriodState,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.pay_item.voce.rules import VoceUnit

_HIRED = date(2026, 3, 1)
_PILOTS = [
    "chimica-farmaceutica-federchimica",
    "turismo-federalberghi",
    "pubblici-esercizi-fipe-angem",
    "terziario-confesercenti",
    "metalmeccanico-confapi",
    "metalmeccanico-federmeccanica",
    "studi-professionali-confprofessioni",
    "commercio-confcommercio",
]


def _run(ccnl_id: str) -> PeriodResult:
    engine = PayrollEngine.bundled()
    levels = engine.list_levels(ccnl_id)
    return engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=levels[len(levels) // 2].code,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
                roles=frozenset(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(20), provincial_pay_element=False
            ),
            opening_state=PeriodState.zero(),
            facts=PeriodFacts(
                regione="IT-25",
                comune_belfiore="F205",
                family_composition=FamilyComposition(),
                events=(
                    OvertimeEvent(
                        event_date=date(2026, 3, 10),
                        hours=Decimal(4),
                        hourly_rate=Decimal("12.50"),
                        multiplier=Decimal("1.25"),
                    ),
                ),
            ),
        )
    )


@pytest.mark.parametrize("ccnl_id", _PILOTS)
def test_the_lines_add_up_to_the_net(ccnl_id: str) -> None:
    """Competenze less trattenute is the net; the overtime line counts hours."""
    result = _run(ccnl_id)
    lines = result.payslip_lines()

    earnings = sum((line.earning for line in lines), Decimal(0))
    deductions = sum((line.deduction for line in lines), Decimal(0))
    assert earnings - deductions == result.period_net
    (overtime,) = [line for line in lines if line.engine_code == "overtime_earning"]
    assert (overtime.quantity, overtime.unit, overtime.rate, overtime.earning) == (
        Decimal(4),
        VoceUnit.HOURS,
        Decimal("15.62500"),
        Decimal("62.50"),
    )
    assert {"employee_contributions", "ordinary_tax"} <= {
        line.engine_code for line in lines
    }


def test_a_provider_maps_the_engine_codes() -> None:
    """A mapped code prints the provider's voce; the rest keep their own."""
    lines = _run("commercio-confcommercio").payslip_lines({
        "base_salary_earning": "0001",
        "employee_contributions": "9100",
    })
    voci = {line.engine_code: line.voce for line in lines}

    assert voci["base_salary_earning"] == "0001"
    assert voci["employee_contributions"] == "9100"
    assert voci["ordinary_tax"] == "ordinary_tax"


def test_the_progressives_of_the_first_run() -> None:
    """From a zero state the progressivi are the amounts of the run."""
    result = _run("commercio-confcommercio")
    progressives = result.progressives
    lines = result.payslip_lines()

    def total(code: str) -> Decimal:
        return sum(
            (line.deduction for line in lines if line.engine_code == code), Decimal(0)
        )

    assert progressives.tax_year == 2026
    assert progressives.gross == result.paid_gross
    assert progressives.inps_employee == total("employee_contributions")
    assert progressives.irpef == total("ordinary_tax")
    assert progressives.inps_base > 0
