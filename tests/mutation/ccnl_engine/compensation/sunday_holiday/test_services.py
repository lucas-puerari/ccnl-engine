"""The further daily quota of a holiday falling on a Sunday.

L. 260/1949 art. 5 pays it for 25 April, 1 May and 2 June; a CCNL clause
(Chimica art. 11) names the other holidays it pays.  25 April 2027, 4 October
2026 and 1 November 2026 fall on a Sunday.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.sunday_holiday.rules import divisor as _divisor
from ccnl_engine.compensation.sunday_holiday.services import (
    CAPABILITY,
    CLAUSE_LIMITATION,
    SundayHoliday,
)
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.event.total.handlers import _EventTotals
from ccnl_engine.inputs import SeniorityFact, SenioritySource
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

#: A CCNL without a Sunday-holiday clause, absences by 26.
_ANAS = ("anas", "C1")
_CHIMICA = ("chimica-farmaceutica-federchimica", "D1")
_CONCIA = ("concia-unic", "D2")
_ALIMENTARI = ("alimentari-federalimentare", "3")
_EDILIZIA_OPERAI = ("edilizia-ance", "1")
#: ANAS C1 in April 2027: the monthly pay of the chain.
_ANAS_MONTHLY = Decimal("1926.71")
#: Chimica D1 from 1 July 2026: minimo and IPO.
_CHIMICA_MONTHLY = Decimal("2420.26")
_COMMERCIO = ("commercio-confcommercio", "4")
_DMO = ("dmo-federdistribuzione", "IV")


def _run(
    ccnl: tuple[str, str],
    year: int,
    month: int,
    *,
    sector: EmploymentSector = EmploymentSector.PRIVATE,
    employment_period: EmploymentPeriod | None = None,
    seniority: SeniorityFact | None = None,
) -> PeriodResult:
    slug, level = ccnl
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(20)),
            period_id=PeriodId(year, month),
            payment_date=date(year, month, 27),
            ccnl_id=slug,
            level_code=level,
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=(),
            sector=sector,
            employment_period=employment_period,
            seniority=seniority,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _decisions(result: PeriodResult) -> list[tuple[str, Decimal | None]]:
    return [
        (d.reason_code, d.amount)
        for d in result.decisions
        if d.capability == CAPABILITY
    ]


def _limited(result: PeriodResult) -> bool:
    return CLAUSE_LIMITATION in {lim.id for lim in result.limitations}


def _quota(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("sunday_holiday")),
        Decimal(0),
    )


def test_the_statutory_holiday_pays_a_daily_quota() -> None:
    """25 April 2027 pays the monthly pay over the CCNL divisor of 26."""
    result = _run(_ANAS, 2027, 4)
    quota = (_ANAS_MONTHLY / 26).quantize(Decimal("0.01"))

    assert _decisions(result) == [("statutory", quota)]
    assert _quota(result) == quota
    assert not _limited(result)
    (decision,) = (d for d in result.decisions if d.capability == CAPABILITY)
    assert dict(decision.inputs) == {
        "days": "2027-04-25",
        "divisor": Decimal(26),
        "monthly": _ANAS_MONTHLY,
    }
    assert (decision.rule, decision.rule_version) == (
        "law/sunday-holiday:l260-1949-art5",
        "2027",
    )
    (item,) = (i for i in result.pay_items if i.item_id.startswith("sunday_holiday"))
    assert item.kind == "fixed_allowance_earning"
    assert item.quantity == 1
    assert item.source == "Festività cadente di domenica: L. 260/1949 art. 5"
    (entry,) = (e for e in result.ledger_entries if e.pay_item_id == item.item_id)
    assert entry.account == AccountKind.CASH_EARNINGS
    assert entry.amount == quota
    assert entry.policy_decision_id is not None


def _posted(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account), Decimal(0)
    )


@pytest.mark.parametrize(
    ("ccnl", "monthly", "divisor", "days"),
    [
        # Art. 46 c. 1 and art. 50: the quadri function allowance (art. 46
        # lett. g) is out of the paga mensile, divided by 25; 4 November is
        # among the ex festività art. 41 replaces with rest days.
        (("concia-unic", "A"), Decimal("2973.75") - Decimal("25.82"), 25, 1),
        (_CONCIA, Decimal("2052.32"), 25, 1),
        # Art. 34: 1/26 of the retribuzione mensile fissa; 4 November takes
        # the same quota (art. 30), on the same Sunday.
        (_ALIMENTARI, Decimal("2184.22"), 26, 2),
    ],
    ids=["concia-quadro", "concia", "alimentari"],
)
def test_the_clause_names_its_divisor_and_monthly_pay(
    ccnl: tuple[str, str], monthly: Decimal, divisor: int, days: int
) -> None:
    """1 November 2026 on a Sunday, paid at the clause's quota."""
    result = _run(ccnl, 2026, 11)
    quota = (monthly / divisor * days).quantize(Decimal("0.01"))

    assert _decisions(result) == [("ccnl_clause", quota)]
    (decision,) = (d for d in result.decisions if d.capability == CAPABILITY)
    assert decision.inputs["monthly"] == monthly
    assert decision.inputs["divisor"] == divisor
    assert not _limited(result)


