"""A damaged bundle raises DataIntegrityError, never a builtin error.

A resource the manifest lists is read whole, parsed and checked against
the hash the manifest records, once per process.  A caller error such as
``UnknownCcnlError`` is kept for what the caller got wrong.
"""

from __future__ import annotations

import gzip
from unittest.mock import patch

import pytest

from ccnl_engine.bundle import loaders
from ccnl_engine.bundle.loaders import read_resource
from ccnl_engine.errors import DataIntegrityError

_PATH = "family/2026.json"
_READER = "ccnl_engine.bundle.loaders.read_bundled"


@pytest.fixture(autouse=True)
def _fresh_checks() -> None:
    """Forget the verified resources; read the manifest before any patch."""
    loaders._VERIFIED.clear()
    loaders._manifest()


@pytest.mark.parametrize(
    ("fault", "match"),
    [
        pytest.param(FileNotFoundError("gone"), "does not hold it", id="missing"),
        pytest.param(gzip.BadGzipFile("bad"), "cannot be read", id="bad_gzip"),
        pytest.param(EOFError("cut"), "cannot be read", id="truncated"),
    ],
)
def test_an_unreadable_listed_resource_is_an_integrity_error(
    fault: Exception, match: str
) -> None:
    """Missing, corrupt or truncated: the bundle is damaged, not the input."""
    with (
        patch(_READER, side_effect=fault),
        pytest.raises(DataIntegrityError, match=match),
    ):
        read_resource(_PATH)


def test_text_that_is_not_json_is_an_integrity_error() -> None:
    """Garbage in a listed resource is reported, not a JSONDecodeError."""
    with (
        patch(_READER, return_value="{not json"),
        pytest.raises(DataIntegrityError, match="not valid JSON"),
    ):
        read_resource(_PATH)


def test_content_that_differs_from_the_manifest_is_an_integrity_error() -> None:
    """Valid JSON with another content fails the manifest hash."""
    with (
        patch(_READER, return_value='{"year": 2026}'),
        pytest.raises(DataIntegrityError, match="manifest hash"),
    ):
        read_resource(_PATH)


def test_an_unlisted_path_is_still_not_found() -> None:
    """A path the manifest does not list keeps FileNotFoundError for the loaders."""
    with pytest.raises(FileNotFoundError):
        read_resource("family/2099.json")


def test_a_listed_resource_is_checked_once() -> None:
    """The second read of a verified resource does not parse it again."""
    read_resource(_PATH)
    with patch.object(loaders, "source_hash") as digest:
        read_resource(_PATH)
    digest.assert_not_called()
