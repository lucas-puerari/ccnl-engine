"""A state stored by an earlier engine, bundle or schema reads under this one."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ccnl_engine.balance.competence.models import EmploymentAccrualState
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.balance.serializers import (
    FIRST_SCHEMA_VERSION,
    STATE_MIGRATIONS,
    period_state_from_json,
)
from ccnl_engine.contribution.base.models import InpsBaseYtd
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.leave.balance.models import LeaveAccount
from ccnl_engine.run.models import PayrollRunId, RunKind
from ccnl_engine.sickness.models import SicknessEpisode

_STATES = Path(__file__).parent / "persisted_state"


def _stored(schema: int) -> str:
    return (_STATES / f"schema_{schema}.json").read_text(encoding="utf-8")


def _expected() -> PeriodState:
    accrual = EmploymentAccrualState(
        competence_runs=(PayrollRunId(2026, 1, RunKind.REGULAR),),
        inps_bases=(InpsBaseYtd(2026, Decimal("2158.26"), Decimal(0)),),
        sickness_episodes=(SicknessEpisode("A", date(2026, 1, 5), date(2026, 1, 9)),),
        sickness_known_from=date(2026, 1, 1),
        tfr_quotas_known_from=2027,
        leave=LeaveAccount(known=False),
    )
    return PeriodState(
        accrual=accrual, cash=PeriodState.zero().cash, history_known=False
    )


def test_every_stored_schema_has_a_frozen_state() -> None:
    """Each schema from the first one persisted keeps a state written by it."""
    stored = {int(p.stem.removeprefix("schema_")) for p in _STATES.glob("*.json")}

    assert stored == set(range(FIRST_SCHEMA_VERSION, PeriodState.SCHEMA_VERSION + 1))


@pytest.mark.parametrize(
    "schema", range(FIRST_SCHEMA_VERSION, PeriodState.SCHEMA_VERSION + 1)
)
def test_a_state_of_an_earlier_release_reads_under_this_one(schema: int) -> None:
    """Another engine and bundle wrote it; the migrations bring its schema here."""
    payload = json.loads(_stored(schema))

    assert (payload["engine_version"], payload["bundle_version"]) == (
        "0.5.1",
        "2025.1",
    )
    assert period_state_from_json(_stored(schema)) == _expected()


@pytest.mark.parametrize("schema", [14, 15])
def test_a_state_before_schema_16_has_its_leave_unknown(schema: int) -> None:
    """Written before the leave accrued, a state carries no known leave."""
    state = period_state_from_json(_stored(schema))

    assert state.accrual.leave == LeaveAccount(known=False)


def test_a_migration_rejects_a_tree_that_is_not_a_state() -> None:
    """A step reads only a tagged state tree."""
    with pytest.raises(TypeError, match="tagged PeriodState"):
        STATE_MIGRATIONS[15]([])


def test_a_state_of_a_later_schema_is_rejected() -> None:
    """A state written by a newer engine is never guessed at."""
    payload = json.loads(_stored(PeriodState.SCHEMA_VERSION))
    payload["schema_version"] = PeriodState.SCHEMA_VERSION + 1

    with pytest.raises(InvalidInputError, match="newer than"):
        period_state_from_json(json.dumps(payload))
