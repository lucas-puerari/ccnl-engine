"""Every run records one decision per base stage, with its rule and source.

The expected rule identifiers, rates and divisors are read from the bundled
CCNL and tax files; the amounts follow from them with the formula of each
stage and must match what the run posted to the ledger.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.inputs import ContributableHours, WeeklyHours
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.period._capability_traces import build_traces
from ccnl_engine.payroll.domain.decisions import CalculationStatus, DecisionOrigin
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Apprentice
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pension_fund import PensionFundEnrolment
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.trace import TraceState
from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.tax.service.tax_annual_assembler import load_year_rules

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.period import PeriodResult

_METALMECCANICO = "metalmeccanico-federmeccanica.json"
_DAY = date(2026, 3, 1)
_BASE_STAGES = ("base_salary", "inps_employee", "inps_employer", "tfr", "irpef")


def _run(
    ccnl: str = _METALMECCANICO, level: str = "C3", **kwargs: object
) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug=ccnl,
            level_code=level,
            employer=EmployerProfile(headcount=Headcount(50)),
            opening_state=PeriodState.zero(),
            **kwargs,  # type: ignore[arg-type]
        )
    )


def _decision(result: PeriodResult, capability: str) -> CalculationDecision:
    (decision,) = (d for d in result.decisions if d.capability == capability)
    return decision


def _posted(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account is account),
        Decimal(0),
    )


class TestPermanentWorker:
    """A permanent C3 metalmeccanico worker in March 2026."""

    result = _run()
    ccnl = load_ccnl(_METALMECCANICO)
    rules = load_year_rules(2026, TaxSector.INDUSTRIA, 50)

    def test_one_final_engine_decision_per_stage(self) -> None:
        """Each base stage decides once, from a rule the engine applied."""
        for capability in _BASE_STAGES:
            decision = _decision(self.result, capability)
            assert decision.status is CalculationStatus.FINAL
            assert decision.origin is DecisionOrigin.ENGINE

    def test_base_salary_names_the_tranche_in_force(self) -> None:
        """The pay chain reads the C3 tranche of 1 March 2026 and its source."""
        level = self.ccnl.level_by_code("C3")
        period = level.base_salary.period_at(_DAY)
        assert period is not None
        assert self.ccnl.ruleset is not None
        decision = _decision(self.result, "base_salary")
        assert decision.rule == (
            f"{self.ccnl.ruleset.id}:levels[C3].base_salary[{period.valid_from}]"
        )
        assert decision.rule_version == self.ccnl.ruleset.version
        provenance = period.provenance or level.provenance
        assert isinstance(provenance, RuleProvenance)
        assert decision.source == provenance.location
        assert decision.inputs["minimum"] == level.base_salary.value_at(_DAY)
        assert decision.inputs["apprenticeship"] == "none"

    def test_base_salary_amount_is_the_posted_chain(self) -> None:
        """Minimum, seniority and allowances sum to the cash earnings posted."""
        decision = _decision(self.result, "base_salary")
        inputs = decision.inputs
        chain = Decimal(inputs["minimum"]) + Decimal(inputs["seniority"])
        assert decision.amount == chain + Decimal(inputs["allowances"])
        assert decision.amount == _posted(self.result, AccountKind.CASH_EARNINGS)

    def test_inps_applies_the_bundled_rates(self) -> None:
        """Worker INPS is the base times the bundled worker rate, as posted.

        The IVS share (9.19%) and the rest (0.30%) are rounded apart:
        2,158.26 * 0.0919 = 198.34 and 2,158.26 * 0.0030 = 6.47.
        """
        assert self.rules.inps is not None
        assert self.rules.inps_ruleset is not None
        employee = _decision(self.result, "inps_employee")
        assert employee.rule == f"{self.rules.inps_ruleset.id}:inps"
        assert employee.reason_code == "rates_applied"
        assert employee.inputs["rate"] == self.rules.inps.employee_rate
        base = Decimal(employee.inputs["base"])
        assert base == _decision(self.result, "base_salary").amount
        ivs = self.rules.inps.employee_ivs_rate
        rest = self.rules.inps.employee_rate - ivs
        assert employee.amount == money(base * ivs) + money(base * rest)
        assert employee.amount == _posted(
            self.result, AccountKind.EMPLOYEE_CONTRIBUTIONS
        )
        employer = _decision(self.result, "inps_employer")
        assert employer.amount == _posted(
            self.result, AccountKind.EMPLOYER_CONTRIBUTIONS
        )

    def test_tfr_divides_the_base_by_the_bundled_divisor(self) -> None:
        """TFR is the base over 13.5 (art. 2120 c.c.), accrued in the company."""
        assert self.rules.ruleset is not None
        decision = _decision(self.result, "tfr")
        assert decision.rule == f"{self.rules.ruleset.id}:tfr"
        assert decision.inputs["accrual_divisor"] == Decimal("13.5")
        assert decision.inputs["account"] == AccountKind.TFR_ACCRUAL.value
        base = Decimal(decision.inputs["base"])
        assert decision.amount == money(base / Decimal("13.5"))
        assert decision.amount == _posted(self.result, AccountKind.TFR_ACCRUAL)

    def test_irpef_records_the_withholding_and_its_credits(self) -> None:
        """IRPEF withheld is the posted amount; credits are referenced."""
        assert self.rules.ruleset is not None
        decision = _decision(self.result, "irpef")
        assert decision.rule == f"{self.rules.ruleset.id}:irpef_brackets"
        assert decision.reason_code == "withheld"
        assert decision.amount == _posted(self.result, AccountKind.ORDINARY_TAX)
        components = {c.name: c.amount for c in self.result.tax_computation.components}
        assert decision.inputs["irpef_gross"] == components["irpef_gross"]
        assert decision.inputs["work_deduction"] == components["work_deduction"]
        assert decision.inputs["decisions"] == (
            "ulteriore_detrazione_lavoro,trattamento_integrativo"
        )


def test_apprentice_reads_the_apprentice_rates() -> None:
    """An apprentice's INPS reads the apprentice block; scaling is referenced."""
    result = _run(
        contract_type=Apprentice(months_elapsed=6, track="professionalizzante_36")
    )
    assert _decision(result, "inps_employee").rule.endswith(":apprentice")
    assert _decision(result, "base_salary").inputs["apprenticeship"] == (
        "apprenticeship_scaling"
    )
    assert _decision(result, "apprenticeship_scaling").amount is None


