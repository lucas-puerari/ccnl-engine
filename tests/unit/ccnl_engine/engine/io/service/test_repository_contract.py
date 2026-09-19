"""Repository contract tests: identical behavior for source and wheel layouts.

Verifies that BundledResourceStore and read_bundled behave identically under
the editable-install layout (plain ``.json``) and the wheel layout
(``.json.gz``), and that all error scenarios (missing resource, corrupted
archive, invalid JSON, unsupported resource) propagate with consistent
exception types from the caller's perspective.

The "contract" being tested is the expectation held by every loader in the
engine: whatever layout the bundle uses, the same call sequence and the same
error types must be observable.
"""

from __future__ import annotations

import gzip
import json
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

import ccnl_engine.engine.contract.service.loaders as contract_loaders
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.io.service.bundled import read_bundled
from ccnl_engine.engine.io.service.bundled_resources import BundledResourceStore

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# Shared test data for parametric source / wheel fixtures
# ---------------------------------------------------------------------------

_ALPHA_CONTENT = '{"hello": "world"}'
_BETA_CONTENT = '{"answer": 42}'
_ALL_FILES = {"alpha.json": _ALPHA_CONTENT, "beta.json": _BETA_CONTENT}


def _make_source_dir(root: Path) -> Path:
    """Write plain .json files (editable-install layout) into root.

    Returns:
        The same *root* path for chaining.
    """
    for name, body in _ALL_FILES.items():
        (root / name).write_text(body, encoding="utf-8")
    return root


def _make_wheel_dir(root: Path) -> Path:
    """Write .json.gz files (wheel layout) into root.

    Returns:
        The same *root* path for chaining.
    """
    for name, body in _ALL_FILES.items():
        (root / (name + ".gz")).write_bytes(
            gzip.compress(body.encode("utf-8"), compresslevel=9, mtime=0)
        )
    return root


@pytest.fixture(params=["source", "wheel"])
def store_dir(request: pytest.FixtureRequest, tmp_path: Path) -> Path:
    """Parametric fixture: source-layout or wheel-layout data directory.

    Returns:
        A temporary directory populated with the selected layout.
    """
    if request.param == "source":
        return _make_source_dir(tmp_path)
    return _make_wheel_dir(tmp_path)


@pytest.fixture(params=["source", "wheel"])
def populated_store(
    request: pytest.FixtureRequest, tmp_path: Path
) -> BundledResourceStore:
    """Parametric fixture: BundledResourceStore over source or wheel layout.

    Returns:
        A :class:`BundledResourceStore` bound to the selected layout.
    """
    if request.param == "source":
        return BundledResourceStore(_make_source_dir(tmp_path))
    return BundledResourceStore(_make_wheel_dir(tmp_path))


# ---------------------------------------------------------------------------
# BundledResourceStore contract: list_json
# ---------------------------------------------------------------------------


class TestListJsonContract:
    """list_json returns the same .json names regardless of storage format."""

    def test_lists_all_files(self, populated_store: BundledResourceStore) -> None:
        """All resource names appear in list_json output for both layouts."""
        result = populated_store.list_json()
        assert set(result) == {"alpha.json", "beta.json"}

    def test_sorted_output(self, populated_store: BundledResourceStore) -> None:
        """list_json output is alphabetically sorted in both layouts."""
        result = populated_store.list_json()
        assert result == sorted(result)

    def test_names_have_json_extension(
        self, populated_store: BundledResourceStore
    ) -> None:
        """Names end with .json (not .json.gz) in both layouts."""
        for name in populated_store.list_json():
            assert name.endswith(".json"), f"Expected .json suffix, got: {name}"
            assert not name.endswith(".gz")


# ---------------------------------------------------------------------------
# BundledResourceStore contract: read_json
# ---------------------------------------------------------------------------


