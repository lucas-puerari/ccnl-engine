"""Full-year payslip of CCNL Concia D2 against an independent oracle.

The expected figures come from
:mod:`tests.fixtures.normative_oracles.payslips.concia_d2_2026`, computed by hand from
the signed renewal, the TUIR, L. 207/2024, L. 199/2025, the INPS rates and
the MEF surtax tables; the module docstring lists each source.  The engine
runs the whole competence year once; every payment, the annual totals, the
conguaglio and the surtax obligations it leaves for 2027 are compared with
the oracle.

Concia is the first candidate group for ``production``: no bundled CCNL
has zero weak rules, four have one (the accrual rule), and of those only
Concia takes its salaries from a renewal published by the contracting
parties.  It reads only the shared industria tax and INPS rulesets, the
family deduction rules, the variable pay rules (the renewal regime on the
minimo) and the bundled surtax tables.
The employer contributions are not compared: the bundle holds them as one
aggregate rate per headcount band, not as primary-sourced components.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import cache

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    CompetenceYearResult,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
    PeriodResult,
)
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    EmploymentPeriod,
    FamilyComposition,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    SurtaxComponent,
)
from tests.fixtures.normative_oracles.payslips.concia_d2_2026 import (
    CONCIA_D2_2026 as ORACLE,
)
from tests.fixtures.normative_oracles.surtax_2026 import (
    ADVANCE_MONTHS,
    BALANCE_MONTHS,
    installments,
)
from tests.fixtures.seniority import new_hire

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_ZERO = Decimal(0)
#: The rulesets of the candidate group: the CCNL and what it reads; the
#: family deduction rules decide the empty family the scenario states, and
#: the variable pay rules rule out the renewal regime of L. 199/2025 art. 1
#: c. 7 on the 2026 minimo, a table of the renewal signed on 7 March 2024,
#: for a 2025 income of 40,000 EUR.
_GROUP = {
    "tax/variable-pay-rules/2026",
    "ccnl/concia-unic",
    "inps/2026/industria",
    "tax/2026/industria",
    "tax/2026/family-deductions",
    "tax/2026/somma-esente",
    "surtax/2026/regionale",
    "surtax/2026/comunale",
}


@cache
def _year() -> CompetenceYearResult:
    return _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug="concia-unic.json",
                level_code="D2",
                seniority=new_hire(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
                tfr_treasury_fund=False,
                pension_fund=NoPensionFund(),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            default_facts=PeriodFacts(
                regione="IT-88",
                comune_belfiore="A192",
                family_composition=FamilyComposition(),
            ),
            prior_year=PriorYearTaxFacts(employment_income=Decimal(40_000)),
            current_year=CurrentYearTaxFacts.employment_only(2026, date(2026, 1, 1)),
        )
    )


def _runs() -> tuple[PeriodResult, ...]:
    return _year().period_results


def _posted(result: PeriodResult, account: str) -> Decimal:
    return sum((e.amount for e in result.ledger_entries if e.account == account), _ZERO)


def _items(result: PeriodResult, kind: str) -> Decimal:
    return sum((i.amount for i in result.pay_items if i.kind == kind), _ZERO)


def _year_total(account: str) -> Decimal:
    return sum((_posted(r, account) for r in _runs()), _ZERO)


class TestEveryPayment:
    """Each of the thirteen payments pays the oracle month."""

    def test_the_year_has_twelve_months_and_the_tredicesima(self) -> None:
        """The year has twelve months and the tredicesima."""
        assert len(_runs()) == ORACLE.payments

    @pytest.mark.parametrize("index", range(13))
    def test_salary_items_follow_the_signed_table(self, index: int) -> None:
        """Salary items follow the signed table."""
        result = _runs()[index]
        assert _items(result, "base_salary_earning") == ORACLE.minimum
        assert _items(result, "fixed_allowance_earning") == ORACLE.edr
        assert result.period_gross == ORACLE.monthly_gross

    @pytest.mark.parametrize("index", range(13))
    def test_employee_inps_is_ivs_plus_cigs(self, index: int) -> None:
        """Employee INPS is IVS 9.19% plus CIGS 0.30% of the gross."""
        result = _runs()[index]
        assert _posted(result, "employee_contributions") == ORACLE.monthly_inps

    @pytest.mark.parametrize("index", range(13))
    def test_tfr_accrues_on_the_pay_divided_by_13_5(self, index: int) -> None:
        """The TFR base is the pay of the month and the divisor 13.5."""
        (decision,) = (d for d in _runs()[index].decisions if d.capability == "tfr")
        assert decision.inputs["base"] == ORACLE.monthly_gross
        assert decision.inputs["accrual_divisor"] == ORACLE.tfr_divisor
        assert decision.inputs["quota"] == ORACLE.tfr_quota

    @pytest.mark.parametrize("index", range(13))
    def test_tfr_accrual_is_net_of_the_additional_ivs(self, index: int) -> None:
        """The TFR posted is the quota less the 0.50% L. 297/1982 deducts."""
        result = _runs()[index]
        (decision,) = (d for d in result.decisions if d.capability == "tfr")
        assert decision.inputs["additional_ivs_base"] == ORACLE.monthly_gross
        assert decision.inputs["additional_ivs_deduction"] == ORACLE.tfr_deduction
        assert _posted(result, "tfr_accrual") == ORACLE.tfr_net_of_extra_ivs


class TestYearTotals:
    """The conguaglio settles the year on the oracle figures."""

    def test_gross_and_contributions(self) -> None:
        """Gross and employee INPS of the year are thirteen oracle months."""
        assert _year_total("cash_earnings") == ORACLE.gross
        assert _year_total("employee_contributions") == ORACLE.inps

    def test_closing_state_holds_the_year(self) -> None:
        """The closing state holds the gross, INPS and taxable of the year."""
        earnings = _runs()[-1].closing_state.cash.earnings
        assert (earnings.gross, earnings.inps_employee, earnings.taxable) == (
            ORACLE.gross,
            ORACLE.inps,
            ORACLE.taxable,
        )

    def test_irpef_withheld_in_the_year_is_the_annual_net_irpef(self) -> None:
        """The IRPEF withheld in the year is the annual net IRPEF."""
        assert _year_total("ordinary_tax") == ORACLE.irpef
        assert _runs()[-1].closing_state.cash.tax.irpef == ORACLE.irpef

    def test_net_pay_of_the_year(self) -> None:
        """Net pay of the year is gross less INPS less annual IRPEF."""
        assert sum((r.period_net for r in _runs()), _ZERO) == ORACLE.net

    def test_no_credit_is_paid_in_2026(self) -> None:
        """No trattamento integrativo and no somma esente is paid in 2026."""
        cash = _runs()[-1].closing_state.cash
        assert cash.trattamento.recognized == _ZERO
        assert cash.somma_esente.recognized == _ZERO


class TestSurtaxLeftFor2027:
    """The conguaglio determines the 2026 surtaxes and the 2027 acconto."""

    _EXPECTED = {
        SurtaxComponent.REGIONAL_BALANCE: (ORACLE.regional, BALANCE_MONTHS),
        SurtaxComponent.MUNICIPAL_BALANCE: (ORACLE.municipal, BALANCE_MONTHS),
        SurtaxComponent.MUNICIPAL_ADVANCE: (ORACLE.municipal_advance, ADVANCE_MONTHS),
    }

    @pytest.mark.parametrize("component", list(_EXPECTED))
    def test_obligation_amount_and_installments(
        self, component: SurtaxComponent
    ) -> None:
        """Obligation amount and installments."""
        amount, months = self._EXPECTED[component]
        (obligation,) = (
            o
            for o in _runs()[-1].closing_state.cash.obligations.surtax
            if o.component is component
        )
        first = installments(amount, months)[months[0]]
        assert obligation.plan.original_amount == amount
        assert obligation.plan.installments_total == len(months)
        assert obligation.plan.installment_amount == first


class TestCandidateGroupEvidence:
    """What keeps the payslip from being payable is stated, nothing else."""

    def test_the_payslip_reads_only_the_candidate_group(self) -> None:
        """The payslip reads only the candidate group."""
        for result in _runs():
            assert {r.identity.id for r in result.rulesets} == _GROUP

    def test_the_only_blockers_are_the_assumed_rules_it_reads(self) -> None:
        """Only assumed rules block: none of the CCNL, family or surtax data.

        The INPS and tax rules of ``industria`` sit in rulesets that declare
        ``source_type`` ``estimated``, so the provenance label check labels
        them assumed.  The somma esente, quoted from L. 207/2024 art. 1
        cc. 4-5 in its own ruleset, blocks nothing.
        """
        weak = {
            "irpef",
            "trattamento_integrativo",
            "ulteriore_detrazione_lavoro",
            "tfr",
            "inps_employee",
            "inps_employer",
            "ivs_ceiling_eligibility",
        }
        for result in _runs():
            blockers = {(b.code.value, b.feature, b.detail) for b in result.blockers}
            assert blockers == {("rule_source_weak", f, "assumed") for f in weak}
