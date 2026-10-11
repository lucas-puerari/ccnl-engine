"""Seniority increments converted into Previambiente contributions.

Art. 65 lett. A) bis: the worker who opts is paid no seniority increment;
the employer pays the fund "l'importo mensile corrispondente all'aumento
periodico [...] maggiorato del 10% e riproporzionato su 12 mensilità",
Q 50,27 EUR (39.17 x 1.10 x 14 / 12 = 50.268 -> 50.27), outside the TFR.

Q in March 2026, seniority since 1 March 2022: 48 months, one increment of
36 months.  Without the option the pay holds 39.17 of increment and the
employer pays 42.24 + 22 + 5 = 69.24; with it the pay holds none and the
employer pays 69.24 + 50.27 = 119.51.  The worker pays 27.01 either way.

A worker in service since 1 March 2019 who asked on 1 March 2024 (c. 6):
60 months, one increment, stays in the pay frozen; in March 2026, 84
months, the second increment goes to the fund: 39.17 in the pay instead
of 78.34, 119.51 employer.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment, InvalidInputError
from ccnl_engine.inputs import (
    EmploymentPeriod,
    PensionFundEnrolment,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from tests.knowledge.ccnl_engine.payroll.support import regular_period
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_SINCE = date(2022, 3, 1)


def _march(
    converted: bool,
    slug: str = "igiene-ambientale-utilitalia",
    since: date = _SINCE,
    asked_on: date | None = None,
) -> PeriodResult:
    enrolment = PensionFundEnrolment(
        "PREVIAMBIENTE",
        Decimal("0.013"),
        tfr_to_fund=True,
        conventional_base=Decimal("2077.84"),
        seniority_to_fund=converted,
        seniority_converted_on=asked_on,
    )
    employment = Employment(
        ccnl_slug=f"{slug}.json",
        level_code="Q",
        seniority=SeniorityFact.since(since, SenioritySource.EMPLOYER_RECORDS),
        employment_period=EmploymentPeriod(since),
        pension_fund=enrolment,
        contract_type=Permanent(),
    )
    return regular_period(
        employment=employment, month=3, current_year=employment_only()
    )


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def test_increment_paid_to_the_fund_instead_of_the_pay() -> None:
    """119.51 employer instead of 69.24; the gross loses the 39.17."""
    kept, converted = _march(converted=False), _march(converted=True)
    assert _entry(kept, "pension_fund_employer") == Decimal("69.24")
    assert _entry(converted, "pension_fund_employer") == Decimal("119.51")
    assert _entry(converted, "pension_fund_employee") == Decimal("27.01")
    assert kept.period_gross - converted.period_gross == Decimal("39.17")


def test_in_service_keeps_the_increments_already_matured() -> None:
    """C. 6: one increment frozen in the pay, the second to the fund."""
    since, asked = date(2019, 3, 1), date(2024, 3, 1)
    kept = _march(converted=False, since=since)
    converted = _march(converted=True, since=since, asked_on=asked)
    assert _entry(kept, "pension_fund_employer") == Decimal("69.24")
    assert _entry(converted, "pension_fund_employer") == Decimal("119.51")
    assert kept.period_gross - converted.period_gross == Decimal("39.17")


def test_a_fund_without_conversion_rejects_the_option() -> None:
    """Fon.Te. converts no increment."""
    enrolment = PensionFundEnrolment(
        "FONTE", Decimal("0.0055"), tfr_to_fund=True, seniority_to_fund=True
    )
    employment = Employment(
        ccnl_slug="commercio-confcommercio.json",
        level_code="4",
        seniority=SeniorityFact.since(_SINCE, SenioritySource.EMPLOYER_RECORDS),
        pension_fund=enrolment,
        contract_type=Permanent(),
    )
    with pytest.raises(InvalidInputError, match="converts no seniority"):
        regular_period(employment=employment, current_year=employment_only())
