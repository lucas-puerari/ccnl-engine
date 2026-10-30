"""The census of a CCNL is read from the bundle, when it has one."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.agreement.census import loaders
from ccnl_engine.errors import DataIntegrityError

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(autouse=True)
def _fresh_cache() -> Iterator[None]:
    loaders.load_census.cache_clear()
    yield
    loaders.load_census.cache_clear()


def _serve(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    monkeypatch.setattr(loaders, "read_resource", lambda _path: text)


def test_a_ccnl_without_census_has_none() -> None:
    """No file: the CCNL is not censused, which is not an error."""
    assert loaders.load_census("no-such-ccnl") is None


def test_a_census_loads(monkeypatch: pytest.MonkeyPatch) -> None:
    """A file of schema 1 for the CCNL asked for loads."""
    _serve(monkeypatch, json.dumps({"schema_version": 1, "ccnl_id": "x"}))

    census = loaders.load_census("x")

    assert census is not None
    assert census.requirements == ()


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ("not json", "is not JSON"),
        ('{"schema_version": 1}', "is not a valid census"),
        ('{"schema_version": 2, "ccnl_id": "x"}', "must be schema 1 of 'x'"),
        ('{"schema_version": 1, "ccnl_id": "y"}', "must be schema 1 of 'x'"),
    ],
)
def test_a_malformed_census_raises(
    monkeypatch: pytest.MonkeyPatch, text: str, match: str
) -> None:
    """A file that is not the census of the CCNL is a data integrity error."""
    _serve(monkeypatch, text)

    with pytest.raises(DataIntegrityError, match=match):
        loaders.load_census("x")
