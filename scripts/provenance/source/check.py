"""Check that each source of the bundle is still reachable and unchanged.

Every source object of the knowledge bundle that carries a ``url`` and a
``sha256`` names the document a value was read from.  This script fetches
each URL once and compares the SHA-256 of what it serves with the hash on
record.  It never writes the bundle nor stores what it downloads: a changed
document needs a review, not a silent new hash.

A document that changed is not always an error (an HTML page moves, a
publisher re-encodes a PDF), and a site can refuse automated clients, so
the report never fails: the weekly job publishes it for the maintainer.

Run with::

    uv run python scripts/provenance/source/check.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.provenance.rules import KNOWLEDGE_DIR

#: Seconds before a request gives up.
TIMEOUT: Final = 60
#: Identifies the check to the publishers.
USER_AGENT: Final = "ccnl-engine-source-check/1.0"

#: Returns the SHA-256 of what a URL serves; raises ``OSError`` when it fails.
Fetch = Callable[[str], str]


@dataclass(frozen=True)
class Result:
    """The outcome of one URL."""

    url: str
    expected: frozenset[str]
    files: frozenset[str]
    actual: str | None = None
    error: str | None = None

    @property
    def status(self) -> str:
        """``unreachable``, ``changed`` or ``ok``."""
        if self.error is not None:
            return "unreachable"
        return "ok" if self.actual in self.expected else "changed"


def _objects(value: object) -> Iterator[dict[str, object]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _objects(child)


def sources(root: Path = KNOWLEDGE_DIR) -> dict[str, tuple[set[str], set[str]]]:
    """Return each source URL with the hashes on record and the files citing it.

    Returns:
        ``{url: (hashes, files)}``, in URL order.
    """
    found: dict[str, tuple[set[str], set[str]]] = {}
    for path in sorted(root.rglob("*.json")):
        file = path.relative_to(root).as_posix()
        for obj in _objects(json.loads(path.read_text(encoding="utf-8"))):
            url, sha = obj.get("url"), obj.get("sha256")
            if isinstance(url, str) and isinstance(sha, str):
                hashes, files = found.setdefault(url, (set(), set()))
                hashes.add(sha)
                files.add(file)
    return dict(sorted(found.items()))


def fetch(url: str) -> str:
    """Download ``url`` and return the SHA-256 of its body.

    Returns:
        The hex digest.

    Raises:
        OSError: If the URL is not http(s) or the request fails.
    """
    if not url.startswith(("https://", "http://")):
        msg = f"not an http(s) URL: {url}"
        raise OSError(msg)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})  # noqa: S310
    digest = hashlib.sha256()
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
        for chunk in iter(lambda: response.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check(url: str, hashes: set[str], files: set[str], get: Fetch) -> Result:
    expected, cited = frozenset(hashes), frozenset(files)
    try:
        return Result(url, expected, cited, actual=get(url))
    except OSError as error:
        return Result(url, expected, cited, error=str(error) or type(error).__name__)


def check(
    root: Path = KNOWLEDGE_DIR, get: Fetch = fetch, workers: int = 8
) -> list[Result]:
    """Fetch every source of the bundle and compare its hash.

    Returns:
        One result per URL, in URL order.
    """
    found = sources(root)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(
            pool.map(
                lambda item: _check(item[0], item[1][0], item[1][1], get),
                found.items(),
            )
        )


def render(results: list[Result]) -> str:
    """Render the results as Markdown: counts, then each URL not ``ok``.

    Returns:
        The report.
    """
    counts = {
        s: sum(r.status == s for r in results) for s in ("ok", "changed", "unreachable")
    }
    lines = [
        "## Sources",
        "",
        (
            f"{len(results)} URLs: {counts['ok']} ok, {counts['changed']} changed, "
            f"{counts['unreachable']} unreachable."
        ),
    ]
    bad = [r for r in results if r.status != "ok"]
    if bad:
        lines += ["", "| Status | URL | Detail | Cited by |", "|---|---|---|---|"]
        lines += [
            f"| {r.status} | {r.url} | {r.error or r.actual} "
            f"| {', '.join(f'`{f}`' for f in sorted(r.files))} |"
            for r in bad
        ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Print the report.

    Returns:
        Always 0: the report informs the maintainer, it gates nothing.
    """
    parser = argparse.ArgumentParser(description="Check the sources of the bundle.")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args(argv)
    print(render(check(workers=args.workers)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
