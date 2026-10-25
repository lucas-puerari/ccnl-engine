"""Build ``knowledge/manifest.json``, the one index of the knowledge bundle.

Every JSON resource under ``src/ccnl_engine/knowledge`` is listed once, with
its stable identity, path, dataset, model, validity, ruleset and the name it
takes in the wheel.  The manifest is derived from the files: the path gives
the dataset, the year and the scope (``domain/dataset/year/scope.json``),
the ``ruleset`` block gives the identity and validity.

Usage::

    uv run python scripts/knowledge/manifest/build.py           # write
    uv run python scripts/knowledge/manifest/build.py --check   # fail on drift
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ccnl_engine.provenance.ruleset.models import source_hash

KNOWLEDGE_DIR = Path("src/ccnl_engine/knowledge")
MANIFEST_NAME = "manifest.json"
SCHEMA_VERSION = 1
#: Owner of a resource whose file names none.
DEFAULT_OWNER = "ccnl-engine maintainers"

#: Dataset -> (model the loader validates it with, has a year directory).
DATASETS: dict[str, tuple[str, bool]] = {
    "agreement": ("CCNL", False),
    "contribution": ("InpsRates", True),
    "sickness/indemnity": ("InpsSickPayRates", False),
    "absence/insured": ("InsuredAbsenceRates", False),
    "sector": ("YearRulesRaw", True),
    "family": ("FamilyDeductionRules", False),
    "tax_credit/somma_esente": ("SommaEsenteRules", False),
    "irpef/work_deduction": ("WorkDeductionRules", False),
    "variable_pay": ("VariablePayRules", False),
    "severance/revaluation": ("TfrRevaluationRules", False),
    "severance/settlement": ("TfrSettlementRules", False),
    "surtax/regional": ("RegionalSurtaxTable", False),
    "surtax/municipal": ("MunicipalSurtaxTable", False),
    "capability/registry": ("CapabilityCatalog", False),
    "limitation": ("ModelLimitation", False),
    "pay_item": ("PolicyRuleset", False),
}
#: Why a resource with no year and no ruleset validity has none.
NO_VALIDITY = {
    "limitation": "engine limitations follow the engine, not a period",
    "pay_item": "the pay item policy applies to every year the bundle holds",
    "sickness/indemnity": (
        "statutory rates change only by primary legislation; the ruleset "
        "block carries the source"
    ),
}
#: Why an engine-maintained resource carries no enclosing ruleset identity.
NO_RULESET = {
    "capability/registry": (
        "the registry describes engine capabilities for its year; each capability "
        "declares its own evidence"
    ),
    "limitation": (
        "engine limitations follow the engine and carry status, scope and "
        "remediation individually"
    ),
    "pay_item": (
        "the resource is a collection of policies with individual policy ids, "
        "versions, validity and legal bases"
    ),
}


def _dimensions(
    rest: tuple[str, ...], yearly: bool
) -> tuple[int | None, str | None] | None:
    """Return the year and the scope of the path parts after the dataset.

    Returns:
        ``(year, scope)``, or ``None`` when the parts do not fit the dataset.
    """
    if yearly:
        if len(rest) == 2 and rest[0].isdigit():
            return int(rest[0]), rest[1]
        return None
    if len(rest) != 1:
        return None
    return (int(rest[0]), None) if rest[0].isdigit() else (None, rest[0])


def _dataset(rel: Path) -> tuple[str, int | None, str | None]:
    """Return the dataset, the year and the scope of a resource path.

    Returns:
        ``(dataset, year, scope)``; a dimension the path lacks is ``None``.

    Raises:
        ValueError: When the path fits no dataset of :data:`DATASETS`.
    """
    parts = rel.with_suffix("").parts
    for dataset, (_, yearly) in DATASETS.items():
        head = tuple(dataset.split("/"))
        if parts[: len(head)] != head:
            continue
        dims = _dimensions(parts[len(head) :], yearly)
        if dims is not None:
            return dataset, *dims
    msg = f"{rel}: no dataset of the manifest holds this path"
    raise ValueError(msg)


def _object(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _entry(rel: Path, data: object) -> dict[str, Any]:
    """Return the manifest entry of the resource at ``rel``.

    Returns:
        The entry, its keys in a fixed order.

    Raises:
        ValueError: When a recorded ruleset hash does not match the resource.
    """
    dataset, year, scope = _dataset(rel)
    document = _object(data)
    ruleset = _object(document.get("ruleset"))
    computed_hash = source_hash(data)
    recorded_hash = ruleset.get("source_hash")
    if isinstance(recorded_hash, str) and recorded_hash != computed_hash:
        msg = f"{rel}: ruleset source_hash does not match the resource"
        raise ValueError(msg)
    owner = _object(document.get("verification")).get("owner") or DEFAULT_OWNER
    valid_from = ruleset.get("effective_from") or (
        f"{year}-01-01" if year is not None else None
    )
    valid_to = ruleset.get("effective_until") or (
        f"{year}-12-31" if year is not None else None
    )
    entry: dict[str, Any] = {
        "dataset_id": rel.with_suffix("").as_posix(),
        "path": rel.as_posix(),
        "dataset": dataset,
        "year": year,
        "scope": scope,
        "model": DATASETS[dataset][0],
        "schema_version": document.get("schema_version"),
        "valid_from": valid_from,
        "valid_to": valid_to,
        "ruleset_id": ruleset.get("id"),
        "ruleset_version": ruleset.get("version"),
        "source_hash": computed_hash,
        "source_type": ruleset.get("source_type"),
        "owner": owner,
        "wheel_resource": rel.as_posix() + ".gz",
    }
    if valid_from is None:
        entry["validity_note"] = NO_VALIDITY.get(
            dataset, "the resource states no validity"
        )
    if entry["schema_version"] is None:
        entry["schema_note"] = (
            f"validated by {entry['model']}; the resource format does not declare "
            "an explicit schema version"
        )
    if not ruleset:
        entry["ruleset_note"] = NO_RULESET.get(
            dataset, "the resource carries no enclosing ruleset identity"
        )
    if entry["source_type"] is None:
        entry["source_note"] = NO_RULESET.get(
            dataset, "the resource states no source type"
        )
    return entry


def build(root: Path = KNOWLEDGE_DIR) -> dict[str, Any]:
    """Return the manifest of every JSON resource under ``root``.

    Returns:
        The manifest, its resources sorted by path.
    """
    resources = [
        _entry(path.relative_to(root), json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(root.rglob("*.json"))
        if path.name != MANIFEST_NAME
    ]
    return {"schema_version": SCHEMA_VERSION, "resources": resources}


def render(manifest: dict[str, Any]) -> str:
    """Return the manifest as the text written to disk.

    Returns:
        Indented JSON with a trailing newline.
    """
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None, root: Path = KNOWLEDGE_DIR) -> int:
    """Write the manifest, or check it with ``--check``.

    Returns:
        ``0`` when written or up to date, ``1`` on drift.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail on drift")
    args = parser.parse_args(argv)
    target = root / MANIFEST_NAME
    text = render(build(root))
    if args.check:
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        if current != text:
            print(
                f"FAIL: {target} is out of date: run "
                "scripts/knowledge/manifest/build.py"
            )
            return 1
        print(f"OK: {target} lists {len(json.loads(text)['resources'])} resources.")
        return 0
    target.write_text(text, encoding="utf-8")
    print(f"Wrote {target} ({len(json.loads(text)['resources'])} resources).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
