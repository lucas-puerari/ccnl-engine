"""Unit tests for ccnl_engine.io.bundled.read_bundled.

Covers three branches:
  1. Compressed ``.gz`` variant found and decompressed successfully.
  2. No ``.gz`` variant; falls back to reading the plain file.
  3. Corrupt ``.gz`` file propagates an error without silently falling back.
"""

from __future__ import annotations

import gzip
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.io.bundled import read_bundled

if TYPE_CHECKING:
    from pathlib import Path


class TestReadBundled:
    """Tests for read_bundled()."""

    def test_reads_gz_when_present(self, tmp_path: Path) -> None:
        """Decompresses and returns the content of a valid .gz file."""
        content = '{"hello": "world"}'
        (tmp_path / "data.json.gz").write_bytes(
            gzip.compress(content.encode("utf-8"), compresslevel=9, mtime=0)
        )
        result = read_bundled(tmp_path, "data.json")
        assert result == content

    def test_falls_back_to_plain_json(self, tmp_path: Path) -> None:
        """Returns the plain file content when no .gz variant exists."""
        content = '{"key": 42}'
        (tmp_path / "data.json").write_text(content, encoding="utf-8")
        result = read_bundled(tmp_path, "data.json")
        assert result == content

    def test_corrupt_gz_raises(self, tmp_path: Path) -> None:
        """A corrupt .gz file propagates gzip.BadGzipFile, not a silent fallback."""
        (tmp_path / "data.json.gz").write_bytes(b"this-is-not-gzip")
        with pytest.raises(gzip.BadGzipFile):
            read_bundled(tmp_path, "data.json")
