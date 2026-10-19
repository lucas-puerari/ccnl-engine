"""Fondo di solidarietà del settore assicurativo on an ANIA payslip.

INPS circ. 56/2015 p. 11 (https://servizi2.inps.it/CircolariZIP/
Circolare%20numero%2056%20del%2010-03-2015.pdf): "contributo ordinario dello
0,30% (di cui lo 0,20% a carico del datore di lavoro e lo 0,10% a carico dei
lavoratori) calcolato sulla retribuzione imponibile ai fini previdenziali di
tutti i lavoratori dipendenti con contratto a tempo indeterminato".
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
    PeriodInput,
)
from ccnl_engine.inputs import Permanent
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()


def test_permanent_worker_pays_the_fund() -> None:
    """Fund shares are 0.20% and 0.10% of the INPS base of the month."""
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="assicurazioni-ania",
                level_code="L4",
                seniority=new_hire(),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(100)),
        )
    )

    parts = {c.name: c for c in result.contribution_breakdown.components}
    employer, employee = (
        parts["solidarity_fund_employer"],
        parts["solidarity_fund_employee"],
    )
    assert employer.rate == Decimal("0.002")
    assert employee.rate == Decimal("0.001")
    assert employer.amount == (employer.base * Decimal("0.002")).quantize(
        Decimal("0.01")
    )
    ids = {limitation.id for limitation in result.assurance.limitations}
    assert "assicurazioni-ania/solidarity_fund_unsourced" not in ids
