"""Public persistence of a period state, bound to this engine and bundle."""

from __future__ import annotations

import json

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.knowledge.facade import __version__ as bundle_version
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.state.serializers_persistence import (
    period_state_from_json,
    period_state_to_json,
)
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
def test_a_state_of_another_engine_or_bundle_is_rejected(key: str) -> None:
    """Balances computed under other code or rules do not continue the chain."""
    payload = json.loads(period_state_to_json(PeriodState.zero()))
    payload[key] = "0.0.0"

    with pytest.raises(InvalidInputError, match=key):
        period_state_from_json(json.dumps(payload))
