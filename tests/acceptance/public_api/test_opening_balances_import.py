"""Opening balances are imported with a dedicated command and follow competence.

The IVS massimale (L. 335/1995 art. 2 c. 18) caps the INPS base of a
worker in a calendar year across every employment: the base of an earlier
or simultaneous employment counts toward it (INPS circ. 237/2016 par. 3.1).
INPS contributions follow competence (same circolare, par. 2.1): December
2026 paid on 13 January 2027 is IRPEF income of 2027 but INPS base of 2026.

Hand computation, Metalmeccanico C3 of September 2026 (gross 2,211.43, the
minimo of the fixture ``metalmeccanico_c3_2026``), industrial employer with
50 employees, worker first enrolled in 2001 (the massimale applies), INPS
2026 bundle rules: massimale 122,295.00, employee IVS 9.19%, other employee
rate 0.30%, additional 1% on the pay of the month above 4,685.00 within
the massimale, settled in December on the pay of the year above 56,224.00
(INPS circ. 6/2026 par. 5 and 6; msg. 5327/2015 par. 2.3).

- Base of the earlier employer: 121,000.00; headroom 1,295.00.
- IVS employee: 1,295.00 x 9.19% = 119.0105 -> 119.01.
- Other employee rate: 2,211.43 x 0.30% = 6.63429 -> 6.63.
- Additional 1%: the base of September within the massimale, 1,295.00, is
  below 4,685.00: none.
- Employee INPS: 119.01 + 6.63 = 125.64.

Without the import the same run pays 2,211.43 x 9.49% = 209.86.

The same run in December settles the 1% of the year: 122,295.00 -
56,224.00 = 66,071.00, x 1% = 660.71, less the 600.00 the earlier employer
certifies it withheld: 60.71.  Employee INPS: 119.01 + 6.63 + 60.71 =
186.35.
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
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    ContributionHistory,
    EmploymentPeriod,
    InpsBaseYtd,
    OpeningBalances,
    PayrollRunId,
    PeriodState,
)
from tests.fixtures.next_year_repository import NextYearRepository
from tests.fixtures.normative_oracles.payslips.metalmeccanico_c3_2026 import (
    C3_MINIMUM_FROM_JUNE_2026,
)
from tests.fixtures.seniority import new_hire

_ENGINE = PayrollEngine.bundled()
_C3 = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    employment_period=EmploymentPeriod(date(2026, 9, 1)),
    seniority=new_hire(),
    contribution_history=ContributionHistory(first_enrolled_on=date(2001, 9, 1)),
)
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def _september(opening: PeriodState) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 9),
            payment_date=date(2026, 9, 28),
            employment=_C3,
            employer=_EMPLOYER,
            opening_state=opening,
        )
    )


def _employee_components(result: PeriodResult) -> dict[str, Decimal]:
    return {
        c.name: c.amount
        for c in result.contribution_breakdown.components
        if not c.name.endswith("employer")
    }


def _imported(base: InpsBaseYtd) -> PeriodState:
    return _ENGINE.import_opening_balances(
        OpeningBalances(
            tax_year=2026, inps_bases=(base,), recoveries=(), surtax_obligations=()
        )
    )


class TestInpsBaseOfOtherEmployers:
    """The massimale is cumulative across the worker's employments."""

    def test_earlier_employer_base_caps_the_new_employment(self) -> None:
        """121,000.00 elsewhere leaves 1,295.00 of IVS base: 138.59 employee."""
        result = _september(
            _imported(InpsBaseYtd(2026, other_employers=Decimal("121000.00")))
        )

        assert result.period_gross == C3_MINIMUM_FROM_JUNE_2026
        assert _employee_components(result) == {
            "ivs_employee": Decimal("119.01"),
            "non_ivs_employee": Decimal("6.63"),
        }
        assert result.contribution_breakdown.employee == Decimal("125.64")
        base = result.closing_state.accrual.inps_base(2026)
        assert base.own == C3_MINIMUM_FROM_JUNE_2026
        assert base.other_employers == Decimal("121000.00")

    def test_december_deducts_the_1pct_the_earlier_employer_withheld(self) -> None:
        """December settles 660.71 less the 600.00 certified: 60.71."""
        imported = _imported(
            InpsBaseYtd(
                2026,
                other_employers=Decimal("121000.00"),
                other_employers_additional_ivs=Decimal("600.00"),
            )
        )
        result = _ENGINE.calculate_period(
            PeriodInput(
                run=PayrollRun.regular(2026, 12),
                payment_date=date(2026, 12, 28),
                employment=_C3,
                employer=_EMPLOYER,
                opening_state=imported,
            )
        )

        assert result.period_gross == C3_MINIMUM_FROM_JUNE_2026
        assert _employee_components(result) == {
            "ivs_employee": Decimal("119.01"),
            "non_ivs_employee": Decimal("6.63"),
            "addizionale_1pct_conguaglio": Decimal("60.71"),
        }
        assert result.contribution_breakdown.employee == Decimal("186.35")
        base = result.closing_state.accrual.inps_base(2026)
        assert base.additional_ivs == Decimal("60.71")
        assert base.additional_ivs_withheld == Decimal("660.71")

    def test_december_without_the_1pct_of_the_earlier_employer_is_blocked(
        self,
    ) -> None:
        """The base of the earlier employer is known, its 1% is not.

        The conguaglio deducts what other employers withheld (circ. INPS
        156/2025 par. 5): without it the 60.71 above cannot be settled, so
        the run reports the fact missing instead of charging 660.71.
        September, which settles nothing, needs no such fact.
        """
        imported = _imported(InpsBaseYtd(2026, other_employers=Decimal("121000.00")))
        december = _ENGINE.calculate_period(
            PeriodInput(
                run=PayrollRun.regular(2026, 12),
                payment_date=date(2026, 12, 28),
                employment=_C3,
                employer=_EMPLOYER,
                opening_state=imported,
            )
        )
        september = _september(imported)

        def blocked(result: PeriodResult) -> bool:
            return any(
                b.code.value == "missing_fact"
                and b.detail == "other_employers_additional_ivs"
                for b in result.blockers
            )

        assert blocked(december)
        assert not december.is_payable
        assert not blocked(september)

    def test_other_employers_count_as_this_employer_would(self) -> None:
        """Differential: the same base held by this employer gives the same run."""
        other = _september(
            _imported(InpsBaseYtd(2026, other_employers=Decimal(121000)))
        )
        own = _september(_imported(InpsBaseYtd(2026, own=Decimal(121000))))

        assert other.contribution_breakdown == own.contribution_breakdown

    def test_without_the_import_the_run_is_uncapped(self) -> None:
        """No other employment: 2,211.43 x 9.49% = 209.86."""
        result = _september(PeriodState.zero())

        assert result.contribution_breakdown.employee == Decimal("209.86")

    def test_the_import_is_the_only_entry_point_for_external_totals(self) -> None:
        """The command checks its argument like every facade method."""
        with pytest.raises(InvalidInputError) as info:
            _ENGINE.import_opening_balances({"tax_year": 2026})  # type: ignore[arg-type]

        assert info.value.field == "balances"


