"""Rules of the reference cases and the evidence each ``production`` CCNL needs.

A reference case in ``tests/knowledge/ccnl_engine/period/reference_case/``
pins amounts of one run of the engine to a source.  It declares how far its
expected values can be trusted in a top-level ``verification`` field:

- ``source_linked``: the case cites the primary source it models (a signed
  table, a payslip line read as a table value).  It checks the transcription
  of the bundle, not the output of the engine.
- ``verified``: its expected values come from an output the engine did not
  produce, an observed payslip or an official worked example.  The case
  names it in ``source``: its ``kind`` (:data:`SOURCE_KINDS`), an immutable
  reference (a ``sha256`` of the document or the ``path`` of a file
  versioned in the repository), who checked it (``verified_by``) and when
  (``verified_at``), and how the expected values were produced without the
  engine (``independence``).  It also states the ``tolerance`` its amounts
  are compared with.

Every case names the ``axes`` it validates (:data:`AXES`); each expected
value belongs to one of them (:data:`AXIS_OF`).  :func:`index` maps each
CCNL to its cases, and :func:`production_errors` binds the readiness tier
to its evidence in the gate, not by convention:

- a ``production`` CCNL needs at least one valid case;
- it needs a ``verified`` one too, unless :data:`BASELINE` lists it: the
  CCNLs promoted before the rule.  The list only shrinks: an entry that
  gained a ``verified`` case or left ``production`` is stale and fails, so
  no new promotion goes without an independent output.  An entry whose CCNL
  file is not in the knowledge directory scanned is ignored: it allows
  nothing.

The module reads raw JSON with the standard library only.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts.provenance.evidence.check import readiness_by_ccnl

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

__all__ = [
    "AXES",
    "AXIS_OF",
    "BASELINE",
    "CASES_DIR",
    "SOURCE_KINDS",
    "STATUSES",
    "CaseEvidence",
    "count_by_status",
    "index",
    "load_case",
    "production_errors",
    "verification_errors",
]

REPO_ROOT: Final = Path(__file__).resolve().parents[3]
CASES_DIR: Final = REPO_ROOT / "tests/knowledge/ccnl_engine/period/reference_case"
#: ``production`` CCNLs allowed without a ``verified`` case, shrink only.
BASELINE: Final = Path(__file__).with_name("baseline.json")

STATUSES: Final = ("verified", "source_linked")
#: Outputs the engine did not produce, the only sources of a ``verified`` case.
SOURCE_KINDS: Final = ("observed_payslip", "official_worked_example")
#: Outputs of a run a case can validate.
AXES: Final = (
    "base_salary",
    "gross",
    "contributions",
    "employer_cost",
    "tax",
    "net",
    "tfr",
)
#: Axis of each expected value a case can pin.
AXIS_OF: Final[Mapping[str, str]] = {
    "base_salary": "base_salary",
    "hourly_percentages": "base_salary",
    "fixed_allowances": "gross",
    "period_gross": "gross",
}
_SHA256: Final = re.compile(r"^[0-9a-f]{64}$")
_AMOUNT: Final = re.compile(r"^\d+(\.\d+)?$")
#: Fields a ``verified`` source states, besides its kind and reference.
_VERIFIED_FIELDS: Final = ("verified_by", "independence")


@dataclass(frozen=True)
class CaseEvidence:
    """One reference case as evidence of a CCNL.

    Attributes:
        file: File name of the case.
        verification: Its verification status.
        axes: The outputs it validates.
    """

    file: str
    verification: str
    axes: tuple[str, ...]

    def to_json(self) -> dict[str, object]:
        """Return the evidence as a JSON object.

        Returns:
            The file, status and axes.
        """
        return {
            "file": self.file,
            "verification": self.verification,
            "axes": list(self.axes),
        }


def load_case(path: Path) -> dict[str, object]:
    """Read one reference case JSON file.

    Returns:
        The decoded JSON object.

    Raises:
        TypeError: If the file does not contain a JSON object.
    """
    data: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"{path.name}: reference case must be a JSON object"
        raise TypeError(msg)
    return data


def verification_errors(case: Mapping[str, object]) -> list[str]:
    """Return every rule the case violates.

    Returns:
        Human-readable error messages; empty when the case is valid.
    """
    status = case.get("verification")
    if status is None:
        return ["missing 'verification' field"]
    if status not in STATUSES:
        return [f"unknown verification {status!r}; allowed: {list(STATUSES)}"]
    source = case.get("source")
    if source is not None and not isinstance(source, dict):
        return [f"'source' must be an object, got {type(source).__name__}"]
    if not source:
        return [f"verification {status!r} requires a non-empty 'source' object"]
    errors = list(_axes_errors(case))
    if status == "verified":
        errors.extend(_verified_errors(source, case.get("tolerance")))
    return errors


def count_by_status(cases: list[dict[str, object]]) -> dict[str, int]:
    """Count cases per verification status.

    Returns:
        A mapping with one entry per known status, in canonical order.
    """
    counts = Counter(case.get("verification") for case in cases)
    return {status: counts[status] for status in STATUSES}


def _axes_errors(case: Mapping[str, object]) -> Iterator[str]:
    """Yield what is wrong with the axes a case declares.

    Yields:
        One reason per unknown axis, per expected value of no axis or of an
        axis the case does not declare.
    """
    axes = case.get("axes")
    if not isinstance(axes, list) or not axes:
        yield "'axes' must be a non-empty list of " + ", ".join(AXES)
        return
    yield from (f"unknown axis {axis!r}" for axis in axes if axis not in AXES)
    expected = case.get("expected")
    for key in expected if isinstance(expected, dict) else {}:
        axis = AXIS_OF.get(key)
        if axis is None:
            yield f"expected value {key!r} belongs to no axis"
        elif axis not in axes:
            yield f"expected value {key!r} needs the axis {axis!r} in 'axes'"


def _verified_errors(source: Mapping[str, object], tolerance: object) -> Iterator[str]:
    """Yield the evidence a ``verified`` case lacks.

    Yields:
        One reason per missing or invalid field.
    """
    if source.get("kind") not in SOURCE_KINDS:
        yield f"verified requires source.kind in {list(SOURCE_KINDS)}"
    if not _immutable(source):
        yield "verified requires source.sha256 or the source.path of a versioned file"
    for key in _VERIFIED_FIELDS:
        if not (isinstance(source.get(key), str) and source[key]):
            yield f"verified requires source.{key}"
    if not _iso_date(source.get("verified_at")):
        yield "verified requires source.verified_at as an ISO date"
    if not (isinstance(tolerance, str) and _AMOUNT.match(tolerance)):
        yield "verified requires a 'tolerance' amount such as \"0.00\""


def _immutable(source: Mapping[str, object]) -> bool:
    digest, path = source.get("sha256"), source.get("path")
    if isinstance(digest, str) and _SHA256.match(digest):
        return True
    return isinstance(path, str) and (REPO_ROOT / path).is_file()


def _iso_date(value: object) -> bool:
    try:
        return isinstance(value, str) and bool(date.fromisoformat(value))
    except ValueError:
        return False


def _ccnl_id(case: Mapping[str, object]) -> str | None:
    inputs = case.get("inputs")
    slug = inputs.get("ccnl_slug") if isinstance(inputs, dict) else None
    return slug.removesuffix(".json") if isinstance(slug, str) else None


def index(cases_dir: Path = CASES_DIR) -> dict[str, tuple[CaseEvidence, ...]]:
    """Map each CCNL to the valid reference cases that run it.

    A case that breaks a rule of :func:`verification_errors` is no evidence
    and is left out.

    Returns:
        The cases of each CCNL id, in file order; CCNL ids sorted.
    """
    found: dict[str, list[CaseEvidence]] = {}
    for path in sorted(cases_dir.glob("*.json")):
        case = load_case(path)
        ccnl_id = _ccnl_id(case)
        if ccnl_id is None or verification_errors(case):
            continue
        axes = case["axes"]
        evidence = CaseEvidence(
            path.name,
            str(case["verification"]),
            tuple(str(a) for a in axes) if isinstance(axes, list) else (),
        )
        found.setdefault(ccnl_id, []).append(evidence)
    return {ccnl: tuple(found[ccnl]) for ccnl in sorted(found)}


def load_baseline(path: Path = BASELINE) -> frozenset[str]:
    """Read the ``production`` CCNLs allowed without a ``verified`` case.

    Returns:
        Their ids.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    ids = (
        data.get("production_without_verified_case") if isinstance(data, dict) else None
    )
    return frozenset(str(i) for i in ids) if isinstance(ids, list) else frozenset()


