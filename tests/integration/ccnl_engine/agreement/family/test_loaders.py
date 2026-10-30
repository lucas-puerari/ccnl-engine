"""The catalog of contract families is read from the bundle."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ccnl_engine.agreement.family import loaders
from ccnl_engine.errors import DataIntegrityError

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def _fresh_cache() -> Iterator[None]:
    loaders.load_family_catalog.cache_clear()
    yield
    loaders.load_family_catalog.cache_clear()


def test_the_bundled_catalog_loads() -> None:
    """The bundle holds a catalog of schema 1 with the metalworking family."""
    catalog = loaders.load_family_catalog()

    assert catalog.schema_version == 1
    assert "metalmeccanica" in catalog.by_id


@pytest.mark.usefixtures("_fresh_cache")
@pytest.mark.parametrize(
    "text",
    ["not json", '{"schema_version": 1, "families": []}', '{"families": 3}'],
)
def test_a_malformed_catalog_raises(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    """A file that is not a valid catalog is a data integrity error."""
    monkeypatch.setattr(loaders, "read_resource", lambda _path: text)

    with pytest.raises(DataIntegrityError, match="not a valid catalog"):
        loaders.load_family_catalog()


@pytest.mark.usefixtures("_fresh_cache")
def test_a_missing_catalog_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """A bundle without the catalog is a data integrity error."""

    def _missing(path: str) -> str:
        raise FileNotFoundError(path)

    monkeypatch.setattr(loaders, "read_resource", _missing)

    with pytest.raises(DataIntegrityError, match="not a valid catalog"):
        loaders.load_family_catalog()
