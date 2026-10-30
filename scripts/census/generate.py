"""Seed the census of every CCNL from its open limitations and weak rules.

Each open limitation that concerns a CCNL (its own, or an engine one that
lists it) and each weak payable rule of its file becomes a ``seeded``
requirement row: the institute is the capability, the work items come from
:data:`WORK`, and the row links the limitation or the rule, so its open
state follows theirs.  The weak rules of the shared files (INPS, sector,
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

#: Work items of the completion plan, by capability of the row.
WORK: dict[str, tuple[str, ...]] = {
    "base_salary": ("T02.01",),
    "seniority": ("T02.01",),
    "inps_employer": ("T04.01",),
    "inps_employee": ("T04.01",),
    "sickness": ("T03.02",),
    "overtime": ("T02.06",),
    "bilateral_funds": ("T05.01",),
    "contractual_funds": ("T05.01",),
    "assistance_contribution": ("T05.01",),
    "pension_fund_contribution": ("T05.04",),
    "leave": ("T02.10",),
    "territorial_supplement": ("T05.09",),
    "trattamento_integrativo": ("T06.01",),
    "una_tantum": ("T07.01",),
    "workplace_injury": ("T03.06",),
    "inail": ("T04.05",),
    "worker_category": ("T01.02",),
    "irpef": ("T06.01",),
    "welfare": ("T06.09",),
}
#: Work items of a variant more specific than its capability.
VARIANT_WORK: dict[str, tuple[str, ...]] = {
    "apprentice_seniority": ("T02.03",),
    "apprentice_inps_rates_unsourced": ("T04.02",),
    "apprenticeship_pct_undeclared_components": ("T02.03",),
    "sickness_inps_daily_base": ("T03.01",),
    "sickness_cumulation_window": ("T03.03",),
    "sickness_net_basis": ("T03.05",),
    "oncological_comporto": ("T03.03",),
    "provisional_ruleset": ("T00.03", "T09.03"),
    "provisional_inps_ruleset": ("T00.03", "T09.03"),
    "tfr_compensation_apprentice_guarantee_fund": ("T08.05",),
    "inps_minimum_base_exempt_category": ("T04.03",),
    "cigo_rate_by_activity": ("T04.10",),
    "fpls_rates_approximated": ("T04.10",),
    "tourism_special_supplement": ("T06.09",),
    "ordinary_hours_premiums": ("T02.07",),
    "contractual_fund_partial": ("T05.06",),
    "health_and_bilateral_funds": ("T05.01",),
    "una_tantum_2025_2026": ("T07.01",),
    "tranches_2027_2028": ("T07.07",),
    "tranches_from_2027": ("T07.07",),
    "part_time_supplementary_rate": ("T02.06",),
    "rol_schedule_absorption": ("T02.10",),
    "permit_deadline_payout": ("T02.10",),
    "shared_rules_unchecked": ("T09.04",),
    "long_week_divisors": ("T02.04",),
    "long_week_divisor_195": ("T02.04",),
    "approximate_hourly_divisor": ("T02.04",),
    "teacher_hourly_divisor": ("T02.04",),
    "err_unsourced": ("T09.03",),
}
#: Work items of every weak rule: resolve it on the primary source.
WEAK_WORK = ("T09.01", "T09.03")
#: The closing check of each area of the plan: the verification a row of
#: the area is planned for once its work is done.
VERIFICATION: dict[str, str] = {
    "T00": "T00.12",
    "T01": "T01.14",
    "T02": "T02.13",
    "T03": "T03.11",
    "T04": "T04.12",
    "T05": "T05.10",
    "T06": "T06.11",
    "T07": "T07.08",
    "T08": "T08.09",
    "T09": "T09.11",
}


def verification(work: tuple[str, ...]) -> list[str]:
    """Return the planned verification of the work items *work*.

    Returns:
        The closing check of the area of each item, in order, once each.
    """
    return list(dict.fromkeys(VERIFICATION[item[:3]] for item in work))


def work_items(capability: str, name: str) -> tuple[str, ...]:
    """Return the work items that close a limitation.

    Its name decides when :data:`VARIANT_WORK` lists it, its capability
    otherwise; T00.07 reconciles any other with the census.

    Returns:
        The work items, never empty.
    """
    return VARIANT_WORK.get(name) or WORK.get(capability) or ("T00.07",)


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
        "work": list(work := work_items(limitation.capability, name)),
        "verification": verification(work),
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
        "work": list(WEAK_WORK),
        "verification": verification(WEAK_WORK),
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
