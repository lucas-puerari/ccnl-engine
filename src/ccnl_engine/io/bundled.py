"""Helper for reading bundled data files from the package."""

from __future__ import annotations

import gzip
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable


def read_bundled(pkg: Traversable, filename: str) -> str:
    """Read a bundled data file, preferring the compressed variant when present.

    In installed wheels the data files are stored as ``<filename>.gz`` to
    reduce package size. In editable installs (development) the plain
    ``<filename>`` is used as a fallback.

    The caller receives the decoded content regardless of which variant is
    found. If the ``.gz`` file exists but is corrupt, ``gzip.BadGzipFile``
    propagates to the caller. If neither file exists, ``FileNotFoundError``
    propagates from the inner ``read_bytes()`` / ``read_text()`` call.

    Args:
        pkg: A :class:`~importlib.resources.abc.Traversable` pointing to the
            package data directory (e.g. the result of
            ``importlib.resources.files("ccnl_engine.contracts.data")``).
        filename: The uncompressed filename to look up (e.g. ``"foo.json"``).
            The ``.gz`` variant is tried first; ``filename`` itself is the
            fallback.

    Returns:
        The file content decoded as UTF-8.
    """
    try:
        return gzip.decompress(pkg.joinpath(filename + ".gz").read_bytes()).decode(
            "utf-8"
        )
    except FileNotFoundError:
        return pkg.joinpath(filename).read_text(encoding="utf-8")
