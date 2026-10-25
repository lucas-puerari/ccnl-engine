"""TFR settlement at the termination and its separate tax, through the run.

Art. 19 c. 1 TUIR (Normattiva, text in force from 12-8-2006 to 31-12-2026):
the TFR "costituisce reddito per un importo che si determina riducendo il
suo ammontare delle rivalutazioni già assoggettate ad imposta sostitutiva";
the rate is the one "determinata con riferimento all'anno in cui è maturato
il diritto alla percezione, corrispondente all'importo che risulta dividendo
il suo ammontare [...] al netto delle rivalutazioni già assoggettate ad
imposta sostitutiva, per il numero degli anni e frazione di anno preso a
base di commisurazione, e moltiplicando il risultato per dodici".  Art. 11
TUIR as amended by L. 199/2025 art. 1 c. 3: 23% up to EUR 28,000, 33% up to
EUR 50,000, 43% above.  Art. 2120 c. 1 c.c.: a fraction of month of at
least 15 days is a whole month.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine import PayrollEngine
from ccnl_engine.balance.competence.models import EmploymentAccrualState
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.fact.inputs import EmploymentPeriod, PublicEndOfService
from ccnl_engine.employment.inputs import FixedTerm
from ccnl_engine.events import TerminationTFREvent
from ccnl_engine.inputs import (
    InpsBaseYtd,
    NoPensionFund,
    OpeningBalances,
    PensionFundEnrolment,
    SeniorityFact,
    SenioritySource,
    TfrFundBalance,
)
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import calculate_period
from ccnl_engine.run.models import PayrollRun, RunKind
from ccnl_engine.run.types import PeriodId
from ccnl_engine.year.competence.services import calculate_competence_year
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.unit.ccnl_engine.builders import year_plan

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_CENT = Decimal("0.01")
_HIRED_2020 = EmploymentPeriod(date(2020, 1, 1), date(2026, 1, 31))
_FUND = TfrFundBalance(2025, Decimal("20000.00"), Decimal("500.00"), Decimal("0.00"))
_EVENT = TerminationTFREvent(date(2026, 1, 31))


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def _euro(value: Decimal) -> Decimal:
    return value.quantize(Decimal(1), rounding=ROUND_HALF_UP)


def _quota(pay: Decimal) -> Decimal:
    """Return the TFR quota of a run.

    Returns:
        Pay / 13.5 less 0.50% of the whole-euro INPS base, each in cents.
    """
    return _money(pay / Decimal("13.5")) - _money(_euro(pay) * Decimal("0.005"))


def _irpef_2026(income: Decimal) -> Decimal:
    """Return the gross IRPEF of 2026 on ``income`` (art. 11 TUIR).

    Returns:
        The tax, not rounded.
    """
    first = min(income, Decimal(28000)) * Decimal("0.23")
    second = max(min(income, Decimal(50000)) - Decimal(28000), Decimal(0))
    third = max(income - Decimal(50000), Decimal(0))
    return first + second * Decimal("0.33") + third * Decimal("0.43")


def _settlement(result: PeriodResult) -> tuple[CalculationDecision, ...]:
    return tuple(
        d
        for d in result.decisions
        if d.capability == "termination_tfr" and d.origin is DecisionOrigin.ENGINE
    )


def _ledger(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account is account), Decimal(0)
    )


def _codes(result: PeriodResult) -> set[str]:
    return {issue.code for issue in result.issues}


def _run(month: int = 1, **kwargs: Any) -> PeriodResult:  # noqa: ANN401
    """Compute the run of ``month`` 2026 of a Federmeccanica C3 worker.

    Returns:
        The result of the run, a termination run unless ``run`` is given.
    """
    kwargs.setdefault("employment_period", _HIRED_2020)
    kwargs.setdefault("tfr_fund", _FUND)
    kwargs.setdefault("tfr_treasury_fund", False)
    kwargs.setdefault("pension_fund", NoPensionFund())
    kwargs.setdefault("events", (_EVENT,))
    kwargs.setdefault(
        "run", PayrollRun(run_kind=RunKind.TERMINATION, month=month, year=2026)
    )
    year = kwargs.pop("year", 2026)
    kwargs.setdefault("ccnl_id", "metalmeccanico-federmeccanica")
    kwargs.setdefault("level_code", "C3")
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=year, month=month),
            payment_date=date(year, month, 27),
            employer=EmployerProfile(headcount=Headcount(50)),
            seniority=new_hire(2020),
            **kwargs,
        )
    )


@pytest.mark.legal_scenario
def test_chimica_d1_terminated_in_october_2026_against_a_hand_oracle() -> None:
    """A D1 of Chimica Federchimica hired on 2024-01-01, out on 2026-10-31.

    Inputs, every one stated here:

    - CCNL chimica-farmaceutica-federchimica, level D1, full time,
      permanent, TFR kept with the employer (no pension fund, not in the
      Fondo Tesoreria), hired 2024-01-01, last day 2026-10-31;
    - D1 minimo + IPO from the bundled tables: EUR 2,360.26 from
      2025-12-01, EUR 2,420.26 from 2026-07-01; no seniority increment (the
      CCNL pays none to D1), no allowance;
    - TFR fund at 31-12-2025, a fact of the request the engine does not
      compute, with illustrative values (the bundle has no D1 table for
      January-June 2024 nor the December 2024 index to derive it): EUR
      4,384.62, of which EUR 41.17 of revaluations net of the 17%
      substitute tax; no advance paid.

    By hand: each 2026 run accrues pay / 13.5 less 0.50% of the whole-euro
    INPS base (L. 297/1982 art. 3 c. 16): January-June 174.83 - 11.80 =
    163.03; July-September 179.28 - 12.10 = 167.18; October pays its month
    and the ratei of the tredicesima, 10/12 of 2,420.26 = 2,016.88, so
    4,437.14 / 13.5 = 328.68 less 22.19 = 306.49.  Quotas of 2026 =
    1,786.21; TFR paid = 4,384.62 + 1,786.21 = 6,170.83, without the
    revaluation of 2026 (art. 2120 c. 5), which needs the October 2026 FOI
    index, not published on 2026-10-19.  Taxable = 6,170.83 - 41.17 =
    6,129.66; 34 months of service; reference income = 6,129.66 x 12 /
    (34 / 12) = 25,960.91, all in the 23% bracket, so the average rate is
    23% and the tax 6,129.66 x 23% = 1,409.82.
    """
    fund = TfrFundBalance(2025, Decimal("4384.62"), Decimal("41.17"), Decimal(0))
    plan = year_plan(
        2026,
        "chimica-farmaceutica-federchimica",
        "D1",
        employment_period=EmploymentPeriod(date(2024, 1, 1), date(2026, 10, 31)),
        seniority=SeniorityFact.since(
            date(2024, 1, 1), SenioritySource.EMPLOYER_RECORDS
        ),
        tfr_fund=fund,
        events={10: (TerminationTFREvent(date(2026, 10, 31)),)},
    )
    first, july = Decimal("2360.26"), Decimal("2420.26")
    october = july + _money(july * 10 / 12)
    quotas = 6 * _quota(first) + 3 * _quota(july) + _quota(october)
    payout = fund.amount + quotas
    taxable = payout - Decimal("41.17")
    reference = taxable * 12 / (Decimal(34) / 12)
    rate = _irpef_2026(reference) / reference
    tax = _money(taxable * rate)

    result = calculate_competence_year(plan).period_results[-1]
    due, separate = _settlement(result)

    assert (quotas, payout, tax) == (
        Decimal("1786.21"),
        Decimal("6170.83"),
        Decimal("1409.82"),
    )
    assert (due.status, due.reason_code, due.amount) == (
        CalculationStatus.INCOMPLETE,
        "revaluation_pending",
        payout,
    )
    assert (separate.status, separate.reason_code, separate.amount) == (
        CalculationStatus.FINAL,
        "average_rate",
        tax,
    )
    assert separate.inputs["months_of_service"] == "34"
    assert separate.inputs["taxable"] == taxable
    assert separate.inputs["reference_income"] == _money(reference)
    assert separate.inputs["average_rate"] == rate
    assert _ledger(result, AccountKind.TFR_SETTLEMENT) == payout
    assert _ledger(result, AccountKind.SEPARATE_TAX) == tax
    assert "tfr_settlement_revaluation_pending" in _codes(result)


def test_a_reference_income_above_the_first_bracket_takes_its_average_rate() -> None:
    """Hired 2020-01-01, out on 2026-01-31: 73 months, two brackets.

    The fund of EUR 20,000.00 holds EUR 500.00 of revaluations; the run
    accrues its own quota.  Taxable = 19,500.00 + quota; reference income
    = taxable x 12 / (73 / 12), above EUR 28,000.  The fund is revalued
    for January (art. 2120 c. 5): 0.015 / 12 + 0.75 x (100.4 x 1.214 /
    121.5 - 1) = 0.00363025; 20,000.00 x 0.00363025 = 72.60, less the 17%
    tax of 12.34: 60.26 paid, outside the taxable.
    """
    result = _run()
    due, separate = _settlement(result)
    quota = due.inputs["run_quota"]
    assert isinstance(quota, Decimal)
    taxable = Decimal("19500.00") + quota
    reference = taxable * 12 / (Decimal(73) / 12)
    rate = _irpef_2026(reference) / reference

    assert reference > Decimal(28000)
    assert due.amount == Decimal("20000.00") + quota + Decimal("60.26")
    assert due.reason_code == "tfr_due"
    assert separate.inputs["months_of_service"] == "73"
    assert separate.amount == _money(taxable * rate)


def test_a_worker_hired_in_the_year_is_paid_a_final_tfr() -> None:
    """No fund before the year: nothing to revalue, the payout is final."""
    result = _run(
        employment_period=EmploymentPeriod(date(2026, 1, 10), date(2026, 1, 31)),
        tfr_fund=None,
    )
    due, separate = _settlement(result)
    assert (due.status, due.reason_code) == (CalculationStatus.FINAL, "tfr_due")
    assert due.amount == due.inputs["run_quota"]
    assert separate.inputs["months_of_service"] == "1"
    assert separate.inputs["average_rate"] == Decimal("0.23")


def test_a_caller_rate_overrides_the_average_rate_on_the_taxable() -> None:
    """The caller's rate taxes the taxable the engine computes."""
    event = TerminationTFREvent(date(2026, 1, 31), separate_tax_rate=Decimal("0.25"))
    result = _run(events=(event,))
    due, separate = _settlement(result)
    (caller,) = (
        d for d in result.decisions if d.origin is DecisionOrigin.CALLER_SUPPLIED
    )
    taxable = separate.inputs["taxable"]
    assert isinstance(taxable, Decimal)
    assert (separate.reason_code, separate.amount) == (
        "caller_rate",
        _money(taxable * Decimal("0.25")),
    )
    assert "average_rate" not in separate.inputs
    assert (caller.inputs["fields"], caller.amount) == ("separate_tax_rate", None)
    assert due.status is CalculationStatus.FINAL


