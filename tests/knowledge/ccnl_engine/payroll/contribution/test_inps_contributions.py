"""INPS contributions of a run against the 2026 circular and L. 92/2012.

The expected values come from
:mod:`tests.knowledge.ccnl_engine.payroll.contribution.oracles_2026`, written from the
sources; every other fact of the runs is explicit
(:mod:`tests.knowledge.ccnl_engine.payroll.period.builders_explicit_facts`).
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Headcount
from ccnl_engine.events import BonusEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    FixedTerm,
    NaspiExclusion,
    WeeklyHours,
    WorkerCategory,
)
from ccnl_engine.results import BlockerCode
from tests.knowledge.ccnl_engine.payroll.contribution.oracles_2026 import (
    FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR,
    HOURLY_FLOOR_40_HOURS,
    additional_ivs,
    contribution_base,
    naspi_surcharge_rate,
)
from tests.knowledge.ccnl_engine.payroll.period.builders_explicit_facts import (
    CONCIA_D2,
    competence_year,
    regular_run,
)
from tests.knowledge.ccnl_engine.payroll.period.oracles_payslip_metalmeccanico_c3_2026 import (  # noqa: E501
    C3_MINIMUM_FROM_JUNE_2026,
)
from tests.knowledge.ccnl_engine.payroll.support import ENGINE

if TYPE_CHECKING:
    from ccnl_engine import Employment, PeriodResult

pytestmark = pytest.mark.legal_scenario

_ZERO = Decimal(0)
#: Employee IVS 9.19% and CIGS 0.30% of an industrial employer of 50.
_IVS_RATE = Decimal("0.0919")
_CIGS_RATE = Decimal("0.0030")
_CENT = Decimal("0.01")


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


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

    Gross 2,211.43 + 10,000 = 12,211.43, INPS base 12,211 (whole euro, INPS
    circ. 208/2001).  Employee INPS: IVS 9.19% = 1,122.19, CIGS 0.30% =
    36.63, plus 1% of 12,211 - 4,685 = 7,526, that is 75.26: 1,234.08.
    The year-to-date base stays far below 56,224 EUR: the monthly threshold
    alone charges the 1% (circolare 6/2026 section 5, mensilizzazione).
    """
    employment = replace(
        CONCIA_D2,
        category=None,
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_period=EmploymentPeriod(date(2026, 6, 1)),
    )
    bonus = BonusEvent(date(2026, 6, 15), Decimal(10_000))
    result = ENGINE.calculate_period(
        regular_run(employment=employment, events=(bonus,))
    )
    gross = C3_MINIMUM_FROM_JUNE_2026 + Decimal(10_000)
    base = contribution_base(gross)
    expected = (
        _cents(base * _IVS_RATE) + _cents(base * _CIGS_RATE) + additional_ivs(base)
    )

    assert result.period_gross == gross
    assert _account(result, "employee_contributions") == expected == Decimal("1234.08")


def test_monthly_base_reaches_the_daily_floor() -> None:
    """Autoscuole UNASCA level 3, full time, June 2026.

    The signed table pays 987.04 + 439.83 + 10.33 = 1,437.20
    (``tests/knowledge/ccnl_engine/payroll/period/reference_case/autoscuole-unasca_3_2026.json``),
    below 58.13 x 26 = 1,511.38.  The full month of a full-time worker
    without absences is contributed on the floor, 1,511 to the whole euro
    (INPS circ. 208/2001), and no calculation issue
    blocks the INPS amounts; the pay itself is not raised.  A weak rate
    source blocks INPS on every run and says nothing of the floor, so it
    does not count.
    """
    result = ENGINE.calculate_period(regular_run(employment=_AUTOSCUOLE_3))
    blocked = _issue_blocked(result)

    assert result.period_gross == Decimal("1437.20")
    assert _inps_base(result) == contribution_base(FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR)
    assert not {"inps_employee", "inps_employer"} & blocked


_AUTOSCUOLE_3 = replace(
    CONCIA_D2, category=None, ccnl_slug="autoscuole-unasca.json", level_code="3"
)


def test_part_time_base_reaches_the_hourly_floor() -> None:
    """Autoscuole UNASCA level 3, 20 of 40 hours, June 2026.

    Half of 1,437.20 is paid.  The hourly floor of a 40-hour week is 8.72
    (circolare 6/2026 section 4); 20 hours a week over a month of 26 days
    of a six-day week are 20 x 26 / 6 hours: 8.72 x 20 x 26 / 6 = 755.733,
    so the base is 756 to the whole euro.
    """
    employment = replace(
        _AUTOSCUOLE_3,
        weekly_hours=WeeklyHours(20),
        full_time_weekly_hours=WeeklyHours(40),
    )
    result = ENGINE.calculate_period(regular_run(employment=employment))
    floor = (HOURLY_FLOOR_40_HOURS * 20 * 26 / 6).quantize(_CENT)

    assert result.period_gross < floor
    assert _inps_base(result) == contribution_base(floor)


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
    assert _inps_base(result) == contribution_base(result.period_gross)


