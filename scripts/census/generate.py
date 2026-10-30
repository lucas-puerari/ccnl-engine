"""Seed the census of every CCNL from its open limitations and weak rules.

Each open limitation that concerns a CCNL (its own, or an engine one that
lists it) and each weak payable rule of its file becomes a ``seeded``
requirement row: the institute is the capability, the remediation is that
of the limitation, and the row links the limitation or the rule, so its
open state follows theirs.  The weak rules of the shared files (INPS, sector,
fiscal) go to ``census/common.json``.  A seeded row is never read from the
text: the completeness report keeps it open until a row of origin ``text``
replaces it.

The rows a census reads from the text are kept as they are; the seeded
rows are rebuilt on every run, so a closed limitation or a promoted rule
leaves the census.  Running it twice writes the same files.

Usage::

    uv run python scripts/census/generate.py          # write
    uv run python scripts/census/generate.py --check  # fail on drift
"""

from __future__ import annotations

import argparse
import hashlib
import json
import operator
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ccnl_engine.catalog.loaders import list_contracts, load_ccnl
from ccnl_engine.limitation.loaders import load_engine_limitations
from ccnl_engine.limitation.models import LimitationStatus, MonetaryImpact
from scripts.provenance.rules import PayableRule, inventory

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.limitation.models import ModelLimitation

ROOT = Path(__file__).resolve().parents[2]
CENSUS_DIR = ROOT / "src" / "ccnl_engine" / "knowledge" / "census"
COMMON = "common"
SCHEMA = 1
WEAK = frozenset({"assumed", "missing"})
_MAX_ID = 64

#: What closes a weak rule.
WEAK_REMEDIATION = (
    "Verify the value on its primary source and record the provenance; a "
    "derivation states its formula and inputs."
)


def limitation_name(limitation: ModelLimitation) -> str:
    """Return the name of a limitation within its CCNL.

    Returns:
        The variant of a CCNL limitation (``<ccnl id>/<variant>``), the id
        of an engine one.
    """
    return limitation.id.rsplit("/", 1)[-1]


def _variant(limitation: ModelLimitation) -> str:
    scope = limitation.applies_when
    if scope.contract_types == frozenset({"apprentice"}):
        return "apprentice"
    if scope.worker_categories:
        return "_".join(sorted(scope.worker_categories))
    return "all"


def limitation_row(limitation: ModelLimitation) -> dict[str, Any]:
    """Return the seeded row of an open limitation.

    Returns:
        The row, as the census file holds it.
    """
    unknown = limitation.monetary_impact is MonetaryImpact.UNKNOWN
    name = limitation_name(limitation)
    return {
        "id": name,
        "institute": limitation.capability,
        "variant": _variant(limitation),
        "discriminant": f"applies_when.trigger = {limitation.applies_when.trigger}",
        "rule": limitation.summary,
        "calculation": limitation.source,
        "state": "unverified" if unknown else "absent",
        "remediation": limitation.remediation,
        "origin": "seeded",
        "links": {"limitations": [limitation.id]},
    }


def rule_row_id(rule: PayableRule) -> str:
    """Return the census id of a weak rule: its path, snake cased.

    A path longer than the id allows keeps its start and a digest.

    Returns:
        A lower snake case id of at most 64 characters.
    """
    stem = (
        Path(rule.file).with_suffix("").name
        if rule.file.startswith("agreement/")
        else (Path(rule.file).with_suffix("").as_posix())
    )
    base = rule.path if rule.file.startswith("agreement/") else f"{stem}_{rule.path}"
    snake = re.sub(r"[^a-z0-9]+", "_", f"rule_{base}".lower()).strip("_")
    if len(snake) <= _MAX_ID:
        return snake
    digest = hashlib.sha256(snake.encode()).hexdigest()[:8]
    return f"{snake[: _MAX_ID - 9]}_{digest}"