def test_a_caller_payout_is_posted_as_given() -> None:
    """A caller payout and rate post as stated, and nothing is computed."""
    event = TerminationTFREvent(
        date(2026, 1, 31), amount=Decimal("1000.00"), separate_tax_rate=Decimal("0.2")
    )
    result = _run(events=(event,))
    (caller,) = (d for d in result.decisions if d.capability == "termination_tfr")
    assert caller.origin is DecisionOrigin.CALLER_SUPPLIED
    assert caller.inputs["fields"] == "amount,separate_tax_rate"
    assert _ledger(result, AccountKind.TFR_SETTLEMENT) == Decimal("1000.00")
    assert _ledger(result, AccountKind.SEPARATE_TAX) == Decimal("200.00")


def test_the_run_quota_joins_the_quotas_of_the_closing_state() -> None:
    """The closing state counts the TFR the run accrued with the employer."""
    result = _run()
    (due, _) = _settlement(result)
    assert result.closing_state.accrual.tfr_quotas is not None
    (quota,) = result.closing_state.accrual.tfr_quotas
    assert (quota.year, quota.amount) == (2026, due.inputs["run_quota"])


_UNKNOWN_QUOTAS = PeriodState(
    accrual=EmploymentAccrualState(tfr_quotas_known_from=2027)
)


