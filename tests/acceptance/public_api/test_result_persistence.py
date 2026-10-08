"""Results cross process boundaries and states are persisted as JSON."""

from __future__ import annotations

import copy
import pickle

from ccnl_engine import PayrollEngine
from ccnl_engine.inputs import period_state_from_json, period_state_to_json
from tests.fixtures.explicit_facts import competence_year

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
