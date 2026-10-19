"""Public persistence of a period state, bound to this engine and bundle."""

from __future__ import annotations

import json

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.balance.persistence.serializers import (
    period_state_from_json,
    period_state_to_json,
)
from ccnl_engine.bundle.facade import __version__ as bundle_version
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.version import __version__ as engine_version


def test_a_state_carries_this_engine_and_bundle() -> None:
    """The text names the versions that computed the state and reads back."""
    text = period_state_to_json(PeriodState.zero())
    payload = json.loads(text)

    assert (payload["engine_version"], payload["bundle_version"]) == (
        engine_version,
        bundle_version,
    )
    assert period_state_from_json(text) == PeriodState.zero()


@pytest.mark.parametrize("key", ["engine_version", "bundle_version"])
def test_a_state_of_another_engine_or_bundle_reads_back(key: str) -> None:
    """A release of the engine or of the bundle does not invalidate a stored state."""
    payload = json.loads(period_state_to_json(PeriodState.zero()))
    payload[key] = "0.0.0"

    assert period_state_from_json(json.dumps(payload)) == PeriodState.zero()


def test_a_state_of_a_later_schema_is_rejected() -> None:
    """A state written by a newer engine is not read by this one."""
    payload = json.loads(period_state_to_json(PeriodState.zero()))
    payload["schema_version"] = PeriodState.SCHEMA_VERSION + 1

    with pytest.raises(InvalidInputError, match="schema_version"):
        period_state_from_json(json.dumps(payload))