@pytest.mark.parametrize(
    ("kwargs", "payout_reason", "code"),
    [
        (
            {
                "public_end_of_service": PublicEndOfService.TFS,
                "ccnl_id": "funzioni-centrali-aran",
                "level_code": "FUNZIONARI",
            },
            "tfr_at_inps",
            "tfr_settlement_tfr_at_inps",
        ),
        (
            {"tfr_treasury_fund": True},
            "treasury_fund_share",
            "tfr_settlement_treasury_fund_share",
        ),
        (
            {"tfr_treasury_fund": None},
            "required_fact_missing",
            "tfr_settlement_required_fact_missing",
        ),
        ({"employment_period": None}, "required_fact_missing", None),
        ({"tfr_fund": None}, "required_fact_missing", None),
        (
            {"tfr_fund": TfrFundBalance(2024, Decimal("1.00"))},
            "required_fact_missing",
            None,
        ),
        ({"opening_state": _UNKNOWN_QUOTAS}, "required_fact_missing", None),
    ],
)
def test_a_tfr_the_engine_cannot_compute_posts_nothing(
    kwargs: dict[str, Any], payout_reason: str, code: str | None
) -> None:
    """Each gap leaves both decisions incomplete and posts no settlement."""
    result = _run(**kwargs)
    due, separate = _settlement(result)
    assert (due.status, due.reason_code, due.amount) == (
        CalculationStatus.INCOMPLETE,
        payout_reason,
        None,
    )
    assert (separate.status, separate.amount) == (CalculationStatus.INCOMPLETE, None)
    assert _ledger(result, AccountKind.TFR_SETTLEMENT) == Decimal(0)
    if code is not None:
        assert code in _codes(result)


