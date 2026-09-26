"""Tests for the year change: close_tax_year and carried recoveries."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import PayrollEngine
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.application.close_tax_year import close_tax_year
from ccnl_engine.payroll.application.invariants.state import (
    check_carried_recovery_advance,
)
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest, PeriodState
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import TrattamentoAccount
from ccnl_engine.shared.domain.errors import InvalidInputError
from tests.helpers import year_input

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"


def _recovery(tax_year: int, posted: int) -> RecoveryObligation:
    return RecoveryObligation(
        tax_year=tax_year,
        plan=RecoveryPlan(
            kind="trattamento_integrativo",
            original_amount=Decimal(160),
            installment_amount=Decimal(20),
            installments_total=8,
            installments_posted=posted,
        ),
    )


def _carrying(*recoveries: RecoveryObligation) -> EmploymentObligations:
    return EmploymentObligations(recoveries=recoveries)


class TestCloseTaxYear:
    """close_tax_year opens N+1 from a year-end state of N."""

    def test_resets_the_tax_year_and_carries_the_obligations(self) -> None:
        """Every YTD account restarts; the recovery keeps its origin year."""
        obligations = _carrying(_recovery(2026, 4))
        closing = PeriodState(
            ytd=TaxYearState(
                tax_year=2026,
                regular_periods_closed=12,
                tax_withholding_periods_closed=13,
                withholding_slots=13,
                closed_run_ids=(PayrollRunId.parse("2026-12-regular"),),
                trattamento=TrattamentoAccount(
                    recognized=Decimal(160), recovered=Decimal(80)
                ),
            ),
            obligations=obligations,
        )

        opening = close_tax_year(closing)

        assert opening == PeriodState(
            ytd=TaxYearState(tax_year=2027), obligations=obligations
        )

    def test_rejects_a_state_bound_to_no_tax_year(self) -> None:
        """A hand-built state without a run is not a year-end state."""
        with pytest.raises(InvalidInputError, match="bound to no tax year"):
            close_tax_year(PeriodState.zero())

    def test_rejects_a_state_without_a_run(self) -> None:
        """A state that never ran has no withholding schedule to complete."""
        with pytest.raises(InvalidInputError, match="0 of None withholding"):
            close_tax_year(PeriodState(ytd=TaxYearState(tax_year=2026)))

    def test_closes_the_state_of_the_last_run_of_calculate_year(self) -> None:
        """The last run of a year calculation closes every withholding slot."""
        year = calculate_year(year_input(2026, _CCNL, _LEVEL))

        opening = close_tax_year(year.period_results[-1].closing_state)

        assert opening == PeriodState(ytd=TaxYearState(tax_year=2027))


class TestCarriedRecoveryInAYear:
    """A recovery opened in 2025 keeps running on the 2026 runs."""

    def test_remaining_installments_are_deducted_once(self) -> None:
        """Differential oracle: 3 installments left cost exactly 60.00.

        The 2025 plan has 5 of 8 installments posted.  January, February and
        March 2026 post the last three; the 2026 YTD accounts match a year
        without the plan.
        """
        opening = PeriodState(obligations=_carrying(_recovery(2025, 5)))

        with_plan = calculate_year(
            year_input(2026, _CCNL, _LEVEL, opening_state=opening)
        )
        without_plan = calculate_year(year_input(2026, _CCNL, _LEVEL))

        assert without_plan.annual_net - with_plan.annual_net == Decimal("60.00")
        posted = [
            r.closing_state.obligations.recoveries for r in with_plan.period_results[:3]
        ]
        assert posted == [
            (_recovery(2025, 6),),
            (_recovery(2025, 7),),
            (),
        ]
        reasons = [
            d.reason_code
            for d in with_plan.decisions
            if d.capability == "trattamento_integrativo_recovery"
        ]
        assert reasons == [
            "installment_posted",
            "installment_posted",
            "last_installment_posted",
        ]
        last_with = with_plan.period_results[-1].closing_state.ytd
        last_without = without_plan.period_results[-1].closing_state.ytd
        assert last_with == last_without

    def test_rejects_an_opening_state_with_a_closed_run(self) -> None:
        """A year calculation computes every run, so none can be closed."""
        opening = PeriodState(
            ytd=TaxYearState(
                tax_year=2026,
                regular_periods_closed=1,
                tax_withholding_periods_closed=1,
            )
        )

        with pytest.raises(InvalidInputError, match="must close no run"):
            calculate_year(year_input(2026, _CCNL, _LEVEL, opening_state=opening))

    def test_rejects_a_run_before_the_origin_of_a_recovery(self) -> None:
        """A 2027 recovery cannot be applied to a 2026 run."""
        with pytest.raises(InvalidInputError, match="after the tax year of the run"):
            PeriodCalculationRequest(
                employer=EmployerProfile(headcount=Headcount(50)),
                period_id=PeriodId(year=2026, month=1),
                payment_date=date(2026, 1, 28),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
                opening_state=PeriodState(obligations=_carrying(_recovery(2027, 0))),
            )


class TestYearRequestOpeningState:
    """YearInput.opening_state reaches the year calculation."""

    def test_carried_recovery_through_the_facade(self) -> None:
        """The engine applies the 2025 recovery to the 2026 year it computes."""
        engine = PayrollEngine.bundled()
        request = year_input(2026, _CCNL, _LEVEL)
        opening = PeriodState(obligations=_carrying(_recovery(2025, 5)))

        with_plan = engine.calculate_year(replace(request, opening_state=opening))
        without_plan = engine.calculate_year(request)

        first = with_plan.period_results[0].closing_state.obligations
        assert first == _carrying(_recovery(2025, 6))
        assert without_plan.annual_net - with_plan.annual_net == Decimal("60.00")


class TestCurrentYearRecovery:
    """A recovery of the current tax year still runs through the conguaglio."""

    def test_last_installment_in_december_carries_nothing(self) -> None:
        """A plan that ends in December leaves no obligation for 2027."""
        opening = PeriodState(
            ytd=TaxYearState(
                tax_year=2026,
                regular_periods_closed=11,
                tax_withholding_periods_closed=12,
                trattamento=TrattamentoAccount(
                    recognized=Decimal(160), recovered=Decimal(140)
                ),
            ),
            obligations=_carrying(_recovery(2026, 7)),
        )

        result = calculate_period(
            PeriodCalculationRequest(
                employer=EmployerProfile(headcount=Headcount(50)),
                period_id=PeriodId(year=2026, month=12),
                payment_date=date(2026, 12, 28),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
                opening_state=opening,
            )
        )

        assert result.closing_state.obligations == EmploymentObligations()
        assert result.closing_state.ytd.trattamento.recovered == Decimal(160)
        assert close_tax_year(result.closing_state).obligations.recoveries == ()


class TestCarriedRecoveryInvariant:
    """carried_recovery_advance checks the installment and the plan advance."""

    def test_reports_a_missing_installment_and_a_plan_not_advanced(self) -> None:
        """Dropping the posting and the advance yields two violations."""
        opening = PeriodState(obligations=_carrying(_recovery(2025, 5)))
        result = calculate_year(
            year_input(2026, _CCNL, _LEVEL, opening_state=opening)
        ).period_results[0]
        tampered = replace(
            result,
            ledger_entries=tuple(
                e for e in result.ledger_entries if "_recovery_" not in e.entry_id
            ),
            closing_state=replace(
                result.closing_state, obligations=opening.obligations
            ),
        )

        assert check_carried_recovery_advance(result, opening) == []
        violations = check_carried_recovery_advance(tampered, opening)
        assert [v.invariant_id for v in violations] == ["carried_recovery_advance"] * 2
        assert violations[0].expected == Decimal(-20)
        assert violations[0].actual is None
