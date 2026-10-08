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

CCNL rates from the bundle, each run on the base of the fund (the rate
times the base, rounded half up to the cent).  ALIFOND and FONCHIM compute
on the pay that enters the TFR (Alifond Scheda 'I destinatari e i
contributi', note (1); Fonchim opuscolo informativo 2026, page 13), and
FONCHIM adds 0.25% paid by the employer for the insurance of premorienza
and invalidity:

- Tabacco (APTI), level 4A in 2026: 1244.90 minimum + 508.45 contingenza +
  10.33 EDR = 1763.68 a month, 14 runs.  ALIFOND (art. 47 of the accord
  of 02/07/2025): employer 1.50% = 26.4552 -> 26.46, employee minimum 1%
  = 17.6368 -> 17.64; solidarity 10% of 26.46 = 2.646 -> 2.65.  TFR:
  1763.68 / 13.5 = 130.643 -> 130.64, less 0.50% of 1763.68 = 8.8184 ->
  8.82: 121.82.
- Alimentari (Federalimentare), level 3 in January 2026: 1566.16 minimum
  + 522.32 contingenza + 10.33 EDR + 85.41 IAR = 2184.22.  ALIFOND
  employer 1.50% = 32.7633 -> 32.76, employee minimum 1% = 21.8422 ->
  21.84, solidarity 3.276 -> 3.28.
- Alimentari PMI (Unionalimentari), level 4 in January 2026: 1746.87
  minimum + 525.02 contingenza + 10.33 EDR = 2282.22.  Fondapi computes
  on the 'Retribuzione TFR' (Scheda 'I destinatari e i contributi',
  section CCNL PMI ALIMENTARE): employer 1.20% = 27.38664 -> 27.39,
  employee minimum 1.00% = 22.8222 -> 22.82, solidarity 2.739 -> 2.74.
- Chimica farmaceutica (Federchimica), level D1 in January 2026: 2360.26
  a month.  FONCHIM employer 2.10% + 0.25% = 2.35% = 55.46611 -> 55.47,
  employee minimum 1.20% = 28.32312 -> 28.32, solidarity 5.547 -> 5.55.
- Tabacco (APTI), level 3A in 2026: 1524.95 minimum + 515.76 contingenza
  + 10.33 EDR = 2051.04.  TFR: 2051.04 / 13.5 = 151.929 -> 151.93, less
  0.50% of 2051.04 = 10.2552 -> 10.26: 141.67.
- Vetro meccanizzato (Assovetro), level C in 2026: 2354.05 + 10.33 TER =
  2364.38 a month, 13 runs.  FONCHIM employer 1.50% + 0.25% = 1.75% until
  the +0.5% of 1 January 2027: 41.37665 -> 41.38; employee minimum 1.50%
  = 35.4657 -> 35.47; solidarity 4.138 -> 4.14.
- Commercio (Confcommercio), level 4 in 2026: 1257.46 minimum + 524.22
  contingenza and EDR + 2.07 terzo elemento = 1783.75.  Fon.Te. computes
  on the pay that enters the TFR (statute Part I, Scheda III, note 1), not
  on the INPS base: employer 1.55% = 27.648 -> 27.65, employee minimum
  0.55% = 9.81063 -> 9.81, solidarity 2.765 -> 2.77.  A bonus enters the
  INPS base and not the TFR (policy ``it/earning/variable``): it leaves the
  Fon.Te. contributions unchanged.  An apprentice of the CCNL Terziario
  has an employer rate of 1.05% (Allegato 1 of the nota informativa,
  updated to 23 March 2026).
- Turismo (Federalberghi), level 4 in January 2026: 1660.69 a month.
  Fon.Te. employer 0.55% (Allegato 1, row of the CCNL Turismo) = 9.133795
  -> 9.13, solidarity 0.913 -> 0.91.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment, InvalidInputError, PayrollEngine
from ccnl_engine.events import BonusEvent
from ccnl_engine.inputs import (
    Apprentice,
    InpsBaseYtd,
    NoPensionFund,
    OpeningBalances,
    PaymentId,
    PensionFundEnrolment,
    Permanent,
)
from tests.acceptance.legal_scenarios._support import EMPLOYER, ENGINE, regular_period
from tests.fixtures.seniority import new_hire
from tests.fixtures.tfr import no_tfr_fund

if TYPE_CHECKING:
    from ccnl_engine import CompetenceYearResult, PeriodResult
    from ccnl_engine.results import CalculationDecision

pytestmark = pytest.mark.legal_scenario

_TABACCO = "tabacco-apti.json"
_VETRO = "vetro-meccanizzato-assovetro.json"
_CAPABILITY = "pension_fund_contribution"
_ALIFOND = PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=True)
_FONCHIM = PensionFundEnrolment("FONCHIM", Decimal("0.015"), tfr_to_fund=True)
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
    """FONCHIM on vetro level C: 1.75% in 2026, 2.25% only from 2027."""

    def test_employer_cost_rises_at_the_2026_rate(self) -> None:
        """13 x (41.38 + 4.14) = 591.76 a year."""
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
        assert delta == Decimal("591.76")
        first = enrolled.period_results[0]
        assert _entry(first, "pension_fund_employer") == Decimal("41.38")
        assert _entry(first, "pension_fund_employee") == Decimal("35.47")

    def test_bundled_minimum_is_recorded(self) -> None:
        """The FONCHIM employee minimum of vetro, 1.50%, is in the decision."""
        result = regular_period(
            employment=Employment(
                ccnl_slug=_VETRO,
                level_code="C",
                pension_fund=_FONCHIM,
                contract_type=Permanent(),
            )
        )
        assert _pension_decision(result).inputs["employee_min_rate"] == (
            Decimal("0.0150")
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
    """A bonus enters the INPS base of the run, not the TFR base."""

    def test_bonus_stays_out_of_the_tfr_base(self) -> None:
        """ALIFOND on the TFR base: the bonus leaves 26.46 and 17.64."""
        bonus = BonusEvent(event_date=date(2026, 1, 15), amount=Decimal(1000))
        result = regular_period(employment=_tabacco(), events=(bonus,))
        assert _entry(result, "pension_fund_employer") == Decimal("26.46")
        assert _entry(result, "pension_fund_employee") == Decimal("17.64")


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

    def test_ccnl_without_fund_data_still_needs_the_enrolment(self) -> None:
        """Commercio has a negotiated fund the bundle does not hold.

        An unknown enrolment blocks; stated not enrolled, the run takes the
        ``not_enrolled`` reading of no fund and names nothing.
        """
        employment = Employment(
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            seniority=new_hire(),
            tfr_fund=no_tfr_fund(2026),
            tfr_treasury_fund=False,
            contract_type=Permanent(),
        )
        unknown = regular_period(employment=employment)
        assert "pension_fund" in {i.fact for i in unknown.issues}
        assert not unknown.is_payable
        stated = regular_period(
            employment=replace(employment, pension_fund=NoPensionFund())
        )
        assert "pension_fund" not in {i.fact for i in stated.issues}

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


_PERMANENT = Permanent()


class TestCommercioFonte:
    """Fon.Te. on commercio level 4, January 2026, on the TFR base."""

    @staticmethod
    def _run(
        *events: BonusEvent,
        ccnl_slug: str = "commercio-confcommercio.json",
        contract_type: Permanent | Apprentice = _PERMANENT,
    ) -> PeriodResult:
        employment = Employment(
            ccnl_slug=ccnl_slug,
            level_code="4",
            seniority=new_hire(),
            pension_fund=PensionFundEnrolment(
                "FONTE", Decimal("0.0055"), tfr_to_fund=True
            ),
            contract_type=contract_type,
        )
        return regular_period(employment=employment, events=events)

    def test_contributions_on_the_monthly_pay(self) -> None:
        """1.55% and 0.55% of 1783.75, and 10% solidarity on the employer."""
        result = self._run()
        decision = _pension_decision(result)
        assert decision.inputs["base"] == Decimal("1783.75")
        assert _entry(result, "pension_fund_employer") == Decimal("27.65")
        assert _entry(result, "pension_fund_employee") == Decimal("9.81")
        assert decision.inputs["solidarity"] == Decimal("2.77")

    def test_bonus_outside_the_tfr_base_leaves_the_fund_unchanged(self) -> None:
        """A 1000.00 bonus is INPS taxable pay, not pay that enters the TFR."""
        bonus = BonusEvent(event_date=date(2026, 1, 15), amount=Decimal(1000))
        result = self._run(bonus)
        assert _pension_decision(result).inputs["base"] == Decimal("1783.75")
        assert _entry(result, "pension_fund_employer") == Decimal("27.65")

    def test_apprentice_pays_the_apprentice_rate(self) -> None:
        """1.05% of the apprentice pay of the run: 1541.77 -> 16.19."""
        result = self._run(contract_type=Apprentice(months_elapsed=6))
        decision = _pension_decision(result)
        assert decision.inputs["employer_rate"] == Decimal("0.0105")
        assert decision.inputs["base"] == result.period_gross == Decimal("1541.77")
        assert _entry(result, "pension_fund_employer") == Decimal("16.19")

    def test_turismo_employer_rate_is_lower(self) -> None:
        """Turismo Federalberghi level 4: 0.55% of 1660.69 = 9.13."""
        result = self._run(ccnl_slug="turismo-federalberghi.json")
        assert _pension_decision(result).inputs["base"] == Decimal("1660.69")
        assert _entry(result, "pension_fund_employer") == Decimal("9.13")
        assert _pension_decision(result).inputs["solidarity"] == Decimal("0.91")


def test_alifond_on_the_food_industry() -> None:
    """Alimentari level 3 enrolled in ALIFOND at the 1% minimum."""
    employment = Employment(
        ccnl_slug="alimentari-federalimentare.json",
        level_code="3",
        seniority=new_hire(),
        pension_fund=PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=True),
        contract_type=Permanent(),
    )
    result = regular_period(employment=employment)
    decision = _pension_decision(result)
    assert decision.inputs["base"] == Decimal("2184.22")
    assert _entry(result, "pension_fund_employer") == Decimal("32.76")
    assert _entry(result, "pension_fund_employee") == Decimal("21.84")
    assert decision.inputs["solidarity"] == Decimal("3.28")