def test_a_month_of_the_year_not_closed_leaves_the_quotas_unknown() -> None:
    """A March termination opened without January and February runs."""
    result = _run(
        3,
        employment_period=EmploymentPeriod(date(2020, 1, 1), date(2026, 3, 31)),
        events=(TerminationTFREvent(date(2026, 3, 31)),),
    )
    (due, _) = _settlement(result)
    assert due.reason_code == "required_fact_missing"
    assert any(i.fact == "tfr_quotas" for i in result.issues)


def test_a_tfr_paid_to_a_pension_fund_is_not_computed() -> None:
    """Art. 19 c. 1 adds the sums of the pension fund to the reference income."""
    result = _run(
        pension_fund=PensionFundEnrolment("COMETA", Decimal("0.012"), tfr_to_fund=True)
    )
    (due, _) = _settlement(result)
    assert due.reason_code == "pension_fund_tfr"


@pytest.mark.parametrize(
    ("kwargs", "tax_reason", "fact"),
    [
        (
            {"tfr_fund": TfrFundBalance(2025, Decimal("100.00"))},
            "required_fact_missing",
            "revaluations",
        ),
        (
            {"tfr_fund": TfrFundBalance(2025, Decimal("100.00"), Decimal(0))},
            "required_fact_missing",
            "advances",
        ),
        (
            {
                "tfr_fund": TfrFundBalance(
                    2025, Decimal("100.00"), Decimal(0), Decimal("50.00")
                )
            },
            "advances_not_modelled",
            None,
        ),
        (
            {
                "employment_period": EmploymentPeriod(
                    date(2024, 6, 1), date(2026, 1, 31)
                ),
                "contract_type": FixedTerm(),
            },
            "fixed_term_deduction_not_modelled",
            None,
        ),
        # Hired in 1995: the TFR accrued up to 31 December 2000 keeps the
        # rules before D.Lgs. 47/2000 (art. 11 c. 1), which are not modelled.
        (
            {
                "employment_period": EmploymentPeriod(
                    date(1995, 3, 1), date(2026, 1, 31)
                ),
                "tfr_fund": TfrFundBalance(
                    2025, Decimal("40000.00"), Decimal(0), Decimal(0)
                ),
            },
            "tfr_before_2001_not_modelled",
            None,
        ),
    ],
)
def test_a_tax_the_engine_cannot_compute_leaves_the_payout_posted(
    kwargs: dict[str, Any], tax_reason: str, fact: str | None
) -> None:
    """The TFR is posted; its tax is incomplete and not withheld."""
    result = _run(**kwargs)
    due, separate = _settlement(result)
    assert due.amount is not None
    assert (separate.status, separate.reason_code, separate.amount) == (
        CalculationStatus.INCOMPLETE,
        tax_reason,
        None,
    )
    assert _ledger(result, AccountKind.TFR_SETTLEMENT) == due.amount
    assert _ledger(result, AccountKind.SEPARATE_TAX) == Decimal(0)
    if fact is not None:
        assert any(i.fact == fact for i in result.issues)