def test_the_quota_is_paid_on_the_whole_monthly_pay() -> None:
    """Minimo, scatti and allowances, taxed as pay of the month.

    Alimentari PMI level Q with ten years of seniority: the monthly pay of
    July 2027, with no holiday on a Sunday, is the monthly pay the quota of
    15 August divides, and the quota enters the INPS and TFR bases.
    """
    seniority = SeniorityFact(120, date(2027, 1, 1), SenioritySource.PAYSLIP)
    ccnl = ("alimentari-pmi-unionalimentari", "Q")
    july = _run(ccnl, 2027, 7, seniority=seniority)
    august = _run(ccnl, 2027, 8, seniority=seniority)
    quota = (july.period_gross / 26).quantize(Decimal("0.01"))

    (decision,) = (d for d in august.decisions if d.capability == CAPABILITY)
    assert decision.inputs["monthly"] == july.period_gross == Decimal("3818.24")
    assert august.period_gross == july.period_gross + quota
    for account in ("employee_contributions", "tfr_accrual"):
        assert _posted(august, account) > _posted(july, account)


def test_the_ccnl_clause_pays_its_own_holidays() -> None:
    """Chimica pays 1 November on a Sunday at the monthly pay over 25."""
    result = _run(_CHIMICA, 2026, 11)
    quota = (_CHIMICA_MONTHLY / 25).quantize(Decimal("0.01"))

    assert _decisions(result) == [("ccnl_clause", quota)]
    assert _quota(result) == quota == Decimal("96.81")
    assert not _limited(result)
    (item,) = (i for i in result.pay_items if i.item_id.startswith("sunday_holiday"))
    assert item.source == (
        "Festività cadente di domenica: Art. 11 - Riposo settimanale - Giorni festivi"
    )


@pytest.mark.parametrize(
    ("ccnl", "year", "month", "days"),
    [
        # 4 October is more recent than the Chimica text.
        (_CHIMICA, 2026, 10, "2026-10-04"),
        # No clause: 1 November is not a holiday of L. 260/1949 art. 5, nor
        # 4 November, on the same first Sunday of November.
        (_ANAS, 2026, 11, "2026-11-01,2026-11-01"),
        # 4 November alone, on the first Sunday of November 2027.
        (_ANAS, 2027, 11, "2027-11-07"),
        # The statutory holiday of an hourly-paid worker, without a daily
        # divisor the engine applies.
        (_EDILIZIA_OPERAI, 2027, 4, "2027-04-25"),
    ],
    ids=["recent-holiday", "no-clause", "november-fourth", "no-divisor"],
)
def test_an_unsourced_holiday_records_the_limitation(
    ccnl: tuple[str, str], year: int, month: int, days: str
) -> None:
    """Nothing is paid, and the run records the limitation of the clause."""
    result = _run(ccnl, year, month)

    assert _decisions(result) == [("not_paid", Decimal(0))]
    assert _quota(result) == 0
    assert _limited(result)
    (decision,) = (d for d in result.decisions if d.capability == CAPABILITY)
    assert dict(decision.inputs) == {"days": days}


def test_a_public_employment_is_not_paid() -> None:
    """The treatment of a public employment is not sourced."""
    result = _run(_ANAS, 2027, 4, sector=EmploymentSector.PUBLIC)

    assert _decisions(result) == [("not_paid", Decimal(0))]
    assert _limited(result)


@pytest.mark.parametrize(
    "employment_period",
    [
        EmploymentPeriod(date(2027, 4, 26)),
        EmploymentPeriod(date(2026, 1, 1), date(2027, 4, 24)),
    ],
    ids=["hired-after", "ended-before"],
)
def test_a_holiday_outside_the_employment_is_ignored(
    employment_period: EmploymentPeriod,
) -> None:
    """A Sunday holiday before the hire or after the end adds nothing."""
    result = _run(_ANAS, 2027, 4, employment_period=employment_period)

    assert _decisions(result) == []
    assert not _limited(result)


@pytest.mark.parametrize(
    "employment_period",
    [
        EmploymentPeriod(date(2027, 4, 25)),
        EmploymentPeriod(date(2026, 1, 1), date(2027, 4, 25)),
    ],
    ids=["hired-on-it", "ended-on-it"],
)
def test_a_holiday_within_the_employment_is_paid(
    employment_period: EmploymentPeriod,
) -> None:
    """An employment covering the day, starting or ending on it, is paid."""
    result = _run(_ANAS, 2027, 4, employment_period=employment_period)

    assert [reason for reason, _ in _decisions(result)] == ["statutory"]


