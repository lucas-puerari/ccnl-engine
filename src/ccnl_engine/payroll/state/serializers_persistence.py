"""Persist a :class:`~ccnl_engine.payroll.state.models.PeriodState` as JSON.

The public pair of the domain codec, bound to the running engine and the
bundled knowledge: a state is written with the versions that computed it
and read back only by the same engine and bundle.
"""

from __future__ import annotations

from ccnl_engine.knowledge.facade import __version__ as bundle_version
from ccnl_engine.payroll.state import serializers as state_codec
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.version import __version__ as engine_version

__all__ = ["period_state_from_json", "period_state_to_json"]


def period_state_to_json(state: PeriodState) -> str:
    """Return ``state`` as JSON text, with its schema, engine and bundle versions.

    Returns:
        The JSON text of the state.
    """
    return state_codec.period_state_to_json(
        state, engine_version=engine_version, bundle_version=bundle_version
    )


def period_state_from_json(text: str) -> PeriodState:
    """Return the state written by :func:`period_state_to_json`.

    A text that is not such JSON, written by another schema, engine or
    knowledge-bundle version, or that names a type outside the persisted
    state raises :class:`~ccnl_engine.errors.InvalidInputError`:
    recompute the runs, or import the balances with
    :class:`~ccnl_engine.payroll.state.services_opening_balance.OpeningBalances`.

    Returns:
        The state, its invariants checked by its constructors.
    """
    return state_codec.period_state_from_json(
        text, engine_version=engine_version, bundle_version=bundle_version
    )