def test_a_fund_carried_over_into_an_employment_of_the_year_is_paid() -> None:
    """A transfer of undertaking (art. 2112 c.c.) states the fund it carries.

    January revaluation: 3,000.00 x 0.00363025 = 10.89, less 1.85 of tax.
    """
    result = _run(
        employment_period=EmploymentPeriod(date(2026, 1, 10), date(2026, 1, 31)),
        tfr_fund=TfrFundBalance(2025, Decimal("3000.00"), Decimal(0), Decimal(0)),
    )
    due, separate = _settlement(result)
    quota = due.inputs["run_quota"]
    assert isinstance(quota, Decimal)
    assert due.amount == Decimal("3000.00") + quota + Decimal("9.04")
    assert due.reason_code == "tfr_due"
    assert separate.status is CalculationStatus.FINAL


def test_imported_balances_without_quotas_block_only_their_year() -> None:
    """Imported in 2026 without quotas: a 2027 termination knows its own.

    The import leaves the quotas of 2026 unknown; the January 2027 run
    needs none before it, so its payout is computed (2027 has no
    settlement rules, so its tax is not).
    """
    imported = PayrollEngine.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            inps_bases=(InpsBaseYtd(2026, Decimal(0), Decimal(0)),),
            recoveries=(),
            surtax_obligations=(),
        )
    )
    accrual = imported.accrual
    result = _run(
        year=2027,
        employment_period=EmploymentPeriod(date(2020, 1, 1), date(2027, 1, 31)),
        tfr_fund=TfrFundBalance(2026, Decimal(0), Decimal(0), Decimal(0)),
        events=(TerminationTFREvent(date(2027, 1, 31)),),
        run=PayrollRun(run_kind=RunKind.TERMINATION, month=1, year=2027),
        opening_state=PeriodState(accrual=accrual),
    )
    (due, _) = _settlement(result)
    assert (accrual.tfr_quotas_known_from, accrual.tfr_quota(2026)) == (2027, None)
    assert (due.status, due.reason_code) == (CalculationStatus.FINAL, "tfr_due")


def test_a_year_without_settlement_rules_has_no_rate() -> None:
    """The bundle has no settlement rules for 2027 (D.Lgs. 117/2026)."""
    period = EmploymentPeriod(date(2027, 1, 1), date(2027, 1, 31))
    result = _run(
        year=2027,
        employment_period=period,
        tfr_fund=None,
        events=(TerminationTFREvent(date(2027, 1, 31)),),
        run=PayrollRun(run_kind=RunKind.TERMINATION, month=1, year=2027),
    )
    due, separate = _settlement(result)
    assert due.reason_code == "tfr_due"
    assert (separate.reason_code, separate.inputs["months_of_service"]) == (
        "rule_not_in_bundle",
        "not_computed",
    )
