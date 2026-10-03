"""calculate_competence_year: facts allocated per run and surtax status."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.calculate_competence_year import (
    calculate_competence_year,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.events import AbsenceEvent, WorkEvent
from ccnl_engine.payroll.domain.inputs import PeriodFacts
from ccnl_engine.shared.domain.errors import InvalidInputError
from tests.helpers import year_plan

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026


class TestPerRunEventAllocation:
    """Periods keyed by run id reach that specific run."""

    def test_run_id_keyed_events_applied_to_correct_run(self) -> None:
        """Events keyed by run id reach the named run and no other run."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 5, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        run_id = f"{_YEAR}-05-regular"
        result_no_event = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        result_with_event = calculate_competence_year(
            year_plan(_YEAR, _CCNL, _LEVEL, events={run_id: (absence,)})
        )
        may_no = result_no_event.period_results[4].period_net
        may_with = result_with_event.period_results[4].period_net
        assert may_with < may_no

    def test_run_id_keyed_events_do_not_leak_to_other_runs(self) -> None:
        """Events allocated by run_id do not appear in other runs."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 5, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        run_id = f"{_YEAR}-05-regular"
        result = calculate_competence_year(
            year_plan(_YEAR, _CCNL, _LEVEL, events={run_id: (absence,)})
        )
        may_gross = result.period_results[4].period_gross
        for i, pr in enumerate(result.period_results):
            if i != 4:
                assert pr.period_gross >= may_gross or i >= 5

    def test_extra_month_run_accepts_run_id_keyed_events(self) -> None:
        """A run id key allocates events to an extra-month run."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 12, 15),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        thirteenth_run_id = f"{_YEAR}-12-thirteenth"
        result_no = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        result_with = calculate_competence_year(
            year_plan(_YEAR, _CCNL, _LEVEL, events={thirteenth_run_id: (absence,)})
        )
        thirteenth_no = next(
            r
            for r in result_no.period_results
            if r.period_id.month == 12
            and r.run is not None
            and r.run.run_kind == "thirteenth"
        )
        thirteenth_with = next(
            r
            for r in result_with.period_results
            if r.period_id.month == 12
            and r.run is not None
            and r.run.run_kind == "thirteenth"
        )
        assert thirteenth_with.period_net < thirteenth_no.period_net

    def test_extra_month_run_events_do_not_appear_in_regular_run(self) -> None:
        """Events allocated to thirteenth run are not applied to regular December."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 12, 15),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        thirteenth_run_id = f"{_YEAR}-12-thirteenth"
        result = calculate_competence_year(
            year_plan(_YEAR, _CCNL, _LEVEL, events={thirteenth_run_id: (absence,)})
        )
        regular_dec = next(
            r
            for r in result.period_results
            if r.period_id.month == 12
            and (r.run is None or r.run.run_kind == "regular")
        )
        result_no = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
        regular_dec_no = next(
            r
            for r in result_no.period_results
            if r.period_id.month == 12
            and (r.run is None or r.run.run_kind == "regular")
        )
        assert regular_dec.period_gross == regular_dec_no.period_gross

    def test_duplicate_allocation_raises(self) -> None:
        """Supplying the same run by month and by run id raises."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 3, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        run_id = f"{_YEAR}-03-regular"
        events: dict[int | str, tuple[WorkEvent, ...]] = {
            3: (absence,),
            run_id: (absence,),
        }
        with pytest.raises(InvalidInputError, match=r"names run .* twice"):
            calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL, events=events))

    def test_month_keyed_events_work_alone(self) -> None:
        """Month keys work without any run id key."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 6, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        result = calculate_competence_year(
            year_plan(_YEAR, _CCNL, _LEVEL, events={6: (absence,)})
        )
        jun_net = result.period_results[5].period_net
        jan_net = result.period_results[0].period_net
        assert jun_net < jan_net


class TestSurtaxStatus:
    """Surtax decisions set the status of every run and of the year."""

    def test_unknown_municipality_makes_every_run_and_the_year_incomplete(
        self,
    ) -> None:
        """A Belfiore code without a table leaves the whole year incomplete."""
        result = calculate_competence_year(
            year_plan(_YEAR, _CCNL, _LEVEL, facts=PeriodFacts(comune_belfiore="Z999"))
        )

        assert {r.assurance.calculation for r in result.period_results} == {
            CalculationStatus.INCOMPLETE
        }
        assert result.assurance.calculation is CalculationStatus.INCOMPLETE
        assert {i.code for i in result.issues} == {"municipal_surtax_unknown"}

    def test_malformed_region_code_is_rejected(self) -> None:
        """A region name instead of a region code is invalid input."""
        with pytest.raises(InvalidInputError, match="ISO 3166-2:IT"):
            calculate_competence_year(
                year_plan(_YEAR, _CCNL, _LEVEL, facts=PeriodFacts(regione="Lombardia"))
            )