def rule_row(rule: PayableRule) -> dict[str, Any]:
    """Return the seeded row of a weak payable rule.

    Returns:
        The row, as the census file holds it.
    """
    return {
        "id": rule_row_id(rule),
        "institute": rule.capabilities[0],
        "variant": "all",
        "rule": f"{rule.file}#{rule.path}",
        "calculation": ", ".join(rule.capabilities),
        "state": "absent" if rule.status == "missing" else "unverified",
        "remediation": WEAK_REMEDIATION,
        "origin": "seeded",
        "links": {"rules": [f"{rule.file}#{rule.path}"]},
    }


def _open(limitations: Iterable[ModelLimitation]) -> list[ModelLimitation]:
    return [lim for lim in limitations if lim.status is LimitationStatus.OPEN]


def seeded_rows(
    ccnl: CCNL, engine: Iterable[ModelLimitation], rules: Iterable[PayableRule]
) -> list[dict[str, Any]]:
    """Return the seeded rows of *ccnl*.

    Returns:
        One row per open limitation and per weak rule of the CCNL.
    """
    ccnl_id = ccnl.meta.ccnl_id
    shared = [lim for lim in _open(engine) if ccnl_id in lim.rulesets]
    file = f"agreement/{ccnl_id}.json"
    return [
        *(limitation_row(lim) for lim in (*_open(ccnl.limitations), *shared)),
        *(
            rule_row(rule)
            for rule in rules
            if rule.file == file and rule.status in WEAK
        ),
    ]


def merge(
    existing: dict[str, Any] | None, ccnl_id: str, seeded: list[dict[str, Any]]
) -> dict[str, Any]:
    """Return the census of *ccnl_id*: its text rows and the fresh seeded ones.

    A seeded row whose id a text row already takes is left out: the text
    row replaces it.

    Returns:
        The census document, rows sorted by id.

    Raises:
        ValueError: When two seeded rows share an id.
    """
    rows = existing.get("requirements", []) if existing else []
    kept = [row for row in rows if row.get("origin", "text") != "seeded"]
    taken = {row["id"] for row in kept}
    ids = [row["id"] for row in seeded]
    if len(set(ids)) != len(ids):
        msg = f"census {ccnl_id}: two seeded rows share an id"
        raise ValueError(msg)
    fresh = [row for row in seeded if row["id"] not in taken]
    return {
        "schema_version": SCHEMA,
        "ccnl_id": ccnl_id,
        "requirements": sorted([*kept, *fresh], key=operator.itemgetter("id")),
    }


def render(document: dict[str, Any]) -> str:
    """Return a census document as the text written to disk.

    Returns:
        Indented JSON with a trailing newline.
    """
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def _read(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text("utf-8")) if path.is_file() else None


def build(root: Path = CENSUS_DIR) -> dict[Path, str]:
    """Return the text of every census file, by path.

    Returns:
        One file per bundled CCNL and the common census.
    """
    rules = inventory()
    engine = load_engine_limitations()
    files: dict[Path, str] = {}
    for summary in list_contracts():
        ccnl = load_ccnl(summary.ccnl_id)
        path = root / f"{summary.ccnl_id}.json"
        seeded = seeded_rows(ccnl, engine, rules)
        files[path] = render(merge(_read(path), summary.ccnl_id, seeded))
    common = [
        rule_row(rule)
        for rule in rules
        if rule.status in WEAK and not rule.file.startswith("agreement/")
    ]
    path = root / f"{COMMON}.json"
    files[path] = render(merge(_read(path), COMMON, common))
    return files


def main(argv: list[str] | None = None, root: Path = CENSUS_DIR) -> int:
    """Write the census files, or check them with ``--check``.

    Returns:
        ``0`` when written or up to date, ``1`` on drift.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail on drift")
    args = parser.parse_args(argv)
    files = build(root)
    stale = [
        p
        for p, text in files.items()
        if not p.is_file() or p.read_text("utf-8") != text
    ]
    if args.check:
        for path in stale:
            print(f"FAIL: {path.name} is out of date: run scripts/census/generate.py")
        return 1 if stale else 0
    root.mkdir(parents=True, exist_ok=True)
    for path in stale:
        path.write_text(files[path], encoding="utf-8")
    print(f"Wrote {len(stale)} of {len(files)} census files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
