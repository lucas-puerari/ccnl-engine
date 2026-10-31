"""The indemnity of the notice not given, Metalmeccanico Federmeccanica C3.

C3, 2158.26 EUR a month plus five seniority increments of 29.64 (hired 1
January 2016): monthly pay of art. 2121 c.c. 2306.46.  On 10 March 2026,
122 months of service: the band over ten years, 2 months and 15 days of
notice, 2.5 monthly pays (CCNL 2021 Sez. Quarta Tit. VIII Art. 1).

- Dismissed on 10 March, last day 10 March: the notice runs 11 March to 25
  May (76 days), all unworked: 2.5 * 2306.46 = 5766.15.
- Its employee INPS, 9.19% IVS and 0.30% non-IVS: 5766.15 * 0.0949 =
  547.21; separate taxable 5218.94, at the TFR rate the caller states,
  23%: 1200.36 (art. 19 c. 2 TUIR).
- Dismissed on 31 January, last day 31 January, the TFR computed by the
  engine (fund 20000.00): 120 months, the band up to ten years, 2 monthly
  pays: 4612.92; the TFR rate the engine computes, 23%, on 4612.92 less
  437.77 of INPS: 960.28.
- Dismissed on 1 March, last day 31 March: notice 2 March to 16 May (76
  days), 46 unworked: 5766.15 * 46 / 76 = 3490.04.
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
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import NoticeIndemnityEvent, TerminationTFREvent, WorkEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    FixedTerm,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    TfrFundBalance,
)
from ccnl_engine.pay_item.facade import NoticeIndemnityItem
from ccnl_engine.termination.notice.models import TerminationCause

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2016, 1, 1)
_D, _R = TerminationCause.DISMISSAL, TerminationCause.RESIGNATION
_TFR = TerminationTFREvent(
    date(2026, 3, 10), amount=Decimal("20000.00"), separate_tax_rate=Decimal("0.23")
)


def _run(
    *events: WorkEvent,
    ended: date | None = date(2026, 3, 10),
    ccnl: str = "metalmeccanico-federmeccanica",
    seniority: bool = True,
    fixed_term: bool = False,
    month: int = 3,
    fund: TfrFundBalance | None = None,
) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=Employment(
                ccnl_id=ccnl,
                level_code="C3" if ccnl.startswith("metal") else "4",
                category=WorkerCategory.IMPIEGATO,
                contract_type=(FixedTerm() if fixed_term else Permanent()),
                employment_period=EmploymentPeriod(_HIRED, ended),
                seniority=(
                    SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS)
                    if seniority
                    else None
                ),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
                tfr_fund=fund,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=events),
        )
    )


def _notice(
    received: date, cause: TerminationCause = _D, *, just: bool = False
) -> NoticeIndemnityEvent:
    return NoticeIndemnityEvent(received, cause, just_cause=just)


def _indemnity(result: PeriodResult) -> Decimal | None:
    items = [i.amount for i in result.pay_items if isinstance(i, NoticeIndemnityItem)]
    return items[0] if items else None


def _notice_decisions(result: PeriodResult) -> list[tuple[str, str, Decimal | None]]:
    return [
        (d.status, d.reason_code, d.amount)
        for d in result.decisions
        if d.capability == "termination_notice"
    ]


def test_a_notice_not_given_is_paid_and_taxed_at_the_tfr_rate() -> None:
    """The whole notice, its INPS, its separate tax; the ordinary IRPEF holds."""
    result = _run(_notice(date(2026, 3, 10)), _TFR)
    without = _run(_TFR)

    assert _indemnity(result) == Decimal("5766.15")
    assert _notice_decisions(result) == [
        ("final", "notice_indemnity_due", Decimal("5766.15")),
        ("final", "taxed_at_tfr_rate", Decimal("1200.36")),
    ]
    due, tax = (d for d in result.decisions if d.capability == "termination_notice")
    assert (due.inputs["cause"], due.inputs["unworked_days"]) == ("dismissal", "76")
    assert due.source is not None
    assert (tax.inputs["employee_inps"], tax.inputs["taxable"], tax.inputs["rate"]) == (
        Decimal("547.21"),
        Decimal("5218.94"),
        Decimal("0.23"),
    )
    (item,) = (i for i in result.pay_items if isinstance(i, NoticeIndemnityItem))
    assert item.quantity == 1
    separate = sorted(
        e.amount for e in result.ledger_entries if e.account.value == "separate_tax"
    )
    assert separate == [Decimal("1200.36"), Decimal("4600.00")]
    # The TFR base takes the indemnity: 5766.15 / 13.5 = 427.12, less the
    # 0.50% IVS of L. 297/1982 on it, 28.83: the quota grows by 398.30 (one
    # cent of rounding on the whole run).
    quota = [
        sum(i.amount for i in r.pay_items if i.item_id.startswith("tfr_2026"))
        for r in (result, without)
    ]
    assert abs(quota[0] - quota[1] - Decimal("398.30")) <= Decimal("0.01")
    # The ordinary taxable moves only by the cents of the whole-euro INPS base.
    ordinary = (
        result.closing_state.cash.earnings.taxable,
        without.closing_state.cash.earnings.taxable,
    )
    assert abs(ordinary[0] - ordinary[1]) <= Decimal("0.05")
    assert {lim.id for lim in result.limitations} >= {
        "notice_indemnity_extra_months",
        "notice_indemnity_tfr",
    }
    assert "notice_indemnity_partial" not in {lim.id for lim in result.limitations}


def test_the_tfr_rate_the_engine_computes_taxes_the_indemnity() -> None:
    """Art. 19 c. 2 TUIR: the rate of the computed TFR settlement."""
    end = date(2026, 1, 31)
    result = _run(
        _notice(end),
        TerminationTFREvent(end),
        ended=end,
        month=1,
        fund=TfrFundBalance(2025, Decimal("20000.00"), Decimal(0), Decimal(0)),
    )

    assert _notice_decisions(result) == [
        ("final", "notice_indemnity_due", Decimal("4612.92")),
        ("final", "taxed_at_tfr_rate", Decimal("960.28")),
    ]


def test_a_notice_partly_worked_pays_its_days_left() -> None:
    """46 of 76 days unworked: 3490.04, under the partial-notice limitation."""
    result = _run(_notice(date(2026, 3, 1)), ended=date(2026, 3, 31))

    assert _indemnity(result) == Decimal("3490.04")
    assert "notice_indemnity_partial" in {lim.id for lim in result.limitations}
    # No TFR settlement in the run: no rate, no tax, the run says so.
    assert ("incomplete", "notice_indemnity_tax_rate_unknown", None) in (
        _notice_decisions(result)
    )
    (issue,) = (
        i for i in result.issues if i.code == "notice_indemnity_tax_rate_unknown"
    )
    assert (issue.status, issue.capability, issue.cause) == (
        "incomplete",
        "termination_notice",
        "condition",
    )


def test_a_notice_fully_worked_owes_nothing() -> None:
    """Notice from 2 January to 16 March, last day 31 March."""
    result = _run(_notice(date(2026, 1, 1)), ended=date(2026, 3, 31))

    assert _indemnity(result) is None
    assert _notice_decisions(result) == [("final", "notice_worked", Decimal(0))]


@pytest.mark.parametrize(
    ("cause", "just", "paid"),
    [
        (_D, True, False),
        (_R, True, True),
        (TerminationCause.DEATH, False, True),
        (TerminationCause.MUTUAL_AGREEMENT, False, False),
    ],
)
def test_the_cause_decides_who_owes(
    cause: TerminationCause, just: bool, paid: bool
) -> None:
    """Art. 2119: just cause; art. 2118 c. 3: death; mutual agreement: none."""
    result = _run(_notice(date(2026, 3, 10), cause, just=just))

    assert (_indemnity(result) is not None) is paid
    if not paid:
        assert _notice_decisions(result) == [("final", "notice_not_owed", Decimal(0))]


@pytest.mark.parametrize(
    ("kwargs", "event", "code", "cause"),
    [
        ({}, _notice(date(2026, 3, 10), _R), "notice_owed_by_worker", "rule"),
        (
            {"ccnl": "commercio-confcommercio"},
            _notice(date(2026, 3, 10)),
            "notice_rule_missing",
            "rule",
        ),
        (
            {"seniority": False},
            _notice(date(2026, 3, 10)),
            "notice_seniority_unknown",
            "fact",
        ),
    ],
)
def test_what_the_engine_cannot_pay_it_reports(
    kwargs: dict[str, object], event: NoticeIndemnityEvent, code: str, cause: str
) -> None:
    """A worker's debt, a CCNL without notice, an unknown service."""
    result = _run(event, **kwargs)  # type: ignore[arg-type]

    assert _indemnity(result) is None
    (issue,) = (i for i in result.issues if i.capability == "termination_notice")
    assert (issue.code, issue.cause, issue.status) == (code, cause, "incomplete")


@pytest.mark.parametrize(
    ("kwargs", "event", "field"),
    [
        ({"ended": None}, _notice(date(2026, 3, 10)), "Employment.employment_period"),
        ({"fixed_term": True}, _notice(date(2026, 3, 10)), "Employment.contract_type"),
        (
            {"ended": date(2026, 4, 30)},
            _notice(date(2026, 3, 10)),
            "NoticeIndemnityEvent",
        ),
        (
            {"ended": date(2026, 3, 9)},
            _notice(date(2026, 3, 10)),
            "NoticeIndemnityEvent.received_on",
        ),
    ],
)
def test_a_misplaced_notice_is_rejected(
    kwargs: dict[str, object], event: NoticeIndemnityEvent, field: str
) -> None:
    """Open-ended only, on the run of the last month, an act before the end."""
    with pytest.raises(InvalidInputError) as error:
        _run(event, **kwargs)  # type: ignore[arg-type]

    assert error.value.field == field
