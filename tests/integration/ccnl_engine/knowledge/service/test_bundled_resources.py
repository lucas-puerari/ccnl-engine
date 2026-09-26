"""Unit tests for BundledResourceStore."""

from __future__ import annotations

import gzip
from typing import TYPE_CHECKING

from ccnl_engine.knowledge.service.bundled_resources import BundledResourceStore

if TYPE_CHECKING:
    from pathlib import Path


class TestListJson:
    """BundledResourceStore.list_json — file discovery."""

    def test_plain_json_files(self, tmp_path: Path) -> None:
        """Plain .json files are returned as-is."""
        (tmp_path / "a.json").write_text("{}", encoding="utf-8")
        (tmp_path / "b.json").write_text("{}", encoding="utf-8")
        store = BundledResourceStore(tmp_path)
        assert store.list_json() == ["a.json", "b.json"]

    def test_gz_files_normalised(self, tmp_path: Path) -> None:
        """.json.gz files are returned with the .gz stripped."""
        (tmp_path / "c.json.gz").write_bytes(
            gzip.compress(b"{}", compresslevel=1, mtime=0)
        )
        store = BundledResourceStore(tmp_path)
        assert store.list_json() == ["c.json"]

    def test_deduplicates_plain_and_gz(self, tmp_path: Path) -> None:
        """When both .json and .json.gz exist, the name appears once."""
        (tmp_path / "d.json").write_text("{}", encoding="utf-8")
        (tmp_path / "d.json.gz").write_bytes(
            gzip.compress(b"{}", compresslevel=1, mtime=0)
        )
        store = BundledResourceStore(tmp_path)
        assert store.list_json() == ["d.json"]

    def test_ignores_non_json(self, tmp_path: Path) -> None:
        """Non-JSON files (e.g. __init__.py) are excluded."""
        (tmp_path / "a.json").write_text("{}", encoding="utf-8")
        (tmp_path / "__init__.py").write_text("", encoding="utf-8")
        (tmp_path / "readme.txt").write_text("", encoding="utf-8")
        store = BundledResourceStore(tmp_path)
        assert store.list_json() == ["a.json"]

    def test_empty_directory(self, tmp_path: Path) -> None:
        """An empty directory returns an empty list."""
        store = BundledResourceStore(tmp_path)
        assert store.list_json() == []

    def test_sorted(self, tmp_path: Path) -> None:
        """Results are sorted alphabetically."""
        for name in ["z.json", "a.json", "m.json"]:
            (tmp_path / name).write_text("{}", encoding="utf-8")
        store = BundledResourceStore(tmp_path)
        assert store.list_json() == ["a.json", "m.json", "z.json"]


class TestReadJson:
    """BundledResourceStore.read_json — delegates to read_bundled."""

    def test_reads_plain_json(self, tmp_path: Path) -> None:
        """Reads plain .json files correctly."""
        content = '{"x": 1}'
        (tmp_path / "foo.json").write_text(content, encoding="utf-8")
        store = BundledResourceStore(tmp_path)
        assert store.read_json("foo.json") == content

    def test_reads_gz_json(self, tmp_path: Path) -> None:
        """Reads .json.gz files and decompresses them."""
        content = '{"x": 2}'
        (tmp_path / "bar.json.gz").write_bytes(
            gzip.compress(content.encode("utf-8"), compresslevel=9, mtime=0)
        )
        store = BundledResourceStore(tmp_path)
        assert store.read_json("bar.json") == content

    def test_gz_preferred_over_plain(self, tmp_path: Path) -> None:
        """When both exist, the .gz variant is used."""
        (tmp_path / "f.json").write_text("plain", encoding="utf-8")
        (tmp_path / "f.json.gz").write_bytes(
            gzip.compress(b"compressed", compresslevel=1, mtime=0)
        )
        store = BundledResourceStore(tmp_path)
        assert store.read_json("f.json") == "compressed"
