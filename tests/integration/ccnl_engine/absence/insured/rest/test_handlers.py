"""The daily rests of the first year of a child, paid back in full by INPS.

Metalmeccanico Federmeccanica C3 impiegato, 2158.26 EUR a month, hourly
divisor 173.  Two hours of rest on five days of March 2026: 2158.26 * 10 /
173 = 124.75 deducted and paid back in full as the INPS indemnity (art. 43
D.Lgs. 151/2001), out of the INPS base (art. 44 c. 1): 2158.26 - 124.75 =
2033.51, 2034 in whole euros.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.events import LeaveHours, NursingRestEvent
from ccnl_engine.pay_item.facade import AbsenceDeduction, MaternityItem
from tests.integration.ccnl_engine.absence.insured.permit.test_handlers import (
    _ivs_base,
    _run,
)

_BORN = date(2025, 10, 1)
#: The rest of 27 February belongs to the February run.
_RESTS = NursingRestEvent(
    (
        LeaveHours(date(2026, 2, 27), Decimal(1)),
        *(LeaveHours(date(2026, 3, d), Decimal(2)) for d in range(2, 7)),
    ),
    _BORN,
)


def test_ten_hours_are_paid_back_out_of_the_inps_base() -> None:
    """The deduction at the hourly base, the same from INPS."""
    result = _run(_RESTS)

    assert {
        i.item_id.rsplit("_", 1)[-1]: (i.kind, i.amount, i.absence_days)
        for i in result.pay_items
        if isinstance(i, AbsenceDeduction | MaternityItem)
    } == {
        "abs": ("absence_deduction", Decimal("124.75"), Decimal(10)),
        "inps": ("maternity_item", Decimal("124.75"), Decimal(10)),
    }
    (decision,) = (d for d in result.decisions if d.capability == "nursing_rests")
    assert (decision.amount, decision.status) == (Decimal("124.75"), "final")
    assert decision.inputs["deduction"] == Decimal("124.75")
    assert (_ivs_base(_run()), _ivs_base(result)) == (Decimal(2158), Decimal(2034))
    assert result.limitations == _run().limitations


def test_without_a_verified_hourly_base_the_hours_post_nothing() -> None:
    """Chimica PMI: the rests are reported, not paid."""
    result = _run(_RESTS, ccnl=("chimica-affini-pmi-unionchimica", "D"))

    assert not [
        i for i in result.pay_items if isinstance(i, AbsenceDeduction | MaternityItem)
    ]
    (issue,) = (i for i in result.issues if i.capability == "nursing_rests")
    (decision,) = (d for d in result.decisions if d.capability == "nursing_rests")
    assert (issue.code, issue.cause, decision.status, decision.reason_code) == (
        "nursing_rest_hours_underived",
        "rule",
        "incomplete",
        "nursing_rest_hours_underived",
    )