@pytest.mark.parametrize(
    ("taxed", "bases"),
    [
        ((True, True, True), (3, 3, 3)),
        ((True, False, True), (3, 0, 3)),
        ((False, True, False), (0, 3, 0)),
    ],
)
def test_the_quota_adds_to_the_bases_it_is_taxed_in(
    taxed: tuple[bool, bool, bool], bases: tuple[int, int, int]
) -> None:
    """The quota enters the INPS, TFR and IRPEF bases its treatment names."""
    totals = _EventTotals(
        inps_base=Decimal(10),
        tfr_base=Decimal(20),
        irpef_base=Decimal(30),
        fringe_value=Decimal(0),
        fringe_inps=Decimal(0),
        fringe_irpef=Decimal(0),
        substitute_base=Decimal(0),
        limitations=frozenset({"other"}),
    )
    added = SundayHoliday(
        amount=Decimal(3), taxed=taxed, limitations=frozenset({CLAUSE_LIMITATION})
    ).added_to(totals)

    assert [added.inps_base, added.tfr_base, added.irpef_base] == [
        Decimal(10 + bases[0]),
        Decimal(20 + bases[1]),
        Decimal(30 + bases[2]),
    ]
    assert added.limitations == {"other", CLAUSE_LIMITATION}


def test_a_month_without_a_sunday_holiday_adds_nothing() -> None:
    """September 2026 has no holiday."""
    result = _run(_CHIMICA, 2026, 9)

    assert _decisions(result) == []
    assert not _limited(result)


@pytest.mark.parametrize(
    ("method", "divisor"),
    [
        (DailyDivisorMethod.BY_22, Decimal(22)),
        (DailyDivisorMethod.BY_25, Decimal(25)),
        (DailyDivisorMethod.BY_26, Decimal(26)),
        (DailyDivisorMethod.BY_30, Decimal(30)),
        (DailyDivisorMethod.BY_HOURLY, None),
    ],
)
def test_the_divisor_follows_the_absence_method(
    method: DailyDivisorMethod, divisor: Decimal | None
) -> None:
    """Without a clause divisor, the CCNL absence divisor applies."""
    rules = load_ccnl("anas").work_rules
    assert rules is not None
    assert rules.absence_rules is not None
    absence = rules.absence_rules.model_copy(update={"daily_divisor_method": method})

    assert _divisor(rules.model_copy(update={"absence_rules": absence})) == divisor


def test_the_divisor_defaults_to_26() -> None:
    """Without work rules or absence rules, the industria divisor of 26."""
    rules = load_ccnl("anas").work_rules
    assert rules is not None

    assert _divisor(None) == 26
    assert _divisor(rules.model_copy(update={"absence_rules": None})) == 26


def test_the_clause_divisor_prevails() -> None:
    """Chimica art. 20 point 4 divides by 25 despite its hourly absences."""
    rules = load_ccnl("chimica-farmaceutica-federchimica").work_rules
    assert rules is not None
    assert rules.absence_rules is not None
    assert rules.absence_rules.daily_divisor_method is DailyDivisorMethod.BY_HOURLY

    assert _divisor(rules) == 25
    clause = rules.sunday_holidays
    assert clause is not None
    without = rules.model_copy(
        update={"sunday_holidays": clause.model_copy(update={"divisor": None})}
    )
    assert _divisor(without) is None


def test_four_november_is_paid_on_the_first_sunday_of_november() -> None:
    """Commercio art. 154: the treatment of a holiday on a Sunday, 7 Nov 2027."""
    result = _run(_COMMERCIO, 2027, 11)
    (decision,) = (d for d in result.decisions if d.capability == CAPABILITY)

    assert decision.inputs["days"] == "2027-11-07"
    monthly = Decimal(str(decision.inputs["monthly"]))
    assert decision.amount == (monthly / 26).quantize(Decimal("0.01"))
    assert not _limited(result)


def test_a_holiday_a_ccnl_adopted_by_declaration_is_paid() -> None:
    """DMO art. 137 adopts 4 October once in force: paid on Sunday 4 Oct 2026."""
    result = _run(_DMO, 2026, 10)

    assert [reason for reason, _ in _decisions(result)] == ["ccnl_clause"]
    assert not _limited(result)


@pytest.mark.parametrize(
    "ccnl", [_CHIMICA, _CONCIA], ids=["paid-in-august", "replaced-by-rest"]
)
def test_four_november_paid_apart_or_not_adds_nothing_in_november(
    ccnl: tuple[str, str],
) -> None:
    """Chimica pays it in August (art. 13), Concia with rest days (art. 41)."""
    result = _run(ccnl, 2027, 11)

    assert _decisions(result) == []
    assert not _limited(result)