class TestCompetence:
    """A late December counts toward the INPS base of its own year."""

    def test_late_december_adds_to_the_base_of_its_competence_year(self) -> None:
        """December 2026 paid in 2027 grows the 2026 base, not the 2027 one."""
        engine = PayrollEngine(repository=NextYearRepository())
        earlier = tuple(
            PayrollRunId.parse(f"2026-{m:02d}-regular") for m in range(1, 12)
        )
        opening = engine.import_opening_balances(
            OpeningBalances(
                tax_year=2027,
                competence_runs=earlier,
                inps_bases=(InpsBaseYtd(2026, own=Decimal("30000.00")),),
                recoveries=(),
                surtax_obligations=(),
            )
        )

        result = engine.calculate_period(
            PeriodInput(
                run=PayrollRun.regular(2026, 12),
                payment_date=date(2027, 1, 13),
                employment=Employment(
                    ccnl_slug="commercio-confcommercio.json", level_code="4"
                ),
                employer=_EMPLOYER,
                opening_state=opening,
            )
        )

        accrual = result.closing_state.accrual
        assert result.closing_state.tax_year == 2027
        assert accrual.inps_base(2026).own == Decimal("30000.00") + result.period_gross
        assert accrual.inps_base(2027).total == 0
        assert accrual.regular_months(2026) == 12

    def test_late_december_gives_back_the_1pct_of_its_own_year(self) -> None:
        """December 2026 paid in 2027 settles the 1% of 2026 as a credit.

        30,000.00 imported plus December is far below 56,224.00 (Commercio
        level 4 pays under 4,685.00 a month): nothing is due on 2026, so the
        300.00 withheld on it comes back on the late December
        (msg. INPS 5327/2015 par. 2.3).  The credit exceeds the employee
        INPS of the run, which is the first payment of tax year 2027.
        """
        engine = PayrollEngine(repository=NextYearRepository())
        earlier = tuple(
            PayrollRunId.parse(f"2026-{m:02d}-regular") for m in range(1, 12)
        )
        opening = engine.import_opening_balances(
            OpeningBalances(
                tax_year=2027,
                competence_runs=earlier,
                inps_bases=(
                    InpsBaseYtd(
                        2026,
                        own=Decimal("30000.00"),
                        additional_ivs=Decimal("300.00"),
                    ),
                ),
                recoveries=(),
                surtax_obligations=(),
            )
        )

        result = engine.calculate_period(
            PeriodInput(
                run=PayrollRun.regular(2026, 12),
                payment_date=date(2027, 1, 13),
                employment=Employment(
                    ccnl_slug="commercio-confcommercio.json", level_code="4"
                ),
                employer=_EMPLOYER,
                opening_state=opening,
            )
        )

        components = _employee_components(result)
        assert components["addizionale_1pct_conguaglio"] == Decimal("-300.00")
        assert result.contribution_breakdown.employee < 0
        assert result.closing_state.accrual.inps_base(2026).additional_ivs == 0

    def test_imported_competence_run_is_not_paid_again(self) -> None:
        """A run closed in an earlier tax year is rejected in the next one."""
        november = PayrollRunId.parse("2026-11-regular")
        engine = PayrollEngine(repository=NextYearRepository())
        opening = engine.import_opening_balances(
            OpeningBalances(
                tax_year=2027,
                competence_runs=(november,),
                inps_bases=(InpsBaseYtd(2026, other_employers=Decimal(0)),),
                recoveries=(),
                surtax_obligations=(),
            )
        )

        with pytest.raises(InvalidInputError, match="already closed"):
            engine.calculate_period(
                PeriodInput(
                    run=PayrollRun.of(november),
                    payment_date=date(2027, 1, 13),
                    employment=Employment(
                        ccnl_slug="commercio-confcommercio.json", level_code="4"
                    ),
                    employer=_EMPLOYER,
                    opening_state=opening,
                )
            )
