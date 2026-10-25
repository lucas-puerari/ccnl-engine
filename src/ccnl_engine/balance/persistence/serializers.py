"""Persist a :class:`~ccnl_engine.balance.models.PeriodState` as JSON.

The public pair of the domain codec, bound to the running engine and the
bundled knowledge: a state is written with the versions that computed it,
kept for audit, and read back by any later engine or bundle whose schema
migrations reach it.
"""

from __future__ import annotations

from ccnl_engine.balance import serializers as state_codec
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.bundle.loaders import bundle_version
from ccnl_engine.version import __version__ as engine_version

__all__ = ["period_state_from_json", "period_state_to_json"]


def period_state_to_json(state: PeriodState) -> str:
    """Return ``state`` as JSON text, with its schema, engine and bundle versions.

    Returns:
        The JSON text of the state.
    """
    return state_codec.period_state_to_json(
        state, engine_version=engine_version, bundle_version=bundle_version()
    )


def period_state_from_json(text: str) -> PeriodState:
    """Return the state written by :func:`period_state_to_json`.

    A state written by another engine or knowledge-bundle version reads
    back: those versions stay in the text, for audit.  A state of an
    earlier schema is migrated to the current one.  A text that is not such
    JSON, of a schema newer than this engine or older than the first one
    persisted, or that names a type outside the persisted state raises
    :class:`~ccnl_engine.errors.InvalidInputError`: recompute the runs, or
    import the balances with
    :class:`~ccnl_engine.balance.opening.provider.services.OpeningBalances`.

    Returns:
        The state, its invariants checked by its constructors.
    """
    return state_codec.period_state_from_json(text)