def test_the_ex_holiday_of_four_november_is_paid_in_august() -> None:
    """Chimica art. 13: 8/173 of the monthly pay with the August pay."""
    result = _run(_CHIMICA, 2026, 8)
    quota = (_CHIMICA_MONTHLY * 8 / 173).quantize(Decimal("0.01"))

    assert _decisions(result) == [("ex_november_fourth", quota)]
    assert quota == Decimal("111.92")
    (item,) = (
        i for i in result.pay_items if i.item_id.startswith("ex_november_fourth")
    )
    assert item.amount == quota
    assert item.source.startswith("Ex festività 4 novembre: Art. 13")
    (decision,) = (d for d in result.decisions if d.capability == CAPABILITY)
    assert dict(decision.inputs) == {
        "monthly": _CHIMICA_MONTHLY,
        "hours": Decimal(8),
        "hourly_divisor": Decimal(173),
    }
    assert not _limited(result)
    assert _decisions(_run(_CHIMICA, 2026, 7)) == []


@pytest.mark.parametrize(
    "employment_period",
    [
        EmploymentPeriod(date(2026, 1, 2)),
        EmploymentPeriod(date(2025, 1, 1), date(2026, 12, 30)),
    ],
    ids=["hired-in-the-year", "ends-in-the-year"],
)
def test_a_part_year_ex_holiday_records_the_limitation(
    employment_period: EmploymentPeriod,
) -> None:
    """Paid "in ragione annua": the share of a part year is not sourced."""
    result = _run(_CHIMICA, 2026, 8, employment_period=employment_period)

    assert [reason for reason, _ in _decisions(result)] == ["ex_november_fourth"]
    assert _limited(result)


@pytest.mark.parametrize(
    "employment_period",
    [None, EmploymentPeriod(date(2026, 1, 1), date(2026, 12, 31))],
    ids=["open-ended", "the-whole-year"],
)
def test_a_whole_year_ex_holiday_records_nothing(
    employment_period: EmploymentPeriod | None,
) -> None:
    """An employment from 1 January to 31 December is paid in full."""
    result = _run(_CHIMICA, 2026, 8, employment_period=employment_period)

    assert not _limited(result)


def test_a_public_employment_has_no_ex_holiday() -> None:
    """The treatment of a public employment is not sourced."""
    result = _run(_CHIMICA, 2026, 8, sector=EmploymentSector.PUBLIC)

    assert _decisions(result) == []


_CINEMA = ("cinema-audiovisivi-industria", "3")


def test_easter_sunday_is_paid_where_the_clause_lists_it() -> None:
    """Cinema art. 28 lists "Pasqua": Sunday 28 March 2027, at 1/26."""
    result = _run(_CINEMA, 2027, 3)
    (decision,) = (d for d in result.decisions if d.capability == CAPABILITY)

    assert decision.reason_code == "ccnl_clause"
    assert decision.inputs["days"] == "2027-03-28"
    monthly = Decimal(str(decision.inputs["monthly"]))
    assert decision.amount == (monthly / 26).quantize(Decimal("0.01"))
    assert not _limited(result)


def test_chimica_pays_easter_at_one_twenty_fifth() -> None:
    """Chimica art. 12: Easter, Sunday 28 March 2027, at the monthly pay / 25."""
    result = _run(_CHIMICA, 2027, 3)
    (decision,) = (d for d in result.decisions if d.capability == CAPABILITY)

    assert decision.inputs["days"] == "2027-03-28"
    monthly = Decimal(str(decision.inputs["monthly"]))
    assert decision.amount == (monthly / 25).quantize(Decimal("0.01"))


@pytest.mark.parametrize(
    "ccnl", [("metalmeccanico-federmeccanica", "C3"), _ANAS], ids=["clause", "none"]
)
def test_easter_sunday_is_no_holiday_elsewhere(ccnl: tuple[str, str]) -> None:
    """Without "easter" in the clause, or without a clause, nothing in March 2027."""
    result = _run(ccnl, 2027, 3)

    assert _decisions(result) == []
    assert not _limited(result)


@pytest.mark.parametrize(
    ("employment_period", "paid"),
    [
        (EmploymentPeriod(date(2027, 3, 28)), True),
        (EmploymentPeriod(date(2027, 3, 29)), False),
    ],
    ids=["hired-on-easter", "hired-after-easter"],
)
def test_easter_sunday_within_the_employment(
    employment_period: EmploymentPeriod, *, paid: bool
) -> None:
    """Easter is paid only within the employment."""
    result = _run(_CINEMA, 2027, 3, employment_period=employment_period)

    assert bool(_decisions(result)) is paid
