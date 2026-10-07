"""Evidence requirements and the shrink-only evidence ratchet of the bundle.

Two checks back the two gates of :mod:`scripts.ci.check_provenance`:

- :func:`schema_errors`: the fields a record must carry for the status or
  readiness it claims.  A ``verified`` payable rule names its reviewer
  (``extraction.verified_by``, ``extraction.verified_at``), its exact
  location (``location.page`` or ``location.section``) and the sha256 of
  the cited document (``location.source_document.sha256``).  A
  ``production`` CCNL names its owner, its reviewer, the date of the last
  review and the date the next one is due, after the last, with
  ``confidence`` ``verified``.  A CCNL ruleset id is ``ccnl/<ccnl_id>``.
  Labels that outrun their evidence, an estimated or uncited rule labelled
  ``derived`` and a ``reviewed`` CCNL with weak rules, are checked by
  :mod:`scripts.ci.provenance_labels` and have no baseline.
- :func:`compare`: the evidence ratchet.  The weak evidence of the bundle,
  every ``assumed`` or ``missing`` payable rule and every open model
  limitation, is listed in ``provenance_baseline.json``.  A weak entry
  the baseline does not list, or a rule weaker than its baseline status,
  is growth and fails.  A baseline entry that no longer holds is stale
  and fails too, so the baseline only shrinks.  Counts per capability
  and per CCNL follow from the entries and so never grow either.

Promoting a rule to ``verified`` stays a human task: nothing here changes a
status.  The module reads raw JSON with the standard library only.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts.ci import payable_rules

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from scripts.ci.payable_rules import PayableRule

BASELINE: Final = Path(__file__).with_name("provenance_baseline.json")
WEAK: Final = ("assumed", "missing")
ENGINE_LIMITATIONS: Final = "limitations/data/engine.json"
_RANK: Final = {status: rank for rank, status in enumerate(payable_rules.STATUSES)}
_SHA256: Final = re.compile(r"^[0-9a-f]{64}$")
_PRODUCTION_FIELDS: Final = ("owner", "human_reviewed_by", "last_reviewed")

type Json = dict[str, object]


@dataclass(frozen=True)
class Snapshot:
    """The weak evidence of the bundle, as the baseline stores it.

    Attributes:
        weak_rules: Data file to rule path to ``assumed`` or ``missing``.
        open_limitations: Data file to the ids of its open limitations.
    """

    weak_rules: Mapping[str, Mapping[str, str]]
    open_limitations: Mapping[str, tuple[str, ...]]

    def to_json(self) -> Json:
        """Return the snapshot as a JSON object with sorted keys.

        Returns:
            The baseline document.
        """
        return {
            "weak_rules": {
                file: dict(sorted(rules.items()))
                for file, rules in sorted(self.weak_rules.items())
            },
            "open_limitations": {
                file: sorted(ids) for file, ids in sorted(self.open_limitations.items())
            },
        }

    @classmethod
    def from_json(cls, data: object) -> Snapshot:
        """Build a snapshot from a decoded baseline document.

        Returns:
            The snapshot.

        Raises:
            ValueError: When a weak rule holds a status other than
                ``assumed`` or ``missing``.
        """
        document = _mapping(data, "baseline")
        weak: dict[str, dict[str, str]] = {}
        rules = _mapping(document.get("weak_rules"), "weak_rules")
        for file, paths in rules.items():
            entries = _mapping(paths, f"weak_rules[{file}]")
            if any(status not in WEAK for status in entries.values()):
                msg = f"weak_rules[{file}] holds a status other than {WEAK}"
                raise ValueError(msg)
            weak[file] = {path: str(status) for path, status in entries.items()}
        limitations = _mapping(document.get("open_limitations"), "open_limitations")
        open_ids = {
            file: _strings(ids, f"open_limitations[{file}]")
            for file, ids in limitations.items()
        }
        return cls(weak, open_ids)


def _mapping(value: object, name: str) -> Mapping[str, object]:
    """Return ``value`` as a JSON object.

    Returns:
        ``value`` itself.

    Raises:
        TypeError: When ``value`` is not a JSON object.
    """
    if not isinstance(value, dict):
        msg = f"{name} must be a JSON object"
        raise TypeError(msg)
    return value


def _strings(value: object, name: str) -> tuple[str, ...]:
    """Return ``value`` as a tuple of strings.

    Returns:
        The strings, in list order.

    Raises:
        TypeError: When ``value`` is not a list of strings.
    """
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        msg = f"{name} must be a list of strings"
        raise TypeError(msg)
    return tuple(value)


def _ccnl_files(root: Path) -> Iterator[tuple[str, Json]]:
    """Yield each CCNL data file under ``root`` with its decoded content.

    Yields:
        ``(file, data)``, file relative to ``root``, in file-name order.
    """
    for path in sorted((root / "ccnl" / "data").glob("*.json")):
        yield path.relative_to(root).as_posix(), json.loads(path.read_text("utf-8"))


def _as_dict(value: object) -> Json:
    return value if isinstance(value, dict) else {}


def _open_ccnl_limitations(data: Json) -> tuple[str, ...]:
    """Return the ids of the open limitations the notes of a CCNL declare.

    A note declares a limitation when it has a ``limitation`` object, a
    ``capability`` and a ``monetary_impact``, as the CCNL model reads it.

    Returns:
        ``<ccnl_id>/<variant>`` ids, in note order.
    """
    ccnl_id = _as_dict(data.get("meta")).get("ccnl_id")
    notes = _as_dict(data.get("coverage")).get("notes")
    found: list[str] = []
    for note in notes if isinstance(notes, list) else []:
        note_dict = _as_dict(note)
        spec = _as_dict(note_dict.get("limitation"))
        declared = (
            bool(spec)
            and note_dict.get("capability") is not None
            and note_dict.get("monetary_impact") is not None
        )
        if declared and spec.get("status", "open") == "open":
            found.append(f"{ccnl_id}/{spec.get('variant')}")
    return tuple(found)


def open_limitations(root: Path) -> dict[str, tuple[str, ...]]:
    """Return the open model limitations of the bundle by data file.

    Returns:
        Data file to the ids of its open limitations; files without one
        are left out.
    """
    found: dict[str, tuple[str, ...]] = {}
    engine = json.loads((root / ENGINE_LIMITATIONS).read_text("utf-8"))
    entries = _as_dict(engine).get("limitations")
    ids = tuple(
        str(_as_dict(entry).get("id"))
        for entry in (entries if isinstance(entries, list) else [])
        if _as_dict(entry).get("status", "open") == "open"
    )
    if ids:
        found[ENGINE_LIMITATIONS] = ids
    for file, data in _ccnl_files(root):
        if ccnl_ids := _open_ccnl_limitations(data):
            found[file] = ccnl_ids
    return found


def weak_rules(rules: tuple[PayableRule, ...]) -> dict[str, dict[str, str]]:
    """Return the ``assumed`` and ``missing`` rules by data file.

    Returns:
        Data file to rule path to status; files without one are left out.
    """
    found: dict[str, dict[str, str]] = {}
    for rule in rules:
        if rule.status in WEAK:
            found.setdefault(rule.file, {})[rule.path] = str(rule.status)
    return found


def snapshot(
    root: Path = payable_rules.KNOWLEDGE_DIR,
    rules: tuple[PayableRule, ...] | None = None,
) -> Snapshot:
    """Return the weak evidence of the knowledge data under ``root``.

    Args:
        root: Knowledge directory to scan.
        rules: Payable rules of ``root``, inventoried when ``None``.

    Returns:
        The snapshot to compare with the baseline.
    """
    found = payable_rules.inventory(root) if rules is None else rules
    return Snapshot(weak_rules(found), open_limitations(root))


@dataclass(frozen=True)
class Ratchet:
    """Difference between the bundle and the baseline.

    Attributes:
        grown: Weak entries the baseline does not allow: new entries and
            rules weaker than their baseline status.
        stale: Baseline entries that no longer hold and must be removed.
    """

    grown: tuple[str, ...]
    stale: tuple[str, ...]

    @property
    def ok(self) -> bool:
        """Whether the bundle matches the baseline exactly."""
        return not self.grown and not self.stale


def _compare_rules(
    current: Mapping[str, Mapping[str, str]],
    baseline: Mapping[str, Mapping[str, str]],
) -> tuple[list[str], list[str]]:
    grown: list[str] = []
    stale: list[str] = []
    for file, rules in sorted(current.items()):
        allowed = baseline.get(file, {})
        for path, status in sorted(rules.items()):
            before = allowed.get(path)
            if before is None:
                grown.append(f"{file}: {path}: new {status} rule")
            elif _RANK[status] > _RANK[before]:
                grown.append(f"{file}: {path}: {before} became {status}")
            elif status != before:
                stale.append(f"{file}: {path}: {before} is now {status}")
    for file, rules in sorted(baseline.items()):
        stale.extend(
            f"{file}: {path}: no longer {status}"
            for path, status in sorted(rules.items())
            if path not in current.get(file, {})
        )
    return grown, stale


def _compare_ids(
    label: str,
    current: Mapping[str, tuple[str, ...]],
    baseline: Mapping[str, tuple[str, ...]],
) -> tuple[list[str], list[str]]:
    now = {(file, i) for file, ids in current.items() for i in ids}
    before = {(file, i) for file, ids in baseline.items() for i in ids}
    grown = [f"{file}: new {label} {i}" for file, i in sorted(now - before)]
    stale = [f"{file}: {label} {i} no longer open" for file, i in sorted(before - now)]
    return grown, stale


def compare(current: Snapshot, baseline: Snapshot) -> Ratchet:
    """Compare the weak evidence of the bundle with the baseline.

    Returns:
        The growth and the stale entries, each sorted by file.
    """
    rules = _compare_rules(current.weak_rules, baseline.weak_rules)
    limitations = _compare_ids(
        "open limitation", current.open_limitations, baseline.open_limitations
    )
    return Ratchet(
        grown=(*rules[0], *limitations[0]),
        stale=(*rules[1], *limitations[1]),
    )


def load_baseline(path: Path = BASELINE) -> Snapshot:
    """Read the baseline at ``path``.

    Returns:
        The stored snapshot.

    Raises:
        ValueError: When the file is not valid JSON.
    """
    try:
        data = json.loads(path.read_text("utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"{path}: invalid JSON: {exc}"
        raise ValueError(msg) from exc
    return Snapshot.from_json(data)


def write_baseline(current: Snapshot, path: Path = BASELINE) -> None:
    """Write ``current`` to ``path`` as the new baseline."""
    text = json.dumps(current.to_json(), indent=2, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8")


def _verified_errors(rule: PayableRule) -> Iterator[str]:
    """Yield the evidence a ``verified`` rule lacks.

    Yields:
        One reason per missing field.
    """
    record = rule.record or {}
    extraction = _as_dict(record.get("extraction"))
    for key in ("verified_by", "verified_at"):
        if not extraction.get(key):
            yield f"verified without extraction.{key}"
    location = _as_dict(record.get("location"))
    if not (location.get("page") or location.get("section")):
        yield "verified without an exact location (location.page or section)"
    digest = _as_dict(location.get("source_document")).get("sha256")
    if not (isinstance(digest, str) and _SHA256.match(digest)):
        yield "verified without location.source_document.sha256"


def _date(value: object) -> date | None:
    try:
        return date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def _production_errors(verification: Json) -> Iterator[str]:
    """Yield the evidence a ``production`` CCNL lacks.

    Yields:
        One reason per missing or inconsistent field.
    """
    for key in _PRODUCTION_FIELDS:
        if not verification.get(key):
            yield f"production without verification.{key}"
    if verification.get("confidence") != "verified":
        yield "production without confidence 'verified'"
    last = _date(verification.get("last_reviewed"))
    due = _date(verification.get("review_due"))
    if due is None:
        yield "production without a valid verification.review_due"
    elif last is not None and due <= last:
        yield "verification.review_due is not after last_reviewed"


def _ccnl_errors(file: str, data: Json) -> Iterator[str]:
    ruleset_id = _as_dict(data.get("ruleset")).get("id")
    expected = f"ccnl/{_as_dict(data.get('meta')).get('ccnl_id')}"
    if ruleset_id is not None and ruleset_id != expected:
        yield f"{file}: ruleset.id {ruleset_id!r} is not {expected!r}"
    verification = _as_dict(data.get("verification"))
    if verification.get("readiness") == "production":
        yield from (f"{file}: {e}" for e in _production_errors(verification))


def schema_errors(
    rules: tuple[PayableRule, ...], root: Path = payable_rules.KNOWLEDGE_DIR
) -> list[str]:
    """Return the evidence the claimed statuses and readiness lack.

    Args:
        rules: Payable rules of ``root``.
        root: Knowledge directory to scan.

    Returns:
        ``"<file>: <path>: <reason>"`` messages; empty when every record
        carries the fields its status or readiness requires.
    """
    errors = [
        f"{rule.file}: {rule.path}: {reason}"
        for rule in rules
        if rule.status == "verified"
        for reason in _verified_errors(rule)
    ]
    for file, data in _ccnl_files(root):
        errors.extend(_ccnl_errors(file, data))
    return errors


def report_lines(rules: tuple[PayableRule, ...], top: int = 10) -> list[str]:
    """Return the weak-rule report per capability and per CCNL.

    Args:
        rules: Payable rules to count.
        top: Number of CCNL files to list, weakest first.

    Returns:
        Printable lines: ``verified / derived / assumed / missing`` per
        capability, then the CCNL files with the most weak rules.
    """
    lines = ["Rules per capability (verified / derived / assumed / missing):"]
    by_capability = payable_rules.count_by_capability(rules)
    for capability, counts in sorted(by_capability.items()):
        lines.append(f"  {capability}: {_counts(counts)}")
    ccnl = {
        file: counts
        for file, counts in payable_rules.count_by_file(rules).items()
        if file.startswith("ccnl/") and any(counts[s] for s in WEAK)
    }
    ranked = sorted(ccnl.items(), key=lambda item: (-_weak(item[1]), item[0]))
    lines.append(f"CCNL files with weak rules: {len(ranked)}; top {top}:")
    lines.extend(f"  {file}: {_counts(counts)}" for file, counts in ranked[:top])
    return lines


def _counts(counts: Mapping[str, int]) -> str:
    return " / ".join(str(counts.get(s, 0)) for s in payable_rules.STATUSES)


def _weak(counts: Mapping[str, int]) -> int:
    return sum(counts.get(s, 0) for s in WEAK)
