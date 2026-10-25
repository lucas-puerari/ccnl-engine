"""Readers of the knowledge bundle: the manifest and the resources it lists.

``knowledge/manifest.json`` lists every JSON resource of the bundle once,
with its path relative to ``ccnl_engine/knowledge``, its dataset, year and
scope.  The loaders find a resource here, never by globbing directories, so
a file the manifest does not list is not read, and a listed one that is
missing fails loudly.  In a wheel each resource is stored compressed under
the same path with ``.gz``
(:func:`~ccnl_engine.bundle.loaders.read_bundled`).
"""

from __future__ import annotations

import functools
import gzip
import hashlib
import importlib.resources
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.bundle.facade import SERIES
from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.provenance.ruleset.models import source_hash

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable


__all__ = [
    "MANIFEST",
    "Resource",
    "bundle_version",
    "read_resource",
    "resource_dir",
    "resources",
]


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
            ``importlib.resources.files("ccnl_engine.knowledge")`` joined to
            the directory of a manifest resource).
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


#: Name of the manifest, at the root of the knowledge package.
MANIFEST = "manifest.json"


@dataclass(frozen=True)
class Resource:
    """One resource the manifest lists.

    Attributes:
        path: Path relative to ``ccnl_engine/knowledge``.
        dataset: Dataset of the resource, e.g. ``sector``.
        year: Year of the resource, ``None`` when it has none.
        scope: Last dimension of the path (sector, slug, ...), ``None`` when
            the year is the last one.
        source_hash: Digest of the resource the manifest records.
    """

    path: str
    dataset: str
    year: int | None
    scope: str | None
    source_hash: str = ""

    @property
    def name(self) -> str:
        """File name of the resource."""
        return self.path.rsplit("/", 1)[-1]


def _root() -> Traversable:
    return importlib.resources.files("ccnl_engine.knowledge")


@functools.cache
def _manifest() -> dict[str, Resource]:
    """Return the resources of the manifest, keyed by path.

    Returns:
        Every resource of the bundle.
    """
    raw = json.loads(read_bundled(_root(), MANIFEST))
    return {
        entry["path"]: Resource(
            entry["path"],
            entry["dataset"],
            entry["year"],
            entry["scope"],
            entry["source_hash"],
        )
        for entry in raw["resources"]
    }


@functools.cache
def bundle_version() -> str:
    """Return the version of the bundled data: its series and manifest digest.

    The manifest records the content hash of every resource, so any change
    to a resource changes the digest, and a stale manifest fails CI.

    Returns:
        ``<series>+<first 12 hex digits of the manifest digest>``.
    """
    raw = json.loads(read_bundled(_root(), MANIFEST))
    canonical = json.dumps(raw["resources"], sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"{SERIES}+{digest[:12]}"


def resources(dataset: str) -> tuple[Resource, ...]:
    """Return the resources of ``dataset``, in path order.

    Returns:
        The resources the manifest lists for the dataset.
    """
    return tuple(r for path, r in sorted(_manifest().items()) if r.dataset == dataset)


def resource_dir(path: str) -> Traversable:
    """Return the directory that holds the resource at ``path``.

    Every resource sits in a dataset directory, so the path has one.

    Returns:
        The traversable directory, inside the package.
    """
    return _root().joinpath(*path.split("/")[:-1])


def read_resource(path: str) -> str:
    """Return the text of the resource at ``path``.

    Returns:
        The JSON text, from the plain or the compressed file.

    Raises:
        FileNotFoundError: When the manifest does not list ``path``.
        DataIntegrityError: When the manifest lists ``path`` and the
            resource is missing, unreadable, not JSON, or not the content
            whose hash the manifest records.
    """
    resource = _manifest().get(path)
    if resource is None:
        msg = f"the knowledge manifest lists no resource {path!r}"
        raise FileNotFoundError(msg)
    try:
        text = read_bundled(resource_dir(path), resource.name)
    except FileNotFoundError as exc:
        msg = f"{path}: the manifest lists it but the bundle does not hold it"
        raise DataIntegrityError(msg, remediation=_REINSTALL) from exc
    except (OSError, EOFError, UnicodeDecodeError) as exc:
        msg = f"{path}: the bundled resource cannot be read: {exc}"
        raise DataIntegrityError(msg, remediation=_REINSTALL) from exc
    _verify(resource, text)
    return text


#: How to recover a damaged bundle.
_REINSTALL = "reinstall ccnl-engine: the bundled knowledge is damaged"


#: Resources whose content matched the manifest hash in this process.
_VERIFIED: set[tuple[str, str]] = set()


def _verify(resource: Resource, text: str) -> None:
    """Check ``text`` against the hash the manifest records, once per resource.

    Raises:
        DataIntegrityError: When the text is not JSON or its hash differs.
    """
    key = (resource.path, resource.source_hash)
    if key in _VERIFIED:
        return
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        msg = f"{resource.path}: the bundled resource is not valid JSON: {exc}"
        raise DataIntegrityError(msg, remediation=_REINSTALL) from exc
    if source_hash(payload) != resource.source_hash:
        msg = f"{resource.path}: the content does not match the manifest hash"
        raise DataIntegrityError(msg, remediation=_REINSTALL)
    _VERIFIED.add(key)