#: Facts the NASpI surcharge of a fixed term may miss.
_SURCHARGE_FACTS = frozenset({"naspi_exclusion", "renewals", "category"})


def _employer(employment: Employment) -> tuple[Decimal, PeriodResult]:
    """Return the employer contributions of the January 2026 run.

    January is the first run of the employment, so the zero state opening
    it is a fact.

    Returns:
        The employer contributions and the result.
    """
    result = ENGINE.calculate_period(regular_run(1, employment=employment))
    return _account(result, "employer_contributions"), result


def _missing_facts(result: PeriodResult) -> set[str]:
    return {
        b.detail
        for b in result.blockers
        if b.code is BlockerCode.MISSING_FACT and b.detail in _SURCHARGE_FACTS
    }


def test_each_renewal_raises_the_naspi_surcharge_by_half_a_point() -> None:
    """Concia D2, January 2026, a fixed term renewed twice against a permanent.

    L. 92/2012 art. 2 c. 28 and circ. INPS 121/2019 par. 2.3: 1.4% + 2 x
    0.5% = 2.4% of the INPS base, on top of the employer contributions of a
    permanent contract; the two runs differ by that alone, within the cent
    each rounded component may move.
    """
    renewed = FixedTerm(renewals=2, naspi_exclusion=NaspiExclusion.NONE)
    permanent, _ = _employer(CONCIA_D2)
    fixed_term, result = _employer(replace(CONCIA_D2, contract_type=renewed))
    surcharge = _inps_base(result) * naspi_surcharge_rate(2)

    assert abs(fixed_term - permanent - surcharge) <= _CENT
    assert not _missing_facts(result)


def test_replacement_worker_pays_no_naspi_surcharge() -> None:
    """Concia D2, January 2026, hired on a fixed term to replace an absent worker.

    C. 29 lett. a excludes the surcharge, and with it the renewal increase
    (c. 28, third period), so the unknown renewals block nothing.
    """
    replacement = FixedTerm(naspi_exclusion=NaspiExclusion.REPLACEMENT)
    permanent, _ = _employer(CONCIA_D2)
    fixed_term, result = _employer(replace(CONCIA_D2, contract_type=replacement))

    assert fixed_term == permanent
    assert not _missing_facts(result)


@pytest.mark.parametrize(
    ("contract", "fact"),
    [
        pytest.param(FixedTerm(renewals=0), "naspi_exclusion", id="exclusion"),
        pytest.param(
            FixedTerm(naspi_exclusion=NaspiExclusion.NONE), "renewals", id="renewals"
        ),
    ],
)
def test_unknown_surcharge_fact_blocks_the_run(contract: FixedTerm, fact: str) -> None:
    """Concia D2, January 2026, a fixed term with one surcharge fact unstated.

    Whether c. 29 excludes the contract, and how many renewals raise the
    rate, change the employer contributions: left unknown, each is a
    missing fact and the employer INPS amount is not determined.
    """
    _, result = _employer(replace(CONCIA_D2, contract_type=contract))
    (employer,) = (d for d in result.decisions if d.capability == "inps_employer")

    assert _missing_facts(result) == {fact}
    assert employer.amount is None
    assert not result.is_payable


def test_agricultural_fixed_term_pays_no_naspi_surcharge() -> None:
    """Operai agricoli florovivaisti Area 3, operaio, January 2026.

    C. 3 excludes the operai agricoli a tempo determinato o indeterminato
    from the whole article, so from the surcharge of c. 28 and its renewal
    increase.  A fixed term renewed once is an OTD: INPS circ. 43/2026
    allegati 1-2 charge it 33.753% against 33.953% of an OTI, the 0.20%
    Fondo di garanzia TFR the OTD does not owe, and no surcharge: within
    the cent each rounded component may move.
    """
    agricultural = replace(
        CONCIA_D2,
        ccnl_slug="operai-agricoli-florovivaisti.json",
        level_code="Area3",
        category=WorkerCategory.OPERAIO,
    )
    renewed = FixedTerm(renewals=1, naspi_exclusion=NaspiExclusion.NONE)
    permanent, _ = _employer(agricultural)
    fixed_term, result = _employer(replace(agricultural, contract_type=renewed))

    base = next(
        c.base
        for c in result.contribution_breakdown.components
        if c.name == "non_ivs_employer"
    )
    expected = (base * Decimal("0.0020")).quantize(Decimal("0.01"))
    assert abs(permanent - fixed_term - expected) <= Decimal("0.01")
    assert not _missing_facts(result)


