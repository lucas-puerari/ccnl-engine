"""JSON form of a period state: tagged values, a schema version, safe reading."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind
from ccnl_engine.payroll.domain.sickness import SicknessEpisode
from ccnl_engine.payroll.domain.state_codec import (
    period_state_from_json,
    period_state_to_json,
)
from ccnl_engine.shared.domain.errors import InvalidInputError


def _state() -> PeriodState:
    zero = PeriodState.zero()
    accrual = zero.accrual.__class__(
        competence_runs=(PayrollRunId(2026, 1, RunKind.REGULAR),),
        inps_bases=(InpsBaseYtd(2026, Decimal("2158.26"), Decimal(0)),),
        sickness_episodes=(SicknessEpisode("A", date(2026, 1, 5), date(2026, 1, 9)),),
        sickness_known_from=date(2026, 1, 1),
    )
    return PeriodState(accrual=accrual, cash=zero.cash, history_known=False)


@pytest.mark.parametrize("state", [PeriodState.zero(), _state()], ids=["zero", "full"])
def test_a_state_reads_back_equal(state: PeriodState) -> None:
    """Decimals, dates, enums, tuples and nested states survive the round trip."""
    assert period_state_from_json(period_state_to_json(state)) == state


def test_the_json_carries_the_schema_version() -> None:
    """The version of the state is written next to it."""
    payload = json.loads(period_state_to_json(PeriodState.zero()))
    assert payload["schema_version"] == PeriodState.SCHEMA_VERSION


def _payload(**changes: object) -> str:
    payload = json.loads(period_state_to_json(_state()))
    payload.update(changes)
    return json.dumps(payload)


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("not json", id="not-json"),
        pytest.param("[1]", id="not-an-object"),
        pytest.param(_payload(schema_version=1), id="old-version"),
        pytest.param(
            _payload(state={"$type": "builtins.dict", "fields": {}}), id="foreign"
        ),
        pytest.param(
            _payload(state={"$type": "ccnl_engine.payroll.domain.run.RunKind"}),
            id="not-a-dataclass",
        ),
        pytest.param(
            _payload(state={"$enum": "ccnl_engine.payroll.domain.run.PayrollRunId"}),
            id="not-an-enum",
        ),
        pytest.param(_payload(state=[1]), id="bare-list"),
        pytest.param(_payload(state={"x": 1}), id="untagged"),
        pytest.param(_payload(state={"$decimal": "1"}), id="not-a-state"),
    ],
)
def test_a_text_that_is_not_a_current_state_is_invalid_input(text: str) -> None:
    """Reading never builds a type outside the payroll domain."""
    with pytest.raises(InvalidInputError):
        period_state_from_json(text)
