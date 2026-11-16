"""Hand oracle: the night service of the Farmacie private, by its kind.

CCNL Farmacie private art. 19 (PDF p. 13): the night service with the doors
open pays 20% of the normal pay for the first 8 hours, with the doors closed
16%; beyond 8 hours the hourly pay of fact is due on top, with 20% or 10%.
Level 1, June 2026: 1,429.19 + 25.30 + 530.45 + 10.33 = 1,995.27 a month
over 173 = 11.5333 an hour.  8 hours: 18.45 doors open, 14.76 closed;
beyond 8 with the doors closed 9.23, the hours themselves 92.27.
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
from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.period.facts.inputs import PeriodFacts
from ccnl_engine.working_time.inputs import NightShiftEvent

_HIRED = date(2024, 1, 1)


def _night(service: str | None) -> list[tuple[str, Decimal | None, object]]:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="farmacie-private-h121",
                level_code="1",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                roles=frozenset(),
            ),
            employer=EmployerProfile(headcount=Headcount(10)),
            facts=PeriodFacts(
                events=(
                    NightShiftEvent(
                        date(2026, 6, 10), hours=Decimal(8), service=service
                    ),
                )
            ),
        )
    )
    return [
        (str(d.inputs["band_code"]), d.amount, d.inputs.get("hours_amount"))
        for d in result.decisions
        if d.capability == "night_work"
    ]


@pytest.mark.parametrize(
    ("service", "band", "amount", "hours_amount"),
    [
        ("doors_open", "U_NIGHT_0", Decimal("18.45"), None),
        ("doors_closed", "U_NIGHT_2", Decimal("14.76"), None),
        ("doors_closed_beyond_8", "U_NIGHT_3", Decimal("9.23"), Decimal("92.27")),
    ],
)
def test_the_service_chooses_the_band(
    service: str, band: str, amount: Decimal, hours_amount: Decimal | None
) -> None:
    """Each kind of night service is paid at the rate of its own band."""
    assert _night(service) == [(band, amount, hours_amount)]


def test_a_night_without_its_service_is_rejected() -> None:
    """The CCNL pays the night by the service: an unstated one blocks."""
    with pytest.raises(InvalidInputError, match="by the service"):
        _night(None)


def test_a_service_the_ccnl_does_not_name_is_rejected() -> None:
    """No band of the CCNL pays a service it does not name."""
    with pytest.raises(MissingRuleError, match="for the service 'nope'"):
        _night("nope")


def test_the_service_must_be_a_code() -> None:
    """A blank service is rejected."""
    with pytest.raises(InvalidInputError, match=r"NightShiftEvent\.service"):
        NightShiftEvent(date(2026, 6, 10), hours=Decimal(8), service=" ")
