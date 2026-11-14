"""The provincial terzo elemento replaces the national 2,07 (Terziario family).

Confesercenti artt. 214-215 (TU 2019, p. 157), DMO artt. 198-199 (TU 2025,
p. 59): the provincial elements frozen since 1973 are paid in addition to the
levels, and the 2,07 national element only where none is in force. The
caller states the provincial amount as a territorial element; it enters the
thirteenth like the normal pay (Confesercenti art. 206, DMO art. 189).
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
)
from ccnl_engine.compensation.second_level.inputs import (
    SecondLevelAgreement,
    SecondLevelElement,
)
from ccnl_engine.inputs import EmploymentPeriod, NoPensionFund, Permanent

_PROVINCIAL = SecondLevelElement(
    code="terzo_elemento_provinciale",
    monthly=Decimal("5.16"),
    agreement=SecondLevelAgreement.TERRITORIAL,
    valid_from=date(1973, 6, 30),
)


def _third_elements(
    ccnl_id: str, run: PayrollRun, *, provincial: bool
) -> dict[str, Decimal]:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(2026, 12, 18),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code="IV",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2020, 1, 1), None),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(10),
                provincial_pay_element=provincial,
                second_level_elements=(_PROVINCIAL,) if provincial else (),
            ),
        )
    )
    return {
        i.item_id.rsplit("_", 1)[0]: i.amount
        for i in result.pay_items
        if "terzo_elemento" in i.item_id.lower()
    }


@pytest.mark.parametrize(
    "ccnl_id", ["terziario-confesercenti", "dmo-federdistribuzione"]
)
@pytest.mark.parametrize(
    "run", [PayrollRun.regular(2026, 12), PayrollRun.thirteenth(2026, 12)]
)
def test_the_provincial_element_replaces_the_national_one(
    ccnl_id: str, run: PayrollRun
) -> None:
    """2,07 without a provincial element; the provincial 5,16 alone with it."""
    national = _third_elements(ccnl_id, run, provincial=False)
    provincial = _third_elements(ccnl_id, run, provincial=True)
    assert list(national.values()) == [Decimal("2.07")]
    assert list(provincial.values()) == [Decimal("5.16")]
    assert all("provinciale" in key for key in provincial)
