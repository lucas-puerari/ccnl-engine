"""INPS contributions of a run against the 2026 circular and L. 92/2012.

The expected values come from
:mod:`tests.fixtures.normative_oracles.contributions_2026`, written from the
sources; every other fact of the runs is explicit
(:mod:`tests.fixtures.explicit_facts`).  The floor and the NASpI
exclusion do not hold today: each is a strict xfail on the assertion it
breaks.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.events import BonusEvent
from ccnl_engine.inputs import EmploymentPeriod, FixedTerm, Permanent
from ccnl_engine.results import BlockerCode
from tests.acceptance.legal_scenarios._support import ENGINE
from tests.fixtures.explicit_facts import CONCIA_D2, regular_run
from tests.fixtures.normative_oracles.contributions_2026 import (
    FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR,
    additional_ivs,
)
from tests.fixtures.normative_oracles.payslips.metalmeccanico_c3_2026 import (
    C3_MINIMUM_FROM_JUNE_2026,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_ZERO = Decimal(0)
#: Employee IVS 9.19% and CIGS 0.30% of an industrial employer of 50.
_EMPLOYEE_RATE = Decimal("0.0949")


def _account(result: PeriodResult, account: str) -> Decimal:
    return sum((e.amount for e in result.ledger_entries if e.account == account), _ZERO)


def _inps_base(result: PeriodResult) -> Decimal:
    (decision,) = (d for d in result.decisions if d.capability == "inps_employee")
    base = decision.inputs["base"]
    assert isinstance(base, Decimal)
    return base


def test_additional_ivs_uses_the_monthly_threshold() -> None:
    """Metalmeccanico C3 hired 1 June 2026, June pay plus a 10,000 EUR bonus.

    Gross 2,211.43 + 10,000 = 12,211.43.  Employee INPS: 9.49% of it,
    1,158.8647, plus 1% of 12,211.43 - 4,685 = 7,526.43, that is 75.2643:
    1,234.13 within the cents that rounding each component apart moves.
    The year-to-date base stays far below 56,224 EUR: the monthly threshold
    alone charges the 1% (circolare 6/2026 section 5, mensilizzazione).
    """
    employment = replace(
        CONCIA_D2,
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_period=EmploymentPeriod(date(2026, 6, 1)),
    )
    bonus = BonusEvent(date(2026, 6, 15), Decimal(10_000))
    result = ENGINE.calculate_period(
        regular_run(employment=employment, events=(bonus,))
    )
    gross = C3_MINIMUM_FROM_JUNE_2026 + Decimal(10_000)
    expected = gross * _EMPLOYEE_RATE + additional_ivs(gross)

    assert result.period_gross == gross
    employee = _account(result, "employee_contributions")
    assert abs(employee - expected) <= Decimal("0.02")


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "the INPS base is the CCNL pay even below the daily floor of 58.13 EUR "
        "(D.L. 463/1983 art. 7 c. 1, INPS circolare 6/2026 section 1), "
        "26 floors in a full-time month, and no blocker names it"
    ),
)
def test_monthly_base_reaches_the_daily_floor() -> None:
    """Autoscuole UNASCA level 3, full time, June 2026.

    The signed table pays 987.04 + 439.83 + 10.33 = 1,437.20
    (``tests/fixtures/reference_tables/autoscuole-unasca_3_2026.json``),
    below 58.13 x 26 = 1,511.38.  The base must be raised to the floor, or
    the run must say through a blocker on the INPS base that it is not.  A
    weak rate source blocks INPS on every run and says nothing of the
    floor, so it does not count.
    """
    employment = replace(CONCIA_D2, ccnl_slug="autoscuole-unasca.json", level_code="3")
    result = ENGINE.calculate_period(regular_run(employment=employment))
    blocked = {
        b.feature for b in result.blockers if b.code is not BlockerCode.RULE_SOURCE_WEAK
    }

    assert result.period_gross == Decimal("1437.20")
    assert _inps_base(result) >= FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR or (
        {"inps_employee", "inps_employer"} & blocked
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "a fixed-term operaio agricolo is charged the 1.4% surcharge of "
        "L. 92/2012 art. 2 c. 28; c. 3 excludes operai agricoli a tempo "
        "determinato o indeterminato from the whole article"
    ),
)
def test_agricultural_fixed_term_pays_no_naspi_surcharge() -> None:
    """Operai agricoli florovivaisti Area 3, June 2026, fixed term and permanent.

    In the bundle the contract type reaches the employer INPS rate only
    through the surcharge of c. 28, so without it the two runs post the
    same employer contributions; today the fixed term adds 1.4% of the base
    (rate 23.06% against 21.66%).
    """
    agricultural = replace(
        CONCIA_D2, ccnl_slug="operai-agricoli-florovivaisti.json", level_code="Area3"
    )

    def employer(contract: Permanent | FixedTerm) -> Decimal:
        employment = replace(agricultural, contract_type=contract)
        result = ENGINE.calculate_period(regular_run(employment=employment))
        return _account(result, "employer_contributions")

    assert employer(FixedTerm()) == employer(Permanent())
