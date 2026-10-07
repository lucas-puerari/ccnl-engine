"""Employer pension fund contributions on enrolment in the CCNL fund.

Sources:

- D.Lgs. 252/2005 art. 1 c. 2: enrolment is voluntary, so it is an input;
- art. 8 c. 1-2: the fund is financed by the worker, the employer and the
  TFR, at the rates the CCNL sets;
- art. 8 c. 4 (last period as amended by L. 199/2025): employee and
  employer contributions are deductible up to 5 300.00 EUR from tax year
  2026 (TUIR art. 10 c. 1 lett. e-bis, art. 51 c. 2 lett. h); the TFR paid
  to the fund does not count;
- art. 16 c. 1 and art. 9-bis D.L. 103/1991 (conv. L. 166/1991): 10% INPS
  solidarity contribution on the employer contributions, TFR excluded;
- L. 297/1982 art. 3 cc. 15-16 (Normattiva): the 0.50% additional IVS on
  the INPS taxable pay is deducted from the TFR quota of the period, and
  from the TFR paid to the fund when the TFR goes to a pension fund.

CCNL rates from the bundle, each run on its INPS base (the rate times the
base, rounded half up to the cent):

- Tabacco (APTI), level 4A in 2026: 1244.90 minimum + 508.45 contingenza +
  10.33 EDR = 1763.68 a month, 14 runs.  ALIFOND (art. 47 of the accord
  of 02/07/2025): employer 1.50% = 26.4552 -> 26.46, employee minimum 1%
  = 17.6368 -> 17.64; solidarity 10% of 26.46 = 2.646 -> 2.65.  TFR:
  1763.68 / 13.5 = 130.643 -> 130.64, less 0.50% of 1763.68 = 8.8184 ->
  8.82: 121.82.
- Tabacco (APTI), level 3A in 2026: 1524.95 minimum + 515.76 contingenza
  + 10.33 EDR = 2051.04.  TFR: 2051.04 / 13.5 = 151.929 -> 151.93, less
  0.50% of 2051.04 = 10.2552 -> 10.26: 141.67.
- Vetro meccanizzato (Assovetro), level C in 2026: 2354.05 + 10.33 TER =
  2364.38 a month, 13 runs.  FONCHIM employer 1.5% until the +0.5% of
  1 January 2027: 35.4657 -> 35.47; employee 1.2% chosen = 28.37256 ->
  28.37; solidarity 3.547 -> 3.55.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment, InvalidInputError, PayrollEngine
from ccnl_engine.events import BonusEvent
from ccnl_engine.inputs import (
    InpsBaseYtd,
    NoPensionFund,
    OpeningBalances,
    PaymentId,
    PensionFundEnrolment,
    Permanent,
)
from tests.acceptance.legal_scenarios._support import EMPLOYER, ENGINE, regular_period

if TYPE_CHECKING:
    from ccnl_engine import CompetenceYearResult, PeriodResult
    from ccnl_engine.results import CalculationDecision

pytestmark = pytest.mark.legal_scenario

_TABACCO = "tabacco-apti.json"
_VETRO = "vetro-meccanizzato-assovetro.json"
_CAPABILITY = "pension_fund_contribution"
_ALIFOND = PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=True)
_FONCHIM = PensionFundEnrolment("FONCHIM", Decimal("0.012"), tfr_to_fund=True)
_PENSION_ACCOUNTS = frozenset({
    "pension_fund_employee",
    "pension_fund_employer",
    "pension_fund_tfr",
})


def _tabacco(
    pension: PensionFundEnrolment | NoPensionFund | None = _ALIFOND,
) -> Employment:
    return Employment(
        ccnl_slug=_TABACCO,
        level_code="4A",
        pension_fund=pension,
        contract_type=Permanent(),
    )


def _year(employment: Employment) -> CompetenceYearResult:
    return ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=employment, employer=EMPLOYER)
    )


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def _pension_decision(result: PeriodResult) -> CalculationDecision:
    return next(d for d in result.decisions if d.capability == _CAPABILITY)


class TestTabaccoAlifond:
    """ALIFOND on tabacco level 4A, a full 2026 year."""

    def test_run_posts_the_fund_lines(self) -> None:
        """Employer 26.46, employee 17.64, solidarity 2.65 on 1763.68."""
        result = regular_period(employment=_tabacco())
        assert _entry(result, "pension_fund_employer") == Decimal("26.46")
        assert _entry(result, "pension_fund_employee") == Decimal("17.64")
        inps_only = regular_period(employment=_tabacco(NoPensionFund()))
        solidarity = _entry(result, "employer_contributions") - _entry(
            inps_only, "employer_contributions"
        )
        assert solidarity == Decimal("2.65")

    def test_employer_cost_rises_by_fund_and_solidarity(self) -> None:
        """14 x (26.46 + 2.65) = 407.54 a year; the gross does not move."""
        enrolled, not_enrolled = _year(_tabacco()), _year(_tabacco(NoPensionFund()))
        delta = enrolled.annual_employer_cost - not_enrolled.annual_employer_cost
        assert delta == Decimal("407.54")
        assert enrolled.annual_gross == not_enrolled.annual_gross

    def test_employee_contribution_leaves_the_taxable(self) -> None:
        """Within the cap the taxable falls by 14 x 17.64 = 246.96.

        The employer part (370.44) enters the income and is deducted with
        the employee part: 617.40 deducted in the year.
        """
        enrolled, not_enrolled = _year(_tabacco()), _year(_tabacco(NoPensionFund()))
        closing = enrolled.period_results[-1].closing_state.cash.earnings
        base = not_enrolled.period_results[-1].closing_state.cash.earnings
        assert base.taxable - closing.taxable == Decimal("246.96")
        assert closing.pension_deducted == Decimal("617.40")

    def test_net_falls_by_employee_part_less_irpef_saved(self) -> None:
        """The IRPEF saved is the marginal effect on 246.96 of taxable.

        At about 22 100 of taxable: 23% bracket, and the Art. 13 c. 1
        lett. b TUIR deduction 1910 + 1190 x (28000 - R) / 13000 rises by
        1190/13000 per euro.  Saving 246.96 x (0.23 + 1190/13000) = 79.41.
        """
        enrolled, not_enrolled = _year(_tabacco()), _year(_tabacco(NoPensionFund()))
        irpef = (
            not_enrolled.period_results[-1].closing_state.cash.tax.irpef
            - enrolled.period_results[-1].closing_state.cash.tax.irpef
        )
        assert abs(irpef - Decimal("79.41")) <= Decimal("0.02")
        assert enrolled.annual_net - not_enrolled.annual_net == irpef - Decimal(
            "246.96"
        )

    def test_decision_records_rates_and_source(self) -> None:
        """The decision names ALIFOND, its rates and art. 47 of the accord."""
        decision = _pension_decision(regular_period(employment=_tabacco()))
        assert decision.reason_code == "enrolled"
        assert decision.inputs["employer_rate"] == Decimal("0.0150")
        assert decision.inputs["employee_min_rate"] == Decimal("0.0100")
        assert decision.amount == Decimal("44.10")
        assert decision.source is not None
        assert (decision.source.section or "").startswith("Art. 47")

    def test_employee_rate_below_ccnl_minimum_raises(self) -> None:
        """Art. 47 sets the employee part at not less than 1%."""
        low = PensionFundEnrolment("ALIFOND", Decimal("0.005"), tfr_to_fund=True)
        with pytest.raises(InvalidInputError, match="below the minimum"):
            regular_period(employment=_tabacco(low))


class TestTfrToFund:
    """The TFR paid to the fund moves between accounts, not the cost."""

    def test_tfr_moves_to_the_fund_account(self) -> None:
        """130.64 less the 0.50% additional IVS 8.82 goes to the fund."""
        result = regular_period(employment=_tabacco())
        assert _entry(result, "pension_fund_tfr") == Decimal("121.82")
        assert _entry(result, "tfr_accrual") == 0

    def test_tfr_to_the_fund_is_net_of_the_additional_ivs(self) -> None:
        """Level 3A: 151.93 less 10.26 = 141.67 is paid to the fund."""
        employment = Employment(
            ccnl_slug=_TABACCO,
            level_code="3A",
            pension_fund=_ALIFOND,
            contract_type=Permanent(),
        )
        result = regular_period(employment=employment)
        assert _entry(result, "pension_fund_tfr") == Decimal("141.67")

    def test_employer_cost_does_not_depend_on_tfr_choice(self) -> None:
        """With or without the TFR to the fund the cost is the same."""
        kept = PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=False)
        to_fund = regular_period(employment=_tabacco())
        in_company = regular_period(employment=_tabacco(kept))
        assert to_fund.period_employer_cost == in_company.period_employer_cost
        assert _entry(in_company, "tfr_accrual") == Decimal("121.82")
        assert _entry(in_company, "pension_fund_tfr") == 0


class TestVetroFonchim:
    """FONCHIM on vetro level C: 1.5% in 2026, 2.0% only from 2027."""

    def test_employer_cost_rises_at_the_2026_rate(self) -> None:
        """13 x (35.47 + 3.55) = 507.26 a year."""
        employment = Employment(
            ccnl_slug=_VETRO, level_code="C", contract_type=Permanent()
        )
        enrolled = _year(
            Employment(
                ccnl_slug=_VETRO,
                level_code="C",
                pension_fund=_FONCHIM,
                contract_type=Permanent(),
            )
        )
        delta = enrolled.annual_employer_cost - _year(employment).annual_employer_cost
        assert delta == Decimal("507.26")
        first = enrolled.period_results[0]
        assert _entry(first, "pension_fund_employer") == Decimal("35.47")
        assert _entry(first, "pension_fund_employee") == Decimal("28.37")

    def test_no_bundled_minimum_is_recorded(self) -> None:
        """The bundle has no FONCHIM employee minimum: the decision says so."""
        result = regular_period(
            employment=Employment(
                ccnl_slug=_VETRO,
                level_code="C",
                pension_fund=_FONCHIM,
                contract_type=Permanent(),
            )
        )
        assert _pension_decision(result).inputs["employee_min_rate"] == (
            "not_in_bundle"
        )


class TestDeductionCap:
    """Contributions beyond 5 300.00 in the year return to the taxable."""

    def _taxable_change(self, deducted: str) -> tuple[Decimal, PeriodResult]:
        opening = PayrollEngine.import_opening_balances(
            OpeningBalances(
                tax_year=2026,
                payments=(PaymentId.parse("2026-01-regular@2026-01-27"),),
                pension_deducted=Decimal(deducted),
                inps_bases=(InpsBaseYtd(2026, other_employers=Decimal(0)),),
                recoveries=(),
                surtax_obligations=(),
            )
        )
        enrolled = regular_period(employment=_tabacco(), month=2, opening_state=opening)
        plain = regular_period(
            employment=_tabacco(NoPensionFund()), month=2, opening_state=opening
        )
        change = (
            enrolled.closing_state.cash.earnings.taxable
            - plain.closing_state.cash.earnings.taxable
        )
        return change, enrolled

    def test_part_of_the_run_within_the_cap(self) -> None:
        """10.00 of cap left: taxable + 26.46 - 10.00 = +16.46."""
        change, enrolled = self._taxable_change("5290.00")
        assert change == Decimal("16.46")
        assert enrolled.closing_state.cash.earnings.pension_deducted == Decimal(
            "5300.00"
        )

    def test_cap_used_up(self) -> None:
        """No cap left: the employer part 26.46 is taxable income."""
        change, enrolled = self._taxable_change("5300.00")
        assert change == Decimal("26.46")
        assert _pension_decision(enrolled).inputs["deductible"] == 0


class TestEventBase:
    """The fund rate applies to the INPS base of the run, events included."""

    def test_bonus_enters_the_base(self) -> None:
        """1763.68 + 1000.00 bonus: employer 41.46, employee 27.64."""
        bonus = BonusEvent(event_date=date(2026, 1, 15), amount=Decimal(1000))
        result = regular_period(employment=_tabacco(), events=(bonus,))
        assert _entry(result, "pension_fund_employer") == Decimal("41.46")
        assert _entry(result, "pension_fund_employee") == Decimal("27.64")


class TestNotEnrolled:
    """No enrolment: no fund line, and the capability is not applicable."""

    def test_no_pension_line_and_not_enrolled_reason(self) -> None:
        """A CCNL with a fund records that the worker is not enrolled."""
        result = regular_period(employment=_tabacco(NoPensionFund()))
        accounts = {e.account for e in result.ledger_entries}
        assert not accounts & _PENSION_ACCOUNTS
        decision = _pension_decision(result)
        assert decision.reason_code == "not_enrolled"
        assert decision.amount is None
        assert _CAPABILITY not in {g.feature for g in result.capability_report.gaps}
        assert _CAPABILITY not in result.capability_report.rule_sources

    def test_unknown_enrolment_is_not_no_enrolment(self) -> None:
        """A CCNL with a fund and no stated enrolment: undetermined, blocked.

        Enrolment is voluntary (D.Lgs. 252/2005 art. 1 c. 2), so it is a
        fact of the worker: left unknown, the contributions to ALIFOND are
        not computed and the run names the missing fact.
        """
        result = regular_period(employment=_tabacco(None))
        accounts = {e.account for e in result.ledger_entries}
        assert not accounts & _PENSION_ACCOUNTS
        decision = _pension_decision(result)
        assert decision.reason_code == "required_fact_missing"
        assert decision.inputs["funds"] == "ALIFOND"
        stated = regular_period(employment=_tabacco(NoPensionFund()))
        facts = {i.fact for i in result.issues} - {i.fact for i in stated.issues}
        assert facts == {"pension_fund"}
        assert not result.is_payable

    def test_ccnl_without_fund_takes_no_decision(self) -> None:
        """Commercio has no fund in the bundle: nothing to enrol in."""
        result = regular_period()
        assert all(d.capability != _CAPABILITY for d in result.decisions)
        assert "pension_fund" not in {i.fact for i in result.issues}

    def test_enrolment_in_a_fund_the_ccnl_lacks_raises(self) -> None:
        """A fund code the CCNL does not declare is rejected."""
        employment = Employment(
            ccnl_slug=_TABACCO,
            level_code="4A",
            pension_fund=PensionFundEnrolment(
                "FONCHIM", Decimal("0.01"), tfr_to_fund=False
            ),
            contract_type=Permanent(),
        )
        with pytest.raises(InvalidInputError, match="not a fund of CCNL"):
            regular_period(employment=employment)
