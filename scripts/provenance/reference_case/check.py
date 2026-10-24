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
  versioned in the repository; both, when stated, must agree), who checked
  it (``verified_by``) and when (``verified_at``), and how the expected
  values were produced without the engine (``independence``).  It also
  states the ``tolerance`` its amounts are compared with.

Every case names the complete outputs it validates in ``axes``
(:data:`AXES`) and the parts of a total or rates it pins in ``elements``
(:data:`ELEMENTS`); each expected value belongs to one of them
(:data:`AXIS_OF`), and each declared axis or element is backed by an
expected value.  A component or a rate never stands for a total: fixed
allowances do not validate the gross, an INPS rate does not validate the
amount of the contributions.  :func:`index` maps each
CCNL to its cases, and :func:`production_errors` binds the readiness tier
to its evidence in the gate, not by convention:

- a ``production`` CCNL needs at least one valid case;
- it needs a ``verified`` one too: no CCNL is exempt, so no promotion goes
  without an independent output;
- ``verification.verified_cases`` of every CCNL equals its ``verified``
  cases (:func:`verified_count_errors`).

The module reads raw JSON with the standard library only.
"""

from __future__ import annotations

import hashlib
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
    "CASES_DIR",
    "CASE_KEYS",
    "COMPONENTS",
    "ELEMENTS",
    "RULES",
    "SOURCE_KINDS",
    "STATUSES",
    "CaseEvidence",
    "count_by_status",
    "index",
    "load_case",
    "production_errors",
    "verification_errors",
    "verified_count_errors",
]

REPO_ROOT: Final = Path(__file__).resolve().parents[3]
CASES_DIR: Final = REPO_ROOT / "tests/knowledge/ccnl_engine/period/reference_case"

STATUSES: Final = ("verified", "source_linked")
#: Outputs the engine did not produce, the only sources of a ``verified`` case.
SOURCE_KINDS: Final = ("observed_payslip", "official_worked_example")
#: Complete outputs of a run: the only axes readiness counts.
AXES: Final = (
    "base_salary",
    "gross",
    "employee_contributions",
    "employer_contributions",
    "tax",
    "net",
    "tfr",
    "employer_cost",
)
#: Parts of a total: compared on their own, never as the total.
COMPONENTS: Final = (
    "fixed_allowances",
    "contribution_base",
    "taxable_income",
    "gross_irpef",
    "tax_deductions",
    "tax_credits",
    "tax_surcharges",
    "employee_funds",
    "employer_funds",
)
#: Rates and rules: they fix how a total is computed, not its amount.
RULES: Final = ("hourly_percentages", "employee_inps_rate", "employer_inps_rate")
#: Everything a case can pin besides a complete output.
ELEMENTS: Final = COMPONENTS + RULES
#: Axis or element of each expected value a case or a replay can pin.
#: Keys named ``annual_`` or ``ytd_`` read an amount of the year, as a
#: conguaglio or a termination prints it; the others read the run alone.
AXIS_OF: Final[Mapping[str, str]] = {
    "base_salary": "base_salary",
    "period_gross": "gross",
    "employee_contributions": "employee_contributions",
    "employer_contributions": "employer_contributions",
    "period_tax": "tax",
    "period_net": "net",
    "tfr_accrual": "tfr",
    "employer_cost": "employer_cost",
    "fixed_allowances": "fixed_allowances",
    "inps_base": "contribution_base",
    "ytd_taxable_income": "taxable_income",
    "annual_gross_irpef": "gross_irpef",
    "annual_tax_deductions": "tax_deductions",
    "period_tax_credits": "tax_credits",
    "period_surtax": "tax_surcharges",
    "employee_funds": "employee_funds",
    "employer_funds": "employer_funds",
    "hourly_percentages": "hourly_percentages",
    "employee_inps_rate": "employee_inps_rate",
    "employer_inps_rate": "employer_inps_rate",
}
#: Expected values a reference case can pin: the values a salary table
#: states, read by ``tests/integration/ccnl_engine/api/test_reference_cases.py``.
CASE_KEYS: Final = frozenset({
    "base_salary",
    "period_gross",
    "fixed_allowances",
    "hourly_percentages",
})
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
        axes: The complete outputs it validates.
        elements: The components and rates it pins.
    """

    file: str
    verification: str
    axes: tuple[str, ...]
    elements: tuple[str, ...] = ()

    def to_json(self) -> dict[str, object]:
        """Return the evidence as a JSON object.

        Returns:
            The file, status and axes.
        """
        return {
            "file": self.file,
            "verification": self.verification,
            "axes": list(self.axes),
            "elements": list(self.elements),
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


def _labels(case: Mapping[str, object], key: str) -> list[object] | None:
    value = case.get(key, [])
    return value if isinstance(value, list) else None


def _axes_errors(case: Mapping[str, object]) -> Iterator[str]:
    """Yield what is wrong with the axes and elements a case declares.

    Yields:
        One reason per unknown axis or element, per expected value of none
        or of one the case does not declare, and per declared axis or
        element no expected value backs.
    """
    axes, elements = _labels(case, "axes"), _labels(case, "elements")
    if axes is None or elements is None or not (axes or elements):
        yield (
            "'axes' and 'elements' must be lists, not both empty, of "
            + ", ".join(AXES + ELEMENTS)
        )
        return
    yield from (f"unknown axis {axis!r}" for axis in axes if axis not in AXES)
    yield from (f"unknown element {e!r}" for e in elements if e not in ELEMENTS)
    expected = case.get("expected")
    backed = set()
    for key in expected if isinstance(expected, dict) else {}:
        label = AXIS_OF.get(key)
        backed.add(label)
        if label is None:
            yield f"expected value {key!r} belongs to no axis or element"
        elif key not in CASE_KEYS:
            yield f"expected value {key!r} is not read by the reference case runner"
        elif label in AXES and label not in axes:
            yield f"expected value {key!r} needs the axis {label!r} in 'axes'"
        elif label in ELEMENTS and label not in elements:
            yield f"expected value {key!r} needs the element {label!r} in 'elements'"
    yield from (
        f"{label!r} is declared but no expected value backs it"
        for label in [*axes, *elements]
        if label in AXES + ELEMENTS and label not in backed
    )


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
    """Return whether the source is pinned: by its digest, its file, or both.

    A versioned file and a digest stated together must agree.

    Returns:
        ``True`` for a valid digest, an existing file, and no mismatch.
    """
    digest, path = source.get("sha256"), source.get("path")
    pinned = isinstance(digest, str) and bool(_SHA256.match(digest))
    file = REPO_ROOT / path if isinstance(path, str) else None
    if file is None or not file.is_file():
        return pinned
    actual = hashlib.sha256(file.read_bytes()).hexdigest()
    return digest is None or actual == digest


def _iso_date(value: object) -> bool:
    try:
        return isinstance(value, str) and bool(date.fromisoformat(value))
    except ValueError:
        return False


def _ccnl_id(case: Mapping[str, object]) -> str | None:
    inputs = case.get("inputs")
    ccnl_id = inputs.get("ccnl_id") if isinstance(inputs, dict) else None
    return ccnl_id if isinstance(ccnl_id, str) else None


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
        evidence = CaseEvidence(
            path.name,
            str(case["verification"]),
            tuple(str(a) for a in _labels(case, "axes") or ()),
            tuple(str(e) for e in _labels(case, "elements") or ()),
        )
        found.setdefault(ccnl_id, []).append(evidence)
    return {ccnl: tuple(found[ccnl]) for ccnl in sorted(found)}


def _evidence_errors(cases: tuple[CaseEvidence, ...]) -> Iterator[str]:
    """Yield what the evidence of one ``production`` CCNL lacks.

    Yields:
        One reason per failed rule.
    """
    if not cases:
        yield "production without a valid reference case"
    if not any(case.verification == "verified" for case in cases):
        yield "production without a verified reference case"


def verified_count_errors(
    knowledge_dir: Path, cases_dir: Path = CASES_DIR
) -> list[str]:
    """Return the CCNLs whose ``verification.verified_cases`` is not the count.

    The field is what the engine reports as externally compared
    (:class:`~ccnl_engine.provenance.ruleset.assurance.models.AssuranceAxes`),
    so it must equal the ``verified`` reference cases that run the CCNL.

    Returns:
        ``"agreement/<id>.json: ..."`` messages; empty when every count holds.
    """
    cases = index(cases_dir)
    errors = []
    for path in sorted((knowledge_dir / "agreement").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        verification = data.get("verification") if isinstance(data, dict) else None
        if not isinstance(verification, dict):
            continue
        recorded = verification.get("verified_cases", 0)
        actual = sum(c.verification == "verified" for c in cases.get(path.stem, ()))
        if recorded != actual:
            errors.append(
                f"agreement/{path.name}: verification.verified_cases is "
                f"{recorded}, the verified reference cases are {actual}"
            )
    return errors


def production_errors(knowledge_dir: Path, cases_dir: Path = CASES_DIR) -> list[str]:
    """Return the evidence the ``production`` CCNLs lack.

    A ``production`` CCNL needs a valid reference case and a ``verified``
    one, checked against an output the engine did not produce.  No CCNL is
    exempt.

    Args:
        knowledge_dir: Knowledge directory holding ``agreement/``.
        cases_dir: Directory of the reference cases.

    Returns:
        ``"agreement/<id>.json: ..."`` messages; empty when each
        ``production`` CCNL has the cases it needs.
    """
    cases = index(cases_dir)
    tiers = readiness_by_ccnl(knowledge_dir)
    return [
        f"agreement/{ccnl_id}.json: {reason}"
        for ccnl_id, tier in sorted(tiers.items())
        if tier == "production"
        for reason in _evidence_errors(cases.get(ccnl_id, ()))
    ]
