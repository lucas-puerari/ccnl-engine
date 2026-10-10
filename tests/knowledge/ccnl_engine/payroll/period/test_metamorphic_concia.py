"""Metamorphic properties of the payslip, on the Concia D2 scenario.

Each test compares two runs whose relation is known without computing
either: an unknown fact must not behave like a known zero, a 100 EUR bonus
moves only the axes a bonus touches, the order of independent events and
the split of a year at an exported state change nothing, and the public
totals are the sums of the postings.  The scenario is the one of
:mod:`tests.knowledge.ccnl_engine.payroll.period.oracles_payslip_concia_d2_2026`.
"""

from __future__ import annotations

from dataclasses import replace
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
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.events import BonusEvent, OvertimeEvent, WorkEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    OpeningBalances,
    PeriodState,
    Permanent,
    PriorYearTaxFacts,
)
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_ZERO = Decimal(0)
_CENT = Decimal("0.01")
_EMPLOYMENT = Employment(
    ccnl_slug="concia-unic.json",
    level_code="D2",
    seniority=new_hire(),
    employment_period=EmploymentPeriod(date(2026, 1, 1)),
    contract_type=Permanent(),
)
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_ALGHERO = PeriodFacts(regione="IT-88", comune_belfiore="A192")
#: 2025 income above the 33,000 EUR of L. 199/2025 art. 1 c. 7.
_ABOVE_RENEWAL_CEILING = PriorYearTaxFacts(employment_income=Decimal(40_000))
#: 2025 income within the renewal regime.
_WITHIN_RENEWAL_CEILING = PriorYearTaxFacts(employment_income=Decimal(25_000))
_BONUS = BonusEvent(date(2026, 6, 15), Decimal(100))
_OVERTIME = OvertimeEvent(date(2026, 6, 10), Decimal(4), Decimal("14.00"))
#: Signed 7 March 2024, inside the 2024-2026 window of L. 199/2025 c. 7.
_RENEWAL = BonusEvent(
    date(2026, 6, 15),
    Decimal(100),
    kind="contract_renewal",
    agreement_signed_on=date(2024, 3, 7),
)


def _june(
    *,
    events: tuple[WorkEvent, ...] = (),
    facts: PeriodFacts = _ALGHERO,
    prior_year: PriorYearTaxFacts = _ABOVE_RENEWAL_CEILING,
    employment: Employment = _EMPLOYMENT,
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 28),
            employment=employment,
            employer=_EMPLOYER,
            facts=replace(facts, events=events),
            prior_year=prior_year,
        )
    )


def _year(opening: PeriodState | None = None) -> CompetenceYearResult:
    return _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
            default_facts=_ALGHERO,
            prior_year=_ABOVE_RENEWAL_CEILING,
            opening_state=opening,
        )
    )


@cache
def _one_pass() -> CompetenceYearResult:
    return _year()


def _by_account(result: PeriodResult) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for entry in result.ledger_entries:
        totals[entry.account.value] = (
            totals.get(entry.account.value, _ZERO) + entry.amount
        )
    return totals


def _blocked_features(result: PeriodResult) -> set[str | None]:
    return {b.feature for b in result.blockers}


class TestUnknownIsNotZero:
    """An unknown fact blocks the feature it decides; a known one does not."""

    def test_unknown_seniority_is_not_zero_seniority(self) -> None:
        """Unknown recognised seniority blocks; zero months does not."""
        unknown = _june(employment=replace(_EMPLOYMENT, seniority=None))
        assert "seniority" in _blocked_features(unknown)
        assert "seniority" not in _blocked_features(_june())

    def test_unknown_prior_income_is_not_income_above_the_ceiling(self) -> None:
        """A renewal increment with unknown 2025 income is not taxed as ordinary."""
        unknown = _june(events=(_RENEWAL,), prior_year=PriorYearTaxFacts())
        known = _june(events=(_RENEWAL,))
        assert "rinnovo_substitute_tax" in _blocked_features(unknown)
        assert "rinnovo_substitute_tax" not in _blocked_features(known)

    def test_unknown_residence_is_not_no_surtax(self) -> None:
        """A run without residence cannot decide the regional and municipal surtax.

        A resident owes both surtaxes when net IRPEF is due (D.Lgs. 446/1997
        art. 50 c. 2, D.Lgs. 360/1998 art. 1 c. 4): left unknown, the
        residence cannot rule them out.
        """
        result = _june(facts=PeriodFacts())
        assert {"addizionale_regionale", "addizionale_comunale"} <= (
            _blocked_features(result)
        )

    def test_renewal_increments_in_the_minimo_are_not_ignored(self) -> None:
        """Renewal increments inside the minimo reach the renewal regime.

        The 2026 minimo of Concia D2 is a table of the renewal signed on 7
        March 2024, inside the window of L. 199/2025 art. 1 c. 7; with 2025
        income within 33,000 EUR the minimo cannot be taxed as ordinary
        income without a renewal decision or a blocker.
        """
        result = _june(prior_year=_WITHIN_RENEWAL_CEILING)
        regime = {d.capability for d in result.decisions}
        assert (
            "rinnovo_substitute_tax" in regime
            or "rinnovo_substitute_tax" in _blocked_features(result)
        )