def test_agricultural_fixed_term_without_category_blocks_the_run() -> None:
    """Operai agricoli florovivaisti Area 3, January 2026, no category stated.

    The level fixes no category and c. 3 exempts the operai only, so the
    surcharge depends on the category: a missing fact.
    """
    agricultural = replace(
        CONCIA_D2,
        category=None,
        ccnl_slug="operai-agricoli-florovivaisti.json",
        level_code="Area3",
        contract_type=FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE),
    )
    _, result = _employer(agricultural)

    assert "category" in _missing_facts(result)


def _terziario_of_five(reduced: bool | None) -> PeriodResult:
    """Compute Terziario level 5, February 2026, at an employer of five.

    Returns:
        The result of the run.
    """
    request = regular_run(
        2,
        employment=replace(
            CONCIA_D2,
            category=None,
            ccnl_slug="commercio-confcommercio.json",
            level_code="5",
        ),
    )
    employer = replace(request.employer, headcount=Headcount(5), fis_reduction=reduced)
    return ENGINE.calculate_period(replace(request, employer=employer))


@pytest.mark.parametrize(
    ("reduced", "employee"),
    [
        # Base 1,660: x 9.19% = 152.55; x (9.29% - 9.19%) = 1.66.
        (True, Decimal("154.21")),
        # Base 1,660: x 9.19% = 152.55; x (9.36% - 9.19%) = 2.82.
        (None, Decimal("155.37")),
    ],
    ids=["cut", "unknown"],
)
def test_small_terziario_employer_pays_the_cut_fis(
    reduced: bool | None, employee: Decimal
) -> None:
    """An employer of five pays 0.10% of FIS by the worker when it is cut.

    D.Lgs. 148/2015 art. 29 c. 8: 0.50% up to five employees, one third by
    the worker (art. 33 c. 1, 0.17% in INPS circ. 117/2022 all. 1); c.
    8-bis cuts it by 40% for an employer that has not applied for the
    assegno for 24 months: 0.30%, 0.10% by the worker.  The observed
    payslip p04 (Terziario level 5, February 2026, 2,005.67 of gross)
    charges 9.19% IVS and a separate 2.01 line, 0.10% of the base.  The
    gross of level 5 is 1,136.07 + 521.94 + 2.07 = 1,660.08, contributed on
    1,660 (whole euro, INPS circ. 208/2001).  Without the
    fact the full 0.17% applies, with a ``missing_fact`` blocker.
    """
    result = _terziario_of_five(reduced)
    blockers = {(b.code, b.detail) for b in result.blockers}

    assert result.period_gross == Decimal("1660.08")
    assert result.contribution_breakdown.employee == employee
    assert ((BlockerCode.MISSING_FACT, "fis_reduction") in blockers) is (
        reduced is None
    )


@pytest.mark.parametrize(
    ("category", "employer"),
    [
        # Base 1,591 x 33.68% = 535.85.
        (WorkerCategory.OPERAIO, Decimal("535.85")),
        # Base 1,591 x 28.46% = 452.80.
        (WorkerCategory.IMPIEGATO, Decimal("452.80")),
        # A dirigente is raised to the 160.77 daily minimum of industria
        # (INPS circ. 6/2026 allegato 1, Tabella A): 26 x 160.77 = 4,180.02,
        # base 4,180 (whole euro); 4,180 x 26.96% = 1,126.93.
        (WorkerCategory.DIRIGENTE, Decimal("1126.93")),
    ],
)
def test_edilizia_employer_rate_follows_the_category(
    category: WorkerCategory, employer: Decimal
) -> None:
    """Edilizia ANCE level 1, January 2026, at an employer of ten.

    Assimpredil ANCE table 1/2026 (imprese edili industriali up to 15
    employees): employer 33.68% for operai (CIGO edile 4.70%, malattia
    2.22%), 28.46% for impiegati (CIGO 1.70%), 26.96% for dirigenti (no
    CIGO, Fondo Garanzia TFR 0.40%).  The gross 1,590.56 is contributed on
    1,591 (whole euro, INPS circ. 208/2001).
    """
    employment = replace(
        CONCIA_D2, category=category, ccnl_slug="edilizia-ance.json", level_code="1"
    )
    request = regular_run(1, employment=employment)
    employer_profile = replace(request.employer, headcount=Headcount(10))
    result = ENGINE.calculate_period(replace(request, employer=employer_profile))

    assert result.period_gross == Decimal("1590.56")
    assert result.contribution_breakdown.employer == employer