class TestReadJsonContract:
    """read_json returns identical content regardless of storage format."""

    def test_reads_alpha(self, populated_store: BundledResourceStore) -> None:
        """alpha.json content is the same for source and wheel layouts."""
        assert populated_store.read_json("alpha.json") == _ALPHA_CONTENT

    def test_reads_beta(self, populated_store: BundledResourceStore) -> None:
        """beta.json content is the same for source and wheel layouts."""
        assert populated_store.read_json("beta.json") == _BETA_CONTENT


# ---------------------------------------------------------------------------
# read_bundled error contracts
# ---------------------------------------------------------------------------


class TestReadBundledErrorContracts:
    """read_bundled propagates consistent error types for both layouts."""

    def test_missing_in_source_layout_raises_file_not_found(
        self, tmp_path: Path
    ) -> None:
        """When neither .json nor .json.gz exists, FileNotFoundError propagates."""
        with pytest.raises(FileNotFoundError):
            read_bundled(tmp_path, "nonexistent.json")

    def test_missing_gz_plain_fallback_also_absent_raises(self, tmp_path: Path) -> None:
        """If .gz is absent and .json is also absent, FileNotFoundError propagates."""
        with pytest.raises(FileNotFoundError):
            read_bundled(tmp_path, "ghost.json")

    def test_corrupt_gz_raises_bad_gzip_file(self, tmp_path: Path) -> None:
        """A file with .gz extension but corrupt content raises gzip.BadGzipFile."""
        (tmp_path / "bad.json.gz").write_bytes(b"not-a-valid-gzip-stream")
        with pytest.raises(gzip.BadGzipFile):
            read_bundled(tmp_path, "bad.json")

    def test_valid_gz_but_invalid_json_returns_raw_text(self, tmp_path: Path) -> None:
        """read_bundled returns raw text even when JSON is malformed; caller parses."""
        bad_json = "this is not json {{{"
        (tmp_path / "broken.json.gz").write_bytes(
            gzip.compress(bad_json.encode("utf-8"), compresslevel=1, mtime=0)
        )
        result = read_bundled(tmp_path, "broken.json")
        assert result == bad_json


# ---------------------------------------------------------------------------
# load_ccnl error contracts (caller-level view)
# ---------------------------------------------------------------------------


class TestLoadCcnlErrorContracts:
    """load_ccnl raises consistent error types for unsupported resources."""

    @pytest.fixture(autouse=True)
    def _clear_cache(self) -> None:
        """Clear the @cache on load_ccnl before each test."""
        load_ccnl.cache_clear()

    def test_nonexistent_file_raises_file_not_found(self) -> None:
        """load_ccnl with a nonexistent filename raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_ccnl("this-ccnl-does-not-exist.json")

    def test_invalid_json_content_raises_json_decode_error(self) -> None:
        """load_ccnl raises json.JSONDecodeError when content is not valid JSON."""
        with (
            patch.object(
                contract_loaders,
                "read_bundled",
                return_value="not valid JSON {{{",
            ),
            pytest.raises(json.JSONDecodeError),
        ):
            load_ccnl("fake.json")


# ---------------------------------------------------------------------------
# Parametric source vs wheel: same round-trip via read_bundled
# ---------------------------------------------------------------------------


class TestReadBundledSourceWheelParity:
    """read_bundled reads identical content from both source and wheel layouts."""

    def test_plain_json_readable(self, store_dir: Path) -> None:
        """alpha.json content is the same regardless of underlying storage."""
        result = read_bundled(store_dir, "alpha.json")
        assert result == _ALPHA_CONTENT

    def test_second_file_readable(self, store_dir: Path) -> None:
        """beta.json content is the same regardless of underlying storage."""
        result = read_bundled(store_dir, "beta.json")
        assert result == _BETA_CONTENT

    def test_content_is_valid_json(self, store_dir: Path) -> None:
        """Content returned by read_bundled is valid parseable JSON."""
        raw = read_bundled(store_dir, "alpha.json")
        parsed = json.loads(raw)
        assert parsed == {"hello": "world"}