def _evidence_errors(
    ccnl_id: str, tier: str, cases: tuple[CaseEvidence, ...], allowed: bool
) -> Iterator[str]:
    """Yield what the evidence of one CCNL lacks or what its baseline entry outran.

    Yields:
        One reason per failed rule.
    """
    verified = any(case.verification == "verified" for case in cases)
    if tier == "production" and not cases:
        yield "production without a valid reference case"
    if tier == "production" and not verified and not allowed:
        yield "production without a verified reference case"
    if allowed and (verified or tier != "production"):
        yield f"stale entry of {BASELINE.name}: remove {ccnl_id}"


def production_errors(
    knowledge_dir: Path,
    cases_dir: Path = CASES_DIR,
    baseline: frozenset[str] | None = None,
) -> list[str]:
    """Return the evidence the ``production`` CCNLs lack.

    Args:
        knowledge_dir: Knowledge directory holding ``agreement/``.
        cases_dir: Directory of the reference cases.
        baseline: CCNLs allowed without a ``verified`` case; read from
            :data:`BASELINE` when ``None``.

    Returns:
        ``"agreement/<id>.json: ..."`` messages; empty when each
        ``production`` CCNL has the cases it needs and the baseline is
        not stale.
    """
    cases = index(cases_dir)
    allowed = load_baseline() if baseline is None else baseline
    tiers = readiness_by_ccnl(knowledge_dir)
    return [
        f"agreement/{ccnl_id}.json: {reason}"
        for ccnl_id, tier in sorted(tiers.items())
        for reason in _evidence_errors(
            ccnl_id, tier, cases.get(ccnl_id, ()), ccnl_id in allowed
        )
    ]
