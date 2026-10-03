"""Tests for the competence state: each run closes once, in order per year."""

from __future__ import annotations

import pytest

from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.run import PayrollRunId
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

    def test_rejects_a_run_out_of_order_in_its_year(self) -> None:
        """The quattordicesima of June cannot close after July."""
        with pytest.raises(InvalidInputError, match="out of order"):
            _state("2026-07-regular", "2026-06-fourteenth")

    def test_adjustment_runs_are_not_ordered(self) -> None:
        """A correction of March closes after May."""
        state = _state("2026-05-regular", "2026-03-adjustment")

        assert len(state.competence_runs) == 2

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
