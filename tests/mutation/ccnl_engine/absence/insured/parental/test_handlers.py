"""The parental leave, paid by INPS at its rate on the pay of the month before.

Metalmeccanico Federmeccanica C3 impiegato, 2158.26 EUR a month, daily
quota by 26; February paid 2400.00 with 13 monthly payments a year, so the
RMGG of art. 23 D.Lgs. 151/2001 is (2400 + 2400 / 12) / 30 = 86.666667.
By hand (art. 34 c. 1):

- the whole of March, child born on 1 June 2025, maternity ended on 1
  September 2025 (three months of the couple at 80%), nothing taken: the
  calendar month is one month at 80%, its 31 days paid 86.666667 * 0.80 *
  31 = 2149.33; the whole monthly pay 2158.26 is deducted;
- the same with 80 days already taken, all at 80%: 10 days at 80% and 21
  at 30%, 86.666667 * (8 + 6.3) = 1239.33;
- 2-13 March, child born in 2022 and no maternity end stated: no month at
  80% the birth gives, 12 days at 30%, 86.666667 * 3.6 = 312.00; 11 CCNL
  days deducted, 2158.26 * 11 / 26 = 913.11.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.absence.insured.parental.handlers import _top_up_days
from ccnl_engine.absence.insured.parental.holiday import (
    covered_parental_holidays,
    parental_holiday_extra,
    parental_holiday_units,
)
from ccnl_engine.absence.insured.parental.rules import ParentalDays
from ccnl_engine.absence.insured.rules import MonthPay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import (
    InpsSicknessBase,
    ParentalLeaveEvent,
    ParentalLeaveTaken,
    WorkEvent,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.sickness.term.rules import DailyQuota

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2025, 1, 1)
_FEBRUARY = InpsSicknessBase(Decimal(2400), Decimal(0))
_BORN = date(2025, 6, 1)
_MATERNITY_END = date(2025, 9, 1)
_NOTHING = ParentalLeaveTaken(0, 0, 0)


def _march(
    taken: ParentalLeaveTaken = _NOTHING,
    *,
    base: InpsSicknessBase | None = _FEBRUARY,
) -> ParentalLeaveEvent:
    return ParentalLeaveEvent(
        date(2026, 3, 1),
        date(2026, 3, 31),
        _BORN,
        taken,
        _MATERNITY_END,
        parental_base_pay=base,
    )


def _run(
    *events: WorkEvent,
    category: WorkerCategory = WorkerCategory.IMPIEGATO,
    ccnl_id: str = "metalmeccanico-federmeccanica",
    level_code: str = "C3",
    year: int = 2026,
    month: int = 3,
) -> PeriodResult:
    """Return March 2026 with ``events``.

    Returns:
        The result of the run.
    """
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year, month),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level_code,
                category=category,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=events),
        )
    )


def _amounts(result: PeriodResult) -> dict[str, tuple[str, Decimal]]:
    return {
        i.kind: (i.item_id.rsplit("_", 1)[-1], i.amount)
        for i in result.pay_items
        if "_evt" in i.item_id
    }


def test_ced_optional_may_holiday_with_and_without_target() -> None:
    """May 2026: daily 3000/30 = 100, INPS 30% of 100 = 30.

    May 1 adds 100 - 30 = 70; with no target it adds zero. The
    31-day INPS indemnity is 930 in either case.
    """
    rules = load_ccnl("ced-assoced").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    assert maternity.parental_holiday is not None
    first, last = date(2026, 5, 1), date(2026, 5, 31)
    pay = MonthPay(
        MonthlyPayChain(Decimal(3000), Decimal(0), ()),
        DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
        0,
        Decimal(0),
    )
    rates: dict[date, Decimal | None] = {
        date(2026, 5, day): Decimal("0.30") for day in range(1, 32)
    }
    span = list(rates)
    for target, expected in (
        (None, Decimal(0)),
        (maternity.parental_holiday, Decimal("70.00")),
    ):
        holidays = covered_parental_holidays(target, first, last, None)
        assert parental_holiday_units(holidays, span, rates) == (1 if target else 0)
        assert (
            parental_holiday_extra(
                target,
                first,
                last,
                pay,
                Decimal(100),
                rates,
                [],
                Decimal(0),
                [],
                Decimal(0),
                holidays,
            )
            == expected
        )


def test_optional_holiday_offsets_other_pay_and_skips_non_indemnified_days() -> None:
    """May 1: 100 quota - 30 INPS - 20 ordinary top-up = 50.

    With a sixth-month top-up of 80%, the shortfall is 20 instead.
    Sunday May 3, a holiday outside the span and an unindemnified May 2
    add nothing; with no other share the May 1 shortfall is 70.
    """
    rules = load_ccnl("ced-assoced").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    target = maternity.parental_holiday
    assert target is not None
    may_day = date(2026, 5, 1)
    pay = MonthPay(
        MonthlyPayChain(Decimal(3000), Decimal(0), ()),
        DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
        0,
        Decimal(0),
    )
    rates: dict[date, Decimal | None] = {
        may_day: Decimal("0.30"),
        date(2026, 5, 2): None,
        date(2026, 5, 3): Decimal("0.30"),
    }
    holidays = frozenset({date(2026, 4, 30), *rates})
    for topped, ordinary_rate, sixth, sixth_rate, expected in (
        ([], Decimal(0), [], Decimal(0), Decimal("70.00")),
        ([may_day], Decimal("0.50"), [], Decimal(0), Decimal("50.00")),
        ([], Decimal(0), [may_day], Decimal("0.80"), Decimal("20.00")),
    ):
        assert (
            parental_holiday_extra(
                target,
                may_day,
                date(2026, 5, 3),
                pay,
                Decimal(100),
                rates,
                topped,
                ordinary_rate,
                sixth,
                sixth_rate,
                holidays,
            )
            == expected
        )
    assert parental_holiday_units(holidays, list(rates), rates) == 1


def test_ced_optional_may_holiday_is_posted_in_the_run() -> None:
    """May 2026: 31 INPS days at 31.1111 = 964.44.

    May 1 adds 71.60 - 31.1111 = 40.49; before the optional holiday
    target the employer posted no integration.
    """
    leave = ParentalLeaveEvent(
        date(2026, 5, 1),
        date(2026, 5, 31),
        _BORN,
        _NOTHING,
        _MATERNITY_END,
        parental_base_pay=InpsSicknessBase(Decimal(1000), Decimal(0)),
    )
    result = _run(leave, ccnl_id="ced-assoced", level_code="3", month=5)
    assert _amounts(result)["maternity_item"] == ("inps", Decimal("964.44"))
    assert _amounts(result)["absence_integration_item"] == ("intg", Decimal("40.49"))


def _limitations(result: PeriodResult) -> set[str]:
    """Return the parental limitations of the run but the extra-month one.

    Returns:
        Their ids; every run on leave has ``parental_extra_month_share``.
    """
    ids = {lim.id for lim in result.limitations if lim.id.startswith("parental")}
    assert "parental_extra_month_share" in ids
    return ids - {"parental_extra_month_share"}


def test_a_whole_month_at_80_percent() -> None:
    """A calendar month is one month: its 31 days are paid at 80%."""
    result = _run(_march())

    assert _amounts(result) == {
        "absence_deduction": ("abs", Decimal("2158.26")),
        "maternity_item": ("inps", Decimal("2149.33")),
    }
    (decision,) = (d for d in result.decisions if d.capability == "parental_leave")
    assert (decision.amount, decision.status) == (Decimal("2149.33"), "provisional")
    (item,) = (i for i in result.pay_items if i.kind == "maternity_item")
    assert item.absence_days == Decimal(31)
    assert ("insured_absence_ccnl_not_modelled", "parental_leave") in {
        (i.code, i.capability) for i in result.issues
    }
    assert _limitations(result) == set()
    assert "inps_minimum_base_undetermined" not in {i.code for i in result.issues}


def test_the_80_percent_months_run_out_inside_the_month() -> None:
    """The last 10 days at 80%, then the shared months at 30%."""
    result = _run(_march(ParentalLeaveTaken(80, 80, 0)))

    assert _amounts(result)["maternity_item"] == ("inps", Decimal("1239.33"))
    assert _limitations(result) == {"parental_month_split"}


def test_the_days_beyond_the_indemnified_months_are_not_paid() -> None:
    """The income condition of c. 3 is not modelled: the engine says so."""
    taken = ParentalLeaveTaken(90, 90, 90)

    result = _run(_march(taken))

    assert "maternity_item" not in _amounts(result)
    assert _limitations(result) == {"parental_income_condition"}


def test_an_unstated_end_of_the_maternity_leave_is_a_missing_fact() -> None:
    """Born in 2022: only a late end of the maternity gives 80% months."""
    leave = ParentalLeaveEvent(
        date(2026, 3, 2),
        date(2026, 3, 13),
        date(2022, 6, 1),
        _NOTHING,
        parental_base_pay=_FEBRUARY,
    )

    result = _run(leave)

    assert _amounts(result) == {
        "absence_deduction": ("abs", Decimal("913.11")),
        "maternity_item": ("inps", Decimal("312.00")),
    }
    assert ("missing_fact", "protection_ended_on") in {
        (b.code, b.detail) for b in result.blockers
    }
    (issue,) = (i for i in result.issues if i.code == "parental_protection_end_unknown")
    assert (issue.capability, issue.fact) == ("parental_leave", "protection_ended_on")


def test_without_the_pay_before_a_fact_is_missing() -> None:
    """The base is a fact of the payroll history: its absence blocks."""
    result = _run(_march(base=None))

    (issue,) = (i for i in result.issues if i.code == "parental_base_pay_unknown")
    assert (issue.capability, issue.fact) == ("parental_leave", "parental_base_pay")
    assert "ParentalLeaveEvent.parental_base_pay" in issue.message
    # The pay of the run: (2158.26 + 2158.26 / 12) / 30 * 0.80 * 31 = 1932.84.
    assert _amounts(result)["maternity_item"] == ("inps", Decimal("1932.84"))


def test_an_operaio_keeps_the_pay_of_the_run_under_a_limitation() -> None:
    """Art. 23 c. 5 is not computed: the engine says so."""
    result = _run(_march(), category=WorkerCategory.OPERAIO)

    assert _limitations(result) == {"parental_daily_base"}


def test_the_leave_keeps_the_13th_and_the_leave_accrual_not_the_tfr() -> None:
    """Art. 34 c. 5; art. 2120 c. 3 c.c. keeps no parental leave in the TFR."""
    worked, away = _run(), _run(_march())

    assert away.extra_months == worked.extra_months
    assert away.closing_state.accrual.leave == worked.closing_state.accrual.leave
    (tfr,) = (d.amount for d in away.decisions if d.capability == "tfr")
    assert tfr == Decimal(0)


def test_autorimesse_forty_days_cap_and_later_run() -> None:
    """At 93.333333/day: 30 * (80%-30%) = 1400; nine April days add zero."""
    leave = ParentalLeaveEvent(
        date(2026, 3, 1),
        date(2026, 4, 9),
        date(2022, 1, 1),
        _NOTHING,
        parental_base_pay=_FEBRUARY,
        topped_up_days_before=0,
    )
    march = _run(leave, ccnl_id="autorimesse-ic35", level_code="C4")
    april = _run(leave, ccnl_id="autorimesse-ic35", level_code="C4", month=4)
    assert _amounts(march)["absence_integration_item"] == ("intg", Decimal("1400.00"))
    assert "absence_integration_item" not in _amounts(april)
    assert _amounts(march)["maternity_item"] == ("inps", Decimal("868.00"))
    assert "insured_absence_ccnl_not_modelled" not in {i.code for i in march.issues}


def test_autorimesse_prior_pieces_and_unknown_history() -> None:
    """With 25 used, five at 93.333333 * 50% add 233.33; unknown adds zero."""

    def leave(prior: int | None) -> ParentalLeaveEvent:
        return ParentalLeaveEvent(
            date(2026, 3, 1),
            date(2026, 3, 10),
            date(2022, 1, 1),
            _NOTHING,
            parental_base_pay=_FEBRUARY,
            topped_up_days_before=prior,
        )

    result = _run(leave(25), ccnl_id="autorimesse-ic35", level_code="C4")
    assert _amounts(result)["absence_integration_item"] == ("intg", Decimal("233.33"))
    unknown = _run(leave(None), ccnl_id="autorimesse-ic35", level_code="C4")
    assert "absence_integration_item" not in _amounts(unknown)
    assert "parental_top_up_history_unknown" in {i.code for i in unknown.issues}


def test_an_earlier_leave_and_the_earlier_month_of_this_one_both_count() -> None:
    """10 days of an earlier leave; March 21 days here: April gets the last 0.

    The counter holds only the earlier leaves (10); the run counts the 21
    March days of this leave itself: 10 + 21 > 30, so April adds nothing
    and March pays 20 days, 20 * 93.333333 * 50% = 933.33.
    """
    leave = ParentalLeaveEvent(
        date(2026, 3, 11),
        date(2026, 4, 9),
        date(2022, 1, 1),
        _NOTHING,
        parental_base_pay=_FEBRUARY,
        topped_up_days_before=10,
    )
    march = _run(leave, ccnl_id="autorimesse-ic35", level_code="C4")
    april = _run(leave, ccnl_id="autorimesse-ic35", level_code="C4", month=4)
    assert _amounts(march)["absence_integration_item"] == ("intg", Decimal("933.33"))
    assert "absence_integration_item" not in _amounts(april)


def test_lapidei_starts_in_july_and_excludes_enhanced_months() -> None:
    """On July 1 the 30% becomes eligible; enhanced months never qualify."""

    def leave(year: int, month: int, born: date) -> ParentalLeaveEvent:
        return ParentalLeaveEvent(
            date(year, month, 1),
            date(year, month, 10),
            born,
            _NOTHING,
            parental_base_pay=_FEBRUARY,
            topped_up_days_before=0,
        )

    clause = load_ccnl("materiali-costruzione-lapidei-confapi").work_rules
    assert clause is not None
    assert clause.insured_absence is not None
    rule = clause.insured_absence.parental
    assert rule is not None
    june_day, july_day = date(2025, 6, 30), date(2025, 7, 1)
    days = ParentalDays(rates={june_day: Decimal("0.3"), july_day: Decimal("0.3")})
    assert _top_up_days(
        leave(2025, 6, date(2022, 1, 1)),
        days,
        (june_day, july_day),
        rule,
        Decimal("0.3"),
    ) == [july_day]

    def lapidei(event: ParentalLeaveEvent) -> PeriodResult:
        return _run(
            event,
            year=2026,
            month=7,
            ccnl_id="materiali-costruzione-lapidei-confapi",
            level_code="8",
        )

    enhanced_days = ParentalDays(rates={july_day: Decimal("0.8")})
    assert (
        _top_up_days(
            leave(2025, 7, date(2025, 1, 1)),
            enhanced_days,
            (july_day, july_day),
            rule,
            Decimal("0.3"),
        )
        == []
    )
    single = ParentalLeaveEvent(
        july_day,
        july_day,
        date(2022, 1, 1),
        _NOTHING,
        single_parent=True,
        topped_up_days_before=0,
    )
    assert _top_up_days(single, days, (july_day, july_day), rule, Decimal("0.3")) == []
    july = lapidei(leave(2026, 7, date(2022, 1, 1)))
    assert "insured_absence_without_daily_quota" in {i.code for i in july.issues}


def test_the_leave_ends_before_the_child_is_fourteen() -> None:
    """Art. 32 c. 1: the leave is due in the first fourteen years."""
    leave = ParentalLeaveEvent(
        date(2026, 3, 1),
        date(2026, 3, 31),
        date(2012, 3, 15),
        _NOTHING,
        parental_base_pay=_FEBRUARY,
    )

    with pytest.raises(InvalidInputError, match="14th birthday"):
        _run(leave)


def _autorimesse(prior: int | None, *, born: date = date(2022, 1, 1)) -> PeriodResult:
    leave = ParentalLeaveEvent(
        date(2026, 3, 1),
        date(2026, 3, 10),
        born,
        _NOTHING,
        parental_base_pay=_FEBRUARY,
        topped_up_days_before=prior,
    )
    return _run(leave, ccnl_id="autorimesse-ic35", level_code="C4")


def _reason_of(result: PeriodResult) -> str:
    (decision,) = (d for d in result.decisions if d.capability == "parental_leave")
    return decision.reason_code


@pytest.mark.parametrize("prior", [30, 31], ids=["used-up", "beyond"])
def test_a_used_up_cap_tops_up_nothing(prior: int) -> None:
    """30 days already topped up by earlier leaves: none left."""
    result = _autorimesse(prior)
    assert "absence_integration_item" not in _amounts(result)
    assert _reason_of(result) == "ccnl_treatment_applied"


def test_the_counter_is_a_missing_fact_only_where_the_ccnl_tops_up() -> None:
    """Autorimesse without the counter: an incomplete issue naming the fact."""
    result = _autorimesse(None)
    (issue,) = (i for i in result.issues if i.code == "parental_top_up_history_unknown")
    assert (issue.status, issue.capability, issue.fact, issue.cause) == (
        "incomplete",
        "parental_leave",
        "topped_up_days_before",
        "fact",
    )
    assert issue.message.startswith(
        "ParentalLeaveEvent.topped_up_days_before is required to cap "
    )
    assert _reason_of(result) == "statutory_only"
    plain = _run(
        ParentalLeaveEvent(
            date(2026, 3, 2),
            date(2026, 3, 13),
            _BORN,
            _NOTHING,
            parental_base_pay=_FEBRUARY,
        )
    )
    assert "parental_top_up_history_unknown" not in {i.code for i in plain.issues}
    assert "absence_integration_item" not in _amounts(plain)


def test_an_enhanced_day_at_eighty_percent_needs_no_top_up() -> None:
    """A child born in 2025: INPS already pays 80%, the top-up adds nothing."""
    result = _autorimesse(0, born=_BORN)
    assert "absence_integration_item" not in _amounts(result)


def test_the_cohort_issue_explains_the_eighty_percent_months() -> None:
    """The message of the unstated end of the maternity leave."""
    leave = ParentalLeaveEvent(
        date(2026, 3, 2),
        date(2026, 3, 13),
        date(2022, 6, 1),
        _NOTHING,
        parental_base_pay=_FEBRUARY,
    )
    (issue,) = (
        i for i in _run(leave).issues if i.code == "parental_protection_end_unknown"
    )
    assert issue.message.startswith(
        "the months INPS pays at 80% depend on the day the last maternity "
    )
