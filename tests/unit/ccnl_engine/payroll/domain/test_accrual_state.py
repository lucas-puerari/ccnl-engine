"""Tests for the competence state: each run closes once, in order per year."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.sickness import SicknessEpisode
from ccnl_engine.shared.domain.errors import InvalidInputError

_FIELD = "EmploymentAccrualState.competence_runs"


def _state(*texts: str) -> EmploymentAccrualState:
    return EmploymentAccrualState(
        competence_runs=tuple(PayrollRunId.parse(t) for t in texts)
    )


def _full_year(year: int) -> tuple[str, ...]:
    months = [f"{year}-{m:02d}-regular" for m in range(1, 13)]
    return (*months[:6], f"{year}-06-fourteenth", *months[6:], f"{year}-12-thirteenth")


class TestEmploymentAccrualState:
    """Competence runs across the employment."""

    def test_counts_the_months_of_each_competence_year(self) -> None:
        """Two full years: twelve regular months and two extra months each."""
        state = _state(*_full_year(2026), *_full_year(2027))

        for year in (2026, 2027):
            assert state.regular_months(year) == 12
            assert [str(r) for r in state.extra_months_paid(year)] == [
                f"{year}-06-fourteenth",
                f"{year}-12-thirteenth",
            ]
        assert state.runs_of(2028) == ()

    def test_late_december_follows_the_next_january(self) -> None:
        """Different competence years are not ordered against each other."""
        state = _state("2027-01-regular", "2026-12-regular", "2027-02-regular")

        assert state.regular_months(2026) == 1
        assert state.regular_months(2027) == 2

    def test_a_thirteenth_regular_month_cannot_close(self) -> None:
        """A competence year has at most twelve regular months."""
        state = _state(*_full_year(2026))

        with pytest.raises(InvalidInputError, match="already closed") as info:
            state.after(PayrollRunId.parse("2026-12-regular"))

        assert info.value.field == _FIELD

    def test_rejects_a_regular_month_out_of_order_in_its_year(self) -> None:
        """February cannot close after March."""
        with pytest.raises(InvalidInputError, match="out of order"):
            _state("2026-03-regular", "2026-02-regular")

    @pytest.mark.parametrize(
        "runs",
        [
            ("2026-12-thirteenth", "2026-12-regular"),
            ("2026-07-fourteenth", "2026-07-regular"),
            ("2026-08-regular", "2026-06-fourteenth"),
        ],
        ids=["december after the tredicesima", "july after the 14th", "late 14th"],
    )
    def test_extra_months_are_not_ordered_against_regular_months(
        self, runs: tuple[str, ...]
    ) -> None:
        """An employer paying in arrears closes extra months independently."""
        state = _state(*runs)

        assert len(state.competence_runs) == 2

    @pytest.mark.parametrize("run", ["2026-05-regular", "2026-12-thirteenth"])
    def test_nothing_closes_after_the_termination_run(self, run: str) -> None:
        """The termination run ended the employment: a rehire opens anew.

        The error names the termination run and the remedy, not an order of
        months the caller did not break.
        """
        state = _state("2026-04-regular", "2026-04-termination")

        with pytest.raises(InvalidInputError) as info:
            state.check_next_run(PayrollRunId.parse(run))
        message = str(info.value)
        assert "termination run '2026-04-termination' ended the employment" in message
        assert "PeriodState.zero()" in message
        assert "out of order" not in message
        assert info.value.field == _FIELD
        state.check_next_run(PayrollRunId.parse("2026-04-adjustment"))

    def test_a_termination_closes_its_competence_year_only(self) -> None:
        """A run of the next competence year is not ordered against it."""
        state = _state("2026-12-regular", "2026-12-termination")

        state.check_next_run(PayrollRunId.parse("2027-01-regular"))

    def test_adjustment_runs_are_not_ordered(self) -> None:
        """A correction of March closes after May."""
        state = _state("2026-05-regular", "2026-03-adjustment")

        assert len(state.competence_runs) == 2

    def test_second_adjustment_of_a_month_closes_once(self) -> None:
        """A second correction of a month is a new run; repeating it is not."""
        state = _state("2026-12-regular", "2026-12-adjustment")

        state.check_next_run(PayrollRunId.parse("2026-12-adjustment-2"))
        with pytest.raises(InvalidInputError, match="already closed"):
            state.after(PayrollRunId.parse("2026-12-adjustment-2")).check_next_run(
                PayrollRunId.parse("2026-12-adjustment-2")
            )

    def test_check_next_run(self) -> None:
        """The rules apply to the next run before it is computed."""
        state = _state("2026-03-regular")

        state.check_next_run(PayrollRunId.parse("2026-04-regular"))
        with pytest.raises(InvalidInputError, match="out of order"):
            state.check_next_run(PayrollRunId.parse("2026-02-regular"))

    def test_after_appends_the_run(self) -> None:
        """Closing a run returns a new state with it last."""
        run = PayrollRunId.parse("2026-01-regular")

        assert EmploymentAccrualState().after(run).competence_runs == (run,)

    @pytest.mark.parametrize("runs", [("2026-01-regular",), "2026-01-regular"])
    def test_rejects_elements_that_are_not_run_ids(self, runs: object) -> None:
        """Each element is a PayrollRunId."""
        with pytest.raises(InvalidInputError):
            EmploymentAccrualState(competence_runs=runs)  # type: ignore[arg-type]


class TestInpsBases:
    """The INPS base toward the massimale, per competence year."""

    def test_a_run_adds_its_base_to_its_competence_year(self) -> None:
        """December 2026 adds to 2026 even after January 2027."""
        state = (
            EmploymentAccrualState()
            .after(PayrollRunId.parse("2027-01-regular"), Decimal(10))
            .after(PayrollRunId.parse("2026-12-regular"), Decimal(20))
        )

        assert [b.year for b in state.inps_bases] == [2026, 2027]
        assert state.inps_base(2026).own == Decimal(20)
        assert state.inps_base(2025) == InpsBaseYtd(2025)

    @pytest.mark.parametrize("years", [(2027, 2026), (2026, 2026)])
    def test_rejects_bases_out_of_year_order(self, years: tuple[int, int]) -> None:
        """One base per year, in year order."""
        bases = tuple(InpsBaseYtd(y) for y in years)
        with pytest.raises(InvalidInputError, match="one base per year") as info:
            EmploymentAccrualState(inps_bases=bases)

        assert info.value.field == "EmploymentAccrualState.inps_bases"

    def test_an_extra_month_closes_once_whatever_its_month(self) -> None:
        """The quattordicesima of 2026 paid in July is the one of June."""
        state = _state("2026-06-fourteenth")

        with pytest.raises(InvalidInputError, match="already closed as"):
            state.check_next_run(PayrollRunId.parse("2026-07-fourteenth"))


class TestSicknessEpisodes:
    """Recorded sickness episodes have distinct ids, in start order."""

    def test_rejects_repeated_or_unordered_episodes(self) -> None:
        """Two records of one id, or a later episode first, are rejected."""
        first = SicknessEpisode("a", date(2026, 2, 2), date(2026, 2, 11))
        second = SicknessEpisode("b", date(2026, 3, 2), date(2026, 3, 4))
        for episodes in ((first, first), (second, first)):
            with pytest.raises(InvalidInputError, match="distinct ids"):
                EmploymentAccrualState(sickness_episodes=episodes)
        state = EmploymentAccrualState(sickness_episodes=[first, second])  # type: ignore[arg-type]
        assert state.sickness_episodes == (first, second)
