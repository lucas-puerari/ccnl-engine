"""The cash value of the board and lodging a live-in worker does not take.

CCNL lavoro domestico of 28 October 2025 (Assindatcolf PDF, sha256
122ca6a72196a835976abac7fb988dc1502973941d52891a546512347fdc9dcf): Art. 36
c. 3 values the board and lodging of the convivente by Tabella F, monthly
= daily x 30 (2026: 2.33 + 2.33 + 2.00 = 6.66 a day, 199.80 a month); on
the days the worker does not take them (ferie, Art. 17 c. 7; sospensioni,
Art. 18 c. 1; congedo matrimoniale, Art. 24 c. 2; illness outside hospital
and the employer's home, Art. 27 c. 9) the employer pays that value in
cash.  Ten days: 199.80 / 30 x 10 = 66.60.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.events import BoardLodgingEvent, SicknessEpisode
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)

_ENGINE = PayrollEngine.bundled()


def _march(ccnl_id: str, *events: BoardLodgingEvent | SicknessEpisode) -> PeriodResult:
    hours = WeeklyHours(Decimal(54 if ccnl_id.endswith("convivente") else 40))
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code="CS" if ccnl_id.endswith("convivente") else "B",
                seniority=SeniorityFact(36, date(2026, 1, 1), SenioritySource.PAYSLIP),
                weekly_hours=hours,
                full_time_weekly_hours=hours,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2023, 1, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(
                contributable_hours=ContributableHours(Decimal(234)), events=events
            ),
        )
    )


def test_ten_days_without_board_pay_66_60() -> None:
    """Paid in cash on top of the month; the TFR base does not move."""
    plain = _march("lavoro-domestico-convivente")
    away = _march(
        "lavoro-domestico-convivente", BoardLodgingEvent(date(2026, 3, 9), 10)
    )
    (decision,) = (d for d in away.decisions if d.capability == "board_lodging")

    assert decision.amount == Decimal("66.60")
    assert dict(decision.inputs) == {
        "days": Decimal(10),
        "monthly_in_kind": Decimal("199.80"),
        "daily_value": Decimal("6.66"),
    }
    assert away.period_gross - plain.period_gross == Decimal("66.60")
    (item,) = (i for i in away.pay_items if "_evt" in i.item_id)
    assert (item.kind, item.quantity, item.amount) == (
        "fixed_allowance_earning",
        Decimal(10),
        Decimal("66.60"),
    )
    (entry,) = (e for e in away.ledger_entries if e.source_item_id == item.item_id)
    assert entry.policy_decision_id == "it/earning/ordinary"
    before, after = plain.closing_state, away.closing_state
    assert after.cash.earnings.taxable - before.cash.earnings.taxable == Decimal(
        "66.60"
    )
    assert after.accrual.inps_bases[0].own - before.accrual.inps_bases[0].own == 66
    tfr = [
        sum(e.amount for e in r.ledger_entries if e.account.value == "tfr_accrual")
        for r in (plain, away)
    ]
    assert tfr[0] == tfr[1]


def test_a_worker_without_board_in_kind_is_rejected() -> None:
    """The non convivente takes no board and lodging from the employer."""
    with pytest.raises(
        InvalidInputError,
        match=r"^BoardLodgingEvent: the pay of the worker provides no",
    ) as error:
        _march(
            "lavoro-domestico-non-convivente",
            BoardLodgingEvent(date(2026, 3, 9), 2),
        )
    assert (error.value.field, error.value.feature) == (
        "BoardLodgingEvent",
        "board_lodging",
    )


@pytest.mark.parametrize("days", [0, 32])
def test_the_days_fall_in_the_month(days: int) -> None:
    """From 1 to the days of the month."""
    with pytest.raises(InvalidInputError, match=r"BoardLodgingEvent\.days"):
        BoardLodgingEvent(date(2026, 3, 9), days)


def test_february_has_28_days() -> None:
    """29 days do not fit February 2026."""
    with pytest.raises(InvalidInputError, match="at most 28"):
        BoardLodgingEvent(date(2026, 2, 9), 29)


def test_sick_days_away_from_the_employer_add_the_value_in_kind() -> None:
    """Art. 27 c. 9: sick 2-6 March at home, outside the employer's house.

    The sick pay is thirtieths of the cash monthly pay, without the value
    in kind (206.93 deducted, 144.85 paid, as in the sickness tests); the
    five days without board and lodging add 5 x 6.66 = 33.30.
    """
    episode = SicknessEpisode("A", date(2026, 3, 2), date(2026, 3, 6))
    sick = _march("lavoro-domestico-convivente", episode)
    away = _march(
        "lavoro-domestico-convivente", episode, BoardLodgingEvent(date(2026, 3, 2), 5)
    )

    def sickness(result: PeriodResult) -> Decimal:
        items = (i.amount for i in result.pay_items if i.kind == "sickness_item")
        return sum(items, Decimal(0))

    assert sickness(sick) == sickness(away) == Decimal("144.85")
    assert away.period_gross - sick.period_gross == Decimal("33.30")
