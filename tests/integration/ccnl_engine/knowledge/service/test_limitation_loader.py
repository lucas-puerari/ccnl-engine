"""Engine limitation loader: the bundled file and the rejected documents."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

import ccnl_engine.knowledge.service.limitation_loader as _loader_mod
from ccnl_engine.knowledge.service.limitation_loader import (
    load_engine_limitations,
    parse_engine_limitations,
)
from ccnl_engine.shared.domain.errors import DataIntegrityError
from ccnl_engine.shared.domain.limitation import LimitationTrigger

_ENTRY: dict[str, Any] = {
    "id": "engine_path",
    "capability": "base_salary",
    "variant": "engine_path",
    "summary": "what differs",
    "monetary_impact": "yes",
    "rulesets": ["ccnl-a"],
    "applies_when": {"trigger": "path"},
    "source": "module",
    "remediation": "fix it",
}


def test_bundled_engine_limitations_are_path_triggered() -> None:
    """Every engine limitation is recorded when its code path is taken.

    The open ones block the runs they apply to; a resolved one no longer
    does.
    """
    limitations = load_engine_limitations()
    blocking = {lim.id for lim in limitations if lim.blocks}
    assert blocking == {
        "sickness_inps_daily_base",
        "sickness_cumulation_window",
    }
    assert {lim.id for lim in limitations} - blocking == {
        "apprenticeship_midpoint_allowances",
        "apprentice_seniority_simplified",
    }
    assert all(
        lim.applies_when.trigger is LimitationTrigger.PATH for lim in limitations
    )


@pytest.mark.parametrize(
    ("document", "match"),
    [
        ([], "expected an object"),
        ({"schema_version": 2, "limitations": []}, "expected an object"),
        ({"schema_version": 1, "limitations": {}}, "must be a list"),
        ({"schema_version": 1, "limitations": [{"id": "x"}]}, "invalid entry"),
        ({"schema_version": 1, "limitations": [_ENTRY, _ENTRY]}, "declared twice"),
    ],
)
def test_malformed_documents_are_rejected(document: object, match: str) -> None:
    """A malformed document is a data integrity error."""
    with pytest.raises(DataIntegrityError, match=match):
        parse_engine_limitations(document)


def test_unreadable_file_is_a_data_error() -> None:
    """A missing file is a data integrity error, not a crash."""
    _loader_mod._load_cached.cache_clear()
    try:
        with (
            patch.object(_loader_mod, "read_bundled", side_effect=FileNotFoundError),
            pytest.raises(DataIntegrityError, match="cannot read"),
        ):
            load_engine_limitations()
    finally:
        _loader_mod._load_cached.cache_clear()