def test_fondapi_on_the_food_pmi() -> None:
    """Alimentari PMI level 4 enrolled in FONDAPI at the 1% minimum."""
    employment = Employment(
        ccnl_slug="alimentari-pmi-unionalimentari.json",
        level_code="4",
        seniority=new_hire(),
        pension_fund=PensionFundEnrolment("FONDAPI", Decimal("0.01"), tfr_to_fund=True),
        contract_type=Permanent(),
    )
    result = regular_period(employment=employment)
    decision = _pension_decision(result)
    assert decision.inputs["base"] == Decimal("2282.22")
    assert _entry(result, "pension_fund_employer") == Decimal("27.39")
    assert _entry(result, "pension_fund_employee") == Decimal("22.82")
    assert decision.inputs["solidarity"] == Decimal("2.74")


def test_fonchim_on_the_chemical_industry() -> None:
    """Chimica farmaceutica D1 enrolled in FONCHIM at the 1.20% minimum."""
    employment = Employment(
        ccnl_slug="chimica-farmaceutica-federchimica.json",
        level_code="D1",
        seniority=new_hire(),
        pension_fund=PensionFundEnrolment(
            "FONCHIM", Decimal("0.012"), tfr_to_fund=True
        ),
        contract_type=Permanent(),
    )
    result = regular_period(employment=employment)
    decision = _pension_decision(result)
    assert decision.inputs["base"] == Decimal("2360.26")
    assert _entry(result, "pension_fund_employer") == Decimal("55.47")
    assert _entry(result, "pension_fund_employee") == Decimal("28.32")
    assert decision.inputs["solidarity"] == Decimal("5.55")