def test_household_employer_takes_no_irpef_decision() -> None:
    """A household employer pays flat hourly INPS and computes no IRPEF.

    Convivente level A, 40 weekly hours, 173 contributable hours: 40 > 24,
    so the worker pays 173 * 0.31 = 53.63.
    """
    result = _run(
        "lavoro-domestico-convivente.json",
        "A",
        weekly_hours=WeeklyHours(40),
        contributable_hours=ContributableHours(Decimal(173)),
    )
    employee = _decision(result, "inps_employee")
    assert employee.reason_code == "domestic_hourly_rates"
    assert employee.rule.endswith(":domestic_contributions")
    assert employee.amount == Decimal("53.63")
    assert {d.reason_code for d in result.decisions if d.capability == "irpef"} == {
        "not_withholding_agent"
    }
    traces = {t.feature: t.state for t in build_traces(result.decisions, frozenset())}
    assert traces["irpef"] is TraceState.NOT_APPLICABLE


def test_tfr_paid_to_the_pension_fund() -> None:
    """With the TFR paid to the fund, the decision names the fund account."""
    result = _run(
        "tabacco-apti.json",
        "4A",
        pension_fund=PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=True),
    )
    decision = _decision(result, "tfr")
    assert decision.inputs["account"] == AccountKind.PENSION_FUND_TFR.value
    assert decision.amount == _posted(result, AccountKind.PENSION_FUND_TFR)


def test_low_part_time_pay_withholds_nothing() -> None:
    """Eight hours a week fall in the no-tax area: nothing is withheld.

    The C3 chain of about 2,000 EUR scaled to 8/40 is about 400 EUR a
    month, some 5,600 EUR a year over 14 slots: the work deduction of
    art. 13 TUIR exceeds the gross tax on it.
    """
    result = _run(weekly_hours=WeeklyHours(8), full_time_weekly_hours=WeeklyHours(40))
    decision = _decision(result, "irpef")
    assert decision.reason_code == "nothing_due"
    assert decision.amount == Decimal(0)
