"""Results cross process boundaries; states, requests and results go to JSON."""

from __future__ import annotations

import copy
import json
import pickle

from ccnl_engine import CompetenceYearPlan, PayrollEngine, PeriodInput
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.inputs import (
    period_state_from_json,
    period_state_to_json,
    request_from_json,
    request_to_json,
)
from ccnl_engine.reconciliation.validators import reconcile
from ccnl_engine.results import result_to_json
from tests.knowledge.ccnl_engine.period.builders import (
    competence_year,
    regular_run,
)

_ENGINE = PayrollEngine.bundled()


def test_a_year_of_results_pickles_and_copies_equal() -> None:
    """A batch can fan the runs out to worker processes and collect them."""
    year = _ENGINE.calculate_competence_year(competence_year())
    for result in year.period_results:
        assert pickle.loads(pickle.dumps(result)) == result
        assert copy.deepcopy(result) == result


def test_every_closing_state_of_a_year_reads_back_from_json() -> None:
    """The state persisted between runs is the state the next run opens on."""
    year = _ENGINE.calculate_competence_year(competence_year())
    for result in year.period_results:
        state = result.closing_state
        assert period_state_from_json(period_state_to_json(state)) == state


def test_a_request_read_from_json_computes_the_same_result() -> None:
    """A request stored as JSON replays to the same payslip."""
    request = regular_run(1)
    replayed = request_from_json(request_to_json(request), PeriodInput)
    assert _ENGINE.calculate_period(replayed) == _ENGINE.calculate_period(request)


def test_a_year_plan_and_its_result_go_to_json() -> None:
    """A plan reads back equal; its result is written for a reader outside Python."""
    plan = competence_year()
    assert request_from_json(request_to_json(plan), CompetenceYearPlan) == plan
    payload = json.loads(result_to_json(_ENGINE.calculate_competence_year(plan)))
    assert payload["result"]["$type"] == "CompetenceYearResult"


def test_runs_opened_on_states_read_back_from_json_match_the_year() -> None:
    """January to March run one by one, each on the state of the one before.

    The state goes to JSON and back between the runs, as a payroll stores
    it; the three payslips are those the year computes in memory, and
    each reconciles.
    """
    year = _ENGINE.calculate_competence_year(competence_year())
    in_memory = [r for r in year.period_results if r.run is not None][:3]
    state = PeriodState.zero()
    for month, expected in enumerate(in_memory, start=1):
        result = _ENGINE.calculate_period(regular_run(month, opening_state=state))

        assert (result.run, result.period_net) == (expected.run, expected.period_net)
        assert result.ledger_entries == expected.ledger_entries
        assert reconcile(result, state).ok
        state = period_state_from_json(period_state_to_json(result.closing_state))
