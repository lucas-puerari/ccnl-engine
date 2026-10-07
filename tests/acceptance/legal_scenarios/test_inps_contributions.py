"""INPS contributions of a run against the 2026 circular and L. 92/2012.

The expected values come from
:mod:`tests.fixtures.normative_oracles.contributions_2026`, written from the
sources; every other fact of the runs is explicit
(:mod:`tests.fixtures.explicit_facts`).  The NASpI exclusion does not
hold today: it is a strict xfail on the assertion it breaks.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.events import BonusEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    FixedTerm,
    Permanent,
    WeeklyHours,
    WorkerCategory,
)
from ccnl_engine.results import BlockerCode
from tests.acceptance.legal_scenarios._support import ENGINE
from tests.fixtures.explicit_facts import CONCIA_D2, competence_year, regular_run
from tests.fixtures.normative_oracles.contributions_2026 import (
    FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR,
    HOURLY_FLOOR_40_HOURS,
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


def _issue_blocked(result: PeriodResult) -> set[str | None]:
    """Return the features a calculation issue or a missing fact blocks.

    A weak rate source blocks the INPS amounts of every run and says
    nothing of the minimum base, so it is left out.

    Returns:
        The features of the calculation-issue and missing-fact blockers.
    """
    return {
        b.feature
        for b in result.blockers
        if b.code in {BlockerCode.CALCULATION_ISSUE, BlockerCode.MISSING_FACT}
    }


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


def test_monthly_base_reaches_the_daily_floor() -> None:
    """Autoscuole UNASCA level 3, full time, June 2026.

    The signed table pays 987.04 + 439.83 + 10.33 = 1,437.20
    (``tests/fixtures/reference_tables/autoscuole-unasca_3_2026.json``),
    below 58.13 x 26 = 1,511.38.  The full month of a full-time worker
    without absences is contributed on the floor, and no calculation issue
    blocks the INPS amounts; the pay itself is not raised.  A weak rate
    source blocks INPS on every run and says nothing of the floor, so it
    does not count.
    """
    result = ENGINE.calculate_period(regular_run(employment=_AUTOSCUOLE_3))
    blocked = _issue_blocked(result)

    assert result.period_gross == Decimal("1437.20")
    assert _inps_base(result) == FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR
    assert not {"inps_employee", "inps_employer"} & blocked


_AUTOSCUOLE_3 = replace(CONCIA_D2, ccnl_slug="autoscuole-unasca.json", level_code="3")
_CENT = Decimal("0.01")


def test_part_time_base_reaches_the_hourly_floor() -> None:
    """Autoscuole UNASCA level 3, 20 of 40 hours, June 2026.

    Half of 1,437.20 is paid.  The hourly floor of a 40-hour week is 8.72
    (circolare 6/2026 section 4); 20 hours a week over a month of 26 days
    of a six-day week are 20 x 26 / 6 hours: 8.72 x 20 x 26 / 6 = 755.733,
    so the base is 755.73.
    """
    employment = replace(
        _AUTOSCUOLE_3,
        weekly_hours=WeeklyHours(20),
        full_time_weekly_hours=WeeklyHours(40),
    )
    result = ENGINE.calculate_period(regular_run(employment=employment))
    floor = (HOURLY_FLOOR_40_HOURS * 20 * 26 / 6).quantize(_CENT)

    assert result.period_gross < floor
    assert _inps_base(result) == floor


def test_part_time_of_an_unpublished_week_blocks_the_inps_amounts() -> None:
    """Autoscuole UNASCA level 3, 20 of 38 hours, June 2026.

    The circular publishes the hourly floor of 40 and 36-hour weeks only,
    and the days of a 38-hour normal week are not stated: the floor of
    D.Lgs. 81/2015 art. 11 c. 1 can reach 58.13 x 6 / 38 x 20 x 26 / 6 =
    795.46, above the 756.42 paid, so the INPS amounts are blocked.
    """
    employment = replace(
        _AUTOSCUOLE_3,
        weekly_hours=WeeklyHours(20),
        full_time_weekly_hours=WeeklyHours(38),
    )
    result = ENGINE.calculate_period(regular_run(employment=employment))
    assert {"inps_employee", "inps_employer"} <= _issue_blocked(result)


def test_ratei_settled_at_termination_leave_the_floor_open() -> None:
    """Autoscuole UNASCA level 3, employed 1 January to 30 June 2026.

    The June run pays 1,437.20 and settles the tredicesima accrued from
    January, 6/12 of it.  The month alone is below 26 x 58.13 = 1,511.38;
    whether the settled ratei count toward the floor is not sourced (INPS
    circ. 196/1995 leaves them out for the Fondo Volo only), so the INPS
    amounts of the June run are blocked instead of guessed.
    """
    employment = replace(
        _AUTOSCUOLE_3,
        employment_period=EmploymentPeriod(date(2026, 1, 1), date(2026, 6, 30)),
    )
    year = ENGINE.calculate_competence_year(competence_year(employment=employment))
    (june,) = (
        r for r in year.period_results if r.run and r.run.run_id == "2026-06-regular"
    )

    assert june.period_gross > FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR
    assert _issue_blocked(june) >= {"inps_employee", "inps_employer"}


def test_operaio_agricolo_is_contributed_on_the_pay() -> None:
    """Operai agricoli florovivaisti Area 3, operaio, June 2026.

    D.L. 463/1983 art. 7 c. 5: the floor of c. 1 does not apply to the
    operai agricoli, so the base stays the pay, below 1,511.38.
    """
    employment = replace(
        CONCIA_D2,
        ccnl_slug="operai-agricoli-florovivaisti.json",
        level_code="Area3",
        category=WorkerCategory.OPERAIO,
    )
    result = ENGINE.calculate_period(regular_run(employment=employment))

    assert result.period_gross < FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR
    assert _inps_base(result) == result.period_gross


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