class TestOneHundredEuroBonus:
    """A 100 EUR ordinary bonus moves gross, INPS, IRPEF and net only."""

    def test_only_the_bonus_axes_move(self) -> None:
        """Salary items stay put; gross, contributions and IRPEF move."""
        before, after = _by_account(_june()), _by_account(_june(events=(_BONUS,)))
        moved = {
            k for k in before.keys() | after.keys() if before.get(k) != after.get(k)
        }
        assert moved - {"tfr_accrual"} == {
            "cash_earnings",
            "employee_contributions",
            "employer_contributions",
            "ordinary_tax",
        }

    def test_the_moves_have_the_expected_size(self) -> None:
        """Gross +100, INPS +9.49% of it, IRPEF below the taxable increase."""
        before, after = _june(), _june(events=(_BONUS,))
        assert after.period_gross - before.period_gross == Decimal(100)
        inps = (
            _by_account(after)["employee_contributions"]
            - _by_account(before)["employee_contributions"]
        )
        assert abs(inps - Decimal("9.49")) <= _CENT
        irpef = _by_account(after)["ordinary_tax"] - _by_account(before)["ordinary_tax"]
        assert _ZERO < irpef < Decimal(100) - inps
        assert after.period_net - before.period_net == Decimal(100) - inps - irpef

    def test_the_salary_items_do_not_move(self) -> None:
        """Base salary and EDR are the same with and without the bonus."""

        def salary(result: PeriodResult) -> list[tuple[str, Decimal]]:
            return sorted(
                (i.kind, i.amount)
                for i in result.pay_items
                if i.kind in {"base_salary_earning", "fixed_allowance_earning"}
            )

        assert salary(_june()) == salary(_june(events=(_BONUS,)))


def test_order_of_independent_events_does_not_change_the_payslip() -> None:
    """Overtime then bonus and bonus then overtime post the same ledger."""

    def postings(result: PeriodResult) -> list[tuple[str, Decimal]]:
        return sorted((e.account.value, e.amount) for e in result.ledger_entries)

    first = _june(events=(_OVERTIME, _BONUS))
    second = _june(events=(_BONUS, _OVERTIME))
    assert postings(first) == postings(second)
    assert (first.period_gross, first.period_net) == (
        second.period_gross,
        second.period_net,
    )


@pytest.mark.parametrize("index", range(13))
def test_public_totals_are_the_sums_of_the_postings(index: int) -> None:
    """Gross, net and employer cost of every 2026 payment come from the ledger."""
    result = _one_pass().period_results[index]
    ledger = _by_account(result)

    def total(*accounts: str) -> Decimal:
        return sum((ledger.get(a, _ZERO) for a in accounts), _ZERO)

    gross = total("cash_earnings")
    assert result.period_gross == gross
    assert result.period_net == gross - total(
        "employee_contributions",
        "ordinary_tax",
        "surtax",
    )
    assert result.period_employer_cost == gross + total(
        "employer_contributions", "tfr_accrual"
    )
    remitted = sum((line.amount for line in result.remittance_summary()), _ZERO)
    assert remitted == total("ordinary_tax", "surtax")


class TestStateExportAndImport:
    """A year split at an exported June state equals the year in one pass."""

    @staticmethod
    def _exported_june() -> OpeningBalances:
        state = _one_pass().period_results[5].closing_state
        cash = state.cash
        return OpeningBalances(
            tax_year=2026,
            payments=cash.payments,
            inps_bases=state.accrual.inps_bases,
            gross=cash.earnings.gross,
            taxable=cash.earnings.taxable,
            inps_employee=cash.earnings.inps_employee,
            irpef_withheld=cash.tax.irpef,
            trattamento_due=cash.trattamento.due,
            trattamento_reason=cash.trattamento.reason,
            somma_esente_due=cash.somma_esente.due,
            somma_esente_reason=cash.somma_esente.reason,
            ulteriore_recognized=cash.ulteriore_detrazione.recognized,
            ulteriore_due=cash.ulteriore_detrazione.due,
            ulteriore_reason=cash.ulteriore_detrazione.reason,
            recoveries=(),
            surtax_obligations=(),
            employment_spells=cash.employment_spells,
        )

    @staticmethod
    def _imported(state: PeriodState) -> PeriodState:
        """Return ``state`` as an import knows it: sickness from 1 January.

        The engine's own state lists every sick day of the employment; an
        import without ``sickness_known_from`` lists those of its tax year.

        Returns:
            The state with its sickness known from 1 January 2026.
        """
        accrual = replace(state.accrual, sickness_known_from=date(2026, 1, 1))
        return replace(state, accrual=accrual)

    def test_import_gives_back_the_exported_state(self) -> None:
        """The imported June totals are the state the engine closed June with."""
        imported = _ENGINE.import_opening_balances(self._exported_june())
        assert imported == self._imported(_one_pass().period_results[5].closing_state)

    def test_resuming_from_the_import_equals_one_pass(self) -> None:
        """July to the tredicesima from the import match the one-pass year."""
        resumed = _year(_ENGINE.import_opening_balances(self._exported_june()))
        tail = _one_pass().period_results[6:]
        assert [r.period_net for r in resumed.period_results] == [
            r.period_net for r in tail
        ]
        assert resumed.period_results[-1].closing_state == self._imported(
            _one_pass().period_results[-1].closing_state
        )
